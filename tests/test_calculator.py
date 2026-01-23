import unittest
import sys
import os
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.calculator import Calculator

class TestTaxCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = Calculator()

    def test_basic_buy(self):
        # Case 1: First buy
        trade = {
            '股票代码': 'AAPL',
            '数量': 100,
            '成交价格': 150.0,
            '合计手续费': 5.0
        }
        self.calculator.process_buy(trade)
        
        hold = self.calculator.holdings['AAPL']
        self.assertEqual(hold['quantity'], 100)
        # Cost = (100 * 150 + 5) / 100 = 150.05
        self.assertAlmostEqual(hold['avg_cost'], 150.05)

    def test_multiple_buys_avg_cost(self):
        # Buy 1: 100 @ 100, fee 5 -> Cost 10005
        trade1 = {'股票代码': 'A', '数量': 100, '成交价格': 100.0, '合计手续费': 5.0}
        self.calculator.process_buy(trade1)
        
        # Buy 2: 100 @ 200, fee 5 -> Cost 20005
        trade2 = {'股票代码': 'A', '数量': 100, '成交价格': 200.0, '合计手续费': 5.0}
        self.calculator.process_buy(trade2)
        
        hold = self.calculator.holdings['A']
        self.assertEqual(hold['quantity'], 200)
        # Total cost = 10005 + 20005 = 30010
        # Avg cost = 30010 / 200 = 150.05
        self.assertAlmostEqual(hold['avg_cost'], 150.05)

    def test_partial_sell(self):
        # Setup: Buy 100 @ 100 + 5 fee = 100.05 cost
        self.calculator.holdings['A'] = {'quantity': 100, 'avg_cost': 100.05}
        
        # Sell 50 @ 120, fee 2
        trade = {
            '股票代码': 'A',
            '数量': 50,
            '成交价格': 120.0,
            '合计手续费': 2.0,
            '结算币种': 'USD',
            '交易时间': '2023-01-01'
        }
        
        records = self.calculator.process_sell(trade)
        
        # Verify Holdings
        hold = self.calculator.holdings['A']
        self.assertEqual(hold['quantity'], 50)
        self.assertAlmostEqual(hold['avg_cost'], 100.05) # Cost shouldn't change on sell
        
        # Verify Profit
        # Revenue = 50 * 120 = 6000
        # Cost = 50 * 100.05 = 5002.5
        # Fee = 2.0
        # Profit = 6000 - 5002.5 - 2.0 = 995.5
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(records[0]['利润'], 995.5)

    def test_oversell_handling(self):
        # Setup: Buy 10 @ 100
        self.calculator.holdings['A'] = {'quantity': 10, 'avg_cost': 100.0}
        
        # Sell 20
        trade = {
            '股票代码': 'A',
            '数量': 20, 
            '成交价格': 110.0,
            '合计手续费': 0.0,
            '结算币种': 'USD',
            '交易时间': '2023-01-01'
        }
        
        records = self.calculator.process_sell(trade)
        
        # Should only sell 10
        self.assertEqual(records[0]['数量'], 10)
        self.assertEqual(self.calculator.holdings['A']['quantity'], -10) 
        
        self.assertEqual(records[0]['利润'], 10 * 110 - 10 * 100) # 100 profit

if __name__ == '__main__':
    unittest.main()
