import os
from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.uic import loadUi
from controllers.Transaction import Transaction_logic
from controllers.Dashboard import Dashboard_logic
from controllers.Budget import Budget_logic
ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'Mainscreen.ui')
class Main_screen(QMainWindow):
    logout_requested = pyqtSignal()
    def __init__(self, userdata):
        super(Main_screen, self).__init__()
        loadUi(ui_path, self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.drag_position = QPoint()
        self.user_data = userdata
        self.CloseBtn.clicked.connect(self.close)
        self.username.setText(self.user_data['username'].upper())
        self.hide_button.clicked.connect(self.showMinimized)
        self.logout_btn.clicked.connect(self.logout_function)
        self.dashboard_button.clicked.connect(self.on_dashboard_button_clicked)
        self.transaction_button.clicked.connect(self.on_transaction_button_clicked)
        self.budget_btn.clicked.connect(self.on_budget_button_clicked)
        self.pages_stack.setCurrentWidget(self.dashboard_page)

        dashboard_widget = self.pages_stack.findChild(QWidget, "dashboard_page")
        transaction_widget = self.pages_stack.findChild(QWidget,"transaction_page")
        budget_widget = self.pages_stack.findChild(QWidget,"Budget_page")


        self.transaction_logic_handler = Transaction_logic(transaction_widget,self.user_data,self)
        self.dashboard_logic_handler = Dashboard_logic(dashboard_widget,self.user_data)
        self.budget_logic_handler = Budget_logic(budget_widget,self.user_data,self)

        self.transaction_logic_handler.transaction_updated.connect(self.dashboard_logic_handler.update_dashboard)
        self.transaction_logic_handler.transaction_updated.connect(self.dashboard_logic_handler.refresh_transaction_top5)
        self.transaction_logic_handler.transaction_updated.connect(self.dashboard_logic_handler.redraw_bar_chart)
        self.dashboard_logic_handler.see_more.connect(self.on_transaction_button_clicked)
        self.transaction_logic_handler.transaction_updated.connect(self.budget_logic_handler.refresh)
        self.on_dashboard_button_clicked()

    def on_dashboard_button_clicked(self):
        button_style = """
            QPushButton {
                background-color: rgb(72, 145, 222);
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgb(11, 93, 181);
            }
            QPushButton:selected {
                background-color: rgb(11, 93, 181);
            }
            """
        self.transaction_logic_handler.transactionTable.clearSelection()
        self.pages_stack.setCurrentWidget(self.dashboard_page)
        self.dashboard_button.setStyleSheet("background-color: rgb(11, 93, 181); color: white;")
        self.transaction_button.setStyleSheet(button_style)
        self.budget_btn.setStyleSheet(button_style)

    def on_transaction_button_clicked(self):
        button_style = """
            QPushButton {
                background-color: rgb(72, 145, 222);
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgb(11, 93, 181);
            }
            QPushButton:selected {
                background-color: rgb(11, 93, 181);
            }
            """
        self.pages_stack.setCurrentWidget(self.transaction_page)
        self.transaction_button.setStyleSheet("background-color: rgb(11, 93, 181); color: white;")
        self.dashboard_button.setStyleSheet(button_style)
        self.budget_btn.setStyleSheet(button_style)

    def on_budget_button_clicked(self):
        button_style = """
            QPushButton {
                background-color: rgb(72, 145, 222);
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgb(11, 93, 181);
            }
            QPushButton:selected {
                background-color: rgb(11, 93, 181);
            }
            """
        self.pages_stack.setCurrentWidget(self.Budget_page)
        self.budget_btn.setStyleSheet("background-color: rgb(11, 93, 181); color: white;")
        self.dashboard_button.setStyleSheet(button_style)
        self.transaction_button.setStyleSheet(button_style)

    def logout_function(self):
        self.logout_requested.emit()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()
