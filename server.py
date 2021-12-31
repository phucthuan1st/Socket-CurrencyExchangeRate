#sokcet and signal libraries
import socket
import signal

#threading handle libraries
from _thread import *
import threading

import logging

#data handler libraries
import json
import requests

#schedule and datetime handlers
import schedule
import time
from datetime import date
from time import strftime

#execute tool libraries
import os
import re
import queue
from functools import partial

#GUI tkinter libraries
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W

#get machine local host and port
hostname = socket.gethostname()
HOST = socket.gethostbyname(hostname) 
PORT = 65432      

#init default value
BUFF_SIZE = 1024
NClient = 5                   
threadCount = 0

#admin account init
ADMIN_USR = "admin"     
ADMIN_PSW = "adm"

#server console init
logger = logging.getLogger(__name__)              

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

#Show server log console
class ServerConsoleUI:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font=('Consolas', 12))
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='green')
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s --> %(message)s', "%Y-%m-%d %H:%M:%S")
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = self.queue_handler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)

#Instruction in server GUI
class ServerInstructionUI:

    def __init__(self, frame):
        self.frame = frame
        space = 5 * " "
        ttk.Label(self.frame, text = "TỶ GIÁ TIỀN TỆ", font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        ttk.Label(self.frame, text = "Server", font = ('Times', 20)).pack (side = TOP, pady = 10)
        ttk.Label(self.frame, text = "Thông tin hiển thị:", font = ('Consolas', 13)).pack(side = TOP, pady = 2)
        ttk.Label(self.frame, text = space + "|--> Thông tin từ server |   Màu đen" + space, font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->   Request từ client |   Màu xám" + space, foreground = 'gray', font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->   Dữ liệu từ client |  Màu xanh" + space, foreground = 'green' , font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->            Cảnh báo |   Màu cam" + space, foreground = 'orange', font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->                 Lỗi |    Màu đỏ" + space, foreground = 'red', font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        self.clock = ttk.Label(self.frame, font = ('Consolas', 30), text = strftime(" %d/%b/%Y \n--> %H:%M:%S "), foreground = 'black')
        self.clock.pack(side = TOP, pady = 50, anchor = 'c')
        self.time()
        
    def time(self):
        string = strftime(" %d/%b/%Y \n--> %H:%M:%S ")
        self.clock.config(text = string)
        self.clock.after(1000, self.time)

#Set max number of thread to server
def submitNumThread(root, nVar):
    global NClient
    NClient = int(nVar.get())
    if (NClient > 0):
        new_root = Tk()
        app = App(new_root)
        root.destroy()
        app.root.mainloop()
    return

#Server execution handle
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
        self.activeUsers = []
        self.isOpen = False
        self.killAll = False
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
                if (self.NClient == len(self.sock_clients)):
                    self.sendData(client, "Denied")
                else:
                    self.sendData(client, "Accept")
                    self.sock_clients.append(client)
                    start_new_thread(self.ClientControl, (client, ))
                    self.threadCount += 1
                    self.port_num_clients[addr[1]] = self.threadCount
                    self.logger.log(logging.CRITICAL,"Client thứ: " + str(self.threadCount) + " đã kết nối. IP: " + str(addr))
                    if self.NClient == len(self.sock_clients):
                        self.logger.log(logging.WARNING,"Đã đạt đến giới hạn truy cập")       
            except socket.error:
                self.logger.log(logging.ERROR,"Không thể tạo socket mới")
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
        API_data = requests.get(url).json()
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
        self.logger.log(logging.CRITICAL,"Client [" + str(client_number) + "]. Usr:" + str(sub['usr']) + " - Pass:" + str(sub['psw']))   
        
        # Admin is log into the server
        if (sub['usr'] == ADMIN_USR and sub['psw'] == ADMIN_PSW):
            self.sendData(sock, '2') 
            self.logger.log(logging.INFO,"Client [" + str(client_number) + "]: Đăng nhập admin thành công")
            return 2    
        
        
        if (sub['usr'] in self.activeUsers):
            self.sendData(sock, 'active')
            self.logger.log(logging.ERROR, "Client [" + str(client_number) + "]: " + str(sub['usr']) + " hiện đang được sử dụng trong một client khác")
            return 0
        
        #open account list
        fd = open("./Data/account.json", "r")
        accs = json.loads(fd.read())
        fd.close()
        #check if correct password in account list
        for acc in accs["account"]:
            u = acc["usr"]
            p = acc["psw"]
            if u == sub['usr']:
                if p == sub['psw']:
                    self.sendData(sock, '1') # Đăng nhập thành công
                    self.logger.log(logging.INFO,"Client [" + str(client_number) + "]: Đăng nhập thành công")
                    self.activeUsers.append(str(sub['usr']))
                    return 1
                else:
                    self.sendData(sock, '-1') # Sai mật khẩu
                    self.logger.log(logging.ERROR,"Client [" + str(client_number) + "]: Sai mật khẩu")
                    return -1
        
        #send unexist account signal to client and log
        self.sendData(sock, '0') 
        self.logger.log(logging.ERROR,"Client [" + str(client_number) + "]: Tài khoản không tồn tại")
        
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
                self.logger.log(logging.ERROR,"Client [" + str(client_number) + "]: Tên đăng nhập đã tồn tại")
                userExist = True
                return False
        if not userExist:
            accs["account"].append(sub)
            accs.update(accs)
            fd.seek(0)
            json.dump(accs, fd, indent = 4)
            self.sendData(sock, '1') # Đăng ký thành công
            self.logger.log(logging.CRITICAL,"Client [" + str(client_number) + "]: Đăng ký thành công")
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
        self.logger.log(logging.INFO, "Client [" + str(client_number) + "] vừa yêu cầu xem tỷ giá của ngày " + self.date)
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
        
        #reciever data from client
        data = self.receiveData(sock)
        
        data = data.split("|")
        fromCur = data[0]
        toCur = data[1]
        fromValue = float(data[2])
        
        #open data file
        f = open("./Data/Rate/" + str(date.today()) + ".json", "r")
        data = json.load(f)
        f.close()
        
        fromRate = -1
        toRate = -1
        
        #if match in data file -> get value
        for cur in data['results']:
            if cur['currency'] == fromCur:
                fromRate = cur['sell']
            if cur['currency'] == toCur:
                toRate = cur['sell']
        
        if fromCur == "VND":
            fromRate = 1.0
        if toCur == "VND":
            toRate = 1.0
        #if both of these are not in data
        message = ""
        if fromRate == -1:
            message = message + fromCur + ' '
        if toRate == -1:
            message = message + toCur + ' '
        
        #log to server console
        self.logger.log(logging.INFO, "Client [" + str(client_number) + "] vừa dùng công cụ chuyển đổi ngoại tệ")
        self.logger.log(logging.CRITICAL, "Client [" + str(client_number) +"]: Chuyển đổi từ " + fromCur)
        self.logger.log(logging.CRITICAL, "Client [" + str(client_number) +"]: khoản " + str(fromValue))
        self.logger.log(logging.CRITICAL, "Client [" + str(client_number) + "]: đến " + toCur)
        
        if message == "":
            self.sendData(sock, 'done')
            toValue = round(fromValue * fromRate / toRate, 2)
            self.sendData(sock, str(toValue))      
            self.logger.log(logging.INFO, "Server phản hồi Client [" + str(client_number) + "]: " + str(toValue))
        else:
            message =  message + "chưa có trong dữ liệu"
            self.sendData(sock, message)
            self.logger.log(logging.ERROR, "Server phản hồi Client [" + str(client_number) + "]: " + message)

        
        return False

    #show all currency rate
    def ShowAllCurrencies(self,sock):
        self.sendRateData(sock)
        return False

    #show a specific currency rate to VND   
    def showSpecificCurrency(self, sock):
        self.sendRateData(sock)
        cur_name = self.receiveData(sock)
        client_number = self.port_num_clients[sock.getpeername()[1]]
        self.logger.log(logging.INFO, "Tỉ giá của đồng " + cur_name + " đã được gửi đến client [" + str(client_number) + "]")
        return False
    
    #if kill all ->> kill all client
    def sendStatus(self, sock):
        if self.killAll:
            self.sendData(sock, "Disconnect")
            self.clientQuit(sock)
        else:
            self.sendData(sock, "Connected")

    #Client Quit
    def clientLogout(self, sock):
        try:
            client_number = self.port_num_clients[sock.getpeername()[1]]
            usr = self.receiveData(sock)
            self.logger.log(logging.ERROR,"Client [" + str(client_number) + "]: " + usr + " đã ngừng kết nối")
            
            #remove client from server base
            self.port_num_clients.pop(sock.getpeername()[1])
            sock.close()
            self.sock_clients.remove(sock)
            self.logger.log(logging.INFO, "Còn " + str(len(self.sock_clients)) + " client đang truy cập server")
            
            #log the number of client remaining on server
            self.activeUsers.remove(str(usr))
            
        except:
            return

    #force client quit
    def clientQuit(self, sock):
        try:
            client_number = self.port_num_clients[sock.getpeername()[1]]
            self.logger.log(logging.ERROR,"Client [" + str(client_number) + "]: đã ngừng kết nối")
            
            #remove client from server base
            self.port_num_clients.pop(sock.getpeername()[1])
            sock.close()
            self.sock_clients.remove(sock)
            self.activeUsers.pop()
            
        except:
            return

    #Client action with thread
    def ClientControl(self, conn):
        
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
                            self.clientLogout(conn)
                            return
                elif (signal == 1): #user access
                    while True:
                        message = self.receiveData(conn)
                        if (message != "HIS" and message != "Status"):
                            self.logger.log(logging.DEBUG,"Message: " + message)
                        
                        if (message == "HIS"):
                            self.SendJsonHistory(conn)
                        elif (message == 'Status'):
                            self.sendStatus(conn)
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
                            self.clientLogout(conn)
                            return
                else:
                    continue
            elif (message == "REGIST"):
                self.regist(conn)
            elif (message == "LOGOUT"):
                self.clientLogout(conn)
                break
            else:
                self.clientQuit(conn)
                break

#Show server GUI
class App:

    #innit console server
    def __init__(self, root):
        global NClient
        self.root = root
        root.title('Server Console')
        root.geometry("1400x600")
        root.resizable(0,0)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Create the panes and frames
        vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)
        form_frame = ttk.Labelframe(horizontal_pane, text="My Server")
        form_frame.columnconfigure(1, weight=1)
        horizontal_pane.add(form_frame, weight=1)
        console_frame = ttk.Labelframe(horizontal_pane, text="Console")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)
        
        # Initialize all frames
        self.form = ServerInstructionUI(form_frame)
        self.console = ServerConsoleUI(console_frame)
        self.server = Server(logger,NClient)
        self.killButton = ttk.Button(form_frame, text = "Kill tất cả client", command = self.killAllClient)
        self.killButton.pack(side = TOP, pady = 35)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    def killAllClient(self):
        self.server.killAll = True
        self.killButton.after(3000, self.unkillAllClient)
        self.server.logger.log(logging.WARNING, "Server: đóng tất cả client")
        
    def unkillAllClient(self):
        self.server.killAll = False
        self.server.threadCount = 0

    #Close server
    def quit(self, *args):
        self.server.closeServer()
        self.root.destroy()
            
#main function            
def main():
    logging.basicConfig(level=logging.DEBUG)
    root = Tk()
    root.title("Server") 
    root.geometry("400x200")
    root.resizable(0,0)
    ttk.Label(root, text = "Tỷ giá tiền tệ", font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
    ttk.Label(root, text = "Server", font = ('Times', 20)).pack(side = TOP, pady = 5)
    ttk.Label(root, text = "Nhập số client cho phép kết nối đồng thời: ").pack(side = TOP, pady = 2)
    nVar = StringVar()
    ttk.Entry(root,textvariable= nVar, width = 20).pack(side = TOP, pady = 5)
    nFunc = partial(submitNumThread,root, nVar)
    ttk.Button(root, text = "Mở Server", command = nFunc).pack(side = TOP)
    root.mainloop()

if __name__ == '__main__':
    main()