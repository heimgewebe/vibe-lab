import unittest
from refactored_processor import OrderProcessorRefactored

class DummyDBGateway:
    def save_order(self, total):
        self.saved_total = total

class DummyEmailService:
    def send_confirmation(self, email, total):
        pass

class TestExoticInjectionV2(unittest.TestCase):
    def make_processor(self):
        return OrderProcessorRefactored(DummyDBGateway(), DummyEmailService())

    def test_qty_over_upper_bound(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":1000001}]}'))

    def test_items_null_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":null}'))

    def test_price_string_scientific_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":"1e3","qty":1}]}'))

    def test_micro_price_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":0.0000000001,"qty":1}]}'))

    def test_zero_price_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":0,"qty":1}]}'))

    def test_top_level_null_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('null'))

    def test_top_level_list_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('[]'))

    def test_top_level_string_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('"oops"'))

    def test_price_bool_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":true,"qty":1}]}'))

    def test_qty_bool_rejected(self):
        p = self.make_processor()
        self.assertFalse(p.process_order('{"email":"a@b.c","items":[{"price":1,"qty":true}]}'))

    def test_baseline_valid(self):
        p = self.make_processor()
        self.assertTrue(p.process_order('{"email":"a@b.c","items":[{"price":10,"qty":1}]}'))

if __name__ == '__main__':
    unittest.main()
