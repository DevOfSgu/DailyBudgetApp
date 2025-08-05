import os
from datetime import datetime
from controllers.Mainscreen_controllers import Main_screen
from models.dashboard_model import update_balance, get_income, get_expense
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PyQt5.uic import loadUi
from models.user_model import mark_user_as_old
ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'balance.ui')

class Balance(QWidget):
    def __init__(self, userdata):
        super(Balance, self).__init__()
        loadUi(ui_path, self)
        self.userdata = userdata
        self.user_id = userdata["user_id"]
        self.frame_check.hide()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.balance_input.textChanged.connect(self.format_number)
        self.acceptBtn.clicked.connect(self.Balance_function)
        self.cancel_btn.clicked.connect(self.close)
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        if hasattr(self,"balance_input"):
            self.balance_input.returnPressed.connect(self.Balance_function)
            self.balance_input.textChanged.connect(self.hide_error_frame)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.findChild(QWidget, "mainFrame").setGraphicsEffect(shadow)

    def show_message(self, text):
        if hasattr(self,"text_error"):
            self.text_error.setText(f"{text}")
            self.frame_check.show()
    def hide_error_frame(self):
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()
    def format_number(self):
        text = self.balance_input.text().replace(",", "").strip()
        if text.isdigit():
            formatted = "{:,}".format(int(text))
            self.balance_input.blockSignals(True)
            self.balance_input.setText(formatted)
            self.balance_input.blockSignals(False)
            self.balance_input.setCursorPosition(len(formatted))
    def Balance_function(self):
        balance_input = self.balance_input.text().replace(",","").strip()
        if not balance_input:
            self.show_message("please enter your initial balance!")
            return
        try:
            Balance_value = float(balance_input)
        except ValueError:
                self.show_message("Balance must be a number")
                return
        if Balance_value < 0:
            self.show_message("Balance must be higher than 0")
            return
        Balance_value = float(Balance_value)
        income = get_income(self.user_id, self.currentMonth, self.currentYear) or 0
        expense = get_expense(self.user_id, self.currentMonth, self.currentYear) or 0
        final_balance = Balance_value + income - expense
        print(f"total balance: {final_balance}")
        data ={
                "balance": final_balance,
                "user_id": self.user_id,
                "month": self.currentMonth,
                "year": self.currentYear
        }
        update = update_balance(data)
        if update:
            mark_user_as_old(self.user_id)
            self.DashBoard_screen = Main_screen(self.userdata)
            self.DashBoard_screen.show()
            self.close()
        else:
            print("lỗi")
def show_balance_ui(userdata):
    balance_widget = Balance(userdata)
    balance_widget.show()









