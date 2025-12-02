import os
import re
import pandas as pd
from glob import glob

# 汇总结果列表
results = []

# 遍历data目录下所有利润文件(支持 method1, method2, moving_avg 等)
for file in glob('data/*_profit_*.csv'):
    
    filename = os.path.basename(file)
    parts = filename.split(".")[0].split("_")
    
    # 解析文件名: platform_method_profit_year.csv 或 platform_moving_avg_profit_year.csv
    if len(parts) == 4:
        platform, method, _, year = parts
    elif len(parts) == 5:
        platform, method1, method2, _, year = parts
        method = f"{method1}_{method2}"
    else:
        continue
    df = pd.read_csv(file)
    # 只保留配对原因为年度汇总的条目
    df = df[df['配对原因'] == '年度汇总']
    for _, row in df.iterrows():
        results.append({
            '平台': platform,
            '方式': method,
            '年份': year,
            '币种': row['结算币种'],
            '股票代码': row['股票代码'],
            '利润': row['利润'],
        })

# 转为DataFrame
summary_df = pd.DataFrame(results)
# 获取所有方式
methods = summary_df['方式'].unique()
tax_methods= summary_df['股票代码'].unique()

for method in methods:
    for tax_method in tax_methods:
        print(f'\n方式: {method},计税方式：{tax_method}')
        sub_df = summary_df[(summary_df['方式'] == method) & (summary_df['股票代码'] == tax_method)]
        grouped = sub_df.groupby(['年份', '币种']).agg({'利润': 'sum'}).reset_index()
        
        # 格式化输出，确保对齐
        print(f"{'年份':>6}  {'币种':>6}  {'利润':>20}")
        for _, row in grouped.iterrows():
            profit = f"{row['利润']:,.4f}"
            print(f"{row['年份']:>6}  {row['币种']:>6}  {profit:>20}") 