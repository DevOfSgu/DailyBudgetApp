import random
import time

class OTPService:
    def __init__(self, expiry_time_seconds=60):
        self.pending_otps = {}
        self.EXPIRY_TIME_SECONDS = expiry_time_seconds

    def generate_and_store_otp(self, identifier, user_data):
        code = str(random.randint(100000, 999999))
        self.pending_otps[identifier] = {
            'code': code,
            'timestamp': time.time(),
            'data': user_data
        }
        # Debug log
        print(f"[OTPService] Generated OTP for {identifier}: {code}")
        print(f"[OTPService] Current pending_otps: {list(self.pending_otps.keys())}")
        return code

    def verify_otp(self, identifier, user_otp):
        if identifier not in self.pending_otps:
            return False, "OTP request not found or expired.", None

        otp_info = self.pending_otps[identifier]

        if time.time() - otp_info['timestamp'] > self.EXPIRY_TIME_SECONDS:
            del self.pending_otps[identifier]
            return False, "OTP has expired.", None

        if user_otp == otp_info['code']:
            user_data = otp_info['data']
            del self.pending_otps[identifier]
            return True, "Verification successful!", user_data
        else:
            return False, "Invalid OTP.", None