import json
import sqlite3
import smtplib

class OrderProcessor:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)

    def process_order(self, order_json):
        try:
            order = json.loads(order_json)
            # validation
            if 'items' not in order or len(order['items']) == 0:
                print("No items")
                return False

            total = 0
            for item in order['items']:
                total += item['price'] * item['qty']

            # save to db
            cur = self.db.cursor()
            cur.execute("INSERT INTO orders (total) VALUES (?)", (total,))
            self.db.commit()

            # send email
            try:
                server = smtplib.SMTP('localhost')
                server.sendmail('sales@example.com', order['email'], f"Order total: {total}")
            except:
                print("Email failed")

            return True
        except Exception as e:
            print(e)
            return False
