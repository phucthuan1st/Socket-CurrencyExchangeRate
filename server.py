import socket
import json
from _thread import *
import logging
from serverGUI import*
import json
import requests

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
                self.logger.log(logging.INFO,"Client number: " + str(self.threadCount) + " connected. Address: " + str(addr))
            except socket.error:
                #print("close")
                break

    #Open server
    def openServer(self):
        if not self.isOpen:
            self.logger.log(logging.INFO,"Server đã mở!.")
            self.logger.log(logging.INFO,"Cho phép tối đa " + str(self.NClient) + " client kết nối đồng thời.")
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((HOST, PORT))
            self.s.listen(self.NClient)
            self.isOpen = True
            start_new_thread(self.threadServer, ())
                
    #Close server
    def closeServer(self):
        self.isOpen = False
        self.s.close()
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
        self.logger.log(logging.INFO,"Client " + str(client_number) + ". Usr:" + sub['usr'] + " - Pass:" + sub['psw']) 
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
            self.logger.log(logging.INFO,"Client " + str(client_number) + ": Đăng ký thành công")
        fd.close()
        return True

    def updateCurrencyRate(self, sock):
        client_number = self.port_num_clients[sock.getpeername()[1]]
        #get data from API
        url = "https://vapi.vnappmob.com/api/request_api_key?scope=exchange_rate"
        API_data = requests.get(url).json();
        API_key = API_data["results"]
    
        request = "https://vapi.vnappmob.com/api/v2/exchange_rate/bid?api_key=" + str(API_key)
        recieve = requests.get(request).json()
        with open('./Data/Currency-Rate.json', 'w', encoding='utf-8') as _file_:
            json.dump(recieve, _file_, ensure_ascii=False, indent=4)
        self.logger.log(logging.INFO,"Admin từ client " + str(client_number) + ": vừa cập nhật tỷ giá hối đoái")
        return True

    #convert amount of money to another one
    def CurrencyConvertor (self,sock):
        #recieve socket
        id = self.receiveData(sock)
        client_number = self.port_num_clients[sock.getpeername()[1]]
        
        self.logger.log(logging.CRITICAL,"Client " + str(client_number) + ": loại tiền tệ " + id)
        f = open("./Data/Currency-Rate.json", "r")
        data = json.load(f)
        f.close()

        pos = -1

        for i in range(0,len(data["results"])):
            if (data["match"][i]["id"] == id):
                pos = i

        if (pos != -1):
            res = data["match"][pos]
            res["events"] = data["match"][pos]["events"]
            self.sendData(sock, json.dumps(res))
            self.logger.log(logging.INFO,"Client " + str(client_number) + ": Mở chi tiết trận đấu thành công")
            return True
        else:
            self.sendData(sock, '0') # Khong ton tai match detail
            self.logger.log(logging.ERROR,"Client " + str(client_number) + ": Không tồn tại id trận đấu")
            return False

    #show all currency rate
    def ShowAllCurrencies(self,sock):
        client_number = self.port_num_clients[sock.getpeername()[1]]
        f = open("./Data/Currency-Rate.json", "r")
        data = json.load(f)
        f.close()
        self.sendData(sock, json.dumps(data))
        self.logger.log(logging.INFO,"Client " + str(client_number) + ": vừa xem danh sách tổng hợp tỷ giá hối đoái")
        return False
        
    def showSpecificCurrency(self, sock):
        client_number = self.port_num_clients[sock.getpeername()[1]]
        f = open("./Data/Currency-Rate.json", "r")
        data = json.load(f)
        f.close()
        self.sendData(sock, json.dumps(data))
        self.logger.log(logging.INFO,"Client " + str(client_number) + ": vừa xem một tỷ giá hối đoái")
        return False
    
    ### ADMIN ###

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
        str = ""
        while True:
            str = self.receiveData(conn)
            self.logger.log(logging.DEBUG,str)
            if (str == "LOGIN"):
                signal = self.login(conn)
                if (signal == 2): #admin access
                    while True:
                        str = self.receiveData(conn)
                        self.logger.log(logging.DEBUG,str)
                        if (str == "UPDR"):
                            self.updateCurrencyRate(conn)
                        elif (str == "UPDEV"):
                            self.upEvent(conn)
                        else:
                            self.clientQuit(conn)
                            return
                elif (signal == 1): #user access
                    while True:
                        self.logger.log(logging.DEBUG,str)
                        str = self.receiveData(conn)
                        if (str == "SAC"):
                            self.ShowAllCurrencies(conn)
                        elif (str == "CRC"):
                            self.convert(conn)
                        elif (str == "SSC"):
                            self.showSpecificCurrency(conn)
                        else:
                            self.clientQuit(conn)
                            return
            elif (str == "REGIST"):
                self.regist(conn)
            else:
                self.clientQuit(conn)
                break