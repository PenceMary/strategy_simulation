# strategy_simulation/main.py

import json
import random
from datetime import datetime
from strategy_simulation.data_loader import get_stock_info_with_retry, download_stock_data
from strategy_simulation.simulator import execute_strategy

def main():
    # 读取配置文件
    with open("strategy_simulation/config.json", "r") as file:
        config = json.load(file)

    init_date = config['init_date']
    num_stocks = config['stockNum']
    strategies = {k: v for k, v in config.items() if k.startswith("strategy")}
    results = {}

    current_date = datetime.now().strftime('%Y-%m-%d')

    # 获取所有A股股票代码
    stock_info = get_stock_info_with_retry()
    stock_list = stock_info['code'].tolist()
    stock_names = stock_info['name'].tolist()

    # 随机选择指定数量的股票
    selected_indices = random.sample(range(len(stock_list)), num_stocks)
    tickers = [stock_list[i] for i in selected_indices]
    stock_names = [stock_names[i] for i in selected_indices]

    batch_size = 50

    for i in range(0, len(tickers), batch_size):
        batch_tickers = tickers[i:i + batch_size]
        batch_names = stock_names[i:i + batch_size]

        # 下载当前批次的股票数据
        all_stock_data, success = download_stock_data(batch_tickers, batch_names, init_date, current_date)
        if not success:
            break  # 如果下载失败，提前结束模拟

        for strategy_name, strat in strategies.items():
            print(f"Executing {strategy_name} for batch {i // batch_size + 1}...")
            strat['name'] = strategy_name  # 添加策略名称到策略对象
            execute_strategy(strat, all_stock_data, results)

    # 打印所有策略的合并结果
    print("\nAll Strategies Results:")
    for strategy_name, result in results.items():
        total_value = result['total_cash'] + result['total_stock_value']
        win_rate = (result['num_profitable'] / result['num_stocks']) * 100 if result['num_stocks'] > 0 else 0
        avg_profit = result['total_profit'] / result['num_profitable'] if result['num_profitable'] > 0 else 0
        avg_loss = result['total_loss'] / result['num_loss'] if result['num_loss'] > 0 else 0

        print(f"{strategy_name}: Win Rate {win_rate:.2f}%")
        print(f"Total Cash: {result['total_cash']:.2f}")
        print(f"Total Stock Value: {result['total_stock_value']:.2f}")
        print(f"Total Portfolio Value: {total_value:.2f}")
        print(f"Number of Stocks Simulated: {result['num_stocks']}")
        print(f"Number of Profitable Stocks: {result['num_profitable']}")
        print(f"Number of Losing Stocks: {result['num_loss']}")
        print(f"Average Profit: {avg_profit:.2f}")
        print(f"Average Loss: {avg_loss:.2f}")

if __name__ == "__main__":
    main()
