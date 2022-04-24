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
import pandas as pd
import mplfinance as mpf
import arrow
import Analyzer
import numpy as np

class Candle_Chart:
    """신버전 캔들 차트 그리기"""
    def New_Candle_Chart(self, market):
        
        mk = Analyzer.MarketDB()
        
        """3개월 전 날짜로 상대 모멘텀 상위 10개 구하기"""
        today = arrow.now()
        three_months_ago = today.shift(months=-1)

        today = today.strftime('%Y-%m-%d') # 오늘 날짜
        three_months_ago = three_months_ago.strftime('%Y-%m-%d') # 3개월 전 날짜

        df = mk.get_daily_price(market, three_months_ago, today)
        
        
        df.index = pd.to_datetime(df.date)
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        
        #mpf.plot(df, title = f"{market} candle chart", type = 'candle',mav = (5,10,20), volume = True)
        
        kwargs = dict(title = f"{market} candle chart", type = 'candle', mav =(5,10,20), volume = True, ylabel = 'ohlc candles')
        mc = mpf.make_marketcolors(up='r', down='b', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc)
        
        mpf.plot(df, **kwargs, style=s)
        return 
# -


