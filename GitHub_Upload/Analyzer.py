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
import pymysql 
from datetime import datetime
from datetime import timedelta
import re

class MarketDB:
    def __init__(self):
        """생성자 : MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host='localhost', user='root',
                                   password='1234', db='Auto_Upbit', charset = 'utf8')
        self.codes = {}
        self.get_market_info()
    
    def __del__(self):
        """소멸자 : MariaDB 연결 해제"""
        self.conn.close()
        
    def get_market_info(self):
        """KRWData 테이블에서 읽어와서 codes에 저장"""
        sql = "SELECT * FROM KRWData"
        data_all = pd.read_sql(sql, self.conn)
        for idx in range(len(data_all)):
            self.codes[data_all['market'].values[idx]] = data_all['korean_name'].values[idx]
    
    def get_daily_price(self, market, start_date = None, end_date = None):
        """data_all 종목의 일별 시세를 데이터프레임 형태로 반환
            - market  : data_all 종목("KRW-BTC") 또는 한글 이름("비트코인")
            - start_date : 조회 시작일('2020-01-01'), 미입력 시 1년 전 오늘
            - end_date : 조회 종료일('2020-12-31'), 미입력 시 오늘 날짜
        """
        if(start_date is None):
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime('%Y-%m-%d')
            print("start_date is initalized to '{}'".format(start_date))
        else:
            start_lst = re.split('\D+', start_date)
            if (start_lst[0] == ''):
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > 2200:
                print("ValueError to Year")
                return
            if start_month < 1 or start_month > 12:
                print("ValueError to Month")
                return
            if start_day < 1 or start_day > 31:
                print("ValueError to Day")
                return
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"
        
        if (end_date is None):
            end_date = datetime.today().strftime('%Y-%m-%d')
            print("end_date is initialized to '{}'".format(end_date))
        else:
            end_lst = re.split('\D+', end_date)
            if (end_lst[0] == ''):
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            
            if end_year < 1800 or end_year > 2200:
                print("ValueError to End_year")
                return
            if end_month < 1 or end_month > 12:
                print("ValueError to End_month")
                return
            if end_day < 1 or end_day > 31:
                print("ValueError to End_day")
                return
            end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"
            
        codes_keys = list(self.codes.keys())
        codes_values = list(self.codes.values())
        if market in codes_keys:
            pass
        elif market in codes_values:
            idx = codes_values.index(market)
            market = codes_keys[idx]
        else:
            print("Doesn't exist")

        sql = f"SELECT * FROM daily_price WHERE market = '{market}'"\
            f"and date >= '{start_date}' and date <= '{end_date}'"
        df = pd.read_sql(sql, self.conn)
        df.index = df['date']
        return df
