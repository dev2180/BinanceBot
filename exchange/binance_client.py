import logging
from binance import Client
from binance.exceptions import BinanceAPIException

from config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    USE_TESTNET,
)

# -----------------------------
# Logger for this module
# -----------------------------
logger = logging.getLogger(__name__)


class BinanceExchangeClient:
    def __init__(self):
        if not BINANCE_API_KEY or not BINANCE_API_SECRET:
            raise ValueError("Binance API key/secret not found in config.")

        self.client = Client(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET,
            testnet=USE_TESTNET
        )

        logger.info("BinanceExchangeClient initialized (testnet=%s)", USE_TESTNET)

    # -----------------------------
    # Market Data
    # -----------------------------
    def get_last_price(self, symbol: str) -> float:
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker["price"])
            logger.info("Fetched price for %s: %s", symbol, price)
            return price
        except BinanceAPIException as e:
            logger.exception("Error fetching price for %s: %s", symbol, e)
            raise

    # -----------------------------
    # Account Info
    # -----------------------------
    def get_account_info(self):
        try:
            info = self.client.get_account()
            logger.info("Fetched account info")
            return info
        except BinanceAPIException as e:
            logger.exception("Error fetching account info: %s", e)
            raise

    # -----------------------------
    # Orders
    # -----------------------------
    def place_market_order(self, symbol: str, side: str, quantity: float):
        try:
            logger.info(
                "Placing MARKET order | Symbol=%s Side=%s Qty=%s",
                symbol, side, quantity
            )

            order = self.client.create_order(
                symbol=symbol,
                side=side.upper(),
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )

            logger.info("Market order response: %s", order)
            return order

        except BinanceAPIException as e:
            logger.exception("Market order failed: %s", e)
            raise

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = Client.TIME_IN_FORCE_GTC,
    ):
        try:
            logger.info(
                "Placing LIMIT order | Symbol=%s Side=%s Qty=%s Price=%s",
                symbol, side, quantity, price
            )

            order = self.client.create_order(
                symbol=symbol,
                side=side.upper(),
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=time_in_force,
                quantity=quantity,
                price=str(price)
            )

            logger.info("Limit order response: %s", order)
            return order

        except BinanceAPIException as e:
            logger.exception("Limit order failed: %s", e)
            raise

    # -----------------------------
    # Order Queries
    # -----------------------------
    def get_open_orders(self, symbol: str | None = None):
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()

            logger.info("Fetched open orders")
            return orders

        except BinanceAPIException as e:
            logger.exception("Error fetching open orders: %s", e)
            raise

    def cancel_order(self, symbol: str, order_id: int):
        try:
            logger.info("Cancelling order %s on %s", order_id, symbol)

            result = self.client.cancel_order(
                symbol=symbol,
                orderId=order_id
            )

            logger.info("Cancel response: %s", result)
            return result

        except BinanceAPIException as e:
            logger.exception("Order cancellation failed: %s", e)
            raise
    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = Client.TIME_IN_FORCE_GTC,
    ):
        try:
            logger.info(
                "Placing STOP-LIMIT order | Symbol=%s Side=%s Qty=%s Price=%s StopPrice=%s",
                symbol, side, quantity, price, stop_price
            )

            order = self.client.create_order(
                symbol=symbol,
                side=side.upper(),
                type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                timeInForce=time_in_force,
                quantity=quantity,
                price=str(price),
                stopPrice=str(stop_price)
            )

            logger.info("Stop-Limit order response: %s", order)
            return order

        except BinanceAPIException as e:
            logger.exception("Stop-Limit order failed: %s", e)
            raise
    def get_order_by_id(self, symbol: str, order_id: int):
        try:
            order = self.client.get_order(
                symbol=symbol,
                orderId=order_id
            )
            logger.info("Fetched order by ID %s: %s", order_id, order)
            return order

        except BinanceAPIException as e:
            logger.exception("Error fetching order %s: %s", order_id, e)
            raise
    # -----------------------------
    # Balances
    # -----------------------------
    def get_balances(self):
        try:
            account = self.client.get_account()
            balances = account.get("balances", [])
            logger.info("Fetched balances")
            return balances
        except BinanceAPIException as e:
            logger.exception("Error fetching balances: %s", e)
            raise

    # -----------------------------
    # Open Orders
    # -----------------------------
    def get_open_orders(self, symbol: str | None = None):
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()

            logger.info("Fetched open orders")
            return orders

        except BinanceAPIException as e:
            logger.exception("Error fetching open orders: %s", e)
            raise
    # -----------------------------
    # Symbol Trading Rules
    # -----------------------------
    def get_symbol_filters(self, symbol: str):
        try:
            exchange_info = self.client.get_exchange_info()

            for s in exchange_info["symbols"]:
                if s["symbol"] == symbol:
                    filters = {f["filterType"]: f for f in s["filters"]}
                    logger.info("Fetched filters for %s", symbol)
                    return filters

            raise ValueError(f"Symbol not found: {symbol}")

        except BinanceAPIException as e:
            logger.exception("Error fetching symbol filters for %s: %s", symbol, e)
            raise
