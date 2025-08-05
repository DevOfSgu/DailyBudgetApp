from datetime import datetime
from PyQt5.QtCore import QObject, Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QLineEdit, QTableWidgetItem, QHeaderView, \
    QAbstractScrollArea, QAbstractItemView, QLabel, QTableWidget, QFrame, QGraphicsDropShadowEffect, QPushButton, \
    QVBoxLayout
from models.dashboard_model import get_expense, get_income,get_balance, get_top_5_transaction, \
get_income_each_month, get_expense_each_month, get_data_of_expense
from Utils.Draw_chart import draw_bar_chart,draw_pie_chart
class Dashboard_logic(QObject):
    see_more = pyqtSignal()
    def __init__(self, dashboard_page_widget: QWidget, user_data):
        super().__init__()
        self.ui = dashboard_page_widget
        self.user_data = user_data
        self.userid = user_data["user_id"]
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        self.currentBalance = self.ui.findChild(QLineEdit, "currentBalance")
        self.totalIncome = self.ui.findChild(QLineEdit, "total_income")
        self.totalExpense = self.ui.findChild(QLineEdit, "total_expense")
        self.see_more_btn = self.ui.findChild(QPushButton,"see_more_btn")
        self.transaction_table_top5 = self.ui.findChild(QTableWidget, "transaction_table_top5")
        self.frame_bar_chart = self.ui.findChild(QFrame, "frame_bar_chart")
        self.frame_pie_chart = self.ui.findChild(QFrame, "frame_pie_chart")
        self.content = self.ui.findChild(QLabel,"content")
        self.content.hide()
        self.placeholder_label = QLabel("No Transactions in this month!", self.transaction_table_top5)
        self.placeholder_label.setStyleSheet("border-top-radius: 0px;")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: grey; font-size: 14px;")
        self.placeholder_label.setWordWrap(True)
        self.placeholder_label.hide()

        # Label thông báo không có dữ liệu cho biểu đồ cột
        self.bar_chart_placeholder = QLabel("No data available for bar chart!", self.frame_bar_chart)
        self.bar_chart_placeholder.setStyleSheet("color: grey; font-size: 14px;")
        self.bar_chart_placeholder.hide()

        # Label thông báo không có dữ liệu cho biểu đồ tròn
        self.pie_chart_placeholder = QLabel("No data available for pie chart!", self.frame_pie_chart)
        self.pie_chart_placeholder.setAlignment(Qt.AlignCenter)
        self.pie_chart_placeholder.setStyleSheet("color: grey; font-size: 14px;")
        self.pie_chart_placeholder.hide()

        layout = QVBoxLayout(self.frame_bar_chart)
        layout.addWidget(self.bar_chart_placeholder, alignment=Qt.AlignCenter)
        self.frame_bar_chart.setLayout(layout)

        layout = QVBoxLayout(self.frame_pie_chart)
        layout.addWidget(self.pie_chart_placeholder, alignment=Qt.AlignCenter)
        self.frame_pie_chart.setLayout(layout)

        self.transaction_table_top5.viewport().installEventFilter(self)
        self.see_more_btn.clicked.connect(self.see_more.emit)
        self.load_transaction(get_top_5_transaction(self.userid))
        self.update_dashboard()
        total_income = get_income_each_month(self.userid)
        total_expense = get_expense_each_month(self.userid)
        data_expense = get_data_of_expense(self.userid, self.currentMonth)
        print(f"DATA BAN ĐẦU:{data_expense} ")
        if total_expense and total_income:
            draw_bar_chart(self.frame_bar_chart, total_income, total_expense)
            self.bar_chart_placeholder.hide()
        else:
            self.bar_chart_placeholder.show()

        if data_expense:
            draw_pie_chart(self.frame_pie_chart, data_expense)
            self.pie_chart_placeholder.hide()
        else:
            self.pie_chart_placeholder.show()
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.frame_amount = self.ui.findChild(QFrame, "frame_amount")
        if self.frame_amount:
            self.frame_amount.setGraphicsEffect(self.create_configured_shadow())

        self.frame_table = self.ui.findChild(QFrame, "frame_table")
        if self.frame_table:
            self.frame_table.setGraphicsEffect(self.create_configured_shadow())

        self.frame_pie_chart = self.ui.findChild(QFrame, "frame_pie_chart")
        if self.frame_pie_chart:
            self.frame_pie_chart.setGraphicsEffect(self.create_configured_shadow())

        self.frame_notification = self.ui.findChild(QFrame, "frame_notification")
        if self.frame_notification:
            self.frame_notification.setGraphicsEffect(self.create_configured_shadow())

        if self.frame_bar_chart:
            self.frame_bar_chart.setGraphicsEffect(self.create_configured_shadow())

    def create_configured_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 150))
        return shadow

    def update_dashboard(self):
        print("Đang cập nhật dashboard...")
        current_Balance = get_balance(self.userid, self.currentMonth, self.currentYear)
        total_income = get_income(self.userid, self.currentMonth, self.currentYear)
        total_expense = get_expense(self.userid, self.currentMonth, self.currentYear)

        print("Balance:", current_Balance, "Income:", total_income, "Expense:", total_expense)

        formatted_currentBalance = "{:,.0f} đ".format(current_Balance or 0)
        formatted_income = "{:,.0f} đ".format(total_income or 0)
        formatted_expense = "{:,.0f} đ".format(total_expense or 0)

        self.currentBalance.setText(formatted_currentBalance)
        self.totalIncome.setText(formatted_income)
        self.totalExpense.setText(formatted_expense)


    def center_widget_on_parent(self, widget, parent):
        parent_geometry = parent.geometry()
        parent_center_point = parent_geometry.center()

        widget_geometry = widget.frameGeometry()

        new_x = parent_center_point.x() - widget_geometry.width() / 2
        new_y = parent_center_point.y() - widget_geometry.height() / 2

        widget.move(int(new_x), int(new_y))

    def load_transaction(self,data):
                if not data:
                    self.transaction_table_top5.setRowCount(0)
                    self.placeholder_label.show()
                    return # Dừng hàm tại đây
                else:
                    self.placeholder_label.hide()
                custom_header = ["Date", "Category", "Type", "Amount"]

                self.transaction_table_top5.setRowCount(len(data))
                self.transaction_table_top5.setColumnCount(len(custom_header))
                self.transaction_table_top5.setHorizontalHeaderLabels(custom_header)
                self.transaction_table_top5.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)

                for row_idx, row_data in enumerate(data):
                    for col_idx, value in enumerate(row_data):
                        if col_idx == 3 and isinstance(value, (int, float)):
                            formatted_value = "{:,.0f} đ".format(value)
                            item = QTableWidgetItem(formatted_value)
                        else:
                            item = QTableWidgetItem(str(value))
                        self.transaction_table_top5.setItem(row_idx, col_idx, item)
                self.transaction_table_top5.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
                self.transaction_table_top5.verticalHeader().setVisible(False)
                self.transaction_table_top5.setFocusPolicy(Qt.NoFocus)
                self.transaction_table_top5.setAlternatingRowColors(True)
                self.transaction_table_top5.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.transaction_table_top5.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.transaction_table_top5.setColumnWidth(2, 90)

    def eventFilter(self, obj, event):
            if obj is self.transaction_table_top5.viewport() and event.type() == QEvent.Resize:
                self.placeholder_label.setGeometry(self.transaction_table_top5.viewport().rect())
            elif obj == self.frame_bar_chart and event.type() == QEvent.Resize:
                self.no_data_label.setGeometry(obj.rect())
            return super().eventFilter(obj, event)

    def refresh_transaction_top5(self):
        new_data = get_top_5_transaction(self.userid)
        self.load_transaction(new_data)

    def redraw_bar_chart(self):
        total_income = get_income_each_month(self.userid)
        total_expense = get_expense_each_month(self.userid)
        data_expense = get_data_of_expense(self.userid,self.currentMonth)

        print(f"DATA SAU KHI VẼ LẠI:{data_expense} ")

        if total_income and total_expense:
            draw_bar_chart(self.frame_bar_chart, total_income, total_expense)
            self.bar_chart_placeholder.hide()
        else:
            self.bar_chart_placeholder.show()

        if data_expense:
            draw_pie_chart(self.frame_pie_chart, data_expense)
            self.pie_chart_placeholder.hide()
        else:
            self.pie_chart_placeholder.show()









