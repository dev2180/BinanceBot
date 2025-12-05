from trading import TradeEngine


class TradingCLI:
    def __init__(self):
        self.engine = TradeEngine()

    def show_menu(self):
        print("\n----- TRADING TERMINAL (SPOT TESTNET) -----")
        print("1. Place Order")
        print("2. View Balances")
        print("3. View Open Orders")
        print("4. Cancel Order")
        print("5. Exit")

    def place_order_flow(self):
        symbol = input("Enter trading symbol (e.g., BTCUSDT): ").strip().upper()
        side = input("Enter side (BUY / SELL): ").strip().upper()
        order_type = input("Enter order type (MARKET / LIMIT / STOP_LIMIT): ").strip().upper()
        quantity = float(input("Enter quantity: ").strip())

        order_data = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity
        }

        if order_type == "LIMIT":
            price = float(input("Enter limit price: ").strip())
            order_data["price"] = price

        elif order_type == "STOP_LIMIT":
            stop_price = float(input("Enter STOP price (trigger): ").strip())
            price = float(input("Enter LIMIT price: ").strip())
            order_data["stop_price"] = stop_price
            order_data["price"] = price

        confirm = input("Confirm order? (y/n): ").strip().lower()
        if confirm != "y":
            print("Order cancelled by user.")
            return

        print("\nPlacing order...")
        result = self.engine.execute_trade(order_data)

        print("----- ORDER RESULT -----")
        for key, value in result.items():
            print(f"{key}: {value}")

    def view_balances_flow(self):
        balances = self.engine.get_balances()

        important_assets = {"USDT", "BTC", "ETH", "BNB"}
        show_all = input("Show all assets? (y/n): ").strip().lower() == "y"

        print("----- ACCOUNT BALANCES -----")
        shown = False

        for asset in balances:
            symbol = asset["asset"]
            free = float(asset["free"])
            locked = float(asset["locked"])

            if not show_all and symbol not in important_assets:
                continue

            if free > 0 or locked > 0:
                shown = True
                print(f"{symbol}: Free={free}, Locked={locked}")

        if not shown:
            print("No balances to display.")

    def view_open_orders_flow(self):
        symbol = input("Enter symbol to filter (or press Enter for all): ").strip().upper()
        symbol = symbol if symbol else None

        orders = self.engine.get_open_orders(symbol)

        if not orders:
            print("No open orders.")
            return

        print("----- OPEN ORDERS -----")
        for o in orders:
            print(
                f"OrderID={o['orderId']} | {o['symbol']} | {o['side']} | "
                f"{o['type']} | Price={o['price']} | Qty={o['origQty']} | Status={o['status']}"
            )

    def cancel_order_flow(self):
        symbol = input("Enter symbol: ").strip().upper()
        order_id = int(input("Enter Order ID to cancel: ").strip())

        confirm = input("Confirm cancel? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancellation aborted.")
            return

        result = self.engine.cancel_order(symbol, order_id)
        print("Cancel result:", result.get("status", result))

    def run(self):
        while True:
            try:
                self.show_menu()
                choice = input("Select option (1-5): ").strip()

                if choice == "1":
                    self.place_order_flow()

                elif choice == "2":
                    self.view_balances_flow()

                elif choice == "3":
                    self.view_open_orders_flow()

                elif choice == "4":
                    self.cancel_order_flow()

                elif choice == "5":
                    print("Exiting trading terminal.")
                    break

                else:
                    print("Invalid choice.")

                cont = input("\nContinue? (y/n): ").strip().lower()
                if cont != "y":
                    print("Session ended by user.")
                    break

            except Exception as e:
                print("Error:", e)
                break
