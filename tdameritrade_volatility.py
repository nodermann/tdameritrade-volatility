import asyncio
import aiohttp
import pandas as pd
import datetime as dt

# Your TD Ameritrade API key
consumer_key = 'YOUR_CONSUMER_KEY'

# Your TD Ameritrade API access token
access_token = 'YOUR_ACCESS_TOKEN'

# The base URL for TD Ameritrade's API
base_url = 'https://api.tdameritrade.com/v1/'

# The endpoint for retrieving historical prices for a symbol
price_endpoint = 'marketdata/{}/pricehistory'

# The endpoint for retrieving account balances
balance_endpoint = 'accounts/{}/balances'

# The endpoint for retrieving a user's watchlists
watchlist_endpoint = 'accounts/{}/watchlists'

# The account ID for the account you want to retrieve balances for
account_id = '123456789'

# The watchlist ID for the watchlist you want to retrieve
watchlist_id = 'My Watchlist'

# The number of days of historical prices to retrieve
days = 5

# The number of minutes between intraday price updates
interval = 5

# Function to retrieve data for a given symbol
async def get_data_for_symbol(session, symbol):
    # Construct the URL for the API call to retrieve the historical prices for the symbol
    price_url = base_url + price_endpoint.format(symbol)
    price_headers = {'Authorization': 'Bearer {}'.format(access_token)}
    price_params = {'periodType': 'day', 'frequencyType': 'minute', 'frequency': interval}
    async with session.get(price_url, headers=price_headers, params=price_params) as price_response:
        # Check the status code of the response
        if price_response.status == 200:
            # If the response was successful, parse the JSON data
            price_data = await price_response.json()
            # Convert the data to a Pandas DataFrame
            prices = pd.DataFrame(price_data['candles'])
            # Convert the timestamps to Python datetime objects
            prices['datetime'] = prices['datetime'].apply(lambda x: dt.datetime.fromtimestamp(int(x/1000)))
            # Calculate the intraday volatility
            prices['range'] = prices['high'] - prices['low']
            volatility = prices['range'].std()
            return symbol, volatility
        else:
            # If the response was not successful, return None
            return symbol, None

async def main():
    async with aiohttp.ClientSession() as session:
        # Retrieve the watchlist
        watchlist_url = base_url + watchlist_endpoint.format(account_id)
        watchlist_headers = {'Authorization': 'Bearer {}'.format(access_token)}
        async with session.get(watchlist_url, headers=watchlist_headers) as watchlist_response:
            # Check the status code of the response
            if watchlist_response.status == 200:
                # If the response was successful, parse the JSON data
                watchlist_data = await watchlist_response.json()
                # Find the watchlist with the specified ID
                watchlist = next((w for w in watchlist_data if w['name'] == watchlist_id), None)
                if watchlist:
                    # If the watchlist was found, retrieve the symbols
                    symbols = [s['symbol'] for s in watchlist['watchlistItems']]
                else:
                    # If the watchlist was not found, print an error message and exit
                    print('Error: Watchlist not found')
                    return
            else:
                # If the response was not successful, print the status code and reason and exit
                print('Error: Status Code {} - {}'.format(watchlist_response.status, watchlist_response.reason))
                return

        # Create a list of tasks to retrieve data for each symbol
        tasks = [get_data_for_symbol(session, symbol) for symbol in symbols]
        # Run the tasks concurrently
        results = await asyncio.gather(*tasks)
        # Create a dictionary to store the intraday volatility for each symbol
        volatility = {symbol: vol for symbol, vol in results if vol is not None}
        # Print the intraday volatility for each symbol
        print('Intraday Volatility:')
        for symbol, vol in volatility.items():
            print('{}: {:.2f}%'.format(symbol, vol * 100))

        # Retrieve the account balances
        balance_url = base_url + balance_endpoint.format(account_id)
        balance_headers = {'Authorization': 'Bearer {}'.format(access_token)}
        async with session.get(balance_url, headers=balance_headers) as balance_response:
            # Check the status code of the response
            if balance_response.status == 200:
                # If the response was successful, parse the JSON data
                balance_data = await balance_response.json()
                # Get the available buying power for the account
                available_funds = balance_data['securitiesAccount']['initialBalances']['availableFunds']
            else:
                # If the response was not successful, print the status code and reason and exit
                print('Error: Status Code {} - {}'.format(balance_response.status, balance_response.reason))
                return

        # Calculate the total value of the portfolio
        total_value = 0
        for symbol in symbols:
            # Construct the URL for the API call to retrieve the quote for the symbol
            quote_url = base_url + 'marketdata/quotes'
            quote_headers = {'Authorization': 'Bearer {}'.format(access_token)}
            quote_params = {'symbol': symbol}
            async with session.get(quote_url, headers=quote_headers, params=quote_params) as quote_response:
                # Check the status code of the response
                if quote_response.status == 200:
                    # If the response was successful, parse the JSON data
                    quote_data = await quote_response.json()
                    # Get the last price for the symbol
                    last_price = quote_data[symbol]['lastPrice']
                    # Get the quantity of the symbol in the watchlist
                    quantity = next((s['quantity'] for s in watchlist['watchlistItems'] if s['symbol'] == symbol), 0)
                    # Calculate the value of the position
                    position_value = last_price * quantity
                    # Add the position value to the total value
                    total_value += position_value
                else:
                    # If the response was not successful, print the status code and reason and exit
                    print('Error: Status Code {} - {}'.format(quote_response.status, quote_response.reason))
                    return

        # Print the total value of the portfolio
        print('Total Value: ${:.2f}'.format(total_value))

        # Print the available buying power for the account
        print('Available Buying Power: ${:.2f}'.format(available_funds))

if __name__ == '__main__':
    asyncio.run(main())
