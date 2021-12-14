from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint

chatting_ui = uic.loadUiType("Chatting.ui")[0]

class ChattingWindow(QWidget, chatting_ui):
    def __init__(self, client):
        super().__init__()
        self.setupUi(self)
        self.client = client

        self.textEdit.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.textEdit:
            if event.key() == QtCore.Qt.Key_Return and self.textEdit.hasFocus():
                self.client.chatting_func()
                
                return True
        return False

    def closeEvent(self, event):
        self.client.stop()