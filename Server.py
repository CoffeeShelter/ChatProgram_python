import socket
import threading
import time

from S_Client import S_Client
from Database import DBManager
import pandas as pd

from User import User

class Server:
    def __init__(self):
        self.db = DBManager()
        self.db.connect("root","1234","localhost")

        self.host = '127.0.0.1'
        self.port = 1004 

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

        self.users = []

        self.server_socket.listen()

        self.running = False

    def accept(self):
        self.running = True
        print("서버 시작...!")
        while self.running:
            client_socket, addr = self.server_socket.accept()

            user = User()
            user.setClient(S_Client(client_socket, addr))
            self.users.append(user)

            print('Connected by', user.client.addr)

            t = threading.Thread(target=self.recv, args=(user, ))
            t.daemon = True
            t.start()

    def run(self):
        t = threading.Thread(target=self.accept)
        t.daemon = True
        t.start()

        data = ""
        while(data != "stop"):
            data = input()

            if len(self.users) > 0:
                for user in self.users:
                    user.client.send(data)
        
        self.sendAll("SERVER_CLOSE")
        self.stop()


    def recv(self, user):
        while self.running:
            data = user.client.recv()
            print(data)

            if data == "":
                break

            if data == "stop":
                break

            self.func(user, data)

        print("[{}] : 종료".format(user.name))
        self.remove(user)
        user.client.stop()

    def remove(self, user):
        for i in range(len(self.users)):
            if user.name == self.users[i].name:
                del self.users[i]

    def func(self, user, data):
        data = data.split('_')
        
        if data[0] == "login":
            id = data[1]
            pwd = data[2]
            self.login(user, id, pwd)

        elif data[0] == "signup":
            id = data[1]
            pwd = data[2]
            email = data[3]
            name = data[4]
            self.signup(user, id, pwd, email, name)

        elif data[0] == "findId":
            email = data[1]
            self.findId(user, email)

        elif data[0] == "repwd":
            id = data[1]
            pwd = data[2]
            email = data[3]
            self.repwd(user, id, pwd, email)

        elif data[0] == "chat":
            msg = data[1]
            msg = "chat_" + "{}_{}".format(user.name, msg)
            self.sendAll(msg)

    def repwd(self, user, id, pwd, email):
        result = self.db.search_by_id_email(id, email)
        result = pd.DataFrame(result)
        if len(result) > 0:
            self.db.update_pwd(id, pwd)
            msg = "repwd_success"
            user.client.send(msg)
            user.client.recv()
        else:
            msg = "repwd_error"
            user.client.send(msg)
            user.client.recv()

    def findId(self, user, email):
        result = self.db.search_by_email(email)
        result = pd.DataFrame(result)
        if len(result) > 0:
            email_ = result.at[0, "ID"]
            msg = "signup_success_{}".format(email_)
            user.client.send(msg)
            user.client.recv()
        else:
            msg = "signup_error"
            user.client.send(msg)
            user.client.recv()

    def signup(self, user, id, pwd, email, name):
        result = self.db.search_by_id(id)
        result = pd.DataFrame(result)
        if len(result) > 0:
            user.client.send("signup_error_id")
            user.client.recv()
        else:
            result = self.db.search_by_name(name)
            result = pd.DataFrame(result)
            if len(result) > 0:
                user.client.send("signup_error_name")
                user.client.recv()
            else:
                self.db.insertUser(id, pwd, email, name)
                user.client.send("signup_success")
                user.client.recv()

    def login(self, user, id, pwd):
        result = self.db.search_by_id(id)
        result = pd.DataFrame(result)
        if len(result) > 0:
            pwd_ = result.at[0, "PWD"]
            if pwd_ == pwd:
                user.id = result.at[0, "ID"]
                user.pwd = result.at[0, "PWD"]
                user.name = result.at[0, "NAME_"]
                user.email = result.at[0, "EMAIL"]
                user.date = result.at[0, "DATE_"]

                user.client.send("login_OK")

                data = user.client.recv()
                if data == "ready":
                    msg = "{}_{}_{}_{}_{}".format(user.id, user.pwd, user.name, user.email, user.date)
                    user.client.send(msg)

                    data = user.client.recv()

            else:
                user.client.send("login_FAIL")

        else:
            user.client.send("login_FAIL")

    def stop(self):
        for user in self.users:
            user.client.stop()

        self.running = False
        self.server_socket.close()

    def sendAll(self, msg):
        for user in self.users:
            user.client.send(msg)

if __name__ == "__main__":
    server = Server()
    server.run()