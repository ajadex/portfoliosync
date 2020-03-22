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

from finviz import finviz_service
from google import sheets

LOGGER = logging.getLogger(__name__)


async def main_loop(session: TastyAPISession, worksheet_id):

    accounts = await TradingAccount.get_remote_accounts(session)
    acct = accounts[0]
    LOGGER.info('Accounts available: %s', accounts)

    equity = await TradingAccount.get_positions(session, acct, TradingAccount.just_equity)

    values = []
    dividend_values = []
    initialIndex = 5
    finalIndex = initialIndex
    for stock in equity:
        dividend = await finviz_service.dividend(stock['symbol'])
        if (dividend > 0):
            values.append([stock["symbol"], stock["quantity"], stock["average-open-price"]])
            dividend_values.append([dividend])
            finalIndex = finalIndex + 1
    
    symbol_range = "A{}:C{}".format(initialIndex, finalIndex)
    dividend_range = "G{}:G{}".format(initialIndex, finalIndex)

    sheets.update(worksheet_id, symbol_range, values)
    sheets.update(worksheet_id, dividend_range, dividend_values)



def main():
    worksheet_id = environ.get('WORKSHEET_ID', "")
    print
    if worksheet_id == "":
        print("Missing required environment variable WORKSHEET_ID. Pass the ID of the google worksheet that you want to update.")
        return
    tasty_client = tasty_session.create_new_session(environ.get('TW_USER', ""), environ.get('TW_PASSWORD', ""))
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main_loop(tasty_client, worksheet_id))
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
