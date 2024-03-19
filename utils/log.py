import time

from utils.db import Database


def write_log(data):
    # print(data)
    event_id = data.get('event_id')
    status = data.get('status')
    payload = data.get('payload')
    error = data.get('error')
    created = time.time()
    updated = time.time()

    db = Database()
    db.query("""
        INSERT INTO event_log (event_id, status, payload, error, created, updated)
        VALUES (%s, %s, %s, %s, %s, %s);
    """, [event_id, status, payload, error, created, updated])
