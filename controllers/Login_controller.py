import os
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from controllers.Mainscreen_controllers import Main_screen
from models import user_model
from controllers.Button_controller import ButtonController
import hashlib

ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'login.ui')

class LoginController(QMainWindow):
    def __init__(self, Show_tab):
        super(LoginController, self).__init__()
        loadUi(ui_path, self)
        self.Show_tab = Show_tab
        self.frame_check.hide()
        self.currentMonth = datetime.now().month
        self.currentYear = datetime.now().year
        self.ButtonController = ButtonController(self.password, self.toggle_password_button)
        self.loginbutton.clicked.connect(self.login_function)
        # Kết nối sự kiện nhấn Enter cho ô username
        self.username.returnPressed.connect(self.login_function)
        # Kết nối sự kiện nhấn Enter cho ô password
        self.password.returnPressed.connect(self.login_function)
        self.gotosignupbutton.clicked.connect(self.Show_tab.show_signup)
        self.forgotBtn.clicked.connect(self.Show_tab.show_forgot)
        self.CloseBtn.clicked.connect(self.Show_tab.close)
        if hasattr(self,'username'):
            self.username.textChanged.connect(self.hide_error_frame)
        if hasattr(self,'password'):
            self.password.textChanged.connect(self.hide_error_frame)

    def hide_error_frame(self):
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()

    def show_message(self, message, is_error = True):
        if hasattr(self, 'check_login'):
                self.check_login.setText(message)
                if is_error:
                    self.check_login.setStyleSheet("color: red;")
                else:
                    self.check_login.setStyleSheet("color: green;")
                self.frame_check.show()


    def login_function(self):
        username = self.username.text().strip().lower()
        password = self.password.text()
        #Check null
        if not username or not password:
            self.show_message("Please, fill in all information!")
            return
        user_data = user_model.get_user_by_username(username)
        if user_data:
            stored_password_hash = user_data['password_hash']
            input_password_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_password_hash == stored_password_hash:
                    self.main_window = Main_screen(user_data)
                    self.main_window.logout_requested.connect(self.handle_logout)
                    self.main_window.show()
                    self.Show_tab.close()
            else:
                self.show_message("Username or password not correct!")

            # self.main_window.logout_requested.connect(self.show)
        else:
            self.show_message("Username or password not correct!")

    def handle_logout(self):
        print("[DEBUG] LoginController: Received logout signal.")
        print("[DEBUG] LoginController: Showing login window...")
        self.Show_tab.show()
        self.username.clear()
        self.password.clear()
        print("[DEBUG] LoginController: Closing main window...")
        self.main_window.close()
        print("[DEBUG] LoginController: handle_logout finished.")



