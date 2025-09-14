# utils/trade.py
# Stub for trade execution logic

def place_order(symbol, side, price, units):
    print(f"[TRADE] {side} {units} {symbol} at {price}")
    return {"status": "stub", "symbol": symbol, "side": side, "price": price}
