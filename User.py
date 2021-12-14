class User:
    def __init__(self):
        self.id = None
        self.pwd = None
        self.name = None
        self.email = None
        self.date = None

        self.client = None

    def setClient(self, client):
        self.client = client