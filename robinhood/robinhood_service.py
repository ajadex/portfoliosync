import asyncio
import aiohttp
import requests

async def accounts(token):
    request_url = 'https://api.robinhood.com/accounts/'

    async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(token) }) as resp:
        if resp.status != 200:
            print('Warning: Searching for accounts failed.')
            return 0
        
        data = await resp.json()
    
    return data['results']

async def positions(token, account):
    request_url = 'https://api.robinhood.com/positions/?nonzero=true'

    async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(token) }) as resp:
        if resp.status != 200:
            print('Warning: Searching for positions failed.')
            return 0
        
        data = await resp.json()
        equity = data['results']
        instrument_ids = []
        for stock in equity:
            instrument_ids.append(stock['instrument'].replace('https://api.robinhood.com/instruments/', '').replace('/', ''))
        
        instrument_details = await instruments(token, instrument_ids)
        for i, instrument in enumerate(instrument_details):
            equity[i]['symbol'] = instrument['symbol']
    
    return equity


async def instruments(token, instrument_ids):
    request_url = 'https://api.robinhood.com/instruments/?ids={}'.format('%2C'.join(instrument_ids))

    async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(token) }) as resp:
        if resp.status != 200:
            print('Warning: Searching for intruments failed.')
            return 0
        
        data = await resp.json()
    
    return data['results']

# from os import environ
# import authentication_service as authentication_service
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# token = authentication_service.authenticate(environ.get('RH_USER', ""), environ.get('RH_PASSWORD', ""))
# accounts = loop.run_until_complete(accounts(token))
# positions = loop.run_until_complete(positions(token, accounts[0]))
# print(positions)