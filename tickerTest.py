import requests

import pyupbit # 업비트를 더 쉽게 할수 있게 하는 라이브러리

url = "https://api.upbit.com/v1/market/all?isDetails=false"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

tickerList = pyupbit.get_tickers(fiat="KRW")
print(tickerList)

coinTickerList = []

for ticker in tickerList:
    print(ticker[4:])
    coinTickerList.append(ticker[4:])

print(coinTickerList)