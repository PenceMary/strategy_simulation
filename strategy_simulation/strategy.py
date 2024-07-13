# strategy_simulation/strategy.py

from datetime import timedelta

def simulate_strategy(stock_df, ma_short, ma_long, up_ratio, down_ratio, initial_balance=100000):
    balance = initial_balance
    shares = 0
    transactions = []
    buy_price = 0
    consecutive_losses = 0
    last_loss_date = None

    stock_df[f'ma{ma_short}'] = stock_df['close'].rolling(window=ma_short).mean()
    stock_df[f'ma{ma_long}'] = stock_df['close'].rolling(window=ma_long).mean()

    for i in range(1, len(stock_df)):
        today = stock_df.iloc[i]
        yesterday = stock_df.iloc[i - 1]
        day_before_yesterday = stock_df.iloc[i - 2] if i >= 2 else None

        # 判断长均线是否连续3日上涨
        if i >= 3:
            last_three_days = stock_df.iloc[i-3:i]
            ma_long_trend = last_three_days[f'ma{ma_long}'].diff().dropna() > 0
            is_ma_long_upward = ma_long_trend.all()
        else:
            is_ma_long_upward = False

        if last_loss_date is not None and today.name <= last_loss_date + timedelta(days=60):
            continue  # 如果在两个月内，不进行交易

        if day_before_yesterday is not None and day_before_yesterday[f'ma{ma_short}'] < day_before_yesterday[f'ma{ma_long}'] and yesterday[f'ma{ma_short}'] >= yesterday[f'ma{ma_long}'] and shares == 0:
            # 买入信号（以今天开盘价买入）
            buy_price = today['open']
            shares_to_buy = (balance // buy_price) // 100 * 100  # 使买入的数量是100的整数倍
            cost = shares_to_buy * buy_price
            balance -= cost
            shares += shares_to_buy
            print(f"{today.name.date()}, B, {shares_to_buy}, {buy_price:.2f}, {balance:.2f}")
        elif shares > 0 and (today['high'] >= (1 + up_ratio) * buy_price or today['low'] <= (1 - down_ratio) * buy_price):
            # 卖出信号（当日最高价达到上涨比例时卖出）
            if today['high'] >= (1 + up_ratio) * buy_price:
                sell_price = (1 + up_ratio) * buy_price  # 设定卖出价格为涨幅比例
            else:
                sell_price = (1 - down_ratio) * buy_price
            income = shares * sell_price
            balance += income
            print(f"{today.name.date()}, S, {shares}, {sell_price:.2f}, {balance:.2f}")
            shares = 0

            # 计算是否亏损
            if sell_price < buy_price:
                consecutive_losses += 1
                if consecutive_losses >= 2:
                    last_loss_date = today.name
            else:
                consecutive_losses = 0

    return transactions, balance, shares
