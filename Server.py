import socket
from S_Client import S_Client

class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 1004 

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

        self.clients = []

        self.server_socket.listen()

    def run(self):
        while True:
            client_socket, addr = self.server_socket.accept()

            client = S_Client(client_socket, addr)
            self.clients.append(client)

            print('Connected by', client.addr)

            client.send("welcome~!")

    def recv(self, client):
        data = client.recv(1024)
        return data.decode()

    def send(self, client, data):
        client.sendall(data.encode())

    def stop(self):
        for client in self.clients:
            client.stop()

        self.server_socket.close()

if __name__ == "__main__":
    server = Server()
    server.run()