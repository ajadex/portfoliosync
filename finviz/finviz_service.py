import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

async def dividend(symbol):
    """
    Performs a stock search through the finviz API.

    Args:
        symbols (list): The list of string symbols to search for.

    Returns:
        list (dict): A list of stock details including full name, implied volatility, liquidity etc.

    Raises:
        Exception: raises a general exception when the request does not succeed.
    """

    request_url = 'https://finviz.com/quote.ashx?t={}'.format(
        symbol
    )

    dividend = 0.0

    async with aiohttp.request('GET', request_url) as resp:
        if resp.status != 200:
            print('Warning: Searching for stocks {} failed'.format(symbol))
            return 0
        
        data = await resp.text()
        soup = BeautifulSoup(data, features="html.parser")
        table = soup.find("table", attrs={"class":"snapshot-table2"})
        dividend_value = table.find_all("tr")[6].find_all("td")[1].get_text()
        if (dividend_value) != "-":
            dividend = float(dividend_value)
    
    return dividend


# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# result = loop.run_until_complete(stock_search("JNJ"))
# print(result)