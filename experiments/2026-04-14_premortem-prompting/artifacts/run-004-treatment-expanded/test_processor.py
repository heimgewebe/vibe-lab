import unittest
from refactored_processor import OrderProcessorRefactored

class DummyDBGateway:
    def __init__(self, should_fail=False):
        self.saved_total = 0
        self.should_fail = should_fail
    def save_order(self, total):
        if self.should_fail:
            raise RuntimeError("db down")
        self.saved_total = total

class DummyEmailService:
    def __init__(self, should_fail=False):
        self.sent_to = None
        self.sent_total = 0
        self.should_fail = should_fail
    def send_confirmation(self, email, total):
        if self.should_fail:
            raise RuntimeError("smtp down")
        self.sent_to = email
        self.sent_total = total

class TestExpandedControl(unittest.TestCase):
    def make_processor(self, db_fail=False, email_fail=False):
        return OrderProcessorRefactored(DummyDBGateway(db_fail), DummyEmailService(email_fail))

    def test_success(self):
        p = self.make_processor()
        self.assertTrue(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":2}]}'))

    def test_invalid_json_returns_false(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":'))

    def test_missing_items_returns_false(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c"}'))

    def test_missing_email_returns_false(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"items":[{"price":10,"qty":1}]}'))

    def test_empty_items_returns_false(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[]}'))

    def test_missing_qty_returns_false(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":10}]}'))

    def test_string_price_should_fail_validation(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":"10","qty":2}]}'))

    def test_db_failure_returns_false(self):
        p = self.make_processor(db_fail=True)
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":1}]}'))

    def test_email_failure_is_swallowed_and_true(self):
        p = self.make_processor(email_fail=True)
        self.assertTrue(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":1}]}'))

if __name__ == '__main__':
    unittest.main()
