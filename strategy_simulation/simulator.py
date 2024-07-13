# strategy_simulation/simulator.py

from strategy_simulation.strategy import simulate_strategy

def execute_strategy(strategy, all_stock_data, results):
    ma_short = strategy['ma_short']
    ma_long = strategy['ma_long']
    up_ratio = strategy['up_ratio']
    down_ratio = strategy['down_ratio']
    
    if ma_short < 1 or ma_long < 1 or up_ratio <= 0 or down_ratio <= 0:
        raise ValueError("All input values must be positive and up/down ratios must be greater than 0.")

    # 如果ma_short大于ma_long，交换它们的值
    if ma_short > ma_long:
        ma_short, ma_long = ma_long, ma_short

    total_cash = 0
    total_stock_value = 0
    num_profitable = 0
    num_loss = 0
    total_profit = 0
    total_loss = 0

    for ticker, stock_data in all_stock_data.items():
        stock_name = stock_data['name'].iloc[0]
        transactions, final_balance, shares = simulate_strategy(stock_data, ma_short, ma_long, up_ratio, down_ratio)

        # 计算截止到当前日期的股票市值
        current_stock_price = stock_data['close'].iloc[-1]
        stock_value = shares * current_stock_price

        # 累计总现金和股票市值
        total_cash += final_balance
        total_stock_value += stock_value

        # 计算利润或损失
        total_balance = final_balance + stock_value
        profit_or_loss = total_balance - 100000

        if profit_or_loss > 0:
            num_profitable += 1
            total_profit += profit_or_loss
        else:
            num_loss += 1
            total_loss += profit_or_loss

        # 打印每只股票的买卖结果
        print(f"{ticker} ({stock_name}) Initial Balance: 100000.00")
        print(f"{ticker} ({stock_name}) Final Balance: {final_balance:.2f}")
        print(f"{ticker} ({stock_name}) Stock Value: {stock_value:.2f}")
        print(f"{ticker} ({stock_name}) Total Profit/Loss: {profit_or_loss:.2f}")
        print("===")

    # 合并统计结果
    if strategy['name'] not in results:
        results[strategy['name']] = {
            "total_cash": 0,
            "total_stock_value": 0,
            "total_value": 0,
            "num_stocks": 0,
            "num_profitable": 0,
            "num_loss": 0,
            "total_profit": 0,
            "total_loss": 0
        }

    results[strategy['name']]['total_cash'] += total_cash
    results[strategy['name']]['total_stock_value'] += total_stock_value
    results[strategy['name']]['total_value'] += total_cash + total_stock_value
    results[strategy['name']]['num_stocks'] += len(all_stock_data)
    results[strategy['name']]['num_profitable'] += num_profitable
    results[strategy['name']]['num_loss'] += num_loss
    results[strategy['name']]['total_profit'] += total_profit
    results[strategy['name']]['total_loss'] += total_loss
