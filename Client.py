import socket
import threading
import sys

from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from Chatting import ChattingWindow
from PyQt5.QtWidgets import QListWidgetItem

from Chatting import ChattingWindow
from LoginWindow import LoginWindow
from User import User

class Client:
    def __init__(self, myAdr=None):
        self.host = "127.0.0.1"
        self.port = 1004
        self.myAdr = myAdr

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        self.app = QtCore.QCoreApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.loginWindow = None
        self.chattingWindow = None

        self.me = User()

    def run(self):
        self.chatting()

    def chatting(self):
        self.chattingWindow = ChattingWindow(self)
        self.chattingWindow.pushButton.clicked.connect(self.chatting_func)

        t = threading.Thread(target=self.recv_chat)
        t.daemon = True
        t.start()

        self.chattingWindow.show()


    def chatting_func(self):
        msg = self.chattingWindow.textEdit.toPlainText()
        msg = "chat_" + msg

        self.chattingWindow.textEdit.setPlainText("")

        self.send(msg)

    def login(self):
        self.loginWindow = LoginWindow()
        self.loginWindow.pushButton_login.clicked.connect(self.login_func)

        self.loginWindow.show()

    def login_func(self):
        id = self.loginWindow.textEdit_id.toPlainText()
        pwd = self.loginWindow.textEdit_pwd.toPlainText()

        self.loginWindow.textEdit_id.setPlainText("")
        self.loginWindow.textEdit_pwd.setPlainText("")
        
        self.send("login_{}_{}".format(id, pwd))

        result = self.recv()
        print(result)
        if result == "login_OK":
            self.send("ready")
            data = self.recv()
            data = data.split('_')

            self.me.id = data[0]
            self.me.pwd = data[1]
            self.me.name = data[2]
            self.me.email = data[3]
            self.me.date = data[4]

            self.loginWindow.close()
            self.run()
        else:
            self.loginWindow.label_info.setText("로그인 실패")


    def recv_chat(self):
        data = ""
        while(data != "SERVER_CLOSE"):
            data = self.recv()

            data = data.split('_')
            if len(data) == 3:
                if data[0] == "chat":
                    name = data[1]
                    msg = data[2]

                    msg = "[{}] : {}".format(name, msg)
                    self.chattingWindow.listWidget_chat.addItem(QListWidgetItem(msg))

    def recv(self):
        data = ""
        data = self.client_socket.recv(1024)
        data = data.decode()

        return data
        
    def func(self,data):
        if data == "stop":
            self.stop()
        else:
            message = QListWidgetItem(data)
            self.chattingWindow.listWidget_chat.addItem(message)
            # print(data)

    def send(self, data):
        data = self.client_socket.sendall(data.encode())

    def stop(self):
        self.send("stop")
        self.client_socket.close()

if __name__ == "__main__":
    client = Client()

    client.login()

    sys.exit(client.app.exec_())