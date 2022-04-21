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
import Dual
from datetime import datetime
import arrow
import numpy as np
import pyupbit
import DBUpdater
import time
import datetime
import Analyzer


access = ''
secret = ''



def get_momentum(count):
    """3개월 전 날짜로 상대 모멘텀 상위 10개 구하기"""
    today = arrow.now()
    three_months_ago = today.shift(months=-3)

    today = today.strftime('%Y-%m-%d') # 오늘 날짜
    three_months_ago = three_months_ago.strftime('%Y-%m-%d') # 3개월 전 날짜

    dm = Dual.DualMomentum()
    rm = dm.get_rltv_momentum(three_months_ago, today, count) #상대 모멘텀

    market = np.array(rm['market']) # 배열로 저장
    return market

def get_BollingerBand(market):
    mk = Analyzer.MarketDB()
    
    today = arrow.now()
    three_months_ago = today.shift(months=-3)

    today = today.strftime('%Y-%m-%d') # 오늘 날짜
    three_months_ago = three_months_ago.strftime('%Y-%m-%d') # 3개월 전 날짜
    
    df = mk.get_daily_price(market, three_months_ago, today)
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
    
    return df
    

def get_start_time(market):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(market, interval="day", count=1)
    start_time = df.index[0]
    return start_time


def get_balance(market):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == market:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(market):
    """현재가 조회"""
    return pyupbit.get_orderbook(market)["orderbook_units"][0]["ask_price"]




upbit = pyupbit.Upbit(access, secret)

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(get_momentum(1)) # 09:00
        end_time = start_time + datetime.timedelta(days=1) # 다음 날 09:00
    
        if start_time < now < end_time - datetime.timedelta(seconds=15):
            market = get_momentum(50)
            """market 개수인 10번을 반복하여 매수 매매 반복 시킨다 (10만원 까지만 사용 가능하도록 한다.)"""
            for mk in range(len(market)):
                df = get_BollingerBand(market[mk])
                current_price = get_current_price(market[mk])
                slice_market = market[mk].split('-')[1]  # KRW- 뒤에 부분만 얻기 위함
                krw = get_balance("KRW")
                buy_krw = get_balance(slice_market)
                """내 잔고가 5천원 이상이고 매수 한 종목의 잔고가 10만원 이하일 때까지"""
                if df.PB.values[mk] > 0.8 and df.MFI10.values[mk] > 80:
                    if buy_krw * current_price <= 400000:
                        upbit.buy_market_order(market[mk], krw*0.9995)
                        print(f"{market[mk]} 구매, {buy_krw * current_price}현재 보유 금액")
                    else:
                        continue
                elif df.PB.values[mk] < 0.2 and df.MFI10.values[mk] < 20:
                    if buy_krw > 0.0000001:  
                        upbit.sell_market_order(market[mk], buy_krw*0.9995)
                        print(f"{market[mk]} 매도, 남은 금액 {buy_krw * current_price}")
                    else:
                        continue
                else:
                    continue
                        
        elif start_time == now:
            dbu = DBUpdater.DBUpdater()
            dbu.execute_daily()
            
        else:
            for bk in range(len(market)):
                slice_market = market[bk].split('-')[1]  # KRW- 뒤에 부분만 얻기 위함
                buy_krw = get_balance(slice_market)
                if df.PB.values[bk] < 0.2 and df.MFI10.values[bk] < 20:
                    upbit.sell_market_order(market[bk], buy_krw*0.9995)
                    print(f"{market[bk]} 매도, 남은 금액 {buy_krw}")
                else:
                    continue
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
