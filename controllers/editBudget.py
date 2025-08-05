import os
from datetime import date, datetime

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect, QWidget, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QPoint, QDateTime, QDate, QTime

from models.Budget_model import update_budget
from models.transaction_model import get_or_create_category_id

ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'edit_budget.ui')

class editBudget(QDialog):
    def __init__(self, user_id, data, parent=None):
        super(editBudget, self).__init__(parent)
        loadUi(ui_path, self)
        self.user_id = user_id
        self.data = data
        print(data)
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        self.categories_combobox.setCurrentText(self.data["category"])
        convert_amount = self.data["amount"]
        amount_value = str(convert_amount)
        self.amount_line_edit.setText(amount_value)
        self.format_number()
        self.amount_line_edit.textChanged.connect(self.format_number)
        if self.data["period"] == "week":
            self.TimecomboBox.setCurrentText("This week")
        elif self.data["period"] == "month":
            self.TimecomboBox.setCurrentText("This month")
        elif self.data["period"] == "year":
            self.TimecomboBox.setCurrentText("This Year")
        self.budget_id = self.data["budget_id"]

        self.frame_check.hide()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.edit_btn.clicked.connect(self.check_data)
        self.amount_line_edit.returnPressed.connect(self.check_data)
        self.cancel_btn.clicked.connect(self.reject)
        if hasattr(self,"categories_combobox"):
            self.categories_combobox.currentIndexChanged.connect(self.hide_error_frame)
        if hasattr(self,"amount_line_edit"):
            self.amount_line_edit.textChanged.connect(self.hide_error_frame)
        if hasattr(self,"TimecomboBox"):
            self.TimecomboBox.currentIndexChanged.connect(self.hide_error_frame)


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
        text = self.amount_line_edit.text().replace(",", "").strip()
        try:
            number = float(text)
            if number.is_integer():
                formatted = "{:,}".format(int(number))
            else:
                formatted = "{:,.2f}".format(number)
            self.amount_line_edit.blockSignals(True)
            self.amount_line_edit.setText(formatted)
            self.amount_line_edit.blockSignals(False)
            self.amount_line_edit.setCursorPosition(len(formatted))
        except ValueError:
            pass


    def check_data(self):
        amount_text = self.amount_line_edit.text().replace(",","").strip()
        categories = self.categories_combobox.currentText()
        time = self.TimecomboBox.currentText()
        if not categories or not amount_text or not time:
            self.show_message("Please. fill in all information!")
            return
        try:
            amount_value = float(amount_text)
        except ValueError:
                self.show_message("Amount must be a number")
                return
        if amount_value < 0:
            self.show_message("Amount must be higher than 0")
            return
        amount_value = float(amount_value)
        category_id = get_or_create_category_id(self.user_id,categories,"expense")
        today = date.today()
        week = today.isocalendar()[1]
        budget_data = {
            "budget_id": self.budget_id,
            "user_id": self.user_id,
            "category_id": category_id,
            "amount": amount_value,
            "month": None,
            "year": None,
            "week": None
        }
        if time == "This week":
            budget_data["year"] = self.currentYear
            budget_data["month"] = self.currentMonth
            budget_data["week"] = week
        elif time == "This month":
            budget_data["year"] = self.currentYear
            budget_data["month"] = self.currentMonth
            budget_data["week"] = None
        elif time == "This Year":
            budget_data["year"] = self.currentYear
            budget_data["month"] = None
            budget_data["week"] = None

        update_result = update_budget(budget_data)
        if update_result:
            self.accept()
        else:
            print("lỗi")


