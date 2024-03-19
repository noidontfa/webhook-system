from flask import Flask
from flask import request, jsonify

from app_server.contrains.exception import InvalidAPIUsage
from app_server.services.webhook_event import WebhookEventService

app = Flask(__name__)


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    return jsonify(e.to_dict()), e.status_code


@app.get('/')
def index():
    return "me run"


@app.post('/ws/v1/webhook')
def subscribe_webhook_event():
    we = WebhookEventService()
    d = we.subscribe(request.json)
    return jsonify(status=200, data=d)


@app.get('/ws/v1/webhook/<int:webhook_id>')
def verify_webhook_event(webhook_id):
    we = WebhookEventService()
    we.verify(dict(webhook_id=webhook_id))
    return jsonify(status=200, data={"message": "ok"})


@app.post('/ws/v1/event')
def trigger_webhook_event():
    we = WebhookEventService()
    d = we.trigger(request.json)
    return jsonify(status=200, data=d)



