# Agent Guide for Stock Tax Calculator

This repository contains Python scripts for calculating stock taxes based on trading records from platforms like Futu.

## 1. Environment & Build

### Setup
- Python 3.7+ is required.
- **Virtual Environment**: Use `.venv` for all dependency management.
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### Build
- There is no build step; these are interpreted Python scripts.

### Testing
- **Current State**: There are no automated tests (no `tests/` directory or `pytest` config).
- **Running Verification**:
  - To verify changes, run the main scripts with sample data (ensure `data/` directory has CSVs):
    ```bash
    source .venv/bin/activate
    python get_tax_moving_avg.py futu
    python report.py
    ```
- **Agent Instruction**:
  - Always use the virtual environment for running scripts and tests.
  - Recommended test command: `.venv/bin/pytest` or `source .venv/bin/activate && pytest`.

### Linting
- **Current State**: No linter configuration (`flake8`, `pylint`) or formatter (`black`) is present.
- **Guideline**: Try to follow PEP 8 generally, but adhere to the existing style in the file you are editing.

## 2. Code Style Guidelines

### Formatting
- **Indentation**: Use **4 spaces**. Do not use tabs.
- **Line Length**: No strict limit, but keep it readable (approx 80-120 chars).
- **Encoding**: Use `utf-8` or `utf-8-sig` (BOM) when reading/writing CSVs containing Chinese characters.
  - Example: `df.to_csv(save_path, index=False, encoding='utf-8-sig')`

### Naming Conventions
- **Variables & Functions**: Use `snake_case`.
  - `process_item`, `summary_year`, `all_profits`
- **Constants**: Use `UPPER_CASE`.
- **Classes**: Use `PascalCase` (if any are added).

### Imports
- Group imports:
  1. Standard library (`os`, `re`, `collections`)
  2. Third-party (`pandas`, `numpy`)
  3. Local modules
- Example:
  ```python
  import os
  import re
  import pandas as pd
  from collections import defaultdict
  ```

### Language
- **Comments**: Chinese comments are used and encouraged for domain-specific logic (e.g., tax rules).
- **Output**: Console output and CSV headers often use Chinese (e.g., "配对原因", "利润"). Maintain this consistency.

### Type Hints
- Type hints are currently **not used**.
- You may add them for complex new functions, but do not refactor existing code solely to add types unless requested.

### Error Handling
- Minimal error handling is currently present.
- **Agent Instruction**: When adding file I/O or API calls, add basic `try-except` blocks where appropriate, but don't over-engineer.

## 3. Project Structure

- `get_tax_moving_avg.py`: Recommended script (Moving Avg + Holdings).
- `report.py`: Generates summary reports from `data/`.
- `futu/`: Scripts for downloading and exporting Futu data.
- `data/`: Storage for CSVs (raw history, processed profits, reports).

## 4. Key Workflows

### Data Processing Flow
1. **Download**: `python futu/download.py ...` -> Raw CSV
2. **Export/Convert**: `python futu/export.py` -> `data/futu_history.csv`
3. **Calculate**: `python get_tax_moving_avg.py futu` -> Profit & Holdings CSVs
4. **Report**: `python report.py` -> Console summary

### Agent Rules
- **Data Integrity**: Never manually edit the CSVs in `data/` unless for creating mock data for tests.
- **Dependencies**: If you add a library, update `requirements.txt`.
- **CSV Handling**: Always handle `NaN` values in pandas DataFrames (e.g., `np.isnan(price)` check in `get_tax1.py`).
- **Git**: Do not commit large CSV files in `data/` if they contain real personal data. (Check `.gitignore`).

## 5. Specific Code Patterns

### Processing Logic
- The core logic often involves iterating through trades and updating a `holdings` dictionary.
- Example pattern:
  ```python
  holdings = defaultdict(lambda: {'quantity': 0.0, 'avg_cost': 0.0, 'total_fee': 0})
  # ... loop through trades ...
  ```

### Regex
- Regex is used for parsing stock symbols (e.g., options).
- `option_pattern = re.compile(r'([A-Z]+)(\d{6})([CP])(\d+).US')`
