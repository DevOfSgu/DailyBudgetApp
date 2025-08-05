import calendar
from datetime import datetime, date
from PyQt5.QtCore import Qt, QObject, QEvent
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox, QTableWidgetItem, QTableWidget, QAbstractScrollArea, \
    QHeaderView, QAbstractItemView, QMainWindow, QLabel, QDialog, QProgressBar
from controllers.Add_budget_controllers import addBudget
from controllers.editBudget import editBudget
from controllers.edit_transaction import editTransaction
from models.Budget_model import budget_data, delete_budget


class Budget_logic(QObject):
        def __init__(self, Budget_page_widget: QWidget, user_data, parent_window: QMainWindow ):
            super().__init__()
            self.user_data = user_data
            self.user_id = user_data["user_id"]
            self.ui = Budget_page_widget
            self.parent_window = parent_window
            self.data = budget_data(self.user_id)
            self.Budget_table = self.ui.findChild(QTableWidget, "Budget_table")
            self.add_budget = self.ui.findChild(QPushButton, "add_budget")
            self.edit_budget_button = self.ui.findChild(QPushButton,"edit_budget_button")
            self.delete_budget_button = self.ui.findChild(QPushButton,"delete_budget_button")
            self.currentMonth = datetime.now().month
            self.currentYear = datetime.now().year

            self.placeholder_label = QLabel("No Budget.\nPlease press 'Add budget' to start.", self.Budget_table)
            self.placeholder_label.setStyleSheet("border-radius: 0px;")
            self.placeholder_label.setAlignment(Qt.AlignCenter)
            self.placeholder_label.setStyleSheet("color: grey; font-size: 14px;")
            self.placeholder_label.setWordWrap(True)
            self.placeholder_label.hide()

            self.Budget_table.viewport().installEventFilter(self)
            self.parent_window.installEventFilter(self)

            self.edit_budget_button.hide()
            self.delete_budget_button.hide()
            self.load_budget(budget_data(self.user_id))
            self.connect_signals()

        def connect_signals(self):
            if self.add_budget:
                self.add_budget.clicked.connect(self.open_add_budget_dialog)
            if self.delete_budget_button:
                self.delete_budget_button.clicked.connect(self.handle_delete_button_clicked)
            if self.edit_budget_button:
                self.edit_budget_button.clicked.connect(self.edit_handle)


        def open_add_budget_dialog(self):
            print("Chuẩn bị mở dialog thêm giao dịch...")
            dialog = addBudget(self.user_id, self.ui)
            self.center_widget_on_parent(dialog, self.ui)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                print("đã accept")
                self.load_budget(self.data)
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

        def load_budget(self,data):
                if not data:
                    self.Budget_table.setRowCount(0)
                    self.placeholder_label.show()
                    return # Dừng hàm tại đây
                else:
                    self.placeholder_label.hide()
                custom_header = ["Category", "Budget", "Spent", "remaining", "Time Left", "Progress"]

                self.Budget_table.setRowCount(len(data))
                self.Budget_table.setColumnCount(len(custom_header))
                self.Budget_table.setHorizontalHeaderLabels(custom_header)

                for row_idx, row_data in enumerate(data):
                    budget_id = row_data[0]
                    category = row_data[1]
                    budget = row_data[2]
                    spent = row_data[3]
                    remaining = row_data[4]
                    period = row_data[5]
                    try:
                        progress = int((spent / budget) * 100) if budget > 0 else 0
                    except:
                        progress = 0
                    over_budget = False
                    if spent > budget:
                        over_budget = True
                        progress = 100
                    today = date.today()
                    if period == "week":
                        days_left = 6 - today.weekday()
                    elif period == "month":
                        total_days = calendar.monthrange(today.year, today.month)[1]
                        days_left = total_days - today.day
                    elif period == "year":
                        last_day = date(today.year, 12, 31)
                        days_left = (last_day - today).days
                    else:
                        days_left = 0
                    display_values = [
                        category,
                        "{:,.0f} đ".format(budget),
                        "{:,.0f} đ".format(spent),
                        "{:,.0f} đ".format(remaining),
                        f"{days_left} days"

                    ]
                    for col_idx, value in enumerate(display_values):
                        item = QTableWidgetItem(value)
                        item.setTextAlignment(Qt.AlignCenter)
                        if col_idx == 0:
                            item.setData(Qt.UserRole, budget_id)
                            item.setData(Qt.UserRole + 1, period)
                        self.Budget_table.setItem(row_idx, col_idx, item)
                    progress_bar = QProgressBar()
                    progress_bar.setValue(progress)
                    progress_bar.setFormat(f"{progress}%")
                    progress_bar.setAlignment(Qt.AlignCenter)
                    progress_bar.setTextVisible(False)
                    if over_budget:
                        bar_color = "#FF0000"
                    elif progress > 70:
                        bar_color = "#FF5733"  # cam/đỏ nếu > 70%
                    else:
                        bar_color = "#4CAF50"
                    progress_bar.setStyleSheet(f"""
                        QProgressBar {{
                            border: 1px solid #bbb;
                            border-radius: 5px;
                            background-color: #f0f0f0;
                            text-align: center;
                        }}
                        QProgressBar::chunk {{
                            background-color: {bar_color};
                            width: 10px;
                            margin: 1px;
                        }}
                    """)
                    # Thêm QProgressBar vào cell
                    self.Budget_table.setCellWidget(row_idx, 5, progress_bar)
                self.Budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.Budget_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                self.Budget_table.verticalHeader().setVisible(False)
                self.Budget_table.setFocusPolicy(Qt.NoFocus)
                self.Budget_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.Budget_table.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.Budget_table.itemSelectionChanged.connect(self.on_row_selected)

        def eventFilter(self, obj, event):
            if obj is self.Budget_table.viewport() and event.type() == QEvent.Resize:
                self.placeholder_label.setGeometry(self.Budget_table.viewport().rect())
            if obj == self.parent_window and event.type() == QEvent.MouseButtonPress:
                mapped_pos = self.ui.mapFrom(self.parent_window, event.pos())
                table_rect = self.Budget_table.geometry()

                if not table_rect.contains(mapped_pos):
                    self.Budget_table.clearSelection()

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
            if self.Budget_table.selectedItems():
                self.edit_budget_button.show()
                self.delete_budget_button.show()
            else:
                self.edit_budget_button.hide()
                self.delete_budget_button.hide()
        def edit_handle(self):
            current_row = self.Budget_table.currentRow()
            if current_row < 0:
                return

            item = self.Budget_table.item(current_row, 0)
            if not item:
                return

            budget_id = item.data(Qt.UserRole)
            period = item.data(Qt.UserRole + 1)

            old_category_item = self.Budget_table.item(current_row, 0)
            old_amount_item = self.Budget_table.item(current_row, 1)

            if old_category_item and old_amount_item:
                old_category = old_category_item.text().strip()
                old_amount_str = old_amount_item.text().replace(",", "").replace("đ", "").strip()
                try:
                    old_amount = float(old_amount_str)
                except ValueError:
                    old_amount = 0
            else:
                old_category = None
                old_amount = 0

            data = {
                "budget_id": budget_id,
                "category": old_category,
                "amount": old_amount,
                "period": period,
                "user_id": self.user_id
            }

            dialog = editBudget(self.user_id, data, self.ui)
            self.center_widget_on_parent(dialog, self.ui)
            result = dialog.exec_()
            if result == QDialog.Accepted:
                QMessageBox.information(self.ui, "Successful", "Updated budget successfully!")
                self.refresh()
            else:
                print("Dialog đã bị hủy.")



        def handle_delete_button_clicked(self):
            current_row = self.Budget_table.currentRow()
            if current_row < 0:
                return
            item = self.Budget_table.item(current_row, 0)  # Cột 0 là category
            if item is None:
                return
            budget_id = item.data(Qt.UserRole)  # Lấy budget_id từ UserRole
            if not budget_id:
                print("Cannot find budget ID.")
                return
            reply = QMessageBox.question(
            self.ui,
            'Confirm',
            f"Are you sure you want to delete this transaction?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    delete_budget(budget_id)
                    QMessageBox.information(self.ui, "Successful", f"Delete budget successfully.")
                    self.refresh()


                except Exception as e:
                     QMessageBox.warning(self.ui, "Error", f"Cannot delete budget")


        def refresh(self):
            self.data = budget_data(self.user_id)
            self.load_budget(self.data)








