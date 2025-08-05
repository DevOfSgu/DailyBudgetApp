import os
from datetime import datetime, date, timedelta
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QDateTime
from sympy.integrals.meijerint_doc import category
from sympy.physics.units import amount

from models.Budget_model import insert_budget
from models.transaction_model import get_or_create_category_id

ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'add_budget.ui')

class addBudget(QDialog):
    def __init__(self, user_id, parent=None):
        super(addBudget, self).__init__(parent)
        loadUi(ui_path, self)
        self.user_id = user_id
        self.frame_check.hide()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.amount_line_edit.returnPressed.connect(self.check_data)
        self.amount_line_edit.textChanged.connect(self.format_number)
        self.cancel_btn.clicked.connect(self.reject)
        self.add_btn.clicked.connect(self.check_data)
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        if hasattr(self,"TimecomboBox"):
            self.TimecomboBox.currentIndexChanged.connect(self.hide_error_frame)
        if hasattr(self,"categories_combobox"):
            self.categories_combobox.currentIndexChanged.connect(self.hide_error_frame)
        if hasattr(self,"amount_line_edit"):
            self.amount_line_edit.textChanged.connect(self.hide_error_frame)

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
        if text.isdigit():
            formatted = "{:,}".format(int(text))
            self.amount_line_edit.blockSignals(True)
            self.amount_line_edit.setText(formatted)
            self.amount_line_edit.blockSignals(False)
            self.amount_line_edit.setCursorPosition(len(formatted))

    def check_data(self):
        print("đã ấn button")
        categories = self.categories_combobox.currentText()
        amount_text = self.amount_line_edit.text().replace(",","").strip()
        time = self.TimecomboBox.currentText()
        print(f"DATA: {categories} - {amount_text} - {time}")
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
        year = today.year
        month = today.month
        week = today.isocalendar()[1]
        budget_data = {
            "user_id": self.user_id,
            "category_id": category_id,
            "amount_limit": amount_value,
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
        elif time == "This Year":
            budget_data["year"] = self.currentYear
        print(budget_data)
        insert_new_budget = insert_budget(budget_data)
        print(insert_new_budget)
        if insert_new_budget:
            print("đã add budget")
            self.accept()
        else:
            print("lỗi")