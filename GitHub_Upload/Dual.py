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
import Analyzer

class DualMomentum:
    
    def __init__(self):
        """생성자: Upbit 종목(market)를 구하기 위한 MarketDB 객체 생성"""
        self.mk = Analyzer.MarketDB()
        
    def get_rltv_momentum(self, start_date, end_date, stock_count):
        """특정 기간 동안 수익률이 제일 높았던 stock_count 개의 종목들 (상대 모멘텀)
            - start_date : 상대 모멘텀을 구할 시작일자 
            - end_date : 상대 모멘텀을 구할 종료일자
            - stock_count : 상대 모멘텀을 구할 종목 수
        """
        
        connection = pymysql.connect(host='localhost', user='root', password='1234', db='Auto_Upbit', charset = 'utf8')
        
        cursor = connection.cursor()
        
        # 사용자가 입력한 시작일자를 DB에서 조회되는 일자를 보정
        sql = f"select max(date) from daily_price where date <= '{start_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if (result[0] is None):
            print("start_date : {} -> returned None".format(sql))
            return
        start_date = result[0].strftime('%Y-%m-%d')
        
        # 사용자가 입력한 종료일자를 DB에서 조회되는 일자로 보정
        sql = f"select max(date) from daily_price where date <= '{end_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print("end_date : {} -> returned None".format(sql))
            return
        end_date = result[0].strftime('%Y-%m-%d')
        
        # KRX 종목별 수익률을 구해서 2차원 리스트 형태로 추가
        rows =[]
        columns = ['market', 'korean_name', 'old_price', 'new_price', 'returns']
        for _, market in enumerate(self.mk.codes):
            sql = f"select close from daily_price "\
                f"where market = '{market}' and date = '{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            old_price = int(result[0])
            sql = f"select close from daily_price "\
                f"where market = '{market}' and date = '{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price - 1) * 100
            rows.append([market, self.mk.codes[market], old_price, new_price, returns])
        
        # 상대 모멘텀 데이터 프레임을 생성한 후 수익률순으로 출력
        df = pd.DataFrame(rows, columns=columns)
        df = df[['market', 'korean_name', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by = 'returns', ascending=False)
        df = df.head(stock_count)
        df.index = pd.Index(range(stock_count))
        connection.close()
        print(df)
        print(f"\nRelative momentum ({start_date} ~ {end_date}) : "\
             f"{df['returns'].mean():.2f}% \n")
        return df
    
    def get_abs_momentum(self, rltv_momentum, start_date, end_date):
        """특정 기간 동안 상대 모멘텀에 투자했을 때의 평균 수익률 (절대 모멘텀)
            - rltv_momentum : get_rltv_momentum() 함수의 리턴값 (상대 모멘텀)
            - start_date : 절대 모멘텀을 구한 매수일
            - end_date : 절대 모멘텀을 구할 매도일
        """
        stockList = list(rltv_momentum['market'])
        connection = pymysql.connect(host='localhost', user='root',
                                   password='1234', db='Auto_Upbit', charset = 'utf8')
        
        cursor = connection.cursor()
        
        # 사용자가 입력한 매수일을 DB에서 조회되는 일자로 변경
        sql = f"select max(date) from daily_price where date <= '{start_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        
        if (result[0] is None):
            print("start_date : {} -> returned None".format(sql))
            return
        start_date = result[0].strftime('%Y-%m-%d')
        
        # 사용자가 입력한 매도일을 DB에서 조회되는 일자로 변경
        sql = f"select max(date) from daily_price where date <= '{end_date}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        if (result[0] is None):
            print("end_date : {} -> returned None".format(sql))
            return
        end_date = result[0].strftime('%Y-%m-%d')
        
        # 상대 모멘텀의 종목별 수익률을 구해서 2차원 리스트 형태로 추가
        rows =[]
        columns = ['market', 'korean_name', 'old_price', 'new_price', 'returns']
        for _, market in enumerate(stockList):
            sql = f"select close from daily_price "\
                f"where market = '{market}' and date = '{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue  
            old_price = int(result[0])
            
            sql = f"select close from daily_price "\
                f"where market = '{market}' and date = '{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price -1) * 100
            rows.append([market, self.mk.codes[market], old_price, new_price, returns])
            
        # 절대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력
        df =pd.DataFrame(rows, columns=columns)
        df = df[['market', 'korean_name', 'old_price', 'new_price', 'returns']]
        df = df.sort_values(by = 'returns', ascending=False)
        connection.close()
        print(df)
        print(f"\nRelative momentum ({start_date} ~ {end_date}) : "\
             f"{df['returns'].mean():.2f}% \n")
        return 
