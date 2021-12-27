import socket
import json
from _thread import *
import logging
from serverGUI import*
import json
import requests
import schedule
import time
import threading
from datetime import date
import os
import re

hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 
PORT = 65432      

BUFF_SIZE = 1024
NClient = 5                   
threadCount = 0

ADMIN_USR = "admin"     
ADMIN_PSW = "adm"

#Server
class Server:

    #Init server
    def __init__(self, logger,mClient = NClient, host = HOST, port = PORT, ):
        self.host = host
        self.port = port
        self.NClient = mClient
        self.logger = logger
        self.s = None
        self.threadCount = 0
        self.sock_clients = []
        self.port_num_clients = {}
        self.isOpen = False
        self.updateJsonData()
        self.schedule = schedule.every(15).minutes.do(self.updateJsonData)
        self.autoUpdateThread = threading.Thread(target = self.autoUpdate)
        self.autoUpdate = True
        self.openServer()

    #Thread server
    def threadServer(self):
        while self.isOpen:
            try:
                client, addr = self.s.accept()
                self.sock_clients.append(client)
                start_new_thread(self.threadClient, (client, ))
                self.threadCount += 1
                self.port_num_clients[addr[1]] = self.threadCount
                self.logger.log(logging.CRITICAL,"Client number: " + str(self.threadCount) + " connected. Address: " + str(addr))
            except socket.error:
                print("cannot create socket")
                break

    #Open server
    def openServer(self):
        if not self.isOpen:
            self.logger.log(logging.INFO,"Server đã mở!.")
            self.logger.log(logging.INFO,"Cho phép tối đa " + str(self.NClient) + " client kết nối đồng thời.")
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.autoUpdateThread.start()
            self.s.bind((HOST, PORT))
            self.s.listen(self.NClient)
            self.isOpen = True
            start_new_thread(self.threadServer, ())          
                
    #Close server
    def closeServer(self):
        self.isOpen = False
        self.s.close()
        self.autoUpdate = False
        self.autoUpdateThread.join()
        schedule.clear()
        for sock in self.sock_clients:
            if sock:
                sock.close()

    #Send data
    def sendData(self,sock, msg):
        try:
            sock.sendall(bytes(msg, "utf8"))
        except socket.error:
            return

    #Receive data
    def receiveData(self, sock): 
        data = b''
        while True:
            while True:
                try:
                    part = sock.recv(BUFF_SIZE)
                    data += part
                    if len(part) < BUFF_SIZE:
                        break
                except socket.error:
                    return
            if data:
                break
        return data.decode().strip()
    
    #auto update data
    def autoUpdate(self):
        while self.autoUpdate:
            schedule.run_pending()
            time.sleep(1)
    
    #update json data from vcb API
    def updateJsonData(self):
        url = "https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
        API_data = requests.get(url).json();
        API_key = API_data["results"]

        request = "https://vapi.vnappmob.com/api/v2/exchange_rate/bid?api_key=" + str(API_key)
        recieve = requests.get(request).json()
        for cur in recieve['results']:
            if cur['buy_transfer'] == 0.0:
                cur['buy_transfer'] = round(cur['sell'] * 99.0 / 100.0, 2)
            if cur['buy_cash'] == 0.0:
                cur['buy_cash'] = round(cur['buy_transfer'] * 99.0 / 100.0, 2)
        file_name = str(date.today()) + '.json'
        with open('./Data/Rate/' + file_name, 'w+', encoding='utf-8') as _file_:
            json.dump(recieve, _file_, ensure_ascii=False, indent=4)
        self.logger.log(logging.INFO,"Dữ liệu đã được cập nhật")
    
    # Đăng nhập
    def login(self,sock):
        sub = self.receiveData(sock)
        sub = json.loads(sub)
        client_number = self.port_num_clients[sock.getpeername()[1]]
        self.logger.log(logging.CRITICAL,"Client " + str(client_number) + ". Usr:" + str(sub['usr']) + " - Pass:" + str(sub['psw']))   
        if (sub['usr'] == ADMIN_USR and sub['psw'] == ADMIN_PSW):
            self.sendData(sock, '2') # Admin đăng nhập thành công
            self.logger.log(logging.INFO,"Client " + str(client_number) + ": Đăng nhập admin thành công")
            return 2    
        fd = open("./Data/account.json", "r")
        accs = json.loads(fd.read())
        fd.close()
        for acc in accs["account"]:
            u = acc["usr"]
            p = acc["psw"]
            if u == sub['usr']:
                if p == sub['psw']:
                    self.sendData(sock, '1') # Đăng nhập thành công
                    self.logger.log(logging.INFO,"Client " + str(client_number) + ": Đăng nhập thành công")
                    return 1
                else:
                    self.sendData(sock, '-1') # Sai mật khẩu
                    self.logger.log(logging.ERROR,"Client " + str(client_number) + ": Sai mật khẩu")
                    return -1
        self.sendData(sock, '0') # Tài khoản không tồn tại
        self.logger.log(logging.ERROR,"Client " + str(client_number) + ": Tài khoản không tồn tại")
        return 0

    # Đăng ký
    def regist(self, sock):
        sub = self.receiveData(sock)
        sub = json.loads(sub)
        client_number = self.port_num_clients[sock.getpeername()[1]]
        self.logger.log(logging.CRITICAL, "Regist request from client " + str(client_number) + ". Usr:" + sub['usr'] + " - Pass:" + sub['psw']) 
        fd = open("./Data/account.json", "r+")
        userExist = False
        accs = json.loads(fd.read())
        for acc in accs["account"]:
            u = acc["usr"]
            if u == sub['usr']:
                self.sendData(sock, '0') # Tên đăng nhập đã tồn tại
                self.logger.log(logging.ERROR,"Client " + str(client_number) + ": Tên đăng nhập đã tồn tại")
                userExist = True
                return False
        if not userExist:
            accs["account"].append(sub)
            accs.update(accs)
            fd.seek(0)
            json.dump(accs, fd, indent = 4)
            self.sendData(sock, '1') # Đăng ký thành công
            self.logger.log(logging.CRITICAL,"Client " + str(client_number) + ": Đăng ký thành công")
        fd.close()
        return True

    #send json history in data directory
    def SendJsonHistory(self, sock):
        file_path = "./Data/Rate/"
        listfile = os.listdir(file_path)
        list_of_file = ""
        for file in listfile:
            list_of_file += file
        self.sendData(sock, list_of_file)
        return

    #read json file and get rate data
    def sendRateData(self, sock):
        client_number = self.port_num_clients[sock.getpeername()[1]]
        file_name = str(self.date) + '.json'
        f = open("./Data/Rate/" + file_name, 'r')
        data = json.load(f)
        f.close()
        self.sendData(sock, json.dumps(data))
        self.logger.log(logging.DEBUG, "Client " + str(client_number) + " vừa yêu cầu xem tỷ giá của ngày " + self.date)
        return

    #update json and data
    def updateCurrencyRate(self, sock):
        client_number = self.port_num_clients[sock.getpeername()[1]]
        self.updateJsonData()
        self.logger.log(logging.INFO,"Admin: vừa cập nhật tỷ giá hối đoái")
        self.logger.log(logging.DEBUG,"Client [" + str(client_number) + "] đã nhận")
        return True

    #convert amount of money to another one
    def CurrencyConvertor(self,sock):
        client_number = self.port_num_clients[sock.getpeername()[1]]
        self.sendRateData(sock)
        self.logger.log(logging.DEBUG, "Client " + str(client_number) + " vừa dùng công cụ chuyển đổi ngoại tệ")
        return False

    #show all currency rate
    def ShowAllCurrencies(self,sock):
        self.sendRateData(sock)
        return False

    #show a specific currency rate to VND   
    def showSpecificCurrency(self, sock):
        self.sendRateData(sock)
        return False

    #Client Quit
    def clientQuit(self, sock):
        try:
            client_number = self.port_num_clients[sock.getpeername()[1]]
            self.logger.log(logging.ERROR,"Client " + str(client_number) + " đã ngừng kết nối")
            sock.close()
        except:
            return

    #Client action with thread
    def threadClient(self, conn):
        message = ""
        while True:
            message = self.receiveData(conn)
            self.logger.log(logging.DEBUG, "Message: " + message)
            if (message == "LOGIN"):
                signal = self.login(conn)
                if (signal == 2): #admin access
                    while True:
                        message = self.receiveData(conn)
                        self.logger.log(logging.DEBUG,message)
                        if (message == "UPDR"):
                            self.updateCurrencyRate(conn)
                        elif (message == "ShAll"):
                            self.date = str(date.today())
                            self.ShowAllCurrencies(conn)
                        else:
                            self.clientQuit(conn)
                            return
                elif (signal == 1): #user access
                    while True:
                        self.logger.log(logging.DEBUG,message)
                        message = self.receiveData(conn)
                        if (message == "HIS"):
                            self.SendJsonHistory(conn)
                        elif (re.match('\S\S\S-\d\d\d\d-\d\d-\d\d', message) is not None):
                            self.execute = message[0:3]
                            self.date = message[4:]
                            if (self.execute == "SAC"):
                                self.ShowAllCurrencies(conn)
                            elif (self.execute == "CRC"):
                                self.CurrencyConvertor(conn)
                            elif (self.execute == "SSC"):
                                self.showSpecificCurrency(conn)
                        else:
                            self.clientQuit(conn)
                            return
            elif (message == "REGIST"):
                self.regist(conn)
            else:
                self.clientQuit(conn)
                break