import pandas as pd
import os
import sys

# Add src to path to import Calculator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.calculator import Calculator

def main(platform='futu'):
    """
    Main function: Reads trading records and calculates annual tax profits.
    """
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Read history file
    history_file = f'data/{platform}_history.csv'
    if not os.path.exists(history_file):
        print(f"Error: File {history_file} does not exist")
        return
    
    df = pd.read_csv(history_file)
    
    # Sort by transaction time
    df['交易时间'] = pd.to_datetime(df['交易时间'])
    df['年份'] = df['交易时间'].dt.strftime('%Y')
    df = df.sort_values('交易时间', kind='stable')
    
    calculator = Calculator()
    
    cur_year = None
    
    # Process each trade
    for trade in df.itertuples():
        # Check for year change
        if cur_year is not None and trade.年份 != cur_year:
            # Save end-of-year snapshot for previous year
            calculator.save_holdings_snapshot(cur_year, 'end', platform, df)
            
            # Save year holdings file (merge start/end)
            calculator.save_year_holdings_file(cur_year, platform)
            
            # Summary previous year profits
            save_path = f"data/{platform}_moving_avg_profit_{cur_year}.csv"
            calculator.summary_year(calculator.all_profits, save_path)
            print(f"Saved {cur_year} annual profit: {save_path}")
            calculator.all_profits = []
            
            # Save start-of-year snapshot for new year
            calculator.save_holdings_snapshot(trade.年份, 'start', platform, df)
        
        # If first year, save start snapshot
        if cur_year is None:
            calculator.save_holdings_snapshot(trade.年份, 'start', platform, df)
        
        cur_year = trade.年份
        
        # Create a dictionary-like interface for compatibility with Calculator
        # using _asdict() from namedtuple but filtering/mapping keys if necessary
        # The Calculator expects keys: '股票代码', '数量', '成交价格', '合计手续费', etc.
        # itertuples attributes will match column names but spaces/special chars might be an issue?
        # Pandas replaces spaces with _ in namedtuples usually, but Chinese characters are fine.
        
        trade_dict = trade._asdict()
        # Ensure we're passing a dict that keys can be accessed via ['key']
        # itertuples returns a namedtuple where access is .attribute
        
        # Determine trade side
        if trade.买卖方向 == "OrderSide.Buy":
            calculator.process_buy(trade_dict)
        elif trade.买卖方向 == "OrderSide.Sell":
            profit_records = calculator.process_sell(trade_dict)
            calculator.all_profits.extend(profit_records)
    
    # Summary for the last year
    if cur_year is not None:
        calculator.save_holdings_snapshot(cur_year, 'end', platform, df)
        calculator.save_year_holdings_file(cur_year, platform)
        
        save_path = f"data/{platform}_moving_avg_profit_{cur_year}.csv"
        calculator.summary_year(calculator.all_profits, save_path)
        print(f"Saved {cur_year} annual profit: {save_path}")

if __name__ == '__main__':
    platform = sys.argv[1] if len(sys.argv) > 1 else 'futu'
    main(platform)
