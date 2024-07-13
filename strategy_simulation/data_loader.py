# strategy_simulation/data_loader.py

import akshare as ak
import time
import pandas as pd

def get_stock_info_with_retry(retries=5, delay=5):
    for attempt in range(retries):
        try:
            stock_info = ak.stock_info_a_code_name()
            return stock_info
        except Exception as e:
            print(f"获取股票信息失败，重试 {attempt + 1}/{retries}...")
            time.sleep(delay)
    raise Exception("多次重试后仍然无法获取股票信息")

def get_stock_data_with_retry(ticker, name, start, end, retries=5, delay=5):
    for attempt in range(retries):
        try:
            start = start.replace("-", "")
            end = end.replace("-", "")
            stock = ak.stock_zh_a_hist(symbol=ticker, period="daily", start_date=start, end_date=end, adjust="qfq")
            stock = stock[['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']]
            stock.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount']
            stock.set_index('date', inplace=True)
            stock.index = pd.to_datetime(stock.index)
            stock['name'] = name
            return stock
        except Exception as e:
            print(f"下载股票数据失败 {ticker}，重试 {attempt + 1}/{retries}...")
            time.sleep(delay)
    raise Exception(f"多次重试后仍然无法下载股票数据 {ticker}")

def download_stock_data(tickers, names, start_date, end_date):
    stock_data = {}
    total_tickers = len(tickers)
    for i, (ticker, name) in enumerate(zip(tickers, names), 1):
        try:
            stock_data[ticker] = get_stock_data_with_retry(ticker, name, start_date, end_date)
            print(f"Downloaded {i}/{total_tickers} stocks")
        except Exception as e:
            print(f"下载股票数据失败，提前结束模拟。异常：{e}")
            return stock_data, False  # 提前结束
    return stock_data, True
