import unittest
from refactored_processor import OrderProcessorRefactored

class DummyDBGateway:
    def save_order(self, total):
        self.saved_total = total

class DummyEmailService:
    def send_confirmation(self, email, total):
        pass

class TestFailureInjection(unittest.TestCase):
    def make_processor(self):
        return OrderProcessorRefactored(DummyDBGateway(), DummyEmailService())

    def test_valid_baseline(self):
        p = self.make_processor()
        self.assertTrue(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":1}]}'))

    def test_missing_email_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"items":[{"price":10,"qty":1}]}'))

    def test_negative_price_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":-10,"qty":1}]}'))

    def test_zero_qty_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":0}]}'))

    def test_extreme_qty_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":1000000000}]}'))

    def test_items_type_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":"oops"}'))

if __name__ == '__main__':
    unittest.main()
