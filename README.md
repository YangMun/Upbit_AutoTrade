# Upbit_AutoTrade

2022-04-17
KRW-BTT 와 KRW-XEC 는 값이 INT형으로 설정 하였기에 모두 0이 입력된다. 
후에 수정 계획이 있지만 이 2개의 값은 빼는 방식으로 갈 것

--> IF문으로 KRW-BTT 와 KRW-XEC가 값에 담기면 continue 하도록 수정함

2022-04-18
date type VARCHAR -> DATE

모멘텀 함수를 사용하기 위한 3개월 전 날짜를 구하는 코드 추가
듀얼 모멘텀으로 상위 10개의 종목을 구해 볼린저 밴드로 나타내는 코드 추가
