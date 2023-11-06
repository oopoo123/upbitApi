import time

import requests

import pprint
import json

while True: # 무한문
    url = "https://api.upbit.com/v1/ticker"

    param = {"markets": "KRW-BTC"} # 이런걸 티커 라고 함

    response = requests.get(url, params=param)

    # print(response.text)

    result = response.json() # 리스트 형태로 바꾸기

    print(result[0]["trade_price"])

    time.sleep(1)

