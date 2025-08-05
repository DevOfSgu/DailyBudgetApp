import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt, QObject, QEvent, QDateTime, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox, QTableWidgetItem, QTableWidget, QAbstractScrollArea, \
    QHeaderView, QAbstractItemView, QMainWindow, QFrame, QDateEdit, QComboBox, QLineEdit, QLabel
from PyQt5.QtWidgets import QDialog

from controllers.Dashboard import Dashboard_logic
from controllers.edit_transaction import editTransaction
from controllers.Add_transaction_controller import addTransaction
from models.transaction_model import delete_transaction
from models.transaction_model import get_oldest_transaction_date
from models.transaction_model import filter_transactions
from models.transaction_model import transaction_data
from models.dashboard_model import update_balance,get_balance
class Transaction_logic(QObject):
        transaction_updated = pyqtSignal()
        def __init__(self, transaction_page_widget: QWidget, user_data, parent_window: QMainWindow ):
            super().__init__()
            self.user_data = user_data
            self.user_id = user_data["user_id"]
            self.ui = transaction_page_widget
            self.parent_window = parent_window
            self.data = transaction_data(self.user_id)
            self.transactionTable = self.ui.findChild(QTableWidget, "transactionTable")
            self.add_button = self.ui.findChild(QPushButton, "add_transactionBtn")
            self.edit_button = self.ui.findChild(QPushButton,"edit_button")
            self.delete_button = self.ui.findChild(QPushButton,"delete_button")
            self.filter_button = self.ui.findChild(QPushButton,"filter_button")
            self.refresh_btn = self.ui.findChild(QPushButton,"refresh_btn")
            self.fromDate = self.ui.findChild(QDateEdit,"fromDate")
            self.toDate = self.ui.findChild(QDateEdit,"toDate")
            self.comboBox_category = self.ui.findChild(QComboBox,"comboBox_category")
            self.comboBox_type = self.ui.findChild(QComboBox,"comboBox_type")
            self.minPrice = self.ui.findChild(QLineEdit,"minPrice")
            self.minPrice.textChanged.connect(lambda: self.format_number(self.minPrice))
            self.maxPrice = self.ui.findChild(QLineEdit,"maxPrice")
            self.maxPrice.textChanged.connect(lambda: self.format_number(self.maxPrice))
            self.fromDate.setDisplayFormat("dd-MM-yyyy")
            self.toDate.setDisplayFormat("dd-MM-yyyy")
            self.currentMonth = datetime.now().month
            self.currentYear = datetime.now().year
            print(f"{self.currentMonth}-{self.currentYear}")
            self.placeholder_label = QLabel("No Transactions.\nPlease press 'Add Transaction' to start.", self.transactionTable)
            self.placeholder_label.setStyleSheet("border-radius: 0px;")
            self.placeholder_label.setAlignment(Qt.AlignCenter)
            self.placeholder_label.setStyleSheet("color: grey; font-size: 14px;")
            self.placeholder_label.setWordWrap(True)
            self.placeholder_label.hide()
            oldest_date = get_oldest_transaction_date()
            print(oldest_date)
            current_datetime = QDateTime.currentDateTime()
            if oldest_date:
                qdatetime = QDateTime.fromString(oldest_date, "dd-MM-yyyy HH:mm:ss")
                qdate = qdatetime.date()
                self.fromDate.setDate(qdate)
            else:
                self.fromDate.setDate(current_datetime.date())
            self.toDate.setDate(current_datetime.date())
            self.transactionTable.viewport().installEventFilter(self)
            self.parent_window.installEventFilter(self)

            self.edit_button.hide()
            self.delete_button.hide()
            self.load_transaction(transaction_data(self.user_id))
            print("Finding button 'add_transactionBtn':", self.add_button)
            self.connect_signals()

        def connect_signals(self):
            if self.add_button:
                print("đã ấn button")
                self.add_button.clicked.connect(self.open_add_transaction_dialog)
            if self.delete_button:
                self.delete_button.clicked.connect(self.handle_delete_button_clicked)
            if self.edit_button:
                self.edit_button.clicked.connect(self.edit_handle)
            if self.filter_button:
                self.filter_button.clicked.connect(self.filter_function)
            if self.refresh_btn:
                self.refresh_btn.clicked.connect(lambda: self.load_transaction(self.data))

        def open_add_transaction_dialog(self):
            print("Chuẩn bị mở dialog thêm giao dịch...")
            dialog = addTransaction(self.user_id, self.ui)
            self.center_widget_on_parent(dialog, self.ui)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                self.transaction_updated.emit()  # <-- Phát tín hiệu
                self.load_transaction(self.data)
                QMessageBox.information(self.ui, "Successful", "Add transaction successfully!")
                self.refresh()

            else:
                print("Dialog đã bị hủy.")

        def center_widget_on_parent(self, widget, parent):

            parent_geometry = parent.geometry()
            parent_center_point = parent_geometry.center()

            widget_geometry = widget.frameGeometry()

            new_x = parent_center_point.x() - widget_geometry.width() / 2
            new_y = parent_center_point.y() - widget_geometry.height() / 2

            widget.move(int(new_x), int(new_y))

        def load_transaction(self,data):
                if not data:
                    self.transactionTable.setRowCount(0)
                    self.placeholder_label.show()
                    return # Dừng hàm tại đây
                else:
                    self.placeholder_label.hide()
                custom_header = ["Transaction ID", "Date", "Category", "Type", "Amount", "Note" ]

                self.transactionTable.setRowCount(len(data))
                self.transactionTable.setColumnCount(len(custom_header))
                self.transactionTable.setHorizontalHeaderLabels(custom_header)

                for row_idx, row_data in enumerate(data):
                    for col_idx, value in enumerate(row_data):
                        if col_idx == 4 and isinstance(value, (int, float)):
                            formatted_value = "{:,.0f} đ".format(value)
                            item = QTableWidgetItem(formatted_value)
                        else:
                            item = QTableWidgetItem(str(value))
                        self.transactionTable.setItem(row_idx, col_idx, item)
                self.transactionTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.transactionTable.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                self.transactionTable.verticalHeader().setVisible(False)
                self.transactionTable.setFocusPolicy(Qt.NoFocus)
                self.transactionTable.setAlternatingRowColors(True)
                self.transactionTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.transactionTable.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.transactionTable.itemSelectionChanged.connect(self.on_row_selected)

        def eventFilter(self, obj, event):
            if obj is self.transactionTable.viewport() and event.type() == QEvent.Resize:
                self.placeholder_label.setGeometry(self.transactionTable.viewport().rect())
            if obj == self.parent_window and event.type() == QEvent.MouseButtonPress:
                mapped_pos = self.ui.mapFrom(self.parent_window, event.pos())
                table_rect = self.transactionTable.geometry()

                if not table_rect.contains(mapped_pos):
                    self.transactionTable.clearSelection()

            return super().eventFilter(obj, event)

        def format_number(self,line_edit):
            text = line_edit.text().replace(",", "").strip()
            if text.isdigit():
                formatted = "{:,}".format(int(text))
                line_edit.blockSignals(True)
                line_edit.setText(formatted)
                line_edit.blockSignals(False)
                line_edit.setCursorPosition(len(formatted))

        def on_row_selected(self):
            if self.transactionTable.selectedItems():
                self.edit_button.show()
                self.delete_button.show()
            else:
                self.edit_button.hide()
                self.delete_button.hide()
        def edit_handle(self):
            current_row = self.transactionTable.currentRow()
            old_type_item = self.transactionTable.item(current_row, 3)
            old_amount_item = self.transactionTable.item(current_row, 4)
            if old_type_item and old_amount_item:
                old_type = old_type_item.text().strip().lower()
                old_amount_str = old_amount_item.text().replace(",", "").replace("đ", "").strip()
                try:
                    old_amount = float(old_amount_str)
                except ValueError:
                    old_amount = 0
            else:
                old_type = None
                old_amount = 0
            data = {}
            for col in range(self.transactionTable.columnCount()):
                header = self.transactionTable.horizontalHeaderItem(col).text()
                item = self.transactionTable.item(current_row,col)
                if item:
                    data[header] = item.text()
                else:
                    data[header] = ""
            dialog = editTransaction(self.user_id, data, self.ui)
            self.center_widget_on_parent(dialog, self.ui)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                self.data = transaction_data(self.user_id)
                new_row_data = self.data[current_row]  # (transaction_id, date, category, type, amount, note)
                new_type = new_row_data[3].strip().lower()
                new_amount = float(new_row_data[4])
                balance = get_balance(self.user_id, self.currentMonth, self.currentYear)
                # TÍNH TOÁN BALANCE MỚI
                if old_type == new_type:
                    if old_type == "income":
                        balance += (new_amount - old_amount)
                    elif old_type == "expense":
                        balance -= (new_amount - old_amount)
                else:
                    if old_type == "income":
                        balance -= old_amount
                    elif old_type == "expense":
                        balance += old_amount

                    if new_type == "income":
                        balance += new_amount
                    elif new_type == "expense":
                        balance -= new_amount

                update_balance({
                    "user_id": self.user_id,
                    "month": self.currentMonth,
                    "year": self.currentYear,
                    "balance": balance
                })
                self.transaction_updated.emit()
                QMessageBox.information(self.ui, "Successful", "Updated transaction successfully!")
                self.refresh()
            else:
                print("Dialog đã bị hủy.")


        def handle_delete_button_clicked(self):
            current_row = self.transactionTable.currentRow()
            if current_row < 0:
                return
            transaction_id = self.transactionTable.item(current_row, 0).text()
            type_item = self.transactionTable.item(current_row, 3)
            amount_item = self.transactionTable.item(current_row, 4)
            if type_item and amount_item:
                trans_type = type_item.text().strip().lower()
                amount_str = amount_item.text().replace(",", "").replace("đ", "").strip()
                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0
            else:
                trans_type = None
                amount = 0
            balance = get_balance(self.user_id,self.currentMonth, self.currentYear)
            if balance is None:
                balance = 0
            if trans_type == "income":
                balance = balance - amount
            else:
                balance = balance + amount
            data = {
                "user_id": self.user_id,
                "month": self.currentMonth,
                "year": self.currentYear,
                "balance": balance
            }
            update_balance(data)
            reply = QMessageBox.question(
            self.ui,
            'Confirm',
            f"Are you sure you want to delete this transaction?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    delete_transaction(transaction_id)
                    self.data = transaction_data(self.user_id)
                    self.transaction_updated.emit()
                    QMessageBox.information(self.ui, "Successful", f"Delete transaction successfully.")
                    self.refresh()


                except Exception as e:
                     QMessageBox.warning(self.ui, "Error", f"Cannot delete transaction")
        def refresh(self):
            oldest_date = get_oldest_transaction_date()
            current_datetime = QDateTime.currentDateTime()
            if oldest_date:
                qdatetime = QDateTime.fromString(oldest_date, "dd-MM-yyyy HH:mm:ss")
                qdate = qdatetime.date()
                self.fromDate.setDate(qdate)
            else:
                self.fromDate.setDate(current_datetime.date())
            self.toDate.setDate(current_datetime.date())
            self.comboBox_category.setCurrentText("Categories")
            self.comboBox_type.setCurrentText("Type")
            self.minPrice.clear()
            self.maxPrice.clear()
            self.data = transaction_data(self.user_id)
            self.load_transaction(self.data)

        def filter_function(self):
            filters = {
                "user_id": self.user_id,
                "from_date": self.fromDate.date().toString("yyyy-MM-dd"),
                "to_date": self.toDate.date().toString("yyyy-MM-dd"),
                "category": self.comboBox_category.currentText(),
                "type": self.comboBox_type.currentText(),
                "min_price": self.minPrice.text().replace(",","").strip(),
                "max_price": self.maxPrice.text().replace(",","").strip()
            }
            if filters["category"] == "Categories" :
                filters["category"] = None
            if filters["type"]=="Type":
                filters["type"]=None
            results = filter_transactions(filters)
            print(results)
            self.load_transaction(results)







