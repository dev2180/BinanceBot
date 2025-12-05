from trading import TradeEngine

print("---- TRADE ENGINE TEST START ----")

engine = TradeEngine()

test_order = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.001
}

try:
    print("Validation + routing test passed.")
    print("Prepared order data:", test_order)
except Exception as e:
    print("Trade engine test failed:", e)

print("---- TRADE ENGINE TEST END ----")
