import socket

class Client:
    def __init__(self, myAdr=None):
        self.host = "127.0.0.1"
        self.port = 1004
        self.myAdr = myAdr

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def recv(self):
        data = self.client_socket.recv(1024)
        return data.decode()

    def stop(self):
        self.client_socket.close()

if __name__ == "__main__":
    client = Client()
    data = client.recv()
    print(data)