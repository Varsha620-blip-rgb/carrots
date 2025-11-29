import re
from datetime import datetime

class Validators:
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        pattern = r'^[0-9]{10}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_gst(gst):
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        return re.match(pattern, gst) is not None
    
    @staticmethod
    def validate_date(date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except:
            return False
    
    @staticmethod
    def validate_number(num_str):
        try:
            float(num_str)
            return True
        except:
            return False
    
    @staticmethod
    def validate_integer(num_str):
        try:
            int(num_str)
            return True
        except:
            return False