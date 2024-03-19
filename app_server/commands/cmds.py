import time

from flask.cli import AppGroup
from flask import Flask
from utils.db import Database

app = Flask(__name__)

foundation_cli = AppGroup('foundation')

@foundation_cli.command('init_database')
def init_database():
    db = Database()
    with db.get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE webhook_event_type (
                    id              SERIAL,
                    event_type      char(10) PRIMARY KEY,
                    description     char(500),
                    schemas         json,
                    is_deleted      boolean,
                    created         integer,
                    updated         integer
                );
                CREATE TABLE webhook (
                    id              SERIAL PRIMARY KEY,
                    url             char(256),
                    event_type      char(10),
                    headers         json,
                    secret_key      char(50),
                    user_id         integer,
                    is_active       boolean,
                    created         integer,
                    updated         integer,
                    CONSTRAINT fk_event_type
                        FOREIGN KEY(event_type)
                        REFERENCES webhook_event_type(event_type)
                );
                CREATE TABLE event(
                    id              SERIAL PRIMARY KEY,
                    webhook_id      integer,
                    task_id         char(37),
                    event_type      char(10),
                    user_id         integer,
                    execution_date  integer,
                    metadata        json,
                    status          char(10),
                    created         integer,
                    updated         integer,
                    CONSTRAINT fk_webhook
                        FOREIGN KEY(webhook_id)
                        REFERENCES webhook(id)
                );
                CREATE TABLE event_log (
                    id              SERIAL PRIMARY KEY,
                    event_id        integer,
                    status          char(10),
                    payload         json,
                    error           json,
                    created         integer,
                    updated         integer,
                    CONSTRAINT fk_event
                        FOREIGN KEY(event_id)
                        REFERENCES event(id)
                );
            """)


@foundation_cli.command('seed_event_type')
def seed_event_type():
    data = [
        {
            "event_type": "EV_ONE",
            "description": "EVENT_ONE",
            "schemas": {
                "hello": "world"
            },
            "is_deleted": False,
            "created": time.time(),
            "updated": time.time()
        },
        {
            "event_type": "EV_TWO",
            "description": "EVENT_TWO",
            "schemas": {
                "hello": "world"
            },
            "is_deleted": False,
            "created": time.time(),
            "updated": time.time()
        },
        {
            "event_type": "EV_THREE",
            "description": "EVENT_THREE",
            "schemas": {
                "hello": "world"
            },
            "is_deleted": False,
            "created": time.time(),
            "updated": time.time()
        },
        {
            "event_type": "EV_FOUR",
            "description": "EVENT_FOUR",
            "schemas": {
                "hello": "world"
            },
            "is_deleted": False,
            "created": time.time(),
            "updated": time.time()
        },
        {
            "event_type": "EV_FIVE",
            "description": "EVENT_FIVE",
            "schemas": {
                "hello": "world"
            },
            "is_deleted": False,
            "created": time.time(),
            "updated": time.time()
        }
    ]
    db = Database()
    with db.get_conn() as conn:
        with conn.cursor() as cursor:
            for d in data:
                cursor.execute("""
                INSERT INTO webhook_event_type(event_type, description, schemas, is_deleted, created, updated)
                VALUES (
                    %(event_type)s,
                    %(description)s,
                    %(schemas)s,
                    %(is_deleted)s,
                    %(created)s,
                    %(updated)s
                );
                """, d)


app.cli.add_command(init_database)
app.cli.add_command(seed_event_type)
