from tastyworks.models.session import TastyAPISession
from tastyworks.models.trading_account import TradingAccount
from tastyworks.models import option_chain, underlying
from tastyworks.models.option import Option, OptionType
from tastyworks.models.order import (Order, OrderDetails, OrderPriceEffect,
                                     OrderType)

from tastyworks.models.underlying import UnderlyingType
from tastyworks.tastyworks_api import tasty_session

from finviz import finviz_service
import datetime as datetime

class TastyworksService:

    def __init__(self, tw_user, tw_password): 
        self.account = None
        if tw_user != '' and tw_password != '':
            self.session = tasty_session.create_new_session(tw_user, tw_password)

    async def get_account(self):
        if self.account is None:            
            accounts = await TradingAccount.get_remote_accounts(self.session)
            self.account = accounts[0]
        return self.account
        

    async def equity(self):
        if self.session is None:
            return {}

        acct = await self.get_account()
        print('Using Tastyworks account: {}'.format(acct))
        equity = await TradingAccount.get_positions(self.session, acct, TradingAccount.just_equity)

        values = {}
        
        for stock in equity:
            dividend = await finviz_service.dividend(stock['symbol'])
            values[stock["symbol"]] = { 'symbol': stock["symbol"], 
                                        'quantity': float(stock["quantity"]), 
                                        'price': float(stock["average-open-price"]), 
                                        'dividend': dividend,
                                        'dividend_payout': 0.0}
        return values

    async def transfers(self, current_year):
        if self.session is None:
            return {}

        acct = await self.get_account()
        transfers = await TradingAccount.get_transfers(self.session, acct, '{}-01-01', '{}-12-31'.format(current_year))

        values = {}        
        for transfer in transfers:
            transfer_date = datetime.datetime.strptime(transfer['transaction-date'], '%Y-%m-%d').date()
            if (transfer_date.month not in values):
                values[transfer_date.month] = 0.0

            credit = -1
            if transfer['value-effect'] == 'Credit':
                credit = 1             
            values[transfer_date.month] = values[transfer_date.month] + (credit * float(transfer['value']))
        return values