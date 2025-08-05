import os
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect, QWidget, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QPoint, QDateTime, QDate, QTime
from models.transaction_model import update_transaction
from models.transaction_model import get_or_create_category_id

ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'edit_transaction.ui')

class editTransaction(QDialog):
    def __init__(self, user_id, data, parent=None):
        super(editTransaction, self).__init__(parent)
        loadUi(ui_path, self)
        self.user_id = user_id
        self.data = data
        self.type_combobox.setCurrentText(self.data["Type"])
        self.categories_combobox.setCurrentText(self.data["Category"])
        convert_amount = self.data["Amount"].replace("đ","").strip()
        amount_value = str(convert_amount)
        self.amount_line_edit.setText(amount_value)
        self.amount_line_edit.textChanged.connect(self.format_number)
        self.describe_line_edit.setText(self.data["Note"])
        self.dateEdit.setDisplayFormat("dd-MM-yyyy")
        date_time_str = self.data["Date"]
        date_part, time_part = date_time_str.split(" ")
        qdate = QDate.fromString(date_part, "dd-MM-yyyy")
        self.dateEdit.setDate(qdate)
        qtime = QTime.fromString(time_part, "HH:mm:ss")
        self.timeEdit.setTime(qtime)
        self.transaction_id = self.data["Transaction ID"]

        self.frame_check.hide()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.ctn_btn.clicked.connect(self.check_data)
        self.amount_line_edit.returnPressed.connect(self.check_data)
        self.describe_line_edit.returnPressed.connect(self.check_data)
        self.cancel_btn.clicked.connect(self.reject)
        if hasattr(self,"type_combobox"):
            self.type_combobox.currentIndexChanged.connect(self.hide_error_frame)
        if hasattr(self,"categories_combobox"):
            self.categories_combobox.currentIndexChanged.connect(self.hide_error_frame)
        if hasattr(self,"amount_line_edit"):
            self.amount_line_edit.textChanged.connect(self.hide_error_frame)
        if hasattr(self,"timeEdit"):
            self.timeEdit.dateChanged.connect(self.hide_error_frame)
        if hasattr(self,"dateEdit"):
            self.dateEdit.dateChanged.connect(self.hide_error_frame)

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
        amount_text = self.amount_line_edit.text().replace(",","").strip()
        date_part = self.dateEdit.date()
        time_part = self.timeEdit.time()
        combined_datetime = QDateTime(date_part, time_part)
        date_value_str = combined_datetime.toString("dd-MM-yyyy HH:mm:ss")
        type = self.type_combobox.currentText()
        categories = self.categories_combobox.currentText()
        describe = self.describe_line_edit.text()
        print(f"type: {type}, categories: {categories}, amount: {amount_text}, describe: {describe}, date: {date_value_str} ")
        if not type or not categories or not amount_text or not date_value_str:
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
        category_id = get_or_create_category_id(self.user_id,categories,type)
        transaction_data = {
            "Transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "category_id": category_id,
            "type": type,
            "amount": amount_value,
            "note": describe,
            "date": date_value_str
        }
        update_result = update_transaction(transaction_data)
        if update_result:
            self.accept()
        else:
            print("lỗi")


