import pandas as pd
from collections import defaultdict
import os


def process_buy(holdings, trade):
    """
    处理买入操作
    更新持有数量和平均成本(手续费计入成本)
    """
    symbol = str(trade['股票代码'])
    qty = trade['数量']
    price = trade['成交价格']
    fee = trade['合计手续费']
    
    hold = holdings[symbol]
    cur_qty = hold["quantity"]
    
    # 计算新的平均成本: (原持有数量 × 原平均成本 + 买入数量 × 买入价格 + 本次手续费) / 新持有数量
    total_cost = cur_qty * hold["avg_cost"] + qty * price + fee
    new_qty = cur_qty + qty
    hold["avg_cost"] = total_cost / new_qty if new_qty > 0 else 0
    hold["quantity"] = new_qty


def process_sell(holdings, trade):
    """
    处理卖出操作
    仅更新持有数量, 并计算利润
    """
    symbol = str(trade['股票代码'])
    qty = trade['数量']
    price = trade['成交价格']
    fee = trade['合计手续费']
    currency = trade['结算币种']
    trade_time = trade['交易时间']
    
    hold = holdings[symbol]
    cur_qty = hold["quantity"]
    
    records = []
    
    # 了结数量 = min(卖出数量, 持仓数量)
    close_qty = min(qty, cur_qty)
    
    if close_qty > 0:
        # 计算了结总成本 = 了结数量 × 原平均成本
        total_cost = close_qty * hold["avg_cost"]
        
        # 对应比例手续费 = 本次手续费 × (了结数量 / 卖出数量)
        fee_ratio = close_qty / qty if qty > 0 else 0
        allocated_fee = fee * fee_ratio
        
        # 计算利润 = 了结数量 × 卖出价格 - 了结总成本 - 本次交易对应比例的手续费
        profit = close_qty * price - total_cost - allocated_fee
        
        records.append({
            "配对原因": "平仓了结",
            "股票代码": symbol,
            "卖出价格": price,
            "成本价": hold["avg_cost"],
            "数量": close_qty,
            "利润": profit,
            "时间": trade_time,
            "结算币种": currency
        })
    
    # 数量更新: 持有数量 = 原持有数量 - 卖出数量
    hold["quantity"] = cur_qty - qty
    # 成本更新: 平均成本保持不变
    
    return records


def summary_year(all_profits, save_path):
    """
    年度汇总: 按币种分组, 生成两种汇总方式
    """
    if not all_profits:
        return
    
    df_result = pd.DataFrame(all_profits)
    
    for currency, sub_df in df_result.groupby("结算币种"):
        # 汇总方式一: 按年度计算(包含正利润和负利润)
        total_profits = sub_df["利润"].sum()
        all_profits.append({
            "配对原因": "年度汇总",
            "股票代码": "按年度计算",
            "卖出价格": 0,
            "成本价": 0,
            "数量": 0,
            "利润": total_profits,
            "时间": sub_df.iloc[-1]["时间"],
            "结算币种": currency
        })
        
        # 汇总方式二: 按单次计算(仅统计正利润)
        total_profits = sub_df[sub_df["利润"] > 0]["利润"].sum()
        all_profits.append({
            "配对原因": "年度汇总",
            "股票代码": "按单次计算",
            "卖出价格": 0,
            "成本价": 0,
            "数量": 0,
            "利润": total_profits,
            "时间": sub_df.iloc[-1]["时间"],
            "结算币种": currency
        })
    
    # 保存到CSV文件
    df_result = pd.DataFrame(all_profits)
    df_result.to_csv(save_path, index=False, encoding='utf-8-sig')


def save_holdings_snapshot(holdings, year, timing, platform, df, year_holdings):
    """
    保存持仓快照
    timing: 'start' 或 'end'
    year_holdings: 存储年度持仓数据的字典
    """
    snapshot = []
    
    # 遍历所有持仓
    for symbol, hold in holdings.items():
        if hold["quantity"] > 0:
            # 从交易历史中查找该股票的结算币种
            currency_info = df[df['股票代码'] == symbol]
            currency = currency_info.iloc[0]['结算币种'] if not currency_info.empty else 'Unknown'
            
            snapshot.append({
                "股票代码": symbol,
                "持有数量": hold["quantity"],
                "平均成本": hold["avg_cost"],
                "结算币种": currency
            })
    
    # 将快照存入年度持仓字典
    if year not in year_holdings:
        year_holdings[year] = {}
    year_holdings[year][timing] = snapshot


def save_year_holdings_file(year, year_holdings, platform):
    """
    将同一年的年初和年末持仓合并保存到一个文件
    """
    if year not in year_holdings:
        return
    
    data = year_holdings[year]
    rows = []
    
    # 获取年初和年末的所有股票代码
    start_data = {item['股票代码']: item for item in data.get('start', [])}
    end_data = {item['股票代码']: item for item in data.get('end', [])}
    all_symbols = set(start_data.keys()) | set(end_data.keys())
    
    for symbol in sorted(all_symbols):
        start_item = start_data.get(symbol, {})
        end_item = end_data.get(symbol, {})
        
        rows.append({
            "股票代码": symbol,
            "结算币种": start_item.get('结算币种', end_item.get('结算币种', 'Unknown')),
            "年初持有数量": start_item.get('持有数量', 0),
            "年初平均成本": start_item.get('平均成本', 0),
            "年末持有数量": end_item.get('持有数量', 0),
            "年末平均成本": end_item.get('平均成本', 0)
        })
    
    if rows:
        df_output = pd.DataFrame(rows)
        # 按结算币种和股票代码排序
        df_output = df_output.sort_values(['结算币种', '股票代码'])
        
        save_path = f"data/{platform}_holdings_{year}.csv"
        df_output.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"  已保存 {year} 年度持仓: {save_path}")


def main(platform='futu'):
    """
    主函数: 读取交易记录, 按年度计算利润
    """
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 读取交易历史数据
    history_file = f'data/{platform}_history.csv'
    if not os.path.exists(history_file):
        print(f"错误: 文件 {history_file} 不存在")
        return
    
    df = pd.read_csv(history_file)
    
    # 按照交易时间排序(稳定排序)
    df['交易时间'] = pd.to_datetime(df['交易时间'])
    df['年份'] = df['交易时间'].dt.strftime('%Y')
    df = df.sort_values('交易时间', kind='stable')
    
    # 初始化持仓字典和利润列表
    holdings = defaultdict(lambda: {'quantity': 0.0, 'avg_cost': 0.0})
    all_profits = []
    cur_year = None
    year_holdings = {}  # 存储每年的持仓快照
    
    # 遍历每笔交易
    for _, trade in df.iterrows():
        # 检查年份变化
        if cur_year is not None and trade["年份"] != cur_year:
            # 保存上一年度年末持仓
            save_holdings_snapshot(holdings, cur_year, 'end', platform, df, year_holdings)
            
            # 保存上一年度持仓文件（合并年初和年末）
            save_year_holdings_file(cur_year, year_holdings, platform)
            
            # 汇总上一年度利润
            save_path = f"data/{platform}_moving_avg_profit_{cur_year}.csv"
            summary_year(all_profits, save_path)
            print(f"已保存 {cur_year} 年度利润: {save_path}")
            all_profits = []
            
            # 保存新年度年初持仓
            save_holdings_snapshot(holdings, trade["年份"], 'start', platform, df, year_holdings)
        
        # 如果是第一年的第一笔交易，保存年初持仓（此时应为空）
        if cur_year is None:
            save_holdings_snapshot(holdings, trade["年份"], 'start', platform, df, year_holdings)
        
        cur_year = trade["年份"]
        
        # 判断买卖方向
        if trade['买卖方向'] == "OrderSide.Buy":
            # 买入处理: 更新持有数量和成本
            process_buy(holdings, trade)
        elif trade['买卖方向'] == "OrderSide.Sell":
            # 卖出处理: 仅更新持有数量, 并计算利润
            profit_records = process_sell(holdings, trade)
            all_profits.extend(profit_records)
    
    # 汇总最后年度
    if cur_year is not None:
        # 保存最后年度年末持仓
        save_holdings_snapshot(holdings, cur_year, 'end', platform, df, year_holdings)
        
        # 保存最后年度持仓文件（合并年初和年末）
        save_year_holdings_file(cur_year, year_holdings, platform)
        
        save_path = f"data/{platform}_moving_avg_profit_{cur_year}.csv"
        summary_year(all_profits, save_path)
        print(f"已保存 {cur_year} 年度利润: {save_path}")


if __name__ == '__main__':
    import sys
    platform = sys.argv[1] if len(sys.argv) > 1 else 'futu'
    main(platform)
