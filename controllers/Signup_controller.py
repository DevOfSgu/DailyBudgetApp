import os
import re
from PyQt5.QtWidgets import QMessageBox,QMainWindow,QDialog,QApplication
from PyQt5.uic import loadUi
from controllers.Button_controller import ButtonController
from Utils.email_sender import send_otp_email
from Utils.otp_service import OTPService
from controllers.otp_controller import OTPDialog
from models import user_model
import hashlib
ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'signup.ui')

class SignupController(QMainWindow):
    def __init__(self, Show_tab):
        super(SignupController, self).__init__()
        loadUi(ui_path, self)
        self.Show_tab = Show_tab
        self.otp_service = OTPService()
        self.signupbutton.clicked.connect(self.initiate_verification)

        self.frame_check.hide()
        self.ButtonController = ButtonController(self.password, self.toggle_password_button)
        self.ButtonController_2 = ButtonController(self.confirmpassword, self.toggle_password_button_2)
        self.username.returnPressed.connect(self.initiate_verification)
        self.email.returnPressed.connect(self.initiate_verification)
        self.password.returnPressed.connect(self.initiate_verification)
        self.confirmpassword.returnPressed.connect(self.initiate_verification)
        self.gotologinbutton.clicked.connect(self.Show_tab.show_login)
        self.CloseBtn.clicked.connect(self.Show_tab.close)
        if hasattr(self,'username'):
            self.username.textChanged.connect(self.hide_error_frame)
        if hasattr(self,'email'):
            self.email.textChanged.connect(self.hide_error_frame)
        if hasattr(self,'password'):
            self.password.textChanged.connect(self.hide_error_frame)
        if hasattr(self,'confirmpassword'):
            self.confirmpassword.textChanged.connect(self.hide_error_frame)

    def hide_error_frame(self):
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()

    def show_message(self, message, is_error = True):
        if hasattr(self, 'check_signup'):
                self.check_signup.setText(message)
                if is_error:
                    self.check_signup.setStyleSheet("color: red;")
                else:
                    self.check_signup.setStyleSheet("color: green;")
                self.frame_check.show()
    def initiate_verification(self):
        username = self.username.text().strip().lower()
        email = self.email.text().strip().lower()
        password = self.password.text()
        confirmpassword = self.confirmpassword.text()
        self.show_message("Sending OTP, please wait...",False)
        QApplication.processEvents()
        # Check null
        if not username or not email or not password or not confirmpassword:
            self.show_message("Please, fill in all information!")
            return
        # Check valid email
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            self.show_message("Invalid Email!")
            return
        # Check password
        if password != confirmpassword:
            self.show_message("Password does not match!")
            return
        # Check length of password
        if len(password)<8 or not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password):
            self.show_message("Password must be 8+ characters with upper & lower \ncase letters and numbers!")
            return
        #check user exists
        if user_model.check_user_exists(username, email):
            self.show_message("Username or email already exists")
            return
        pending_data = {
            "username": username,
            "email": email,
            "password_hash": hashlib.sha256(password.encode()).hexdigest()
        }
        otp_code = self.otp_service.generate_and_store_otp(email, pending_data)
        # Gửi email
        email_sent_successfully = send_otp_email(email, otp_code)
        if email_sent_successfully:
            # Mở dialog nhập OTP
            otp_dialog = OTPDialog(email,self.otp_service, send_otp_email,parent=self)
            otp_dialog.resend_otp_requested.connect(self.initiate_verification)
            result = otp_dialog.exec_()
            if result == QDialog.Accepted:
                # Nếu người dùng nhấn "Verify"
                entered_otp = otp_dialog.get_entered_otp()
                print(f"[DEBUG] OTP người dùng nhập: {entered_otp}")
                print(f"[DEBUG] email người dùng nhập: {email}")
                self.complete_registration(entered_otp, email)
            else:
                QMessageBox.warning(self,"Warning", "Email verification failed")
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể gửi email xác thực. Vui lòng thử lại.")
    def complete_registration(self, entered_otp, email):
            is_valid, message, user_data = self.otp_service.verify_otp(email, entered_otp)
            print(f"[DEBUG]{is_valid} - {message} - {user_data}")
            if is_valid:
                if user_model.create_user(user_data):
                    QMessageBox.information(self, "Successful", "Account created successfully!")
                    self.Show_tab.show_login()
                else:
                    QMessageBox.critical(self, "Lỗi Database", "Không thể tạo tài khoản.")
            else:
                QMessageBox.warning(self, "Authentication failed", message)