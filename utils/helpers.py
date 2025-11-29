from datetime import datetime

class Helpers:
    @staticmethod
    def format_currency(amount):
        return f"₹ {amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj):
        if isinstance(date_obj, str):
            return date_obj
        return date_obj.strftime('%d-%m-%Y')
    
    @staticmethod
    def format_weight(weight):
        return f"{weight:.3f} gm"
    
    @staticmethod
    def generate_bill_number():
        return f"BL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    @staticmethod
    def calculate_profit(selling_price, cost_price):
        return selling_price - cost_price
    
    @staticmethod
    def calculate_profit_percentage(profit, cost_price):
        return (profit / cost_price * 100) if cost_price != 0 else 0