import unittest
from refactored_processor import OrderValidator, OrderCalculator, OrderProcessorRefactored

class DummyDBGateway:
    def __init__(self):
        self.saved_total = 0
    def save_order(self, total):
        self.saved_total = total

class DummyEmailService:
    def __init__(self):
        self.sent_to = None
        self.sent_total = 0
    def send_confirmation(self, email, total):
        self.sent_to = email
        self.sent_total = total

class TestRefactoredProcessor(unittest.TestCase):
    def test_validation_fails(self):
        validator = OrderValidator()
        with self.assertRaises(ValueError):
            validator.validate({"items": []})

    def test_calculator(self):
        calculator = OrderCalculator()
        order = {"items": [{"price": 10, "qty": 2}, {"price": 5, "qty": 1}]}
        total = calculator.calculate_total(order)
        self.assertEqual(total, 25)

    def test_processor_success(self):
        db = DummyDBGateway()
        email = DummyEmailService()
        processor = OrderProcessorRefactored(db, email)
        order_json = '{"email": "test@example.com", "items": [{"price": 10, "qty": 2}]}'
        result = processor.process_order(order_json)
        self.assertTrue(result)
        self.assertEqual(db.saved_total, 20)
        self.assertEqual(email.sent_to, "test@example.com")
        self.assertEqual(email.sent_total, 20)

    def test_processor_failure(self):
        db = DummyDBGateway()
        email = DummyEmailService()
        processor = OrderProcessorRefactored(db, email)
        order_json = '{"email": "test@example.com", "items": []}'
        result = processor.process_order(order_json)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
