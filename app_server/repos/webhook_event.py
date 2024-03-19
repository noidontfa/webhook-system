from utils.db import Database


class WebhookEventRepository:

    def __init__(self):
        self.db = Database()

    def get_one_webhook_event(self, event_type: str):
        res = self.db.query("""
            SELECT * FROM webhook_event_type
            WHERE event_type = %s
        """, [event_type])
        return res[0] if len(res) else None

    def get_one_subscribed_webhook(self, event_type, user_id):
        res = self.db.query("""
            SELECT * FROM webhook
            WHERE event_type = %s AND user_id = %s
        """, [event_type, user_id])
        return res[0] if len(res) else None

    def get_one_webhook(self, webhook_id):
        res = self.db.query("""
            SELECT * FROM webhook
            WHERE id = %s
        """, [webhook_id])
        return res[0] if len(res) else None

    def save_webhook(self, data):
        res = self.db.query("""
            INSERT INTO webhook (url, event_type, headers, secret_key, user_id, is_active, created, updated)
            VALUES (%(url)s, %(event_type)s, %(headers)s, %(secret_key)s, %(user_id)s, %(is_active)s, %(created)s, %(updated)s) 
            RETURNING id
        """, data)
        return res[0] if len(res) else None

    def active_webhook(self, data):
        self.db.query("""
            UPDATE webhook
            SET is_active = true, updated = %(updated)s
            WHERE id = %(webhook_id)s
        """, data)

    def save_event(self, data):
        res = self.db.query("""
            INSERT INTO event (webhook_id, event_type, user_id, execution_date, metadata, status, created, updated)
            VALUES (%(webhook_id)s, %(event_type)s, %(user_id)s, %(execution_date)s, %(metadata)s, %(status)s ,%(created)s, %(updated)s)
            RETURNING id
        """, data)
        return res[0] if len(res) else None
