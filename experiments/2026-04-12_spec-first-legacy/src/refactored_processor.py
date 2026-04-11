import json

class OrderValidator:
    def validate(self, order):
        if 'items' not in order or len(order['items']) == 0:
            raise ValueError("No items in order")
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
