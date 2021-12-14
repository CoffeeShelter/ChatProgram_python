from PyQt5.QtWidgets import *
from PyQt5 import uic

login_ui = uic.loadUiType("login.ui")[0]

class LoginWindow(QWidget, login_ui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)