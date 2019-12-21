import pickle
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5 import QtCore
import socket
import traceback
import threading
from PyQt5.QtCore import QTimer
class Auction(QWidget):
    # 시그널 정의 (멀티 스레드 프로그래밍용)
    updateHistory = QtCore.pyqtSignal(str)
    showErrorMessage = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.dbfilename = 'auctionProgressData.txt'
        self.db = []
        self.db = self.readDB()
        self.initUI()


    def initUI(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ipaddr = s.getsockname()[0]
        except:
            ipaddr = '127.0.0.1'
        finally:
            s.close()


        labelServer = QLabel("서버 ")
        self.serverText = QLineEdit(ipaddr)
        labelPort = QLabel("포트 ")
        self.portText = QLineEdit("8083")
        labelName = QLabel("내 이름 ")
        self.nameText = QLineEdit("suyeon")
        labelPW = QLabel("비밀번호 ")
        self.pwText = QLineEdit("lsls")

        label = QLabel("판매자: 김수연")
        #label.font().setBold(True)
        label2 = QLabel("판매물품: 도시락")
        label3 = QLabel("시작가격: 10000 원")
        self.startAmount = 10000
        self.currentAmount = self.startAmount
        self.myAmount = 0
        print()
        qfont = QFont('Gulim', 15, label.font().weight(), label.font().italic())
        qfont.setBold(True)
        #qfont2 = QFont('Batang', 30, label2.font().weight(), label2.font().italic())
        #qfont3 =QFont('Cronix', 30, label3.font().weight(), label3.font().italic())
        label.setFont(qfont)
        label2.setFont(qfont)
        label3.setFont(qfont)


        pixmap1 = QPixmap('도시락.jpeg')
        label4 = QLabel()
        label4.setPixmap(pixmap1)
        #label4.resize(100, 100) 판매물품 이미지 크기 조정
        self.auctionProgressList = QTextEdit()
        self.purchaseTextEdit = QLineEdit("10001")


        self.purchaseButton = QPushButton("구매")
        self.purchaseButton.clicked.connect(self.purchase)
        #self.purchaseButton.clicked.connect(self.connection)
        self.loginButton = QPushButton("로그인")
        self.loginButton.clicked.connect(self.login)
        lhbox = QHBoxLayout()
        lhbox.addWidget(labelServer)
        lhbox.addWidget(self.serverText)
        lhbox.addSpacing(20)
        lhbox.addWidget(labelPort)
        lhbox.addWidget(self.portText)
        lhbox.addSpacing(20)
        lhbox.addWidget(labelName)
        lhbox.addWidget(self.nameText)
        lhbox.addSpacing(20)
        lhbox.addWidget(labelPW)
        lhbox.addWidget(self.pwText)
        lhbox.addSpacing(20)
        lhbox.addWidget(self.loginButton)

        lvbox = QVBoxLayout()
        lvbox.addLayout(lhbox)
        lvbox.addWidget(label)
        lvbox.addSpacing(10)
        lvbox.addWidget(label2)
        lvbox.addSpacing(10)
        lvbox.addWidget(label3)
        lvbox.addWidget(label4)

        rhbox = QHBoxLayout()
        rhbox.addWidget(labelServer)
        rhbox.addWidget(labelPort)
        rhbox.addWidget(labelName)
        rhbox.addWidget(labelPW)

        rhbox = QHBoxLayout()
        rhbox.addWidget(self.purchaseTextEdit)
        rhbox.addWidget(self.purchaseButton)

        rvbox = QVBoxLayout()
        rvbox.addWidget(self.auctionProgressList)
        rvbox.addLayout(rhbox)


        self.updateHistory.connect(self.auctionProgressList.setText)
        self.showErrorMessage.connect(lambda x: QMessageBox.information(self, '오류', x))

        hbox = QHBoxLayout()
        hbox.addLayout(lvbox)
        hbox.addStretch(1)
        hbox.addLayout(rvbox)

        #lvbox.addStretch(1)
        #hbox.addStretch(1)

        self.setLayout(hbox)

        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle("Kookmin Auction")
        #self.resize(500, 300)
        self.show()

#    def buttonClicked(self):
#        sender = self.sender()
#        print(sender.text())
    '''
    def setAmount(self):
        self.myAmount = int(self.purchaseTextEdit.text())
        print(self.myAmount, self.purchaseTextEdit.text())

        if self.myAmount > self.currentAmount:
            self.currentAmount = self.myAmount
            print("야야")
            #self.auctionProgressList.setText(self.auctionProgressList + "고현성 님이" + str(self.myAmount) + "원으로 구입하기를 희망합니다.")
            self.auctionProgressList.setText(self.auctionProgressList.toPlainText() + "고현성 " + str(self.myAmount) + "\n")
            self.db += [["purchase", self.currentAmount]]
            self.saveDB()
    '''
    def readLine(self):
        alldata = b''
        while True:
            data = self.sock.recv(1)
            if data == b'\n':
                break
            if not data:
                # print("unexpected abnormal connection")
                traceback.print_stack()
                raise Exception("unexpected abnormal connection")
            alldata += data
            if len(data) < 1:
                print("no command")
                traceback.print_stack()
                raise Exception("no command")
        return str(alldata, 'utf-8')

    def login(self):
        try:
            self.sock = socket.socket()
            self.sock.connect((self.serverText.text(), int(self.portText.text())))
            print(self.sock.getpeername(), "에 연결됨")
            self.sock.sendall(b'login\n' + bytes(self.nameText.text() + '\n' + self.pwText.text() + '\n', 'utf-8'))
            self.receiver = threading.Thread(target=self.receive)
            self.receiver.start()
        except KeyboardInterrupt as ke:
            print(ke)
            raise ke
        except Exception as e:
            print(e)
            QApplication.exit()


    def receive(self):
        while True:
            try:
                command = self.readLine()
                print("command:", command)
                if command == 'OK':
                    pass
                elif command == 'ERROR':
                    errmsg = self.readLine()
                    self.showErrorMessage.emit(errmsg)
                elif command == 'current':
                    curpurcahser = self.readLine()
                    curamount = int(self.readLine())
                    self.updateHistory.emit(str(curpurcahser) + " " + str(curamount) + '\n' + self.auctionProgressList.toPlainText())

            except KeyboardInterrupt as ke:
                print(ke)
                raise ke
            except Exception as e:
                print(e)
                QApplication.exit()

    def purchase(self):
        #sock = socket.socket()
        #sock.connect((sys.argv[1]), int(sys.argv[2]))
        self.myAmount = int(self.purchaseTextEdit.text())
        #print(self.myAmount, self.purchaseTextEdit.text())
        self.sock.sendall(b'purchase\n' + bytes(self.purchaseTextEdit.text() + '\n', 'utf-8'))
        print(b'purchase\n' + bytes(self.purchaseTextEdit.text() + '\n', 'utf-8'))

    def saveDB(self):
        fH = open(self.dbfilename, 'wb')
        pickle.dump(self.db, fH)
        fH.close()

    def readDB(self):
        try:
            fH = open(self.dbfilename, 'rb')
        except FileNotFoundError as e:
            print("New DB: ", self.dbfilename)
            return []
        try:
            db = pickle.load(fH)
        except:
            print("Empty DB: ", self.dbfilename)
        else:
            print("Open DB: ", self.dbfilename)
        fH.close()
        return db
if __name__ == '__main__':
    app = QApplication(sys.argv)
    auction = Auction()
    sys.exit(app.exec_())