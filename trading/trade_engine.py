from exchange import BinanceExchangeClient


class TradeEngine:
    def __init__(self):
        self.exchange = BinanceExchangeClient()

    # -----------------------------
    # Validation Helpers
    # -----------------------------
    def _validate_symbol(self, symbol: str) -> str:
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Invalid symbol.")
        return symbol.upper()

    def _validate_side(self, side: str) -> str:
        side = side.upper()
        if side not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL.")
        return side

    def _validate_quantity(self, quantity: float) -> float:
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        return float(quantity)

    def _validate_price(self, price: float) -> float:
        if price <= 0:
            raise ValueError("Price must be greater than 0.")
        return float(price)

    # -----------------------------
    # Public Trade Interface
    # -----------------------------
    def execute_trade(self, order_data: dict) -> dict:
        """
        order_data example:
        {
            "symbol": "BTCUSDT",
            "side": "BUY" or "SELL",
            "type": "MARKET" | "LIMIT" | "STOP_LIMIT",
            "quantity": 0.001,
            "price": 60000,        # for LIMIT & STOP_LIMIT
            "stop_price": 59000   # only for STOP_LIMIT
        }
        """

        symbol = self._validate_symbol(order_data.get("symbol"))
        side = self._validate_side(order_data.get("side"))
        order_type = order_data.get("type", "").upper()

        # ---- SAFE QUANTITY PARSING ----
        raw_qty = order_data.get("quantity")
        quantity = self._safe_float(raw_qty, "quantity")
        quantity = self._validate_quantity(quantity)

        if order_type == "MARKET":
            # Apply LOT_SIZE filter (price not needed for MARKET)
            quantity = self._apply_exchange_filters(symbol, quantity)

            order = self.exchange.place_market_order(
                symbol=symbol,
                side=side,
                quantity=quantity
            )

        elif order_type == "LIMIT":
            if "price" not in order_data:
                raise ValueError("Price is required for LIMIT orders.")

            # ---- SAFE PRICE PARSING ----
            raw_price = order_data.get("price")
            price = self._safe_float(raw_price, "price")
            price = self._validate_price(price)

            # Apply LOT_SIZE + MIN_NOTIONAL filters
            quantity = self._apply_exchange_filters(symbol, quantity, price)

            order = self.exchange.place_limit_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )

        elif order_type == "STOP_LIMIT":
            if "price" not in order_data or "stop_price" not in order_data:
                raise ValueError("Both price and stop_price are required for STOP_LIMIT orders.")

            # ---- SAFE PRICE PARSING ----
            raw_price = order_data.get("price")
            price = self._safe_float(raw_price, "price")
            price = self._validate_price(price)

            raw_stop = order_data.get("stop_price")
            stop_price = self._safe_float(raw_stop, "stop_price")
            stop_price = self._validate_price(stop_price)

            # Apply LOT_SIZE + MIN_NOTIONAL filters
            quantity = self._apply_exchange_filters(symbol, quantity, price)

            order = self.exchange.place_stop_limit_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )

        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        return self._normalize_order_response(order)

    # -----------------------------
    # Response Normalizer
    # -----------------------------
    def _normalize_order_response(self, raw_order: dict) -> dict:
        """
        Always ensures a full order payload even if Binance returns ACK-only.
        """

        # If status is missing, fetch full order from exchange
        if "status" not in raw_order or raw_order.get("status") is None:
            order_id = raw_order.get("orderId")
            symbol = raw_order.get("symbol")

            if order_id and symbol:
                raw_order = self.exchange.get_order_by_id(
                    symbol=symbol,
                    order_id=order_id
                )

        normalized = {
            "order_id": raw_order.get("orderId"),
            "symbol": raw_order.get("symbol"),
            "side": raw_order.get("side"),
            "type": raw_order.get("type"),
            "status": raw_order.get("status"),
            "price": raw_order.get("price"),
            "orig_qty": raw_order.get("origQty"),
            "executed_qty": raw_order.get("executedQty"),
        }

        return normalized
    # -----------------------------
    # Account & Order Management
    # -----------------------------
    def get_balances(self):
        return self.exchange.get_balances()

    def get_open_orders(self, symbol: str | None = None):
        return self.exchange.get_open_orders(symbol)

    def cancel_order(self, symbol: str, order_id: int):
        return self.exchange.cancel_order(symbol, order_id)
    def _apply_exchange_filters(self, symbol: str, quantity: float, price: float | None = None):
        filters = self.exchange.get_symbol_filters(symbol)

        lot_filter = filters.get("LOT_SIZE")
        min_notional_filter = filters.get("MIN_NOTIONAL")

        step_size = float(lot_filter["stepSize"])
        min_qty = float(lot_filter["minQty"])
        max_qty = float(lot_filter["maxQty"])

        # Enforce LOT_SIZE
        quantity = round(quantity / step_size) * step_size

        if quantity < min_qty:
            raise ValueError(f"Quantity below minimum allowed: {min_qty}")

        if quantity > max_qty:
            raise ValueError(f"Quantity above maximum allowed: {max_qty}")

        # Enforce MIN_NOTIONAL (for non-market orders)
        if price is not None and min_notional_filter:
            min_notional = float(min_notional_filter["minNotional"])
            notional = quantity * price

            if notional < min_notional:
                raise ValueError(
                    f"Order value too small. "
                    f"Minimum notional: {min_notional}, your value: {notional}"
                )

        return quantity
    def _safe_float(self, value, field_name: str):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid numeric value for {field_name}")
