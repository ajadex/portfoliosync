import robinhood.authentication_service as authentication_service
import robinhood.robinhood_client as robinhood_client
from finviz import finviz_service
import datetime as datetime

class RobinHoodService:

    def __init__(self, rh_username, rh_password): 
        self.token = authentication_service.authenticate(rh_username, rh_password)

    async def equity(self):
        if self.token is None:
            return {}

        accounts = await robinhood_client.accounts(self.token)
        equity = await robinhood_client.positions(self.token, accounts[0])
        values = {}
        
        for stock in equity:
            dividend = await finviz_service.dividend(stock['symbol'])
            values[stock["symbol"]] = { 'symbol': stock["symbol"], 
                                        'quantity': float(stock["quantity"]), 
                                        'price': float(stock["average_buy_price"]), 
                                        'dividend': dividend}
        return values

    async def transfers(self, current_year):
        if self.token is None:
            return {}

        transfers = await robinhood_client.transfers(self.token)
        values = {}

        for transfer in transfers:
            transfer_date = datetime.datetime.strptime(transfer['expected_landing_date'], '%Y-%m-%d').date()
            if (transfer['state'] != 'completed' or transfer_date.year != current_year):
                continue

            if (transfer_date.month not in values):
                values[transfer_date.month] = 0.0
            values[transfer_date.month] = values[transfer_date.month] + float(transfer['amount'])
            
        return values
                
