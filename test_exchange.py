import logging
from exchange import BinanceExchangeClient


# Basic console logging for test
logging.basicConfig(level=logging.INFO)

print("---- EXCHANGE TEST START ----")

try:
    client = BinanceExchangeClient()
    print("Client initialized successfully.")

    symbol = "BTCUSDT"

    price = client.get_last_price(symbol)
    print(f"Last price for {symbol}: {price}")

    account_info = client.get_account_info()
    print("Account type:", account_info.get("accountType"))
    print("Can trade:", account_info.get("canTrade"))

except Exception as e:
    print("Exchange test failed:", e)

print("---- EXCHANGE TEST END ----")
