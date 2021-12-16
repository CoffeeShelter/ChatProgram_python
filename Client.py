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
        self.chattingWindow.label_info.setText("참여자")

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
        self.loginWindow.stackedWidget.setCurrentIndex(0)
        self.loginWindow.pushButton_login.clicked.connect(self.login_func)
        self.loginWindow.pushButton_signup.clicked.connect(self.signup_func)
        self.loginWindow.pushButton_findId.clicked.connect(self.findId_func)
        self.loginWindow.pushButton_repwd.clicked.connect(self.repwd_func)
        
        self.loginWindow.signup_pushButton_create.clicked.connect(self.signup_create)
        self.loginWindow.signup_pushButton_back.clicked.connect(self.signup_back)

        self.loginWindow.findId_pushButton_search.clicked.connect(self.findId_search)
        self.loginWindow.findId_pushButton_back.clicked.connect(self.findId_back)

        self.loginWindow.repwd_pushButton_repwd.clicked.connect(self.repwd_repwd)
        self.loginWindow.repwd_pushButton_back.clicked.connect(self.repwd_back)

        self.loginWindow.show()

    def repwd_func(self):
        self.loginWindow.stackedWidget.setCurrentIndex(3)

        self.loginWindow.repwd_textEdit_id.setPlainText("")
        self.loginWindow.repwd_textEdit_pwd.setPlainText("")
        self.loginWindow.repwd_textEdit_email.setPlainText("")
        self.loginWindow.repwd_label_info.setText("")

    def repwd_repwd(self):
        id = self.loginWindow.repwd_textEdit_id.toPlainText()
        pwd = self.loginWindow.repwd_textEdit_pwd.toPlainText()
        email = self.loginWindow.repwd_textEdit_email.toPlainText()

        self.send("repwd_{}_{}_{}".format(id, pwd, email))
        result = self.recv()
        result = result.split('_')

        if result[1] == "error":
            self.loginWindow.repwd_label_info.setText("잘못된 정보 입니다.")
            self.send("ok")
        elif result[1] == "success":
            self.loginWindow.stackedWidget.setCurrentIndex(0)
            self.send("ok")

    def findId_func(self):
        self.loginWindow.stackedWidget.setCurrentIndex(2)

        self.loginWindow.findId_textEdit_email.setPlainText("")
        self.loginWindow.findId_label_info.setText("")

    def findId_search(self):
        email = self.loginWindow.findId_textEdit_email.toPlainText()

        self.send("findId_{}".format(email))
        result = self.recv()
        result = result.split('_')

        if result[1] == "error":
            self.loginWindow.findId_label_info.setText("존재하지 않는 이메일 입니다.")
            self.send("ok")
        elif result[1] == "success":
            id = result[2]
            self.loginWindow.findId_label_info.setText("[아이디] : {}".format(id))
            self.send("ok")
        

    def signup_create(self):
        id = self.loginWindow.signup_textEdit_id.toPlainText()
        pwd = self.loginWindow.signup_textEdit_pwd.toPlainText()
        email = self.loginWindow.signup_textEdit_email.toPlainText()
        name = self.loginWindow.signup_textEdit_name.toPlainText()

        self.send("signup_{}_{}_{}_{}".format(id, pwd, email, name))
        result = self.recv()
        result = result.split('_')

        if result[1] == "error":
            msg = result[2]
            if msg == "id":
                self.loginWindow.signup_label_info.setText("존재하는 아이디 입니다.")
                self.send("ok")

            elif msg == "name":
                self.loginWindow.signup_label_info.setText("존재하는 닉네임 입니다.")
                self.send("ok")

        elif result[1] == "success":
            self.send("ok")
            self.loginWindow.stackedWidget.setCurrentIndex(0)


    def signup_func(self):
        self.loginWindow.stackedWidget.setCurrentIndex(1)

        self.loginWindow.signup_textEdit_id.setPlainText("")
        self.loginWindow.signup_textEdit_pwd.setPlainText("")
        self.loginWindow.signup_textEdit_email.setPlainText("")
        self.loginWindow.signup_textEdit_name.setPlainText("")
        self.loginWindow.signup_label_info.setText("")

    def signup_back(self):
        self.loginWindow.stackedWidget.setCurrentIndex(0)

    def findId_back(self):
        self.loginWindow.stackedWidget.setCurrentIndex(0)

    def repwd_back(self):
        self.loginWindow.stackedWidget.setCurrentIndex(0)

    def login_func(self):
        id = self.loginWindow.textEdit_id.toPlainText()
        pwd = self.loginWindow.textEdit_pwd.toPlainText()

        self.loginWindow.textEdit_id.setPlainText("")
        self.loginWindow.textEdit_pwd.setPlainText("")
        
        self.send("login_{}_{}".format(id, pwd))

        result = self.recv()
        if result == "login_OK":
            self.send("ready")
            data = self.recv()
            data = data.split('_')

            self.me.id = data[0]
            self.me.pwd = data[1]
            self.me.name = data[2]
            self.me.email = data[3]
            self.me.date = data[4]

            self.send("login_complete")

            self.loginWindow.close()
            self.run()
        else:
            self.loginWindow.label_info.setText("로그인 실패")


    def recv_chat(self):
        data = ""
        while(data != "SERVER_CLOSE"):
            data = self.recv()

            data = data.split('_')
            if data[0] == "chat":
                name = data[1]
                msg = data[2]

                msg = "[{}] : {}".format(name, msg)
                self.chattingWindow.listWidget_chat.addItem(QListWidgetItem(msg))

            if data[0] == "info":
                self.chattingWindow.listWidget_info.clear()
                count = data[1]
                info = "참여자 [ {} 명 ]".format(count)
                self.chattingWindow.label_info.setText(info)
                for i in range(2, len(data)):
                    self.chattingWindow.listWidget_info.addItem(QListWidgetItem(data[i]))

    def recv(self):
        data = ""
        data = self.client_socket.recv(1024)
        data = data.decode()

        return data

    def send(self, data):
        data = self.client_socket.sendall(data.encode())

    def stop(self):
        self.send("stop")
        self.client_socket.close()

if __name__ == "__main__":
    client = Client()

    client.login()

    sys.exit(client.app.exec_())