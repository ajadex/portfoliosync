import asyncio
import aiohttp
import requests
import datetime as datetime

class RobinHoodClient:

    def __init__(self, token):
        self.token = token
        self.dividends = None

    async def accounts(self):
        request_url = 'https://api.robinhood.com/accounts/'

        async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(self.token) }) as resp:
            if resp.status != 200:
                print('Warning: Searching for accounts failed.')
                return 0
            
            data = await resp.json()
        
        return data['results']

    async def positions(self, account):
        request_url = 'https://api.robinhood.com/positions/?nonzero=true'

        async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(self.token) }) as resp:
            if resp.status != 200:
                print('Warning: Searching for positions failed.')
                return 0
            
            data = await resp.json()
            equity = data['results']
            instrument_ids = []
            for stock in equity:
                instrument_ids.append(stock['instrument'].replace('https://api.robinhood.com/instruments/', '').replace('/', ''))
            
            instrument_details = await self.instruments(instrument_ids)
            for i, instrument in enumerate(instrument_details):
                equity[i]['symbol'] = instrument['symbol']
        
        return equity


    async def instruments(self, instrument_ids):
        request_url = 'https://api.robinhood.com/instruments/?ids={}'.format('%2C'.join(instrument_ids))

        async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(self.token) }) as resp:
            if resp.status != 200:
                print('Warning: Searching for intruments failed.')
                return 0
            
            data = await resp.json()
        
        return data['results']

    async def transfers(self):
        request_url = 'https://api.robinhood.com/ach/transfers'

        async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(self.token) }) as resp:
            if resp.status != 200:
                print('Warning: Searching for transfers failed.')
                return 0
            
            data = await resp.json()
        
        return data['results']

    async def dividends_payouts(self, current_year):
        if self.dividends is not None:
            return self.dividends
        print('Ajadex: called dividends')

        request_url = 'https://api.robinhood.com/dividends/'

        async with aiohttp.request('GET', request_url, headers={ 'Authorization': "Bearer {}".format(self.token) }) as resp:
            if resp.status != 200:
                print('Warning: Searching for transfers failed.')
                return 0
            
            data = await resp.json()
        dividends = filter(lambda e: e['state'] == 'paid', data['results'])
        instrument_ids = []
        results = []
        for entry in dividends:
            instrument_id = entry['instrument'].replace('https://api.robinhood.com/instruments/', '').replace('/', '')
            paid_at = datetime.datetime.strptime(entry['paid_at'][:10], '%Y-%m-%d').date()
            if paid_at.year == current_year and instrument_id not in instrument_ids:
                instrument_ids.append(instrument_id)
                results.append(entry)

        instrument_details = await self.instruments(instrument_ids)        
        for instrument in instrument_details:
            for dividend in results:
                if dividend['instrument'] == instrument['url']:
                    dividend['symbol'] = instrument['symbol']

        self.dividends = results
        return results

# from os import environ
# import authentication_service as authentication_service
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# token = authentication_service.authenticate(environ.get('RH_USER', ""), environ.get('RH_PASSWORD', ""))
# client = RobinHoodClient(token)
# #accounts = loop.run_until_complete(accounts(token))
# #positions = loop.run_until_complete(positions(token, accounts[0]))
# dividends = loop.run_until_complete(client.dividends_payouts(2020))
# # print(dividends)