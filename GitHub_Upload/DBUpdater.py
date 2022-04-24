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
import urllib, pymysql, calendar, time, json
from urllib.request import urlopen,Request
from threading import Timer
import pymysql
import requests
import pyupbit
from datetime import datetime, timedelta
import numpy as np

class DBUpdater:
    def __init__(self):
        """생성자 :MariaDB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host= 'localhost', user='root',
                                   password = '1234', db='Auto_Upbit', charset='utf8')
        
        with self.conn.cursor() as curs:
            sql = """
            CREATE TABLE  IF NOT EXISTS KRWData (
            market varchar(20),
            korean_name varchar(20),
            last_update DATE,
            PRIMARY KEY (market))
            """
            curs.execute(sql)
            
            sql = """
            CREATE TABLE  IF NOT EXISTS daily_price (
            market VARCHAR(20),
            date DATE,
            open BIGINT(20),
            high BIGINT(20),
            low BIGINT(20),
            close BIGINT(20),
            volume BIGINT(20),
            PRIMARY KEY(market, date))
            """
            curs.execute(sql)
        self.conn.commit()
        self.codes = dict()
            
    def __del__(self):
        """소멸자 : MariaDB 연결 해제"""
        self.conn.close()

    def read_KRW_code(self):
        """업비트의 모든 종목을 불러와 KRW로만 시작하는 종목으로 변환 해 데이터 프레임으로 반환"""
        url = "https://api.upbit.com/v1/market/all?"

        headers = {"Accept": "application/json"}
        querystring = {"isDetails" : "true"}

        response = requests.request("GET", url, headers=headers, params = querystring)

        json_data = response.json()
        data_all = pd.DataFrame(json_data)

        condition = data_all['market'].str.contains('KRW')
        data_all = data_all[condition]
        data_all = data_all[['market', 'korean_name']]
        return data_all
        
    def update_market_info(self):
        """종목을 KRWData 테이블에 업데이트한 후 딕셔너리에 저장"""
        sql = "SELECT * FROM KRWData"
        df = pd.read_sql(sql, self.conn)
        for idx in range(len(df)):
            self.codes[df['market'].values[idx]] = df['korean_name'].values[idx]
        
        with self.conn.cursor() as curs:
            sql = "SELECT max(last_update) FROM KRWData"
            curs.execute(sql)
            rs = curs.fetchone()
            today = datetime.today().strftime('%Y-%m-%d')
            
            if rs[0] == None or rs[0].strftime('%Y-%m-%d') < today:
                data_all = self.read_KRW_code()
                for idx in range(len(data_all)):
                    market = data_all.market.values[idx]
                    korean_name = data_all.korean_name.values[idx]
                    if market == "KRW-XEC" and korean_name == '이캐시':
                        continue
                    if market == "KRW-BTT" and korean_name == '비트토렌트':
                        continue
                    sql = f"REPLACE INTO KRWData (market, korean_name, last"\
                    f"_update) VALUES ('{market}', '{korean_name}', '{today}')"
                    curs.execute(sql)
                    self.codes[market] = korean_name
                    tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
                    print(f"[{tmnow}] #{idx+1:04d} REPLACE INTO KRWData"\
                            f"VALUES ({market}, {korean_name}, {today})")
                self.conn.commit()
                print("")
    
    def read_Upbit(self, market, korean_name, pages_to_fetch):
        """업비트 시세를 읽어서 데이터프레임으로 전환"""
        try:          
            df = pyupbit.get_ohlcv(market, count = pages_to_fetch)
            df = df.drop('value', axis=1) # value의 값은 DB에 넣지 않을 것이기에 제거


            tmnow = datetime.now().strftime('%Y-%m-%d')
            tmnow_date_time = datetime.strptime(tmnow, '%Y-%m-%d')
            arr_date = []
            for i in range(1, pages_to_fetch + 1):
                date = (tmnow_date_time - timedelta(days = pages_to_fetch - i)).strftime('%Y-%m-%d')
                arr_date += [date]

            df.insert(0, 'market', market)    
            df.insert(1, 'date', arr_date)
            
            tmnow = datetime.now().strftime('%Y-%m-%d %H:%M')
            print('{} {}/{}are downloading....'.format(tmnow, market, korean_name))
            df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(int)
            
            df = df[['market','date','open','high','low','close','volume']]
        except Exception as e:
            print('Exception occured :', str(e))
            return None
        return df

    
    def replace_into_db(self, df, num, market, korean_name):
        """코인 시세를 DB에 REPLACE"""
        with self.conn.cursor() as curs:
            for r in df.itertuples():
                sql = f"REPLACE INTO daily_price VALUES ('{r.market}', '{r.date}', {r.open}, {r.high}, ""{r.low},{r.close}, {r.volume})"
                curs.execute(sql)
            self.conn.commit()
            print('[{}] # {:04d} {} ({}) : {} rows > REPLACE INTO daily_'\
                  'price [OK]'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), num+1, korean_name, market, len(df)))
    
    def update_daily_price(self, pages_to_fetch):
            """Upbit 주식을 DB에 업데이트"""
            for idx, market in enumerate(self.codes):
                df = self.read_Upbit(market, self.codes[market], pages_to_fetch)
                if df is None:
                    continue
                self.replace_into_db(df, idx, market, self.codes[market])
        
    def execute_daily(self):
        """실행 즉시 및 매일 오후 다섯 시에 daily_price 테이블 업데이트"""
        self.update_market_info()
        try:
            with open('config.json', 'r') as in_file:
                config = json.load(in_file)
                pages_to_fetch = config['pages_to_fetch']
        except FileNotFoundError:
            with open('config.json', 'w') as out_file:
                pages_to_fetch = 850 # 2018년 12월 26일 ~ 현재
                config = {'pages_to_fetch' : 1}
                json.dump(config, out_file)
        self.update_daily_price(pages_to_fetch)

        tmnow = datetime.now()
        lastday = calendar.monthrange(tmnow.year, tmnow.month)[1]
        if tmnow.month == 12 and tmnow.day == lastday:
            tmnext = tmnow.replace(year = tmnow.year + 1, month = 1, day = 1,
                                  hour = 9, minute = 0, second = 0)
        elif tmnow.day == lastday:
            tmnext = tmnow.replace(month = tmnow.month + 1, day = 1, hour = 9,
                                  minute = 0, second = 0)
        else:
            tmnext = tmnow.replace(day = tmnow.day + 1, hour = 9, minute = 0,
                                  second = 0)
        tmdiff = tmnext - tmnow
        secs = tmdiff.seconds

        t = Timer(secs, self.execute_daily)
        print("Waiting for next update({})... ".format(tmnext.strftime('%Y-%m-%d %H:%M')))
        t.start()

if __name__ == '__main__':
    dbu = DBUpdater()
    dbu.execute_daily()


                    
# -
df = pyupbit.get_ohlcv(market, count = pages_to_fetch)



