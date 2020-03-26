import asyncio
import calendar
import logging
from os import environ
from datetime import date, timedelta
from decimal import Decimal

from tastyworks.models import option_chain, underlying
from tastyworks.models.option import Option, OptionType
from tastyworks.models.order import (Order, OrderDetails, OrderPriceEffect,
                                     OrderType)
from tastyworks.models.session import TastyAPISession
from tastyworks.models.trading_account import TradingAccount
from tastyworks.models.underlying import UnderlyingType
from tastyworks.tastyworks_api import tasty_session

from robinhood import authentication_service
from robinhood import robinhood_service

from finviz import finviz_service
from google import sheets

LOGGER = logging.getLogger(__name__)


async def main_loop(session: TastyAPISession, robinhood_token, worksheet_id):

    values_tastyworks = await tastyworks_data(session)  
    values_robinhood = await robinhood_data(robinhood_token)
    values = consolidate(values_tastyworks, values_robinhood)
    update_worksheet_dividend_tab(worksheet_id, values, {"UPRO"})

async def tastyworks_data(session: TastyAPISession):
    if session is None:
        return {}

    accounts = await TradingAccount.get_remote_accounts(session)
    acct = accounts[0]
    LOGGER.info('Accounts available: %s', accounts)

    equity = await TradingAccount.get_positions(session, acct, TradingAccount.just_equity)

    values = {}
    
    for stock in equity:
        dividend = await finviz_service.dividend(stock['symbol'])
        values[stock["symbol"]] = { 'symbol': stock["symbol"], 
                                    'quantity': float(stock["quantity"]), 
                                    'price': float(stock["average-open-price"]), 
                                    'dividend': dividend}
    return values
            

async def robinhood_data(token):
    if token is None:
        return {}

    accounts = await robinhood_service.accounts(token)
    equity = await robinhood_service.positions(token, accounts[0])
    values = {}
    
    for stock in equity:
        dividend = await finviz_service.dividend(stock['symbol'])
        values[stock["symbol"]] = { 'symbol': stock["symbol"], 
                                    'quantity': float(stock["quantity"]), 
                                    'price': float(stock["average_buy_price"]), 
                                    'dividend': dividend}
    return values

def consolidate(values1, values2):
    values = {key:value for key, value in values1.items()}
    for key, value in values2.items():
        if key in values:
            q1 = values[key]['quantity']
            q2 = value['quantity']
            p1 = values[key]['price']
            p2 = value['price']
            values[key]['quantity'] = q1 + q2
            values[key]['price'] = (p1*q1 + p2*q2) / (q1+q2) 
        else:
            values[key] = value
    
    sorted((key,value) for (key,value) in values.items())
    return values

def by_symbol(s):
    return s['symbol']

def update_worksheet_dividend_tab(worksheet_id, values, excluded_symbols):
    initialIndex = 5
    finalIndex = initialIndex

    stock_values = []
    dividend_values = []
    for key, value in values.items():
        if value['dividend'] > 0 and value['symbol'] not in excluded_symbols:
            stock_values.append([value['symbol'], value['quantity'], value['price']])
            dividend_values.append([value['dividend']])
            finalIndex = finalIndex + 1

    symbol_range = "'Dividend Income Portfolio'!A{}:C{}".format(initialIndex, finalIndex)
    dividend_range = "'Dividend Income Portfolio'!G{}:G{}".format(initialIndex, finalIndex)            

    sheets.update(worksheet_id, symbol_range, stock_values)
    sheets.update(worksheet_id, dividend_range, dividend_values)

def main():
    worksheet_id = environ.get('WORKSHEET_ID', "")
    if worksheet_id == "":
        print("Missing required environment variable WORKSHEET_ID. Pass the ID of the google worksheet that you want to update.")
        return
    
    tw_user = environ.get('TW_USER', "")
    tw_password = environ.get('TW_PASSWORD', "")
    tasty_client = None
    if tw_user != '' and tw_password != '':
        tasty_client = tasty_session.create_new_session(tw_user, tw_password)

    rh_user = environ.get('RH_USER', "")
    rh_password = environ.get('RH_PASSWORD', "")
    robinhood_token = None
    if rh_user != '' and rh_password != '':
        robinhood_token = authentication_service.authenticate(environ.get('RH_USER', ""), environ.get('RH_PASSWORD', ""))

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main_loop(tasty_client, robinhood_token, worksheet_id))
    except Exception:
        LOGGER.exception('Exception in main loop')
    finally:
        # find all futures/tasks still running and wait for them to finish
        pending_tasks = [
            task for task in asyncio.Task.all_tasks() if not task.done()
        ]
        loop.run_until_complete(asyncio.gather(*pending_tasks))
        loop.close()


if __name__ == '__main__':
    main()
