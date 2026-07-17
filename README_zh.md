# 股票税务计算器

为辅助 CRS 相关记账与报税准备，本项目利用券商量化 API 自动获取股票交易记录，并按不同配对方式（如移动加权平均）计算盈利。
现在已经支持**富途牛牛**，使用前请自行开通相关平台的 API 并准备好密钥和网关程序。

## 免责声明

**本项目仅供个人记账与参考，不构成任何税务、法律或投资建议。** 计算结果取决于所选配对方式与本地数据，可能与税务机关认定口径不一致。请自行核对结果并自行承担申报责任。因使用本软件产生的任何损失，作者不承担责任。

## 隐私说明

`data/` 目录及所有 `*.csv` 已加入 `.gitignore`。**请勿将真实账户或交易数据提交到仓库**（包括使用 `git add -f`）。若需示例数据，请使用完全虚构的样例文件。

## 功能简介
- 自动获取股票交易流水、资金流水
- 支持多种配对方式（如FIFO、加权等）计算年度盈利
- 按年度、平台、币种、方式等多维度汇总利润，辅助报税

## 支持平台
- 富途牛牛（Futu）

## 快速开始

> **提示：** 开始前请确保富途 OpenD 网关已启动。

### 第1步：下载交易流水

指定日期范围下载历史订单。已下载的交易流水可复用，按起止时间增量下载即可。

```bash
python futu/download.py --start 2022-01-01 --end 2024-12-31
```

### 第2步：流水格式转换

将所有原始数据文件转换并统一合并到 `futu_history.csv`：

```bash
python futu/export.py
```

### 第3步：生成年度利润明细及持仓快照

运行推荐的计算脚本，生成年度利润明细和持仓快照：

```bash
python get_tax_moving_avg.py futu
```

### 第4步：查看税务报表

运行报表脚本，输出年度利润汇总，了解报税情况：

```bash
python report.py
```

## 主要文件说明
- `get_tax_moving_avg.py`（移动加权平均法 + 持仓快照）⭐ **推荐**：计算年度盈利并输出每年年初/年末持仓情况，便于核对账户状态
- `report.py`：汇总报表生成脚本
- `data/`：存放各平台流水、利润明细、年度汇总、持仓快照等csv文件

## 各平台数据下载流程

### 富途牛牛（Futu）
1. **API准备**：
   - 安装富途OpenD网关并启动，确保本地11111端口可用。
   - 参考[富途OpenAPI文档](https://openapi.futunn.com/)获取API密钥。
2. **下载交易流水**：
   - 运行 `futu/download.py`，指定起止日期，自动批量下载所有账户的历史订单，生成 `data/futu_history_raw_起始日期_结束日期.csv`。
   - 使用示例：
     ```bash
     python futu/download.py --start 2022-01-01 --end 2024-12-31
     ```
   - 参数说明：
     - `--start`：开始日期，格式 YYYY-MM-DD（必填）
     - `--end`：结束日期，格式 YYYY-MM-DD（必填）
   - 输出文件：`data/futu_history_raw_20220101_20241231.csv`
3. **格式转换**：
   - 运行 `futu/export.py`，将原始数据转换为标准格式，生成 `data/futu_history.csv`。
   - 注意：`export.py` 会自动合并所有以 `futu_history_raw` 开头的 CSV 文件。
4. **生成年度利润明细**：
   - 运行 `python get_tax_moving_avg.py futu`，除了生成利润文件外，还会生成年度持仓快照文件 `data/futu_holdings_年份.csv`。


## report脚本说明

`report` 脚本用于自动汇总和展示各平台、各方式、各币种、各年度的税务利润数据，便于用户直观查看和后续报税。

### 主要功能
- 自动遍历 `data/` 目录下所有符合 `$platform_$method_profit_$year.csv` 格式的文件
- 筛选“配对原因为年度汇总”的条目
- 按方式（method）分别打印年度税款表
- 每个表按平台、年份、币种、股票代码分组汇总利润
- 支持自定义筛选、导出等扩展

### 使用方法
1. 确保已按前述流程准备好 `data/` 目录下的年度汇总csv文件
2. 运行：
   ```bash
   python report.py
   ```
3. 程序会自动输出每种方式下的年度税款表

### 输入说明
- 需要 `data/` 目录下有如 `futu_method1_profit_2023.csv` 等文件
- 文件需包含“配对原因”、“结算币种”、“股票代码”、“利润”等字段

### 输出说明
- 控制台分别输出每种方式（如method1、method2）下，按平台、年份、币种、股票代码分组的年度利润表
- 可根据需要修改脚本，筛选特定平台、币种、年份或导出为Excel

## 持仓快照功能

使用 `get_tax_moving_avg.py` 脚本时，会自动生成年度持仓快照文件，便于核对账户状态。

### 输出文件格式
- 文件名：`data/{platform}_holdings_{year}.csv`
- 字段说明：
  - `股票代码`：股票代码
  - `结算币种`：结算货币
  - `年初持有数量`：该年度第一笔交易前的持有数量
  - `年初平均成本`：该年度第一笔交易前的平均成本
  - `年末持有数量`：该年度最后一笔交易后的持有数量
  - `年末平均成本`：该年度最后一笔交易后的平均成本

### 使用示例
```bash
python get_tax_moving_avg.py futu
# 会生成：
# data/futu_moving_avg_profit_2023.csv（利润明细）
# data/futu_holdings_2023.csv（2023年持仓快照）
# data/futu_moving_avg_profit_2024.csv（利润明细）
# data/futu_holdings_2024.csv（2024年持仓快照）
```

---

## 依赖要求

安装依赖（推荐使用虚拟环境）：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 许可证

本项目采用 [MIT License](LICENSE)。
