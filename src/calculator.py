from collections import defaultdict
import re
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

class Calculator:
    def __init__(self):
        # holdings: {'quantity': Decimal, 'avg_cost': Decimal}
        self.holdings = defaultdict(lambda: {'quantity': Decimal('0'), 'avg_cost': Decimal('0')})
        self.year_holdings = {}
        self.all_profits = []

    def process_buy(self, trade):
        """
        Process a buy trade.
        Updates holdings quantity and average cost (fees included in cost).
        """
        symbol = str(trade['股票代码'])
        # Convert to Decimal for precision
        qty = Decimal(str(trade['数量']))
        price = Decimal(str(trade['成交价格']))
        fee = Decimal(str(trade['合计手续费']))
        
        hold = self.holdings[symbol]
        cur_qty = hold["quantity"]
        
        # Calculate new average cost: (old_qty * old_cost + new_qty * new_price + fee) / new_total_qty
        total_cost = cur_qty * hold["avg_cost"] + qty * price + fee
        new_qty = cur_qty + qty
        
        if new_qty != 0:
            hold["avg_cost"] = total_cost / new_qty
        else:
            hold["avg_cost"] = Decimal('0')
            
        hold["quantity"] = new_qty

    def process_sell(self, trade):
        """
        Process a sell trade.
        Updates holdings quantity and calculates profit.
        Returns a list of profit records.
        """
        symbol = str(trade['股票代码'])
        qty = Decimal(str(trade['数量']))
        price = Decimal(str(trade['成交价格']))
        fee = Decimal(str(trade['合计手续费']))
        currency = trade['结算币种']
        trade_time = trade['交易时间']
        
        hold = self.holdings[symbol]
        cur_qty = hold["quantity"]
        
        records = []
        
        # Closed quantity = min(sell_qty, holding_qty)
        close_qty = min(qty, cur_qty)
        
        if close_qty > 0:
            # Total cost of closed portion = closed_qty * avg_cost
            total_cost = close_qty * hold["avg_cost"]
            
            # Pro-rated fee = total_fee * (closed_qty / sell_qty)
            if qty > 0:
                fee_ratio = close_qty / qty
            else:
                fee_ratio = Decimal('0')
                
            allocated_fee = fee * fee_ratio
            
            # Profit = Revenue - Cost - Fee
            profit = close_qty * price - total_cost - allocated_fee
            
            records.append({
                "配对原因": "平仓了结",
                "股票代码": symbol,
                "卖出价格": float(price),
                "成本价": float(hold["avg_cost"]),
                "数量": float(close_qty),
                "利润": float(profit),
                "时间": trade_time,
                "结算币种": currency
            })
        
        # Update quantity: old_qty - sell_qty
        hold["quantity"] = cur_qty - qty
        # Average cost remains unchanged on sell
        
        return records

    def save_holdings_snapshot(self, year, timing, platform, df):
        """
        Save a snapshot of current holdings.
        timing: 'start' or 'end'
        """
        snapshot = []
        
        for symbol, hold in self.holdings.items():
            if hold["quantity"] > 0:
                # Find currency from history (fallback to 'Unknown')
                currency_info = df[df['股票代码'] == symbol]
                currency = currency_info.iloc[0]['结算币种'] if not currency_info.empty else 'Unknown'
                
                snapshot.append({
                    "股票代码": symbol,
                    "持有数量": float(hold["quantity"]),
                    "平均成本": float(hold["avg_cost"]),
                    "结算币种": currency
                })
        
        if year not in self.year_holdings:
            self.year_holdings[year] = {}
        self.year_holdings[year][timing] = snapshot

    def save_year_holdings_file(self, year, platform):
        """
        Merge start and end snapshots for a year and save to CSV.
        """
        if year not in self.year_holdings:
            return
        
        data = self.year_holdings[year]
        rows = []
        
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
            df_output = df_output.sort_values(['结算币种', '股票代码'])
            
            save_path = f"data/{platform}_holdings_{year}.csv"
            df_output.to_csv(save_path, index=False, encoding='utf-8-sig')
            print(f"  已保存 {year} 年度持仓: {save_path}")

    def summary_year(self, year_profits, save_path):
        """
        Summarize annual profits by currency.
        """
        if not year_profits:
            return
        
        df_result = pd.DataFrame(year_profits)
        
        # Create a copy to avoid modifying the input list
        final_list = list(year_profits) 
        
        for currency, sub_df in df_result.groupby("结算币种"):
            # Method 1: Total Profit (Net)
            total_profits = sub_df["利润"].sum()
            final_list.append({
                "配对原因": "年度汇总",
                "股票代码": "按年度计算",
                "卖出价格": 0,
                "成本价": 0,
                "数量": 0,
                "利润": total_profits,
                "时间": sub_df.iloc[-1]["时间"],
                "结算币种": currency
            })
            
            # Method 2: Positive Profit Only
            total_profits_pos = sub_df[sub_df["利润"] > 0]["利润"].sum()
            final_list.append({
                "配对原因": "年度汇总",
                "股票代码": "按单次计算",
                "卖出价格": 0,
                "成本价": 0,
                "数量": 0,
                "利润": total_profits_pos,
                "时间": sub_df.iloc[-1]["时间"],
                "结算币种": currency
            })
        
        df_final = pd.DataFrame(final_list)
        df_final.to_csv(save_path, index=False, encoding='utf-8-sig')
