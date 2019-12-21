import socket
import sys
import os
import threading
import traceback

class Con(threading.Thread):
    conList = []
    callHistory = []
    currentAmount = 10000
    currentPerchaser = None

    def __init__(self, sock):
        super().__init__()
        print('conntected to:', sock.getpeername())
        self.sock = sock
        self.id = None


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

    def sendOK(self):
        self.sock.sendall(b'OK\n')

    def sendERROR(self, errmsg):
        self.sock.sendall(b'ERROR\n' + bytes(errmsg, 'utf-8') + b'\n')

    def run(self):
        try:
            # 요청 메시지 읽기 루프
            while True:
                command = self.readLine()
                print("command=" + command)
                if command == 'login':
                    self.id = self.readLine()
                    pw = self.readLine()
                    self.sendOK()
                elif command == 'purchase':
                    amount = int(self.readLine())
                    print("amount "+ str(amount))
                    if self.id == None:
                        self.sendERROR('로그인하지 않았습니다')
                    else:
                        self.sendOK()
                        if amount > Con.currentAmount:
                            Con.currentAmount = amount
                            self.broadcast(self.id, amount)
                else:
                    self.sendERROR('undefined command: ' + command)
        except KeyboardInterrupt as ke:
            traceback.print_stack()
            raise ke
        except OSError as err:
            self.sendERROR('비정상적인 연결')
            traceback.print_stack()
        finally:
            Con.conList.remove(self)


    def broadcast(self, id, amount):
        data = b'current\n'
        data += bytes(id, 'utf-8') + b'\n'
        data += bytes(str(amount), 'utf-8') + b'\n'
        #for each in Con.callHistory:
        #    data += bytes(each[0], 'utf-8') + b'\n'
        #    data += bytes(str(each[1]), 'utf-8') + b'\n'
        for con in Con.conList:
            con.sock.sendall(data)

with socket.socket() as serversock:
    serversock.bind(('', int(sys.argv[1])))
    serversock.listen(10)
    # accept 루프
    while True:
        try:
            sock, addr = serversock.accept() # sock은 상대방과만 통신할 수 있는 전용 소켓, addr은 상대방의 ip주소와 port 번호
            connection = Con(sock)
            Con.conList.append(connection)
            #Con.conList[0].run()
            connection.start()
        except Exception as e:
            print(e)
            traceback.print_exc()
