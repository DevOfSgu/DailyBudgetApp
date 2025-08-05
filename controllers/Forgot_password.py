import re
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox,QApplication
import os
from PyQt5.uic import loadUi
from Utils.otp_service import OTPService
from Utils.email_sender import send_otp_email
from models.user_model import check_email_exist
from controllers.otp_controller import OTPDialog
ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'forgot_password.ui')

class ForgotPassword(QWidget):
    def __init__(self, Show_tab):
        super(ForgotPassword, self).__init__()
        loadUi(ui_path, self)
        self.Show_tab = Show_tab
        self.otp_service = OTPService()
        print(f"[ForgotPassword] Đã tạo OTP Service với ID: {id(self.otp_service)}")
        self.frame_check.hide()
        self.continueBtn.clicked.connect(self.check_function)
        self.Email.returnPressed.connect(self.check_function)
        self.back_login.clicked.connect(self.Show_tab.show_login)
        if hasattr(self, 'Email'):
            self.Email.textChanged.connect(self.hide_error_frame)

    def hide_error_frame(self):
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()

    def show_message(self, message, is_error = True):
        if hasattr(self, 'check_email'):
                self.check_email.setText(message)
                if is_error:
                    self.check_email.setStyleSheet("color: red;")
                else:
                    self.check_email.setStyleSheet("color: green;")
                self.frame_check.show()
    def get_email(self):
        return self.Email.text().strip()
    def reset_ui(self):
        self.Email.clear()
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()
    def hideEvent(self, event):
        self.reset_ui()
        super().hideEvent(event)
    def check_function(self):
        email = self.Email.text().strip().lower()
        if not email:
            self.show_message("Please, fill in all information!")
            return
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            self.show_message("Invalid Email!")
            return
        if not check_email_exist(email):
            self.show_message("Email not found!")
            return
        print("--- Đã vượt qua tất cả validation. Chuẩn bị tạo OTP... ---")
        self.show_message("Sending OTP, please wait...",False)
        QApplication.processEvents()
        otp_code = self.otp_service.generate_and_store_otp(email, {'email': email})
        print("otp đã tạo")
        if send_otp_email(email, otp_code):
            print(f"đã gửi otp: {otp_code}")
            print(f"[ForgotPassword] Đã tạo OTP Service với ID: {id(self.otp_service)}")
            # 3. TÁI SỬ DỤNG OTPDialog
            otp_dialog = OTPDialog(email, self.otp_service, send_otp_email, parent=self)
            if otp_dialog.exec_() == QDialog.Accepted:
                QMessageBox.information(self, "Successful", "Verification successful! Get ready to reset your password.")
                self.Show_tab.show_reset(email)
            else:
                QMessageBox.warning(self,"Warning", "Email verification failed")
                self.Show_tab.show_login()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể gửi email. Vui lòng thử lại.")




