from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
from tkinter import messagebox
from functools import partial
from socket import AF_INET, socket, SOCK_STREAM
import socket
import json
from datetime import date

BUFF_SIZE = 1024
PORT = 65432

#Create socket
try:
    sclient = socket.socket(AF_INET, SOCK_STREAM)
except socket.error:
    messagebox.showerror("Error", "Lỗi không thể tạo socket")

#Send message from Server
def sendData(sclient, msg):
    try:
        sclient.sendall(bytes(msg, "utf-8"))
        return True
    except socket.error:
        return False

#Receive message from Server
def receive(sclient): 
    data = b''
    while True:
        while True:
            try:
                part = sclient.recv(BUFF_SIZE)
                data += part
                if len(part) < BUFF_SIZE:
                    break
            except socket.error:
                return -100
        if data:
            break
    return data.decode().strip()

#Close Client
def closing():
    #sendData(sclient, "QUIT")
    root.destroy()

#Admin
class adminGUI(object):

    #Init Admin
    def __init__(self,master):
        master.withdraw()
        self.master = Toplevel(master)
        self.sclient = sclient
        self.master.title("Admin Access") 
        self.master.geometry("500x250") 
        self.master.resizable(0, 0)
        Label(self.master, text = "TỶ GIÁ NGOẠI TỆ", fg = 'red',font = ('Times', 25, 'bold')).pack(side = TOP, pady = 5)
        Label(self.master, text = "ADMIN", fg = 'brown',font = ('Times', 20)).pack(side = TOP, pady = 7)
        Button(self.master, text = "Xem giá hiện tại", height = 2, width = 30, command = self.showCurrentCurrency).pack(side = TOP, pady = 5)
        Button(self.master, text = "Cập nhật tỉ giá", height = 2, width = 30, command = self.updateRate).pack(side = TOP, pady = 10)
        self.master.protocol("WM_DELETE_WINDOW", self.closeClient)
        self.master.mainloop()

    #show current currency
    def showCurrentCurrency(self):
        self.master1 = Toplevel(self.master)
        self.master1.title("TỶ GIÁ HỐI ĐOÁI HIỆN TẠI")
        self.master1.geometry("600x600")
        self.master1.resizable(0, 0)
        Label(self.master1, text = "XEM TỶ GIÁ HỐI ĐOÁI HIỆN TẠI", fg = 'blue',font = ('Times', 20, 'bold')).pack(side = TOP, pady = 5)
        Label(self.master1, text = "Tỷ giá đang lưu trong dữ liệu", fg = 'brown',font = ('Times', 15)).pack(side = TOP, pady = 5)
        
        #draw and print result to screen
        self.bottomFrame = Frame(self.master1)
        self.bottomFrame.pack(side = TOP, fill = X )
        self.bottomFrame.place(x = 60,y = 100)
        self.treev1 = ttk.Treeview(self.bottomFrame, selectmode ='browse', height = 20)
        self.treev1.pack(side =TOP)
        verscrlbar = ttk.Scrollbar(self.bottomFrame, orient ="vertical", command = self.treev1.yview)
        verscrlbar.pack(side ='top', fill ='x')
        self.treev1.configure(xscrollcommand = verscrlbar.set)
        self.treev1["columns"] = ("1", "2", "3", "4")
        self.treev1['show'] = 'headings'
        self.treev1.column("1", width = 120, anchor ='c')
        self.treev1.column("2", width = 120, anchor ='se')
        self.treev1.column("3", width = 120, anchor ='se')
        self.treev1.column("4", width = 120, anchor ='se')

        self.treev1.heading("1", text ="Tên đồng")
        self.treev1.heading("2", text ="Mua vào")
        self.treev1.heading("3", text ="Chuyển khoản")
        self.treev1.heading("4", text = "Bán ra")
        
        flag = sendData(self.sclient, "ShAll")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = receive(sclient)
        if (data == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = json.loads(data)
        cnt = 0
        for currency in data["results"]:
            self.treev1.insert("", 'end', iid = cnt, text ="", values = (currency['currency'], currency['buy_cash'], currency['buy_transfer'], currency['sell'] ))
            cnt += 1
        self.master1.mainloop()
        return

    #CloseClient
    def closeClient(self):
        sendData(sclient, "QUIT")
        self.master.destroy()
        closing()

    #Update Rate
    def updateRate(self):
        flag = sendData(sclient, "UPDR")
        if flag:
            messagebox.showinfo("Info", "Cập nhật hoàn tất")
        else:
            messagebox.showerror("Error", "Cập nhật thất bại")

#User
class userGUI(object):

    #User init
    def __init__(self, master, username):
        master.withdraw()
        self.master = Toplevel(master)
        self.master.title("TỶ GIÁ TIỀN TỆ") 
        self.master.geometry("700x650") 
        self.master.resizable(0, 0)
        self.sclient = sclient
        self.username = username
        Label(self.master, text = "NGÂN HÀNG NHÀ NƯỚC VIỆT NAM", fg = 'red',font = ('Times', 20)).pack(side = TOP, pady = 5)
        Label(self.master, text = "TỶ GIÁ TIỀN TỆ", fg = 'brown',font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        self.topFrame = Frame(self.master)
        self.topFrame.pack(side = TOP, pady = 2, padx = 5)
        Button(self.topFrame, text = "Chuyển đổi giữa các loại tiền tệ", command = self.CurrencyConvertor).pack(side = LEFT, padx = 5)
        Button(self.topFrame, text = "Hiển thị tất cả tỉ giá hối đoái", command = self.ShowAllCurrencies).pack(side = LEFT, padx = 5)
        self.ListFile()
        self.middleFrame = Frame(self.master)
        self.middleFrame.pack(side = TOP, pady = 2, padx = 5)
        Label(self.middleFrame, text = "Loại ngoại tệ", font = ('Time', 11, 'bold')).pack(side = LEFT, padx = 2)
        self.CurVar = StringVar()
        self.CurVar.set("All")
        Entry(self.middleFrame,textvariable= self.CurVar, width = 50).pack(side = LEFT, padx = 2)
        Button(self.middleFrame, text = "Xem tỷ giá", command = self.showSpecificCurrency).pack(side = LEFT)
        
        #currency tree view
        self.bottomFrame = Frame(self.master)
        self.bottomFrame.pack(side = TOP, fill = X)
        self.treev = ttk.Treeview(self.bottomFrame, selectmode ='browse', height = 20)
        self.treev.pack(side =TOP)
        self.treev["columns"] = ("1", "2", "3", "4")
        self.treev['show'] = 'headings'
        self.treev.column("1", width = 125, anchor ='c')
        self.treev.column("2", width = 125, anchor ='e')
        self.treev.column("3", width = 125, anchor ='e')
        self.treev.column("4", width = 125, anchor ='e')
        self.treev.heading("1", text ="Loại")
        self.treev.heading("2", text ="Mua vào")
        self.treev.heading("3", text = "Chuyển khoản")
        self.treev.heading("4", text = "Bán ra")
        self.master.protocol("WM_DELETE_WINDOW", self.closeClient)
        self.master.mainloop()    
    
    #show all file in data directory
    def ListFile(self):
        flag = sendData(self.sclient, "HIS")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        files = receive(sclient)
        if (files == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        self.options = files.split('.json')
        self.options.pop()
        self.showDate = StringVar()
        self.showDate.set("Select a date to display")
        OptionMenu(self.topFrame, self.showDate, *self.options).pack(side = LEFT, padx = 5, pady = 5)
        return
    
    #Delete showed list match 
    def clearTreeView(self):
        for rec in self.treev.get_children():
            self.treev.delete(rec)
        return 

    #List match
    def ShowAllCurrencies(self):
        self.clearTreeView()
        self.CurVar.set("All")
        date = self.showDate.get()
        if date == "Select a date to display":
            messagebox.showerror("Error", "Vui lòng chọn một ngày để hiển thị")
        else:
            flag = sendData(self.sclient, "SAC-" + date)
            if not flag:
                messagebox.showerror("Error", "Server đã ngừng kết nối")
                return
            data = receive(sclient)
            if (data == -100):
                messagebox.showerror("Error", "Server đã ngừng kết nối")
                return
            data = json.loads(data)
            cnt = 0
            for currency in data["results"]:
                self.treev.insert("", 'end', iid = cnt, text ="", values = (currency['currency'], currency['buy_cash'], currency['buy_transfer'], currency['sell'] ))
                cnt += 1
        return

    #show specific currency
    def showSpecificCurrency(self):
        cur_name = self.CurVar.get()
        self.clearTreeView()
        date = self.showDate.get()
        if date == "Select a date to display":
            messagebox.showerror("Error", "Vui lòng chọn một ngày để hiển thị")
        else:
            if cur_name == "All": 
                self.ShowAllCurrencies()
                return
            flag = sendData(self.sclient, "SSC-" + date)
            if not flag:
                messagebox.showerror("Error", "Server đã ngừng kết nối")
                return
            data = receive(sclient)
            if (data == -100):
                messagebox.showerror("Error", "Server đã ngừng kết nối")
                return
            data = json.loads(data)
            for currency in data["results"]:
                if currency['currency'] == cur_name:
                    self.treev.insert("", 'end', iid = 0, text ="", values = (currency['currency'], currency['buy_cash'], currency['buy_transfer'], currency['sell'] ))
            sendData(self.sclient, cur_name)
        return       
    
    #Convert from one curency --> another
    def CurrencyConvertor(self):
        self.clearTreeView()
        self.master1 = Toplevel(self.master)
        self.master1.title("Chuyển đổi tiền tệ")
        self.master1.geometry("550x550")
        self.master1.resizable(0, 0)
        Label(self.master1, text = "CHUYỂN ĐỔI TIỀN TỆ", fg = 'blue', font = ('Times', 30, 'bold')).pack(side = TOP, pady = 5)
        Label(self.master1, text = "Chuyển đổi giữa các loại tiền tệ", fg = 'brown',font = ('Times', 15)).pack(side = TOP)
        
        #draw and print result to screen
        self.bottomFrame = Frame(self.master1)
        self.bottomFrame.pack(side = TOP, fill = X )
        self.bottomFrame.place(y = 155)
        self.treev1 = ttk.Treeview(self.bottomFrame, selectmode ='browse', height = 15)
        self.treev1.pack(side = TOP, padx = 25, pady = 5)
        verscrlbar = ttk.Scrollbar(self.bottomFrame, orient ="vertical", command = self.treev1.yview)
        verscrlbar.place(x = 520, y = 10, height = 320)
        self.treev1.configure(yscrollcommand = verscrlbar.set)
        self.treev1["columns"] = ("1", "2", "3", "4")
        self.treev1['show'] = 'headings'
        self.treev1.column("1", width = 120, anchor ='c')
        self.treev1.column("2", width = 120, anchor ='se')
        self.treev1.column("3", width = 120, anchor ='se')
        self.treev1.column("4", width = 120, anchor ='se')

        self.treev1.heading("1", text ="Chuyển từ")
        self.treev1.heading("2", text ="Só tiền")
        self.treev1.heading("3", text ="Đến")
        self.treev1.heading("4", text = "Số tiền")
        
        #from currency
        self.fromLabel = Label(self.master1, text = "From:", font = ('Times', 12, 'bold'))
        self.fromLabel.place(x = 30, y = 90)
        self.fromVar = StringVar()
        self.fromEntry = Entry(self.master1,textvariable= self.fromVar,font = ('Times', 12, 'bold'), width = 10, bg = "white")
        self.fromEntry.place(x = 85, y = 90)
        
        #to currency
        self.toLabel = Label(self.master1, text = "  To:", font = ('Times', 12, 'bold'))
        self.toLabel.place(x = 30, y = 120)
        self.toVar = StringVar()
        self.toEntry = Entry(self.master1,textvariable= self.toVar,font = ('Times', 12, 'bold'), width = 10, bg = "white")
        self.toEntry.place(x = 85, y = 120)
        
        #from currency value
        self.fromValueLabel = Label(self.master1, text = "Amount:", font = ('Times', 12, 'bold'))
        self.fromValueLabel.place(x = 200, y = 90)
        self.fromValueVar = StringVar()
        self.fromValueEntry = Entry(self.master1,textvariable= self.fromValueVar,font = ('Times', 12, 'bold'), width = 15, bg = "white")
        self.fromValueEntry.place(x = 265, y = 90)
        
        self.exchangeTimes = 0
        self.exchangeButton = Button(self.master1, text = "Chuyển đổi", command = self.showExchangeResult)
        self.exchangeButton.place(x = 265, y = 120)
        self.master1.mainloop()
        return

    #print the exchange réult to treeview
    def showExchangeResult(self):
        flag = sendData(self.sclient, "CRC-" + str(date.today()))
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        
        toCur = self.toVar.get()
        fromValue = self.fromValueVar.get()
        fromCur = self.fromVar.get()
        message = fromCur + '|' + toCur + '|' + fromValue
        sendData(sclient, message)


        message = receive(sclient)
        if message != 'done':
            messagebox.showerror("Error", message)
        else:
            toValue = float(receive(sclient))
            val = (fromCur, str(fromValue), toCur, str(toValue))
            self.treev1.insert("", 'end', iid = self.exchangeTimes, text = "", value = val)
            self.exchangeTimes += 1
        return

    #CloseClient
    def closeClient(self):
        sendData(sclient, "LOGOUT")
        sendData(sclient, self.username)
        self.master.destroy()
        closing()
        
#Log In
class loginGUI(object):

    #Log In GUI
    def __init__(self, master):
        self.master = master
        self.sclient = sclient
        self.master.title("Client") 
        self.master.geometry("800x500") 
        self.master.resizable(0, 0)
        #CLIENT LOGIN IMAGE
        self.img = Image.open("client.jpg")
        img1 = self.img.resize((800, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(img1)
        self.bgImage = Label(self.master,image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)
        #draw login lable
        self.loginLabel = Label(self.master, text = "ĐĂNG NHẬP",bg = 'white', fg = 'blue',font = ('Times', 30, 'bold'))
        self.loginLabel.place(x = 105, y = 180)
        
        #draw username box
        self.userLabel = Label(self.master, text = " Tên tài khoản:", bg = 'white', font = ('Times', 12, 'bold'))
        self.userLabel.place(x = 60, y = 250)
        self.userVar = StringVar()
        self.userEntry = Entry(self.master,textvariable= self.userVar,font = ('Times', 12, 'bold'), width = 25, bg = "white")
        self.userEntry.place(x = 170, y = 250)
        
        #draw password box
        self.passVar = StringVar()
        self.passLabel = Label(self.master, text = "       Mật khẩu:", bg = 'white', font = ('Times', 12, 'bold'))
        self.passLabel.place(x = 60, y = 280)
        self.passEntry = Entry(self.master,textvariable= self.passVar, show = "*", font = ('Times', 12, 'bold'), width = 25, bg = 'white')
        self.passEntry.place(x = 170, y = 280)
       
        #draw login button
        self.logInButton = Button(self.master, text = "ĐĂNG NHẬP", width = 12, height = 1, font = ('Times', 12, 'bold'), command = self.login)
        self.logInButton.place( x = 185, y = 320)
       
        #draw regist button
        self.regist1Label = Label(self.master, text = "Nếu bạn chưa có tài khoản", bg = 'white', font = ('Times', 12, 'italic'))
        self.regist1Label.place(x = 150, y = 390)
        self.regist1Button = Button(self.master, text = "ĐĂNG KÍ", width = 12, height = 1, font = ('Times', 12, 'bold'), command = self.registrationGUI)
        self.regist1Button.place(x = 185, y = 420)
      
        #update master
        self.master.protocol("WM_DELETE_WINDOW", self.closeClient)
        self.master.mainloop()

    #close client
    def closeClient(self):
        sendData(sclient, "QUIT")
        self.master.destroy()

    #Log In result submit
    def login(self):
        flag = sendData(self.sclient, "LOGIN")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        str = {"usr": self.userVar.get(), "psw": self.passVar.get()}
        flag = sendData(self.sclient,json.dumps(str))
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        signal = receive(self.sclient)
        if (signal == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        elif (signal == '2'):
            messagebox.showinfo("Info", "Đăng nhập admin thành công")
            adminGUI(self.master)
            return True
        elif (signal == '1'):
            messagebox.showinfo("Info", "Đăng nhập thành công")
            userGUI(self.master, self.userVar.get())
            return True
        elif (signal == '-1'):
           messagebox.showwarning("Warning", "Sai mật khẩu")
           return False
        elif (signal == 'active'):
            messagebox.showwarning("Warning", "Tài khoản đang truy cập từ nơi khác")
            return False
        else:
           messagebox.showwarning("Warning", "Tài khoản không tồn tại")
           return False

    #Regist GUI
    def registrationGUI(self):
        self.loginLabel.place(x = 170, y = 180)
        self.logInButton.place( x = 200, y = 320)
        self.regist1Label.place(x = 150, y = 390)
        self.regist1Button.place(x = 200, y = 420)
        self.loginLabel.place_forget()
        self.logInButton.place_forget()
        self.regist1Label.place_forget()
        self.regist1Button.place_forget()
        self.registLabel = Label(self.master, text = "ĐĂNG KÝ TÀI KHOẢN", bg = 'white', fg = 'blue',font = ('Times', 22, 'bold'))
        self.registLabel.place(x = 75, y = 180)
        self.passVar2 = StringVar()
        self.passLabel2 = Label(self.master, text = "Xác nhận MK:", bg = 'white', font = ('Times', 12, 'bold'))
        self.passLabel2.place (x = 60, y = 310)
        self.passEntry2 = Entry(self.master,textvariable= self.passVar2,show = "*",font = ('Times', 12, 'bold'), width = 25, bg = "white")
        self.passEntry2.place (x = 170, y = 310)
        self.regist1Button = Button(self.master, text = "ĐĂNG KÝ", width = 12, height = 1,font = ('Times', 12, 'bold'), command = self.ClientRegist)
        self.regist1Button.place(x = 200, y = 350)

    #Regist Client Confirm Func
    def ClientRegist(self):
        if (self.passVar.get() != self.passVar2.get()):
            messagebox.showwarning("Warning","Nhập mật khẩu lại không đúng")
            return False
        else:
            self.ServerRegist()
            return True

    #Regist to Server Func
    def ServerRegist(self):
        flag = sendData(self.sclient, "REGIST")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        str = {"usr": self.userVar.get(), "psw": self.passVar.get()}
        flag = sendData(self.sclient,json.dumps(str))
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        signal = receive(self.sclient)
        if (signal == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        elif (signal == '1'):
           messagebox.showinfo("Info", "Đăng kí thành công")
           self.ReturnLoginScreen()
           return True
        else:
           messagebox.showwarning("Warning","Tên đăng nhập tồn tại")
           return False

    #Comeback log in GUI
    def ReturnLoginScreen(self):
        self.userVar.set("")
        self.passVar.set("")
        self.registLabel.place_forget()
        self.passLabel2.place_forget()
        self.passEntry2.place_forget()
        self.regist1Button.place_forget()
        self.loginLabel.place(x = 105, y = 180)
        self.logInButton.place( x = 185, y = 320)
        self.regist1Label.place(x = 150, y = 390)
        self.regist1Button.place(x = 185, y = 420)

#Client GUI main
class clientGUI(object):
    def __init__(self, master):
        self.master = master
        self.sclient = sclient
        self.master.title("Client") 
        self.master.geometry(f"400x200") 
        self.master.resizable(0, 0)
        Label(self.master, text = "TỶ GIÁ TIỀN TỆ", fg = 'blue',font = ('Times', 30, 'bold')).pack(side = TOP, pady = 5)
        Label(self.master, text = "Client", fg = 'blue',font = ('Times', 20)).pack(side = TOP, pady = 2)
        Label(self.master, text = "Nhập IP", fg = 'black',font = ('Times', 10)).pack(side = TOP, pady = 2)
        self.hostVar = StringVar()
        self.hostVar.set("")
        self.hostEntry = Entry(self.master,textvariable = self.hostVar, width = 30).pack(side = TOP, pady = 2)
        self.submittedHost = self.hostVar.get()
        connectFunc = partial(self.connectServer, self.hostVar)
        self.connect_message = ""
        Button(self.master, text = "Kết nối đến Server", command = connectFunc).pack(side = TOP, pady = 2)
        self.master.mainloop()

    #Connect to Server
    def connectServer(self, IPVar):
        submittedIP = IPVar.get()
        global sclient
        try:
            ADDR = (submittedIP, PORT)
            sclient.connect(ADDR)
            self.connect_message = receive(sclient)
            if self.connect_message == "Accept":
                messagebox.showinfo("Info", "Kết nối đến server thành công")
                loginGUI(self.master)
            elif self.connect_message == "Denied":
                raise Exception
        except Exception:
            if self.connect_message == "Denied":
                messagebox.showerror("Error", "Server đã đạt đến giới hạn truy cập")
            else:
                messagebox.showerror("Error", "Kết nối đến server thất bại")
            sclient.shutdown(socket.SHUT_RDWR)
            sclient.close()
            try:
                sclient = socket.socket(AF_INET, SOCK_STREAM)
            except socket.error:
                messagebox.showerror("Error", "Lỗi không thể tạo socket")
            self.connect_message = ""
            return False
        return True

#Main
if __name__ == "__main__":
    root = Tk()
    window = clientGUI(root)
    root.mainloop()