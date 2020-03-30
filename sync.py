import asyncio
import calendar
import logging
from os import environ
from datetime import date, timedelta
from decimal import Decimal

from tastyworks.tastyworks_service import TastyworksService
from robinhood.robinhood_service import RobinHoodService
from google import sheets

LOGGER = logging.getLogger(__name__)
logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)


async def main_loop(worksheet_id):

    current_year = 2020
    robinhood = RobinHoodService(environ.get('RH_USER', ""), environ.get('RH_PASSWORD', ""), current_year)
    tastyworks = TastyworksService(environ.get('TW_USER', ""), environ.get('TW_PASSWORD', ""))

    equity_tastyworks, equity_robinhood, transfers_tastworks, transfers_robinhood, monthly_dividends_rh = await asyncio.gather(
        tastyworks.equity(), 
        robinhood.equity(),
        tastyworks.transfers(current_year),
        robinhood.monthly_transfers(),
        robinhood.monthly_dividends())
    values = consolidate_equity(equity_tastyworks, equity_robinhood)
    transfer_monthly_values = consolidate_montly_transactions(transfers_tastworks, transfers_robinhood)
    payouts_monthly_values = consolidate_montly_transactions(monthly_dividends_rh, {})
    update_worksheet_dividend_tab(worksheet_id, values, transfer_monthly_values, payouts_monthly_values, {"UPRO"})

def consolidate_equity(values1, values2):
    values = {key:value for key, value in values1.items()}
    for key, value in values2.items():
        if key in values:
            q1 = values[key]['quantity']
            q2 = value['quantity']
            p1 = values[key]['price']
            p2 = value['price']
            values[key]['quantity'] = q1 + q2
            values[key]['price'] = (p1*q1 + p2*q2) / (q1+q2) 
            values[key]['dividend_payout'] = values[key]['dividend_payout'] + value['dividend_payout']
        else:
            values[key] = value
    
    values = {key:value for key,value in sorted(values.items())}
    return values

def consolidate_montly_transactions(values1, values2):
    values = {key:value for key, value in values1.items()}
    for key, value in values2.items():
        if key in values:
            values[key] = values[key] + value
        else:
            values[key] = value
    
    values = {key:value for key,value in sorted(values.items())}
    return values

def update_worksheet_dividend_tab(worksheet_id, values, transfers, payouts_monthly_values, excluded_symbols):
    initialIndex = 5
    finalIndex = initialIndex

    stock_values = []
    dividend_values = []
    dividend_payout_values = []
    for key, value in values.items():
        if value['dividend'] > 0 and value['symbol'] not in excluded_symbols:
            stock_values.append([value['symbol'], value['quantity'], value['price']])
            dividend_values.append([value['dividend']])
            dividend_payout_values.append([value['dividend_payout']])
            finalIndex = finalIndex + 1

    transfer_values = []
    for month in range(1,12):
        transfer_values.append([transfers[month], payouts_monthly_values[month]])

    symbol_range = "'Dividend Income Portfolio'!A{}:C{}".format(initialIndex, finalIndex)
    dividend_range = "'Dividend Income Portfolio'!G{}:G{}".format(initialIndex, finalIndex)
    dividend_payout_range = "'Dividend Income Portfolio'!J{}:J{}".format(initialIndex, finalIndex)
    transfer_range = "'Dividend Income Portfolio'!O{}:P{}".format(initialIndex, initialIndex+12)            

    sheets.update(worksheet_id, symbol_range, stock_values)
    sheets.update(worksheet_id, dividend_range, dividend_values)
    sheets.update(worksheet_id, dividend_payout_range, dividend_payout_values)
    sheets.update(worksheet_id, transfer_range, transfer_values)

def main():
    worksheet_id = environ.get('WORKSHEET_ID', "")
    if worksheet_id == "":
        print("Missing required environment variable WORKSHEET_ID. Pass the ID of the google worksheet that you want to update.")
        return
    
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main_loop(worksheet_id))
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
