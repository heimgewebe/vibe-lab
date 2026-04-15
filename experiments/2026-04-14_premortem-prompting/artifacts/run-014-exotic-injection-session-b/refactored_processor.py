import json

class OrderValidator:
    def validate(self, order):
        if 'email' not in order or not isinstance(order['email'], str) or '@' not in order['email']:
            raise ValueError("email missing/invalid")
        if 'items' not in order or not isinstance(order['items'], list) or len(order['items']) == 0:
            raise ValueError("No items in order")
        for item in order['items']:
            if not isinstance(item, dict):
                raise ValueError("item must be object")
            if 'price' not in item or 'qty' not in item:
                raise ValueError("Missing price/qty")
            if not isinstance(item['price'], (int, float)):
                raise ValueError("price must be numeric")
            if item['price'] <= 0:
                raise ValueError("price must be > 0")
            if not isinstance(item['qty'], int):
                raise ValueError("qty must be int")
            if item['qty'] <= 0:
                raise ValueError("qty must be > 0")
            if item['qty'] > 1_000_000:
                raise ValueError("qty too large")
        return True

class OrderCalculator:
    def calculate_total(self, order):
        return sum(item['price'] * item['qty'] for item in order['items'])

class OrderProcessorRefactored:
    def __init__(self, db_gateway, email_service):
        self.db = db_gateway
        self.email = email_service
        self.validator = OrderValidator()
        self.calculator = OrderCalculator()

    def process_order(self, order_json):
        try:
            order = json.loads(order_json)
            self.validator.validate(order)
            total = self.calculator.calculate_total(order)
            self.db.save_order(total)
            try:
                self.email.send_confirmation(order.get('email'), total)
            except Exception as email_err:
                print(f"Email Error (swallowed to match legacy behavior): {email_err}")
            return True
        except json.JSONDecodeError as jde:
            print(f"Parsing Error: {jde}")
            return False
        except ValueError as ve:
            print(f"Validation Error: {ve}")
            return False
        except Exception as e:
            print(f"Processing Error: {e}")
            return False
