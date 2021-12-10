from tkinter import *
from tkinter import ttk
from PIL import ImageTk,Image
from tkinter import messagebox
from tkinter import filedialog
from functools import partial
from socket import AF_INET, socket, SOCK_STREAM
import socket
import json
import datetime
from datetime import timedelta
from datetime import datetime
BUFF_SIZE = 1024

#Create socket
try:
    sclient = socket.socket(AF_INET, SOCK_STREAM)
except socket.error:
    messagebox.showerror("Error", "Lỗi không thể tạo socket")

#Send message from Server
def sendData(sclient, msg):
    try:
        sclient.sendall(bytes(msg, "utf8"))
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
        self.master.title("Client admin") 
        self.master.geometry("500x350") 
        self.master.resizable(0, 0)
        Label(self.master, text = "TỶ SỐ VÀNG", fg = 'blue',font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        Label(self.master, text = "ADMIN", fg = 'blue',font = ('Times', 20)).pack(side = TOP, pady = 7)
        #Button(self.master, text = "Tra cứu", height = 2, width = 30, command = self.addMatchGUI).pack(side = TOP, pady = 2)
        Button(self.master, text = "Cập nhật thời gian và tỉ số", height = 2, width = 30, command = self.upMatchGUI).pack(side = TOP, pady = 2)
        Button(self.master, text = "Cập nhật event", height = 2, width = 30, command = self.upEventGUI).pack(side = TOP, pady = 2)
        self.master.protocol("WM_DELETE_WINDOW", self.closeClient)
        self.master.mainloop()

    #CloseClient
    def closeClient(self):
        sendData(sclient, "QUIT")
        self.master.destroy()
        closing()
    


    #Submit add match
    def addMatch(self, IDVar, timeVar, team1Var, team2Var, scoreVar):
        flag = sendData(self.sclient, "ADDMT")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        #type(str) = dict
        str = {"id": IDVar.get(), "time": timeVar.get(), "team1": team1Var.get(),"score": scoreVar.get(), "team2": team2Var.get()}
        flag = sendData(self.sclient,json.dumps(str))
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        signal = receive(self.sclient)
        if (signal == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        elif (signal == '0'):
            messagebox.showinfo("Info", "Thêm trận đấu không thành công")
            return False
        else:
            messagebox.showinfo("Info", "Thêm trận đấu thành công")
            return True

    #Update Match
    def upMatchGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title("UPDATE MATCH") 
        self.master1.geometry("500x350") 
        self.master1.resizable(0, 0)

        #Nhập ID
        IDLabel = Label(self.master1, text = "Nhập ID: ", font = ('Times', 12, 'bold'))
        IDLabel.pack(side = TOP, pady = 2)
        IDVar = StringVar()
        IDEntry = Entry(self.master1,textvariable= IDVar, width = 50, bg = "white")
        IDEntry.pack(side = TOP, pady = 2)

        #Nhập time
        timeVar = StringVar()
        timeLabel = Label(self.master1, text = "Nhập time: ",font = ('Times', 12, 'bold'))
        timeLabel.pack(side = TOP, pady = 2)
        timeEntry = Entry(self.master1,textvariable= timeVar, width = 50, bg = "white")
        timeEntry.pack(side = TOP, pady = 5)

        #Nhập tỉ số 
        scoreVar = StringVar()
        scoreLabel = Label(self.master1, text = "Nhập tỉ số: ",font = ('Times', 12, 'bold'))
        scoreLabel.pack(side = TOP, pady = 2)
        scoreEntry = Entry(self.master1,textvariable= scoreVar, width = 50, bg = "white")
        scoreEntry.pack(side = TOP, pady = 5)

        #Button
        self.upMatchFunc = partial(self.upMatch, IDVar, timeVar, scoreVar)
        upMatchButton = Button(self.master1, text = "UPDATE MATCH", width = 15, height = 1,font = ('Times', 12, 'bold'), command = self.upMatchFunc)
        upMatchButton.pack(side = TOP, pady = 5)
        self.master1.mainloop()
    
    #Submit update match
    def upMatch(self, IDVar, timeVar, scoreVar):
        flag = sendData(self.sclient, "UPDMT")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        str = {"id": IDVar.get(), "time": timeVar.get(), "score": scoreVar.get()}
        flag = sendData(self.sclient,json.dumps(str))
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        signal = receive(self.sclient)
        if (signal == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        elif (signal == '0'):
            messagebox.showinfo("Info", "Cập nhật trận đấu không thành công")
            return False
        else:
            messagebox.showinfo("Info", "Cập nhật trận đấu thành công")
            return True

    #Update Event
    def upEventGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title("UPDATE EVENT") 
        self.master1.geometry("500x500") 
        self.master1.resizable(0, 0)
        
        #Nhập ID Match
        IDMLabel = Label(self.master1, text = "Nhập ID: ", font = ('Times', 12, 'bold'))
        IDMLabel.pack(side = TOP, pady = 2)
        IDMVar = StringVar()
        IDMEntry = Entry(self.master1,textvariable= IDMVar, width = 50, bg = "white")
        IDMEntry.pack(side = TOP, pady = 2)

        #Nhập time
        timeVar = StringVar()
        timeLabel = Label(self.master1, text = "Nhập time: ",font = ('Times', 12, 'bold'))
        timeLabel.pack(side = TOP, pady = 2)
        timeEntry = Entry(self.master1,textvariable= timeVar, width = 50, bg = "white")
        timeEntry.pack(side = TOP, pady = 5)

        #Nhập team
        teamVar = StringVar()
        teamLabel = Label(self.master1, text = "Nhập tên đội: ",font = ('Times', 12, 'bold'))
        teamLabel.pack(side = TOP, pady = 2)
        teamEntry = Entry(self.master1,textvariable= teamVar, width = 50, bg = "white")
        teamEntry.pack(side = TOP, pady = 5)

        #Nhập type
        typeLabel = Label(self.master1, text = "Nhập loại sự kiện: ",font = ('Times', 12, 'bold'))
        typeLabel.pack(side = TOP, pady = 2)
        self.choosenTypes = ["goal", "goalPen", "RedCard", "YellowCard"]
        self.typeVar = StringVar()
        self.TypeChoosen = ttk.Combobox(self.master1, value = self.choosenTypes, textvariable = self.typeVar)
        self.TypeChoosen.pack(side = TOP, pady = 2)
        self.TypeChoosen.bind("<<ComboboxSelected>>", self.option)
        
        self.topFrame = Frame(self.master1)
        self.topFrame.pack(side = TOP, pady = 2 )
        #Nhập player
        playerVar = StringVar()
        self.playerLabel = Label(self.topFrame, text = "Nhập player: ",font = ('Times', 12, 'bold'))
        self.playerLabel.pack(side = TOP, pady = 2)
        self.playerEntry = Entry(self.topFrame,textvariable= playerVar, width = 50, bg = "white")
        self.playerEntry.pack(side = TOP, pady = 5)

        #Nhập assist
        assistVar = StringVar()
        self.assistLabel = Label(self.topFrame, text = "Nhập assist: ",font = ('Times', 12, 'bold'))
        self.assistLabel.pack(side = TOP, pady = 2)
        self.assistEntry = Entry(self.topFrame,textvariable= assistVar, width = 50, bg = "white")
        self.assistEntry.pack(side = TOP, pady = 5)

        #Nhập tỉ số 
        scoreVar = StringVar()
        self.scoreLabel = Label(self.topFrame, text = "Nhập tỉ số: ",font = ('Times', 12, 'bold'))
        self.scoreLabel.pack(side = TOP, pady = 2)
        self.scoreEntry = Entry(self.topFrame,textvariable= scoreVar, width = 50, bg = "white")
        self.scoreEntry.pack(side = TOP, pady = 5)
        
        #Button
        self.bottomFrame = Frame(self.master1)
        self.bottomFrame.pack(side = TOP, pady = 2 )
        self.upEventFunc = partial(self.upEvent, IDMVar, timeVar, teamVar, playerVar, assistVar, scoreVar)
        self.upEventButton = Button(self.bottomFrame, text = "UP EVENT", width = 12, height = 1,font = ('Times', 12, 'bold'), command = self.upEventFunc)
        self.upEventButton.pack(side = TOP, pady = 5)
        self.master1.mainloop()
    
    #Submit update event
    def upEvent(self, IDMVar, timeVar, teamVar, playerVar, assistVar, scoreVar):
        flag = sendData(self.sclient, "UPDEV")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        assist = assistVar.get()
        if (assist == None):
            assist = ""
        str = {"id": IDMVar.get(), "events": {"time": timeVar.get(), "type": self.TypeChoosen.get(), "team": teamVar.get(), "player": playerVar.get(), "assist": assist, "score": scoreVar.get()} }
        flag = sendData(self.sclient,json.dumps(str))
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        signal = receive(self.sclient)
        if (signal == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        elif (signal == '0'):
            messagebox.showinfo("Info", "Cập nhật sự kiện không thành công")
            return False
        else:
            messagebox.showinfo("Info", "Cập nhật sự kiện thành công")
            return True

    #Choosen type event
    def option(self, event):
        ch = self.TypeChoosen.get()
        if (ch == self.choosenTypes[0]):
            self.assistLabel.pack(side = TOP, pady = 2)
            self.assistEntry.pack(side = TOP, pady = 5)
            self.scoreLabel.pack(side = TOP, pady = 2)
            self.scoreEntry.pack(side = TOP, pady = 5)
        else:
            self.assistLabel.pack(side = TOP, pady = 2)
            self.assistEntry.pack(side = TOP, pady = 5)
            self.scoreLabel.pack(side = TOP, pady = 2)
            self.scoreEntry.pack(side = TOP, pady = 5)
            self.assistLabel.pack_forget()
            self.assistEntry.pack_forget()
        return


#User
class userGUI(object):

    #User init
    def __init__(self, master):
        master.withdraw()
        self.master = Toplevel(master)
        self.master.title("DANH SÁCH TRẬN ĐẤU") 
        self.master.geometry("700x400") 
        self.master.resizable(0, 0)
        self.sclient = sclient
        Label(self.master, text = "LIVE SCORE", fg = 'blue',font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        Label(self.master, text = "LIST SCORE", fg = 'blue',font = ('Times', 20)).pack(side = TOP, pady = 5)
        self.topFrame = Frame(self.master)
        self.topFrame.pack(side = TOP, pady = 2, padx = 5)
        Button(self.topFrame, text = "List Match", command = self.listMatch).pack(side = LEFT, padx = 10)
        Button(self.topFrame, text = "List Match RealTime", command = self.listMatchRealTime).pack(side = LEFT, pady = 5)
        self.middleFrame = Frame(self.master)
        self.middleFrame.pack(side = TOP, pady = 2, padx = 5)
        Label(self.middleFrame, text = "Match detail", font = ('Time', 11, 'bold')).pack(side = LEFT, padx = 2)
        self.IDMVar = StringVar()
        self.IDMVar.set("Nhập ID Match")
        IDMEntry = Entry(self.middleFrame,textvariable= self.IDMVar, width = 50).pack(side = LEFT, padx = 2)
        Button(self.middleFrame, text = "Xem", command = self.matchDetailGUI).pack(side = LEFT)
        self.bottomFrame = Frame(self.master)
        self.bottomFrame.pack(side = TOP, fill = X )
        self.treev = ttk.Treeview(self.bottomFrame, selectmode ='browse')
        self.treev.pack(side =TOP)
        verscrlbar = ttk.Scrollbar(self.bottomFrame, orient ="vertical", command = self.treev.yview)
        verscrlbar.pack(side ='right', fill ='x')
        self.treev.configure(xscrollcommand = verscrlbar.set)
        self.treev["columns"] = ("1", "2", "3", "4", "5")
        self.treev['show'] = 'headings'
        self.treev.column("1", width = 110, anchor ='c')
        self.treev.column("2", width = 120, anchor ='se')
        self.treev.column("3", width = 160, anchor ='se')
        self.treev.column("4", width = 120, anchor ='se')
        self.treev.column("5", width = 160, anchor ='se')
        self.treev.heading("1", text ="ID Score")
        self.treev.heading("2", text ="Time")
        self.treev.heading("3", text ="Team 1")
        self.treev.heading("4", text = "Score")
        self.treev.heading("5", text = "Team 2")
        self.master.protocol("WM_DELETE_WINDOW", self.closeClient)
        self.master.mainloop()

    #Delete showed list match 
    def clearScreen(self):
        for rec in self.treev.get_children():
            self.treev.delete(rec)
        return 

    #List match
    def listMatch(self):
        self.clearScreen()
        flag = sendData(self.sclient, "LISTMT")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = receive(sclient)
        if (data == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = json.loads(data)
        cnt = 0
        for mtch in data["match"]:
            realTime = datetime.now()
            endTime = datetime.strptime(mtch["time"], '%Y-%m-%d %H:%M') + timedelta(minutes = 110) # 90 mins official + 5 mins added time + 15 mins between 2 half
            if (realTime >= endTime):    # Trận đấu đã end
                mtch["time"] = "FT"
            else:   # Trận đấu chưa end
                mtch["score"] = ""
            self.treev.insert("", 'end', iid = cnt, text ="", values =(mtch['id'], mtch['time'], mtch['team1'], mtch['score'], mtch['team2']))
            cnt += 1
        return

    #List match realtime
    def listMatchRealTime(self):
        self.clearScreen()
        flag = sendData(self.sclient, "LISTMRT")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = receive(sclient)
        if (data == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = json.loads(data)
        cnt = 0
        for mtch in data["match"]:
            realTime = datetime.now()
            startTime = datetime.strptime(mtch["time"], '%Y-%m-%d %H:%M')
            endTime = startTime + timedelta(minutes = 105)      # 90 mins official + 15 mins between 2 half
            if (realTime >= endTime):    # Trận đấu đã end
                mtch["time"] = "FT"
            elif (realTime >= startTime):   # Trận đấu đang diễn ra
                matchTime = realTime - startTime
                sec = matchTime.seconds
                min = sec // 60
                if (min > 45 and min < 60):
                    mtch["time"] = "HF"
                elif (min <= 45):
                    mtch["time"] = str(min)
                else:
                    mtch["time"] = str(min - 15)
            self.treev.insert("", 'end', iid = cnt, text ="", values =(mtch['id'], mtch['time'], mtch['team1'], mtch['score'], mtch['team2']))
            cnt += 1
        return

    #Match Detail
    def matchDetailGUI(self):
        self.master1 = Toplevel(self.master)
        self.master1.title("DANH SÁCH TRẬN ĐẤU") 
        self.master1.geometry("700x400") 
        self.master1.resizable(0, 0)
        Label(self.master1, text = "LIVE SCORE", fg = 'blue',font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        Label(self.master1, text = "LIST SCORE", fg = 'blue',font = ('Times', 20)).pack(side = TOP, pady = 5)
        Button(self.master1, text = "Hiển thị danh sách sự kiện", command = self.matchDetail).pack(side = TOP, pady = 5)
        self.bottomFrame = Frame(self.master1)
        self.bottomFrame.pack(side = TOP, fill = X )
        self.treev1 = ttk.Treeview(self.bottomFrame, selectmode ='browse')
        self.treev1.pack(side =TOP)
        verscrlbar = ttk.Scrollbar(self.bottomFrame, orient ="vertical", command = self.treev1.yview)
        verscrlbar.pack(side ='right', fill ='x')
        self.treev1.configure(xscrollcommand = verscrlbar.set)
        self.treev1["columns"] = ("1", "2", "3", "4", "5", "6", "7")
        self.treev1['show'] = 'headings'
        self.treev1.column("1", width = 100, anchor ='c')
        self.treev1.column("2", width = 100, anchor ='se')
        self.treev1.column("3", width = 100, anchor ='se')
        self.treev1.column("4", width = 100, anchor ='se')
        self.treev1.column("5", width = 100, anchor ='se')
        self.treev1.column("6", width = 100, anchor ='se')
        self.treev1.column("7", width = 100, anchor ='se')
        self.treev1.heading("1", text ="ID Match")
        self.treev1.heading("2", text ="Time")
        self.treev1.heading("3", text ="Type")
        self.treev1.heading("4", text = "Team")
        self.treev1.heading("5", text = "Player")
        self.treev1.heading("6", text = "Assist")
        self.treev1.heading("7", text = "Score")
        self.master1.mainloop()

    #CloseClient
    def closeClient(self):
        sendData(sclient, "QUIT")
        self.master.destroy()
        closing()
        
    #Show match detail
    def matchDetail(self):
        flag = sendData(self.sclient, "MTCDT")
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        IDM = self.IDMVar.get()
        flag = sendData(self.sclient, IDM)
        if not flag:
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        data = receive(sclient)
        if (data == -100):
            messagebox.showerror("Error", "Server đã ngừng kết nối")
            return
        elif (data == '0'):
            messagebox.showinfo("Info", "Id trận đấu không tồn tại")
        else: 
            data = json.loads(data)
            cnt = 0
            for mtch in data["events"]:
                mtch["id"] = IDM
                self.treev1.insert("", 'end', iid = cnt, text ="", values =(mtch['id'], mtch['time'], mtch['type'], mtch['team'], mtch['player'], mtch['assist'], mtch['score']))
                cnt += 1
        return
        
#Log In
class logInGUI(object):

    #Log In GUI
    def __init__(self, master):
        self.master =master
        self.sclient = sclient
        self.master.title("Client") 
        self.master.geometry("800x500") 
        self.master.resizable(0, 0)
        self.img = Image.open("client.jpg")
        img1 = self.img.resize((800, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(img1)
        self.bgImage = Label(self.master,image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)
        self.loginLabel = Label(self.master, text = "LOG IN",bg = 'white', fg = 'blue',font = ('Times', 30, 'bold'))
        self.loginLabel.place(x = 170, y = 180)
        self.userLabel = Label(self.master, text = "User Name: ",bg = 'white', font = ('Times', 12, 'bold'))
        self.userLabel.place(x = 70, y = 250)
        self.userVar = StringVar()
        self.userEntry = Entry(self.master,textvariable= self.userVar,font = ('Times', 12, 'bold'), width = 30, bg = "white")
        self.userEntry.place(x = 160, y = 250)
        self.passVar = StringVar()
        self.passLabel = Label(self.master, text = "Password: ",bg = 'white', font = ('Times', 12, 'bold'))
        self.passLabel.place(x = 70, y = 280)
        self.passEntry = Entry(self.master,textvariable= self.passVar,show = "*",font = ('Times', 12, 'bold'), width = 30, bg = "white")
        self.passEntry.place(x = 160, y = 280)
        self.logInButton = Button(self.master, text = "LOG IN", width = 10, height = 1,font = ('Times', 12, 'bold'), command = self.logIn)
        self.logInButton.place( x = 200, y = 320)
        self.regist1Label = Label(self.master, text = "Nếu bạn chưa có tài khoản",bg = 'white', font = ('Times', 12, 'italic'))
        self.regist1Label.place(x = 150, y = 390)
        self.regist1Button = Button(self.master, text = "REGIST", width = 10, height = 1, font = ('Times', 12, 'bold'), command = self.registGUI)
        self.regist1Button.place(x = 200, y = 420)
        self.master.protocol("WM_DELETE_WINDOW", self.closeClient)
        self.master.mainloop()

    #close client
    def closeClient(self):
        sendData(sclient, "QUIT")
        self.master.destroy()

    #Log In submit
    def logIn(self):
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
            userGUI(self.master)
            return True
        elif (signal == '-1'):
           messagebox.showwarning("Warning", "Sai mật khẩu")
           return False
        else:
           messagebox.showwarning("Warning", "Tài khoản không tồn tại")
           return False

    #Regist GUI
    def registGUI(self):
        self.loginLabel.place(x = 170, y = 180)
        self.logInButton.place( x = 200, y = 320)
        self.regist1Label.place(x = 150, y = 390)
        self.regist1Button.place(x = 200, y = 420)
        self.loginLabel.place_forget()
        self.logInButton.place_forget()
        self.regist1Label.place_forget()
        self.regist1Button.place_forget()
        self.registLabel = Label(self.master, text = "REGIST",bg = 'white', fg = 'blue',font = ('Times', 30, 'bold'))
        self.registLabel.place(x = 170, y = 180)
        self.passVar2 = StringVar()
        self.passLabel2 = Label(self.master, text = "Confirm Pass: ",bg = 'white', font = ('Times', 12, 'bold'))
        self.passLabel2.place (x = 60, y = 310)
        self.passEntry2 = Entry(self.master,textvariable= self.passVar2,show = "*",font = ('Times', 12, 'bold'), width = 30, bg = "white")
        self.passEntry2.place (x = 160, y = 310)
        self.regist1Button = Button(self.master, text = "REGIST", width = 10, height = 1,font = ('Times', 12, 'bold'), command = self.regist1)
        self.regist1Button.place(x = 200, y = 350)

    #Regist Client Confirm Func
    def regist1(self):
        if (self.passVar.get() != self.passVar2.get()):
            messagebox.showwarning("Warning","Nhập mật khẩu lại không đúng")
            return False
        else:
            self.regist2()
            return True

    #Regist to Server Func
    def regist2(self):
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
           self.comeback()
           return True
        else:
           messagebox.showwarning("Warning","Tên đăng nhập tồn tại")
           return False

    #Comeback log in GUI
    def comeback(self):
        self.userVar.set("")
        self.passVar.set("")
        self.registLabel.place(x = 170, y = 180)
        self.passLabel2.place (x = 60, y = 310)
        self.passEntry2.place (x = 160, y = 310)
        self.regist1Button.place(x = 200, y = 350)
        self.registLabel.place_forget()
        self.passLabel2.place_forget()
        self.passEntry2.place_forget()
        self.regist1Button.place_forget()
        self.loginLabel.place(x = 170, y = 180)
        self.logInButton.place( x = 200, y = 320)
        self.regist1Label.place(x = 150, y = 390)
        self.regist1Button.place(x = 200, y = 420)

#Client main
class clientGUI(object):
    def __init__(self, master):
        self.master = master
        self.sclient = sclient
        self.master.title("Client") 
        self.master.geometry("400x200") 
        self.master.resizable(0, 0)
        Label(self.master, text = "Tỷ giá tiền tệ", fg = 'blue',font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        Label(self.master, text = "Client", fg = 'blue',font = ('Times', 20)).pack(side = TOP, pady = 5)
        hostVar = StringVar()
        hostVar.set("Nhập IP")
        hostEntry = Entry(self.master,textvariable=hostVar, width = 50).pack(side = TOP, pady = 2)
        submittedHost = hostVar.get()
        connectFunc = partial(self.connectServer,hostVar)
        Button(self.master, text = "Connect to Server", command = connectFunc).pack(side = TOP, pady = 2)
        self.master.mainloop()

    #Connect to Server
    def connectServer(self, IPVar):
        submittedIP = IPVar.get()
        global check
        global sclient
        try:
            ADDR = (submittedIP, 65432)
            sclient.connect(ADDR)
        except Exception:
            messagebox.showerror("Error", "Chưa kết nối đến server")
            return False
        messagebox.showinfo("Info", "Kết nối đến server thành công")
        logInGUI(self.master)
        return True


#Main
if __name__ == "__main__":
    root = Tk()
    window = clientGUI(root)
    root.mainloop()