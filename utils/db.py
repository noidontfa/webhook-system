from collections import namedtuple

import psycopg2
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
import config


def namedtuplefetchall(cursor):
    desc = cursor.description
    if not desc:
        return
    nt_result = namedtuple('Result', [col[0] for col in desc], rename=True)
    return [nt_result(*row) for row in cursor.fetchall()]


class Database:
    def __init__(self):
        self.config = dict(
            host=config.DATABASE_HOST,
            database=config.DATABASE_NAME,
            user=config.DATABASE_USERNAME,
            password=config.DATABASE_PASSWORD
        )
        register_adapter(dict, Json)

    def get_conn(self):
        return psycopg2.connect(**self.config)

    def query(self, q, params=[]):
        _conn = self.get_conn()
        cursor = _conn.cursor()
        cursor.execute(q, params)
        results = namedtuplefetchall(cursor)
        _conn.commit()
        _conn.close()
        return results
