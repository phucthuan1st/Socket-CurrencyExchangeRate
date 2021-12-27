import queue
import logging
import signal
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W
from functools import partial
from server import *

# screen_width = win.winfo_screenwidth()
# screen_height = win.winfo_screenheight()
# screen_size = str(screen_width) + 'x' + str(screen_height)

logger = logging.getLogger(__name__)

NClient = 5                  

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

#Show console server
class ConsoleUI:
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
        formatter = logging.Formatter('%(asctime)s: %(message)s')
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

#Info
class InfoUI:

    def __init__(self, frame):
        self.frame = frame
        space = 10 * " "
        ttk.Label(self.frame, text = "TỶ GIÁ TIỀN TỆ", font = ('Times', 30, 'bold')).pack(side = TOP, pady = 2)
        ttk.Label(self.frame, text = "Server", font = ('Times', 20)).pack (side = TOP, pady = 10)
        ttk.Label(self.frame, text = "Thông tin hiển thị:", font = ('Consolas', 13)).pack(side = TOP, pady = 2)
        ttk.Label(self.frame, text = space + "|--> Thông tin từ server |   Màu đen" + space, font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->    Request từ client|   Màu xám" + space, foreground = 'gray', font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->   Dữ liệu từ client |  Màu xanh" + space, foreground = 'green' , font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->             Cảnh báo|   Màu cam" + space, foreground = 'orange', font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')
        ttk.Label(self.frame, text = space + "|-->                Lỗi  |    Màu đỏ" + space, foreground = 'red', font = ('Consolas', 13)).pack(side = TOP, pady = 2, anchor = 'e')

#Show main server
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
        self.form = InfoUI(form_frame)
        self.console = ConsoleUI(console_frame)
        self.server = Server(logger,NClient)
        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    #Close server
    def quit(self, *args):
        self.server.closeServer()
        self.root.destroy()

#Submit max num client can connect
def submitNumThread(root, nVar):
    global NClient
    NClient = int(nVar.get())
    if (NClient > 0):
        new_root = Tk()
        app = App(new_root)
        root.destroy()
        app.root.mainloop()
    return

#Server num thread
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
