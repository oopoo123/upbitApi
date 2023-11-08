import sys
import time

import requests

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import pyupbit

form_class = uic.loadUiType("ui/upbit.ui")[0]


class CoinViewThread(QThread):  # 시그널 클래스

    # 시그널 함수 정의
    coinDataSent = pyqtSignal(float, float, float, float, float, float, float, float)
    alarmDataSent = pyqtSignal(float) # 알람용 현재가격 시그널

    def __init__(self, ticker):
        # MainWindow에서 시그널 클래스로 객체를 선언할 때 ticker 를 인수로 전달
        super().__init__()
        self.ticker = ticker
        self.alive = True

    def run(self):
        while self.alive:
            url = "https://api.upbit.com/v1/ticker"

            param = {"markets": f"KRW-{self.ticker}"}

            response = requests.get(url, params=param)

            result = response.json()

            trade_price = result[0]['trade_price']  # 비트코인의 현재가격
            signed_change_rate = result[0]['signed_change_rate']  # 부호가 있는 변화율
            acc_trade_price_24h = result[0]['acc_trade_price_24h']  # 24시간 누적 거래대금
            acc_trade_volume_24h = result[0]['acc_trade_volume_24h']  # 24시간 거래량
            high_price = result[0]['high_price']  # 최고가
            low_price = result[0]['low_price']  # 최저가
            prev_closing_price = result[0]['prev_closing_price']  # 전일종가
            trade_volume = result[0]['trade_volume']  # 최근 거래량

            # 슬롯에 코인정보 보내주는 함수 호출
            self.coinDataSent.emit(float(trade_price),
                                   float(signed_change_rate),
                                   float(acc_trade_price_24h),
                                   float(acc_trade_volume_24h),
                                   float(high_price),
                                   float(low_price),
                                   float(prev_closing_price),
                                   float(trade_volume))

            self.alarmDataSent.emit(float(trade_price))

            time.sleep(1)  # api 호출 딜레이(1초마다 한번씩 업비트 호출)

    def close(self):  # close 함수가 호출되면 run 함수(while문)이 멈춤
        self.alive = False


class MainWindow(QMainWindow, form_class):  # 슬롯 클래스

    def __init__(self, ticker="BTC"):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Coin Price Overview')
        self.setWindowIcon(QIcon('icon/coin.png'))
        self.statusBar().showMessage('ver 0.8')
        self.ticker = ticker

        self.cvt = CoinViewThread(self.ticker)  # 시그널 클래스로 객체 선언
        self.cvt.coinDataSent.connect(self.fillCoinData)
        self.cvt.alarmDataSent.connect(self.alarmCheck)
        self.cvt.start()  # 시그널 함수의 쓰레드를 시작
        self.coin_comboBox_setting()  # 콤보박스 초기화 셋팅 함수 호출

        self.alarmButton.clicked.connect(self.alarmButtonAction)
        # 알람버튼이 클릭되면 alarmButtonAction 함수가 호출

    def coin_comboBox_setting(self):
        tickerList = pyupbit.get_tickers(fiat="KRW")
        # print(tickerList)

        coinTickerList = []

        for ticker in tickerList:
            # print(ticker[4:])
            coinTickerList.append(ticker[4:])

        coinTickerList.remove('BTC')  # 티커리스트에서 BTC 제거
        coinTickerList = sorted(coinTickerList)  # BTC 제거한 상태의 리스트를 오름차순 정렬
        coinTickerList = ['BTC'] + coinTickerList
        # BTC 제일 첫번째 순서에 오고 나머지는 오름차순 정렬
        self.coin_comboBox.addItems(coinTickerList)
        self.coin_comboBox.currentIndexChanged.connect(self.coin_select_comboBox)
        # 콤보박스의 메뉴 값이 변경되었을때 호출될 함수 설정

    def coin_select_comboBox(self):
        coin_ticker = self.coin_comboBox.currentText()
        # 콤보박스에서 현재 선택된 ticker 텍스트 가져오기
        # print(coin_ticker)
        self.ticker = coin_ticker
        # 콤보박스에서 사용자가 선택한 코인 ticker 값으로 self.ticker 값을 변경
        self.coin_ticker_label.setText(coin_ticker)
        self.cvt.close()  # while문 종료
        self.cvt = CoinViewThread(coin_ticker)
        # 새로운 코인(바뀐) ticker로 다시 시그널 클래스로 객체를 선언
        self.cvt.coinDataSent.connect(self.fillCoinData)
        # 다시 시그널 함수 호출->새로운 ticker의 정보를 가진 시그널 함수가 실행
        self.cvt.alarmDataSent.connect(self.alarmCheck)
        self.cvt.start()  # 시그널 함수의 쓰레드를 시작

    # 시그널클래스에서 보내준 코인정보를 ui에 출력해주는 슬롯 함수
    def fillCoinData(self, trade_price, signed_change_rate, acc_trade_price_24h,
                     acc_trade_volume_24h, high_price, low_price, prev_closing_price, trade_volume):
        self.coin_price_label.setText(f"{trade_price:,.0f}원")  # 코인의 현재가 출력
        self.coin_changelate_label.setText(f"{signed_change_rate:+.2f}")  # 가격변화율->소수2자리까지만 표시
        self.acc_trade_price_label.setText(f"{acc_trade_price_24h:,.0f}")  # 24시간 누적 거래금액
        self.acc_trade_volume_label.setText(f"{acc_trade_volume_24h:.4f}")  # 24시간 거래량
        self.high_price_label.setText(f"{high_price:,.0f}")  # 당일 고가
        self.low_price_label.setText(f"{low_price:,.0f}")  # 당일 저가
        self.prev_closing_price_label.setText(f"{prev_closing_price:,.0f}")  # 전일 종가
        self.trade_volume_label.setText(f"{trade_volume:.4f}")  # 최근 거래량
        self.updateStyle()

    def updateStyle(self):
        if '-' in self.coin_changelate_label.text():
            self.coin_changelate_label.setStyleSheet("background-color:blue;color:white;")
            self.coin_price_label.setStyleSheet("color:blue;")
        else:
            self.coin_changelate_label.setStyleSheet("background-color:red;color:white;")
            self.coin_price_label.setStyleSheet("color:red;")

    def alarmButtonAction(self):
        self.alarmFlag = 0
        if self.alarmButton.text() == "알람시작":
            self.alarmButton.setText("알람중지")
        else:
            self.alarmButton.setText("알람시작")

    def telegram_message(self, message_text):
        telegram_call = TelegramBotclass(self)


    def alarmCheck(self, trade_price): # 알람체크 슬롯함수

        if self.alarmButton.text() == "알람중지":
            if self.alarm_price1.text() == "" or self.alarm_price2.text() == "":
                if self.alarmFlag == 0:
                    self.alarmFlag = 1
                    QMessageBox.warning(self, "입력오류", "알람금액을 모두 입력하신 수에 알람버튼을 눌러주세요!!")
                    self.alarmButton.setText("알람시작")
            else:
                if self.alarmFlag == 0:
                    alarm_price1 = float(self.alarm_price1.text()) # 매도가격칸이 빈칸이 되면
                    alarm_price2 = float(self.alarm_price2.text()) # 매수가격칸이 빈칸이 되면

                    if trade_price >= alarm_price1:
                        QMessageBox.warning(self, "매도가격도달!", f"얼른 {self.ticker}를 매도하세요")
                        self.alarmFlag = 1
                        self.telegram_message(f"{self.ticker} 현재가격 : {trade_price:,.0f}")
                        self.telegram_message(f"알람설정가격 : {trade_price:,.0f}")
                        self.telegram_message(f"매도 시기 입니다!")

                    if trade_price >= alarm_price2:
                        QMessageBox.warning(self, "매수가격도달!", f"얼른 {self.ticker}를 매수하세요")
                        self.alarmFlag = 1
                        self.telegram_message(f"{self.ticker} 현재가격 : {trade_price:,.0f}")
                        self.telegram_message(f"알람설정가격 : {trade_price2:,.0f}")
                        self.telegram_message(f"매수 시기 입니다!")

class TelegramBotclass(QThread): # 텔레그램 메시지 봇 클래스
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        token = "토큰"
        chat_id = "챗아이디"
        self.bot = telegram.Bot(token=token)

    def telegramBot(self, text):
    # 텔레그램으로 보낼 메시지를 인수로 넣어서 호출하면 해당 텍스트를 텔레그램 계정으로 전송하는 메서드
        self.bot.sendMessage(chat_id=, text=text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())