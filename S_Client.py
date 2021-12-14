class S_Client:
    def __init__(self, socket, addr):
        self.socket = socket
        self.addr = addr
        self.user = None

    def send(self, data):
        self.socket.sendall(data.encode())

    def recv(self):
        data = self.socket.recv(1024)
        return data.decode()

    def stop(self):
        self.socket.close()