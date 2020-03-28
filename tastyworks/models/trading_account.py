# uncompyle6 version 3.6.4
# Python bytecode 3.6 (3379)
# Decompiled from: Python 3.6.9 (default, Nov  7 2019, 10:44:02) 
# [GCC 8.3.0]
# Embedded file name: /mnt/d/Projects/MyProjects/portfoliosync/tastyworks_api/tastyworks/models/trading_account.py
# Compiled at: 2020-03-20 21:24:56
# Size of source mod 2**32: 7213 bytes
from typing import List
import aiohttp
from dataclasses import dataclass
from tastyworks.models.order import Order, OrderPriceEffect

@dataclass
class TradingAccount(object):
    account_number: str
    external_id: str
    is_margin: bool

    async def execute_order(self, order, session, dry_run=True):
        """
        Execute an order. If doing a dry run, the order isn't placed but simulated (server-side).

        Args:
            order (Order): The order object to execute.
            session (TastyAPISession): The tastyworks session onto which to execute the order.
            dry_run (bool): Whether to do a test (dry) run.

        Returns:
            bool: Whether the order was successful.
        """
        if not order.check_is_order_executable():
            raise Exception('Order is not executable, most likely due to missing data')
        else:
            if not session.is_active():
                raise Exception('The supplied session is not active and valid')
            url = '{}/accounts/{}/orders'.format(session.API_url, self.account_number)
            if dry_run:
                url = f"{url}/dry-run"
        body = _get_execute_order_json(order)
        async with aiohttp.request('POST', url, headers=(session.get_request_headers()), json=body) as resp:
            if resp.status == 201:
                return True
            else:
                if resp.status == 400:
                    raise Exception('Order execution failed, message: {}'.format(await resp.text()))
                else:
                    raise Exception('Unknown remote error, status code: {}, message: {}'.format(resp.status, await resp.text()))

    @classmethod
    def from_dict(cls, data):
        """
        Parses a TradingAccount object from a dict.
        """
        new_data = {'is_margin':True if data['margin-or-cash'] == 'Margin' else False, 
         'account_number':data['account-number'], 
         'external_id':data['external-id']}
        res = TradingAccount(**new_data)
        return res

    @classmethod
    async def get_remote_accounts(cls, session):
        """
        Gets all trading accounts from the Tastyworks platform.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.

        Returns:
            list (TradingAccount): A list of trading accounts.
        """
        url = f"{session.API_url}/customers/me/accounts"
        res = []
        async with aiohttp.request('GET', url, headers=(session.get_request_headers())) as response:
            if response.status != 200:
                raise Exception('Could not get trading accounts info from Tastyworks...')
            data = (await response.json())['data']
        for entry in data['items']:
            if entry['authority-level'] != 'owner':
                pass
            else:
                acct_data = entry['account']
                acct = TradingAccount.from_dict(acct_data)
                res.append(acct)

        return res

    @classmethod
    def just_equity(self, position):
        return position['instrument-type'] == 'Equity'

    def by_symbol(e):
        return e['symbol']

    async def get_balance(session, account):
        """
        Get balance.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
            account (TradingAccount): The account_id to get balance on.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/balances'.format(session.API_url, account.account_number)
        async with aiohttp.request('GET', url, headers=(session.get_request_headers())) as response:
            if response.status != 200:
                raise Exception('Could not get trading account balance info from Tastyworks...')
            data = (await response.json())['data']
        return data

    async def get_positions(session, account, filter_function):
        """
        Get Open Positions, filtered.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
            account (TradingAccount): The account_id to get positions on.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/positions'.format(session.API_url, account.account_number)
        async with aiohttp.request('GET', url, headers=(session.get_request_headers())) as response:
            if response.status != 200:
                raise Exception('Could not get open positions info from Tastyworks...')
            data = (await response.json())['data']['items']
        return sorted((filter(filter_function, data)), key=(TradingAccount.by_symbol))

    async def get_live_orders(session, account):
        """
        Get live Orders.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
            account (TradingAccount): The account_id to get live orders on.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/orders/live'.format(session.API_url, account.account_number)
        async with aiohttp.request('GET', url, headers=(session.get_request_headers())) as response:
            if response.status != 200:
                raise Exception('Could not get live orders info from Tastyworks...')
            data = (await response.json())['data']['items']
        return data

    async def get_history(session, account):
        """
        Get live Orders.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
            account (TradingAccount): The account_id to get history on.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/transactions'.format(session.API_url, account.account_number)
        async with aiohttp.request('GET', url, headers=(session.get_request_headers())) as response:
            if response.status != 200:
                raise Exception('Could not get history info from Tastyworks...')
            data = (await response.json())['data']
        return data

    async def get_transfers(session, account, start_date, end_date):
        """
        Get live Orders.

        Args:
            session (TastyAPISession): An active and logged-in session object against which to query.
            account (TradingAccount): The account_id to get history on.
        Returns:
            dict: account attributes
        """
        url = '{}/accounts/{}/transactions?type=Money+Movement&start-date={}&end-date={}&per-page=1000'.format(session.API_url, account.account_number, start_date, end_date)
        async with aiohttp.request('GET', url, headers=(session.get_request_headers())) as response:
            if response.status != 200:
                raise Exception('Could not get history info from Tastyworks...')
            data = (await response.json())['data']['items']
        return data


def _get_execute_order_json(order: Order):
    order_json = {'source':order.details.source, 
     'order-type':order.details.type.value, 
     'price':'{:.2f}'.format(order.details.price), 
     'price-effect':order.details.price_effect.value, 
     'time-in-force':order.details.time_in_force.value, 
     'legs':_get_legs_request_data(order)}
    if order.details.gtc_date:
        order_json['gtc-date'] = order.details.gtc_date.strftime('%Y-%m-%d')
    return order_json


def _get_legs_request_data(order):
    res = []
    order_effect = order.details.price_effect
    order_effect_str = 'Sell to Open' if order_effect == OrderPriceEffect.CREDIT else 'Buy to Open'
    for leg in order.details.legs:
        leg_dict = {**(leg.to_tasty_json()), **{'action': order_effect_str}}
        res.append(leg_dict)

    return res
# okay decompiling trading_account.cpython-36.pyc
