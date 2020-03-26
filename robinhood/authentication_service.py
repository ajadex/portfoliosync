import asyncio
import aiohttp
import requests

def authenticate(username, password):
    request_url = 'https://api.robinhood.com/oauth2/token/'

    dividend = 0.0

    body = {
        'username': username,
        'password': password,
        'grant_type': 'password',
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'scope': 'internal',
        'device_token': '1d1bb3a1-0925-48eb-83d5-78ff250fcba3'
    }

    resp = requests.post(request_url, data=body)
    if resp.status_code != 200:
        raise Exception('Failed to login to RobinHood')
    data = resp.json()
    return data['access_token']


# from os import environ
# result = authenticate(environ.get('RH_USER', ""), environ.get('RH_PASSWORD', ""))
# print(result)