# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import matplotlib.pyplot as plt
import Analyzer
from datetime import datetime
import Dual
import arrow
import numpy as np


today = arrow.now()
three_months_ago = today.shift(months=-1)

today = today.strftime('%Y-%m-%d') # 오늘 날짜
three_months_ago = three_months_ago.strftime('%Y-%m-%d') # 3개월 전 날짜

dm = Dual.DualMomentum()
rm = dm.get_rltv_momentum(three_months_ago, today, 50) #상대 모멘텀
# am = dm.get_abs_momentum(rm, '2022-01-20', today) #절대 모멘텀  아직 사용 X

market = np.array(rm['market']) # 배열로 저장

mk = Analyzer.MarketDB()


for krw in range(len(market)):
    df = mk.get_daily_price(market[krw], three_months_ago, today)
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['stddev'] = df['close'].rolling(window=20).std()
    df['upper'] = df['MA20'] + (df['stddev'] * 2)
    df['lower'] = df['MA20'] - (df['stddev'] * 2)
    df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])
    df['TP'] = (df['high'] + df['low'] + df['close']) / 3
    df['PMF'] = 0
    df['NMF'] = 0

    for i in range(len(df.close)-1):
        if df.TP.values[i] < df.TP.values[i+1]:
            df.PMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
            df.NMF.values[i+1] = 0
        else:
            df.NMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
            df.PMF.values[i+1] = 0

    df['MFR'] = df.PMF.rolling(window=10).sum() / df.NMF.rolling(window=10).sum() #MFR = 현금 흐름 비율
    df['MFI10'] = 100 - 100 / (1 + df['MFR'])
    df = df[19:]

    plt.figure(figsize=(9,8))
    plt.subplot(2, 1, 1)

    plt.title(f'{market[krw]} Bolling Band({today}) - Trend Following')

    plt.plot(df.index, df['close'], color='#0000ff', label='close')
    plt.plot(df.index, df['upper'], 'r--', label='Upper band')
    plt.plot(df.index, df['MA20'], 'k--', label='Moving average 20')
    plt.plot(df.index, df['lower'], 'c--', label='Lower band')
    plt.xticks(rotation = 45)

    plt.fill_between(df.index, df['upper'], df['lower'], color='0.9')

    for i in range(len(df.close)):
        if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
            plt.plot(df.index.values[i], df.close.values[i], 'r^')
            buy_name = np.array(market[krw])
            
        elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
            plt.plot(df.index.values[i], df.close.values[i], 'bv')
            sell_name = np.array(market[krw])
    plt.legend(loc='best')

    plt.subplot(2, 1, 2)
    plt.plot(df.index, df['PB'] * 100, 'b', label ='%B * 100')
    plt.plot(df.index, df['MFI10'], 'g--', label='MFI(10 day)')
    plt.xticks(rotation = 45)
    plt.yticks([-20, 0, 20, 40, 60, 80, 100, 120])


    for i in range(len(df.close)):
        if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
            plt.plot(df.index.values[i], 0, 'r^')
        elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
            plt.plot(df.index.values[i], 0, 'bv')
            
    plt.grid(True)
    plt.legend(loc='best')
    plt.show()
# -
print(f"매수 할 것{buy_name} , 팔아야할 것 : {sell_name}")



