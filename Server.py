from os import kill
import socket
import threading

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
            # client.send("welcome~!")

            t = threading.Thread(target=self.recv, args=(user, ))
            t.start()

    def run(self):
        t = threading.Thread(target=self.accept)
        t.daemon = True
        t.start()

        data = None
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
            if data == "":
                break

            if data == "stop":
                break

            self.func(user, data)

        print("[{}] : 종료".format(user.name))
        self.users.remove(user)
        user.client.stop()

    def func(self, user, data):
        data = data.split('_')

        if len(data) < 2:
            data = data[0]

            print("[{}] : {}".format(user.client.addr, data))
            return
        
        if data[0] == "login":
            id = data[1]
            pwd = data[2]
            self.login(user, id, pwd)

        elif data[0] == "chat":
            msg = data[1]
            msg = "chat_" + "{}_{}".format(user.name, msg)

            print("[{}] : {}".format(user.name, msg))
            self.sendAll(msg)

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