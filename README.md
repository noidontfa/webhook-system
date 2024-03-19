# Webhook System
Maintenance: Thinh Ngo <thinhngo1198@gmail.com>
## Documentation: [Link](documentation.pdf)
## Specifications & requirements
1. Framework/libraries: Flask, Celery, RabbitMQ, Redis, Docker, Docker Compose.
2. Database: PostgreSQL.
3. Logger: Grafana.
4. Tools: ngrok (https tunnel), apache benchmark (for performance testing), Postman (API Testing), flower (monitoring celery task)


## Project structure
```
├── Dockerfile
├── README.md
├── app_server
├── config.py
├── docker-compose-prod.yml
├── docker-compose.yml
├── requirements.txt
├── message_queue
├── webhook_handler.py
│   ├── __init__.py
│   ├── commands
│   │   ├── __init__.py
│   │   └── cmds.py
│   ├── contrains
│   │   ├── enums.py
│   │   └── exception.py
│   ├── controllers
│   │   ├── __init__.py
│   │   └── api.py
│   ├── repos
│   │   ├── __init__.py
│   │   └── webhook_event.py
│   └── services
│       ├── __init__.py
│       └── webhook_event.py
│   ├── __init__.py
│   ├── consumer.py
│   └── services
│       ├── __init__.py
│       ├── __pycache__
│       └── webhook_handler.py
├── tasks
│   ├── __init__.py
│   ├── app.py
│   └── services
│       ├── __init__.py
│       ├── consuming_scaler.py
│       └── scheduled_webhook_event.py
├── utils
│   ├── __init__.py
│   ├── db.py
│   ├── execution_calculator.py
│   ├── hmacsha1.py
│   ├── log.py
│   ├── queue.py
│   └── task.py
```

## Development Setup
1. Virtual environment: ```python3 -m venv venv | ./venv/bin/active | pip install -r requirements.txt```
2. Command: ```flask --app app_server.commands.cmds init_database | flask --app app_server.commands.cmds seed_event_type```
3. Run Flask app: ```flask --app app_server.controllers.api run --debug```
4. Run Celery worker: ```celery -A tasks.app worker --loglevel=INFO --concurrency=2 -B```
5. Run Consumer: ```python3 webhook_handler.py```
6. Development Tools: ```docker compose up -d```

## Production Setup
```
PROXY PORT: 8000
env: .env.prod
docker compose -f docker-compose-prod.yml up -d
docker compose -f docker-compose-prod.yml exec postgres createdb -U admin webhook_system2
docker compose -f docker-compose-prod.yml exec app_server flask --app app_server.commands.cmds init_database
docker compose -f docker-compose-prod.yml exec app_server flask --app app_server.commands.cmds seed_event_type
```
## API Usage

### Set up ngrok
```
https://ngrok.com/download
or: docker run -it -e NGROK_AUTHTOKEN=<token> ngrok/ngrok http 80
```
### Code Sample for testing: [Source here](https://github.com/noidontfa/webhook-system-testing)
main.py
```
import hashlib
import hmac


from flask import Flask, request, jsonify

app = Flask(__name__)

_secret_key = "thisissecretkey"


def generate_hmac(secret_key, token):
    hmac_digest = hmac.new(key=secret_key.strip().encode('utf-8'),
                           msg=token.strip().encode('utf-8'),
                           digestmod=hashlib.sha256).hexdigest()
    return hmac_digest


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.post("/webhook/post/verify_success")
def verify_success():
    data = request.json
    _key = data.get('key')
    hmac = generate_hmac(_secret_key, _key)
    print(hmac)
    return jsonify({
        "hmac": hmac
    }), 200


@app.post("/webhook/post/verify_failed")
def verify_failed():
    return jsonify({
        "msg": "me failed"
    }), 400


@app.post("/webhook/post/delivery_success")
def delivery_success():
    data = request.json
    # verify case
    _key = data.get('key')
    if _key:
        hmac = generate_hmac(_secret_key, _key)
        print(hmac)
        return jsonify({
            "hmac": hmac
        }), 200

    # delivery case
    print("received data ", data)
    return jsonify({
        "msg": "ok"
    }), 200


@app.post("/webhook/post/delivery_failed")
def delivery_failed():
    data = request.json
    # verify case
    _key = data.get('key')
    if _key:
        hmac = generate_hmac(_secret_key, _key)
        print(hmac)
        return jsonify({
            "hmac": hmac
        }), 200

    # delivery case
    print("received data ", data)
    return jsonify({
        "msg": "failed"
    }), 400


if __name__ == '__main__':
    app.run(debug=True, port=3000)
```
### Set up https tunnel
```
pip install flask
python3 main.py
ngrok http 3000
```

### API Usage
#### Subscribe an event

```
curl --location 'http://127.0.0.1:8000/ws/v1/webhook' \
--header 'Content-Type: application/json' \
--data '{
    "event_type": "EV_ONE",
    "url": "https://ba95-116-109-60-166.ngrok-free.app/webhook/post/verify_success",
    "headers": {
        "hello": "world"
    },
    "secret_key": "thisissecretkey",
    "user_id": 1,
    "is_active": false
}'
```

```
curl --location 'http://127.0.0.1:8000/ws/v1/webhook' \
--header 'Content-Type: application/json' \
--data '{
    "event_type": "EV_TWO",
    "url": "https://ba95-116-109-60-166.ngrok-free.app/webhook/post/verify_failed",
    "headers": {
        "hello": "world"
    },
    "secret_key": "thisissecretkey",
    "user_id": 1,
    "is_active": false
}'
```
```
curl --location 'http://127.0.0.1:8000/ws/v1/webhook' \
--header 'Content-Type: application/json' \
--data '{
    "event_type": "EV_THREE",
    "url": "https://ba95-116-109-60-166.ngrok-free.app/webhook/post/delivery_success",
    "headers": {
        "hello": "world"
    },
    "secret_key": "thisissecretkey",
    "user_id": 1,
    "is_active": false
}'
```
```
curl --location 'http://127.0.0.1:8000/ws/v1/webhook' \
--header 'Content-Type: application/json' \
--data '{
    "event_type": "EV_FOUR",
    "url": "https://ba95-116-109-60-166.ngrok-free.app/webhook/post/delivery_failed",
    "headers": {
        "hello": "world"
    },
    "secret_key": "thisissecretkey",
    "user_id": 1,
    "is_active": false
}'
```
#### Verify event webhook
```
curl --location 'http://127.0.0.1:8000/ws/v1/webhook/:webhook_id
curl --location 'http://127.0.0.1:8000/ws/v1/webhook/1
curl --location 'http://127.0.0.1:8000/ws/v1/webhook/2
curl --location 'http://127.0.0.1:8000/ws/v1/webhook/3
curl --location 'http://127.0.0.1:8000/ws/v1/webhook/4
```

#### Trigger a webhook event
```
curl --location 'http://127.0.0.1:8000/ws/v1/event' \
--header 'Content-Type: application/json' \
--data '{
    "trigger_type": "NOW",
    "execution_time": 0,
    "event_type": "EV_ONE",
    "user_id": 1,
    "payload": {
        "msg": "message and data delivery to the user system",
    }
}'
```

```
curl --location 'http://127.0.0.1:8000/ws/v1/event' \
--header 'Content-Type: application/json' \
--data '{
    "trigger_type": "SCHEDULED",
    "execution_date": 1710852359,
    "event_type": "EV_ONE",
    "user_id": 1,
    "payload": {
        "msg": "message and data delivery to the user system"
    }
}'
```