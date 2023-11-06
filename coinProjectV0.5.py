import sys
import time

import requests

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

form_class = uic.loadUiType("ui/upbit.ui")[0]

class CoinViewThread(QThread): # 시그널 클래스

    # 시그널 함수 정의
    coinDataSent = pyqtSignal(float, float, float, float, float, float, float, float)

    def __init__(self):
        super().__init__()
        self.alive = True

    def run(self): # 무조건 run 으로 만들어야 함
        while self.alive:
            url = "https://api.upbit.com/v1/ticker"

            param = {"markets": "KRW-BTC"}  # 이런걸 티커 라고 함

            response = requests.get(url, params=param)

            result = response.json()  # 리스트 형태로 바꾸기

            trade_price = result[0]["trade_price"]  # 비트코인의 현재가격
            signed_change_rate = result[0]["signed_change_rate"]  # 부호가 있는 변화율
            acc_trade_price_24h = result[0]["acc_trade_price_24h"]  # 24시간 누적 거래대금
            acc_trade_volume_24h = result[0]["acc_trade_volume_24h"]  # 24시간 누적 거래량
            high_price = result[0]["high_price"]  # 최고가
            low_price = result[0]["low_price"]  # 최저가
            prev_closing_price = result[0]["prev_closing_price"]  # 전일 종가(UTC 0시 기준)
            trade_volume = result[0]["trade_volume"]  # 가장 최근 거래량

            #슬롯에 코인정보 보내주는 함수 호출
            self.coinDataSent.emit(float(trade_price),
                                   float(signed_change_rate),
                                   float(acc_trade_price_24h),
                                   float(acc_trade_volume_24h),
                                   float(high_price),
                                   float(low_price),
                                   float(prev_closing_price),
                                   float(trade_volume))

            time.sleep(1) # api 호출 딜레이(1초마다 한번씩 업비트 호출)

    def close(self): # close 함수가 호출되면 run 함수(while문)이 멈춤
        self.alive = False


class MainWindow(QMainWindow, form_class): # 슬롯 클래스

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Coin Price Overview")
        self.setWindowIcon(QIcon("icon/coin.png"))
        self.statusBar().showMessage("ver 0.5")

        self.cvt = CoinViewThread() # 시그널 클래스로 객체 선언
        self.cvt.coinDataSent.connect(self.fillCoinData)
        self.cvt.start() # 시그널 함수에

    # 시그널 클래스에서 보내준 코인정보를 ui에 출력해주는 슬롯 함수
    def fillCoinData(self, trade_price, signed_change_rate, acc_trade_price_24h,
                     acc_trade_volume_24h, high_price, low_price, prev_closing_price, trade_volume):
        self.coin_price_label.setText(f"{trade_price:,.0f}원") # 코인의 현재가 출력
        self.coin_changelate_label.setText(f"{signed_change_rate:+.2f}") # 가격변화율 -> 소수 2자리까지만 표시
        self.acc_trade_price_label.setText(f"{acc_trade_price_24h:,.0f}") # 24시간 누적 거래 금액
        self.acc_trade_volume_label.setText(f"{acc_trade_volume_24h:.4f}") # 24시간 거래량
        self.high_price_label.setText(f"{high_price:,.0f}") # 당일 고가
        self.low_price_label.setText(f"{low_price:,.0f}") # 당일 저가
        self.prev_closing_price_label.setText(f"{prev_closing_price:,.0f}") # 전일 종가
        self.trade_volume_label.setText(f"{trade_volume:.4f}") # 최근 거래량



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())