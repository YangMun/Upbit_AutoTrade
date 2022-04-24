# Upbit_AutoTrade

2022-04-17
KRW-BTT 와 KRW-XEC 는 값이 INT형으로 설정 하였기에 모두 0이 입력된다. 
후에 수정 계획이 있지만 이 2개의 값은 빼는 방식으로 갈 것

--> IF문으로 KRW-BTT 와 KRW-XEC가 값에 담기면 continue 하도록 수정함

2022-04-18
date type VARCHAR -> DATE

모멘텀 함수를 사용하기 위한 3개월 전 날짜를 구하는 코드 추가
듀얼 모멘텀으로 상위 10개의 종목을 구해 볼린저 밴드로 나타내는 코드 추가

2022-04-20
Main_Code.py 올림 

2022-04-21
볼린저 밴드를 사용하여 count = 100개의 상위 종목을 구해 for문 안 조건에 따라 매수, 매도 실행

Main_Code = 매수기법을 통해 매수, 오전 9시 되기 일정 시간 초 전에 전부 매도 하는 방식
Main_BollingerBand = 볼린저 매수 매매기법을 통해 매수 또는 매도, 마찬가지로 9시 되기 일정 시간 초 전에는 볼린저 매도 기법을 통해 일정치 이하이면 매도

New_Bollinger_Buy = Main_Code 와 Main_BollingerBand 코드를 합쳐 놓은 것 만약 사용한다면 위에 두 코드보다 이 코드를 추천

2022-04-24
Upbit_Candle_Chart 파일은 원하는 종목의 캔들차트를 볼 수 있게 만들었다
사용법 - import Upbit_Candle_Chart 
        변수1 = Candle_Chart()
        변수2 = 변수1.New_Candle_Chart(원하는 종목)  Ex) "KRW-BTC" 또는 비트코인 (단. 한글로 사용 시 title이 깨짐, 결과는 정상적으로 잘 나옴)
