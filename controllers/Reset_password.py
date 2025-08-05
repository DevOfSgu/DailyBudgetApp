import hashlib

from PyQt5.QtWidgets import QWidget, QMessageBox
import os
import re
from models import user_model
from PyQt5.uic import loadUi
from controllers.Button_controller import ButtonController
from models.user_model import get_user_by_email
ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'reset_password.ui')

class ResetPassword(QWidget):
    def __init__(self,Show_tab):
        super(ResetPassword, self).__init__()
        loadUi(ui_path, self)
        self.Show_tab = Show_tab
        self.target_email = None
        if hasattr(self,'frame_check'):
            self.frame_check.hide()
        self.resetBtn.clicked.connect(self.check_valid)
        self.newpassword.returnPressed.connect(self.check_valid)
        self.cf_newpassword.returnPressed.connect(self.check_valid)
        self.back_login.clicked.connect(self.reset_fail)
        self.ButtonController = ButtonController(self.newpassword, self.toggle_password_button)
        self.ButtonController_2 = ButtonController(self.cf_newpassword, self.toggle_password_button_2)
        self.model = user_model
        if hasattr(self,'newpassword'):
            self.newpassword.textChanged.connect(self.hide_error_frame)
        if hasattr(self,'cf_newpassword'):
            self.cf_newpassword.textChanged.connect(self.hide_error_frame)

    def hide_error_frame(self):
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()

    def reset_fail(self):
        self.newpassword.clear()
        self.cf_newpassword.clear()
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()
        QMessageBox.warning(self,"Fail","Update failed.")
        self.Show_tab.show_login()
    def set_target_email(self,email):
        self.target_email = email
        self.userdata = self.model.get_user_by_email(self.target_email)
    def show_message(self, message):
            if hasattr(self, 'check_password'):
                self.check_password.setText(message)
                self.check_password.setStyleSheet("color: red;")
                self.frame_check.show()

    def check_valid(self):
        new_password = self.newpassword.text()
        cf_new_password = self.cf_newpassword.text()
        old_password_hash = self.userdata['password_hash']
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        #check null
        if not new_password or not cf_new_password:
            self.show_message("Please fill in all information!")
            return
        # Check length of password
        if len(new_password)<8 or not re.search(r"[a-z]", new_password) or not re.search(r"[A-Z]", new_password) or not re.search(r"[0-9]", new_password):
            self.show_message("Password must be 8+ characters with upper & lower \ncase letters and numbers!")
            return
        # Check password
        if new_password != cf_new_password:
            self.show_message("Password does not match!")
            return
        if new_password_hash == old_password_hash:
            self.show_message("New password cannot be the same as the old one!")
            return
        if self.target_email:
                success = user_model.update_password_by_email(self.target_email, new_password)
                if success:
                    QMessageBox.information(self, "Successful", "Password updated successfully. please login again!")
                    self.Show_tab.show_login() # Điều hướng về trang đăng nhập
                else:
                    QMessageBox.critical(self, "Error", "Cannot update password!")










