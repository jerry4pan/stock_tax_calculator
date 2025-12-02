[中文说明见此](README_zh.md)

# Stock Tax Calculator

To comply with CRS regulations and facilitate tax reporting, this project leverages quantitative APIs to automatically fetch stock trading records from multiple platforms and calculate profits under different matching methods, providing a reliable basis for tax declaration.
Currently, **Futu** and **Longbridge** are supported. Please make sure to enable the relevant platform APIs and prepare the required keys and gateway programs before use.

## Features
- Automatically fetch stock trading and cash flow records
- Support multiple matching methods (e.g., FIFO, weighted average, moving weighted average) for annual profit calculation
- Summarize profits by year, platform, currency, method, etc., to assist with tax reporting

## Supported Platforms
- Futu
- Longbridge

## Main Files
- `get_tax1.py` (Weighted Average Method): Calculate annual profit using weighted average cost
- `get_tax2.py` (Moving Weighted Average Method): Calculate annual profit using moving weighted average cost
- `get_tax_moving_avg.py` (Moving Weighted Average + Holdings Snapshot): Calculate annual profit and output year-start/year-end holdings
- `report.py`: Summary report generation script
- `data/`: Stores transaction records, profit details, annual summaries, holdings snapshots, etc.

## Data Download Process for Each Platform

### Futu
1. **API Preparation:**
   - Install and start the Futu OpenD gateway, ensuring local port 11111 is available.
   - Refer to the [Futu OpenAPI documentation](https://openapi.futunn.com/) to obtain your API key.
2. **Download Trading Records:**
   - Run `futu/download.py` to batch download all account historical orders, generating `data/futu_history_raw.csv`.
3. **Format Conversion:**
   - Run `futu/export.py` to convert the raw data to standard format, generating `data/futu_history.csv`.
4. **Generate Annual Profit Details:**
   - Run `python get_tax1.py futu` or `python get_tax2.py futu` to automatically generate files like `data/futu_weighted_avg_profit_YEAR.csv`, `data/futu_moving_avg_profit_YEAR.csv`, etc.
   - Run `python get_tax_moving_avg.py futu` to generate profit files plus annual holdings snapshot files `data/futu_holdings_YEAR.csv`.

### Longbridge
1. **API Preparation:**
   - Register and enable Longbridge OpenAPI, and obtain your API key.
   - Configure environment variables or fill in the API key in the script.
2. **Download Trading Records:**
   - Run `longbridge/download_trade_flow.py` to download historical orders, generating `data/longbridge_history.csv`.
3. **Download Cash Flow:**
   - Run `longbridge/download_cash_flow.py` to generate `data/longbridge_cash.csv`.
4. **Generate Annual Profit Details:**
   - Run `python get_tax1.py longbridge` or `python get_tax2.py longbridge` to automatically generate files like `data/longbridge_weighted_avg_profit_YEAR.csv`, `data/longbridge_moving_avg_profit_YEAR.csv`, etc.
   - Run `python get_tax_moving_avg.py longbridge` to generate profit files plus annual holdings snapshot files `data/longbridge_holdings_YEAR.csv`.

## report Script

---

### Description

The `report` script is used to automatically aggregate and display tax profit data by platform, method, currency, and year, making it easy for users to view and prepare for tax reporting.

#### Main Features
- Automatically traverse all files in the `data/` directory matching the `$platform_$method_profit_$year.csv` pattern
- Filter entries where the matching reason is "年度汇总" (annual summary)
- Print annual tax tables by method
- Each table summarizes profits by platform, year, currency, and stock code
- Supports custom filtering and export

#### Usage
1. Make sure the annual summary CSV files are prepared in the `data/` directory as described above
2. Run:
   ```bash
   python report.py
   ```
3. The script will automatically output annual tax tables for each method

#### Input
- Requires files like `futu_method1_profit_2023.csv`, `longbridge_method2_profit_2024.csv`, etc. in the `data/` directory
- Files must contain fields such as "配对原因" (matching reason), "结算币种" (settlement currency), "股票代码" (stock code), "利润" (profit), etc.

#### Output
- The console will output annual profit tables for each method (e.g., method1, method2), grouped by platform, year, currency, and stock code
- You can modify the script as needed to filter by specific platform, currency, year, or export to Excel

## Holdings Snapshot Feature

When using the `get_tax_moving_avg.py` script, it automatically generates annual holdings snapshot files for easy account verification.

### Output File Format
- File name: `data/{platform}_holdings_{year}.csv`
- Field descriptions:
  - `股票代码` (Stock Code): Stock ticker symbol
  - `结算币种` (Settlement Currency): Settlement currency
  - `年初持有数量` (Year-Start Quantity): Holdings before the first trade of the year
  - `年初平均成本` (Year-Start Avg Cost): Average cost before the first trade of the year
  - `年末持有数量` (Year-End Quantity): Holdings after the last trade of the year
  - `年末平均成本` (Year-End Avg Cost): Average cost after the last trade of the year

### Usage Example
```bash
python get_tax_moving_avg.py futu
# Will generate:
# data/futu_moving_avg_profit_2023.csv (profit details)
# data/futu_holdings_2023.csv (2023 holdings snapshot)
# data/futu_moving_avg_profit_2024.csv (profit details)
# data/futu_holdings_2024.csv (2024 holdings snapshot)
```

---

## Dependencies
- Python 3.7+
- pandas

Install dependencies:
```bash
pip install pandas
```

## Issues
If you have further requirements or questions, feel free to open an issue!
