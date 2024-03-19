import hashlib
import hmac


def generate(secret_key, token):
    hmac_digest = hmac.new(
        key=secret_key.strip().encode('utf-8'),
        msg=token.strip().encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac_digest


def verify(secret_key, token, signature):
    print(token)
    hmac_digest = hmac.new(
        key=secret_key.strip().encode('utf-8'),
        msg=token.strip().encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, hmac_digest)
