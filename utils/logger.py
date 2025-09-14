# utils/logger.py
# Stub for trade logging

def log_trade(symbol, side, price, result="pending"):
    print(f"[LOGGER] {side} {symbol} at {price} result={result}")
