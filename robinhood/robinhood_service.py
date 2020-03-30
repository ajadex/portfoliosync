import robinhood.authentication_service as authentication_service
from robinhood.robinhood_client import RobinHoodClient
from finviz import finviz_service
import datetime as datetime

class RobinHoodService:

    def __init__(self, rh_username, rh_password, current_year):
        self.current_year = current_year 
        token = authentication_service.authenticate(rh_username, rh_password)
        self.rhClient = None
        if token is not None:
            self.rhClient = RobinHoodClient(token)

    async def equity(self):
        if self.rhClient is None:
            return {}

        accounts = await self.rhClient.accounts()
        equity = await self.rhClient.positions(accounts[0])
        dividend_payouts = await self.rhClient.dividends_payouts(self.current_year)
        
        values = {}        
        for stock in equity:
            dividend = await finviz_service.dividend(stock['symbol'])
            values[stock["symbol"]] = { 'symbol': stock["symbol"], 
                                        'quantity': float(stock["quantity"]), 
                                        'price': float(stock["average_buy_price"]), 
                                        'dividend': dividend,
                                        'dividend_payout': 0.0}

        for div_payout in dividend_payouts:
            if div_payout['symbol'] in values:
                values[div_payout['symbol']]['dividend_payout'] = values[div_payout['symbol']]['dividend_payout'] + float(div_payout['amount'])
        return values

    async def monthly_transfers(self):
        if self.rhClient is None:
            return {}

        transfers = await self.rhClient.transfers()
        values = {1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0, 7:0.0, 8:0.0, 9:0.0, 10:0.0, 11:0.0, 12:0.0,}

        for transfer in transfers:
            transfer_date = datetime.datetime.strptime(transfer['expected_landing_date'], '%Y-%m-%d').date()
            if (transfer['state'] != 'completed' or transfer_date.year != self.current_year):
                continue
            
            values[transfer_date.month] = values[transfer_date.month] + float(transfer['amount'])
            
        return values
        
    async def monthly_dividends(self):
        if self.rhClient is None:
            return {}

        dividends = await self.rhClient.dividends_payouts(self.current_year)
        values = {1:0.0, 2:0.0, 3:0.0, 4:0.0, 5:0.0, 6:0.0, 7:0.0, 8:0.0, 9:0.0, 10:0.0, 11:0.0, 12:0.0,}

        for dividend in dividends:
            paid_at = datetime.datetime.strptime(dividend['paid_at'][:10], '%Y-%m-%d').date()
            values[paid_at.month] = values[paid_at.month] + float(dividend['amount'])
            
        return values
                
