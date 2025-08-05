from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtCore import Qt, QPoint
from Resource import resource
from controllers.Login_controller import LoginController
from controllers.Signup_controller import SignupController
from controllers.Forgot_password import ForgotPassword
from controllers.Reset_password import ResetPassword
class ShowTab(QStackedWidget):
    def __init__(self):
        super(ShowTab,self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(1305, 829)

        self.drag_position = QPoint()

        self.login_screen = LoginController(self)
        self.addWidget(self.login_screen)
        self.setCurrentWidget(self.login_screen)

        self.center_on_screen()

    def center_on_screen(self):
        screen_geometry = QApplication.screenAt(self.pos()).geometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center() - window_geometry.center()
        self.move(center_point)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def show_signup(self):
        self.signup_screen = SignupController(self)
        self.addWidget(self.signup_screen)
        self.setCurrentWidget(self.signup_screen)

    def show_login(self):
        self.setCurrentWidget(self.login_screen)

    def show_forgot(self):
        self.Forgot_screen = ForgotPassword(self)
        self.addWidget(self.Forgot_screen)
        self.setCurrentWidget(self.Forgot_screen)

    def show_reset(self,email):
        self.reset_screen = ResetPassword(self)
        self.addWidget(self.reset_screen)
        self.reset_screen.set_target_email(email)
        self.setCurrentWidget(self.reset_screen)

