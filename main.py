import hashlib
import hmac
import json
import os
import time

import requests

API_KEY = os.environ['COINS_API_KEY']
API_SECRET = os.environ['COINS_API_SECRET'].encode('utf-8')
PHP_AMOUNT=os.environ['PHP_AMOUNT']


def get_nonce():
    """Return a nonce based on the current time.

    A nonce should only use once and should always be increasing.
    Using the current time is perfect for this.
    """
    # Get the current unix epoch time, and convert it to milliseconds
    return int(time.time() * 1e6)


def sign_request(url, nonce, request_body=None):
    """Return an HMAC signature based on the request."""
    if request_body is None:
        # GET requests don't have a body, so we'll skip that for signing
        message = str(nonce) + url
    else:
        # json_body = json.dumps(request_body, separators=(',', ':'))
        message = str(nonce) + url + request_body

    return str(
        hmac.new(
            API_SECRET,
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
    )


def get_currency_acctid(obj, currency):
    return list(filter(lambda x: x['currency'] == currency, obj))[0]['id']


def get_user_currencies():
    """Gets the IDs of PHP and BTC accounts of the user."""
    url = 'https://coins.ph/api/v3/crypto-accounts/'
    nonce = get_nonce()

    headers = {
        'ACCESS_SIGNATURE': sign_request(url, nonce),
        'ACCESS_KEY': API_KEY,
        'ACCESS_NONCE': str(nonce),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


    r = requests.get(url, headers=headers).json()['crypto-accounts']

    return get_currency_acctid(r, 'PBTC'), get_currency_acctid(r, 'BTC')


def convert_PHP_to_BTC(data, context):
    """Converts PHP to BTC. The amount of PHP converted depends on the environment variable set.

    The arguments are required by PubSub and are currently not used.
    """
    php_id, btc_id = get_user_currencies()
    # HMAC requests require a trailing slash https://github.com/coinsph/api/issues/7
    url = 'https://coins.ph/api/v3/crypto-exchanges/'
    nonce = get_nonce()
    body = {
        'source_account': php_id,
        'target_account': btc_id,
        'source_amount': PHP_AMOUNT
    }
    # http://docs.python-requests.org/en/master/user/quickstart/#more-complicated-post-requests
    body_json = json.dumps(body, separators=(',', ':'))
    signature = sign_request(url, nonce, request_body=body_json)
    headers = {
        'ACCESS_SIGNATURE': signature,
        'ACCESS_KEY': API_KEY,
        'ACCESS_NONCE': str(nonce),
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json'
    }
    return requests.post(url, headers=headers, data=body_json)
