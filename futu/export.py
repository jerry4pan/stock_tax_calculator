import pandas as pd
import os
import glob

def main():
    # 路径
    data_dir = 'data'
    out_path = os.path.join(data_dir, 'futu_history.csv')
    
    # 确保data目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 目标表头
    target_columns = [
        '股票代码', '数量', '成交金额', '买卖方向', '结算币种', '合计手续费', '交易时间'
    ]

    # 查找所有以 futu_history_raw 开头的CSV文件
    pattern = os.path.join(data_dir, 'futu_history_raw*.csv')
    raw_files = glob.glob(pattern)
    
    if not raw_files:
        print(f'未找到匹配的文件: {pattern}')
        return
    
    print(f'找到 {len(raw_files)} 个原始文件:')
    for f in sorted(raw_files):
        print(f'  - {os.path.basename(f)}')
    
    # 读取并合并所有原始数据
    df_list = []
    for file_path in raw_files:
        try:
            temp_df = pd.read_csv(file_path)
            df_list.append(temp_df)
            print(f'已读取: {os.path.basename(file_path)} ({len(temp_df)} 条记录)')
        except Exception as e:
            print(f'读取失败 {os.path.basename(file_path)}: {e}')
    
    if not df_list:
        print('没有成功读取任何文件')
        return
    
    # 合并所有数据
    df = pd.concat(df_list, ignore_index=True)

    # 生成目标DataFrame
    out_df = pd.DataFrame()
    out_df['股票代码'] = df['code']
    out_df['数量'] = df['dealt_qty']
    out_df['成交价格'] = df['dealt_avg_price']
    out_df['买卖方向'] = df['trd_side'].replace({'BUY': 'OrderSide.Buy', 'SELL': 'OrderSide.Sell'})
    out_df['结算币种'] = df['currency']
    out_df['合计手续费'] = df["合计手续费"]  # futu原始数据无手续费字段
    out_df['交易时间'] = df['create_time'].str[:19]  # 去除毫秒
    
    # 按交易时间倒序排序（最新的在前）
    out_df['交易时间_排序'] = pd.to_datetime(out_df['交易时间'])
    out_df = out_df.sort_values('交易时间_排序', ascending=False).drop(columns=['交易时间_排序'])
    out_df = out_df.reset_index(drop=True)

    # 保存为目标格式
    out_df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f'\n合并完成: 共 {len(out_df)} 条记录')
    print(f'已导出到 {out_path}')

if __name__ == '__main__':
    main() 