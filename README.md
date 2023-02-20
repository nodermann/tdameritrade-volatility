# TD Ameritrade Intraday Volatility and Portfolio Value Calculator
This is a Python script that retrieves intraday prices for symbols in a TD Ameritrade watchlist and calculates their intraday volatility, as well as the total value of the portfolio.

The script uses the TD Ameritrade API to retrieve historical prices and quotes, and requires a TD Ameritrade API key and access token.

## Installation
Clone the repository:

git clone https://github.com/nodermann/tdameritrade-volatility.git
Install the required Python packages:

```bash
cd tdameritrade-volatility
pip install -r requirements.txt
```

## Usage
Set your TD Ameritrade API key and access token in the `consumer_key` and access_token variables in the script.

Set the account ID and watchlist ID in the account_id and `watchlist_id` variables in the script.

Set the number of days of historical prices to retrieve in the days variable in the script.

Set the number of minutes between intraday price updates in the interval variable in the script.

Run the script:

```bash
python tdameritrade_volatility.py
```

The script will retrieve the symbols in the watchlist, retrieve intraday prices for each symbol, calculate their intraday volatility, and print the results to the console. It will also calculate the total value of the portfolio and print it to the console.

## License
This script is released under the MIT License. Feel free to use it, modify it, and redistribute it as you like.
