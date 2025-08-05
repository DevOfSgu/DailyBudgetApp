from PyQt5.QtWidgets import QMainWindow, QLineEdit
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon

class ButtonController(QMainWindow):
    def __init__(self, password_edit, toggle_button):
        super().__init__()
        self.password_edit = password_edit
        self.toggle_button = toggle_button
        #Icon ẩn hiện
        self.icon_eye_open = QIcon(":/icon/eye_bl.svg")
        self.icon_eye_closed = QIcon(":/icon/eye-off_bl.svg")
        self.toggle_button.setIcon(self.icon_eye_closed)
        self.toggle_button.clicked.connect(self.Show_hide_password)

    def Show_hide_password(self):
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setIcon(self.icon_eye_open)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.toggle_button.setIcon(self.icon_eye_closed)