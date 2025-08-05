import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal,QThread
from PyQt5.uic import loadUi
from Utils.worker import EmailWorker

ui_path = os.path.join(os.path.dirname(__file__), '..', 'UI', 'OTP.ui')

class OTPDialog(QDialog):
    resend_otp_requested = pyqtSignal()
    def __init__(self, email, otp_service, send_otp_function, parent=None):
        super(OTPDialog, self).__init__(parent)
        loadUi(ui_path, self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.email = email
        self.otp_service = otp_service
        print(f"[OTP] Đã tạo OTP Service với ID: {id(self.otp_service)}")
        self.send_otp_function = send_otp_function
        self.frame_resend.hide()
        # Biến để giữ thread không bị xóa
        self.resend_thread = None
        self.resend_worker = None
        self.countdown_seconds = 60
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

        self.drag_position = QPoint()
        self.otp_instruction_label.setText(f"A 6-digit code has been sent to: {email}")
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()
        # Kết nối các nút bấm với slot có sẵn của QDialog
        self.verify_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        self.resend_button.clicked.connect(self.handle_resend_request)
        self.otp_input.returnPressed.connect(self.validate_and_accept)


        self.start_countdown()

    def hide_error_frame(self):
        if hasattr(self, 'frame_check'):
            self.frame_check.hide()

    def start_countdown(self):
        self.countdown_seconds = 60
        self.resend_button.setDisabled(True)
        self.update_countdown()
        self.countdown_timer.start(1000)

    def update_countdown(self):
        if self.countdown_seconds > 0:
            self.countdown_label.setText(f"OTP code will expire after:{self.countdown_seconds}s")
            self.countdown_seconds -= 1
        else:
            self.countdown_timer.stop()
            self.countdown_label.setText("Didn't receive the code?")
            self.frame_resend.show()
            self.resend_button.setDisabled(False) # Kích hoạt lại nút Gửi lại

    def handle_resend_request(self):
        self.resend_button.setDisabled(True)
        self.verify_button.setDisabled(True)
        new_otp_code = self.otp_service.generate_and_store_otp(self.email, {'email': self.email})
        # Bắt đầu gửi email trong một thread riêng
        self.resend_thread = QThread()
        self.resend_worker = EmailWorker(self.email, new_otp_code)
        self.resend_worker.moveToThread(self.resend_thread)

        self.resend_thread.started.connect(self.resend_worker.run)
        self.resend_worker.finished.connect(self.on_resend_finished) # Kết nối với hàm xử lý kết quả

        # Dọn dẹp
        self.resend_worker.finished.connect(self.resend_thread.quit)
        self.resend_worker.finished.connect(self.resend_worker.deleteLater)
        self.resend_thread.finished.connect(self.resend_thread.deleteLater)

        self.resend_thread.start()

    def on_resend_finished(self, success):
        """Hàm này được gọi khi thread gửi email hoàn thành."""
        if success:
            print("A new OTP has been sent to your email.")
            self.start_countdown()
        else:
            print("Error", "Failed to send new OTP. Please try again.")
            # Kích hoạt lại nút gửi lại nếu thất bại
            self.resend_button.setDisabled(False)
            self.verify_button.setDisabled(False) # Kích hoạt lại nút verify
            self.countdown_label.setText("Please try to resend the code.")

    def get_entered_otp(self):
        return self.otp_input.text().strip()
    def show_otp_message(self, message):
        """Hiển thị thông báo lỗi trên frame_check của dialog này."""
        if hasattr(self, 'check_otp') and hasattr(self, 'frame_check'):
            self.check_otp.setText(message)
            self.check_otp.setStyleSheet("color: red;")
            self.frame_check.show()
    def validate_and_accept(self):
        entered_otp = self.get_entered_otp()
        if not entered_otp:
            self.show_otp_message("Please enter the OTP code.")
            return

        if not entered_otp.isdigit() or len(entered_otp) != 6:
            self.show_otp_message("OTP must be a 6-digit number.")
            return
        self.accept()


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()