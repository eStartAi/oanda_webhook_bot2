import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import oandapyV20
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.orders as orders

# Load .env
load_dotenv()
API_TOKEN = os.getenv("OANDA_API_TOKEN")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
BROKER_URL = "https://api-fxpractice.oanda.com/v3" if os.getenv("DEFAULT_BROKER") == "oanda_practice" else "https://api-fxtrade.oanda.com/v3"

# Configurable settings
MAX_TRADE_AGE_HOURS = int(os.getenv("MAX_TRADE_AGE_HOURS", 24))
MAX_TRADE_LOSS = float(os.getenv("MAX_TRADE_LOSS", -50))  # negative = loss

# Connect to OANDA
client = oandapyV20.API(access_token=API_TOKEN)

# SQLite DB
db = sqlite3.connect("trade_logs.db")
db.execute("""
CREATE TABLE IF NOT EXISTS auto_close_log (
    id INTEGER PRIMARY KEY,
    trade_id TEXT,
    instrument TEXT,
    reason TEXT,
    time_closed TEXT,
    profit_loss REAL
)
""")

def fetch_open_trades():
    r = trades.OpenTrades(accountID=ACCOUNT_ID)
    client.request(r)
    return r.response.get("trades", [])

def close_trade(trade_id, instrument, reason, pl=0):
    order = {
        "order": {
            "instrument": instrument,
            "units": "0",  # Close trade
            "type": "MARKET_ORDER",
            "timeInForce": "FOK",
            "positionFill": "REDUCE_ONLY"
        }
    }
    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order)
    client.request(r)

    db.execute("INSERT INTO auto_close_log (trade_id, instrument, reason, time_closed, profit_loss) VALUES (?, ?, ?, ?, ?)",
               (trade_id, instrument, reason, datetime.utcnow().isoformat(), pl))
    db.commit()

def auto_close():
    print("🔍 Checking open trades for auto-close...")
    open_trades = fetch_open_trades()
    now = datetime.utcnow()

    for t in open_trades:
        trade_id = t["id"]
        instrument = t["instrument"]
        open_time = datetime.fromisoformat(t["openTime"].replace("Z", "+00:00"))
        current_pl = float(t["unrealizedPL"])

        # Rule 1: Close if older than X hours
        if now - open_time > timedelta(hours=MAX_TRADE_AGE_HOURS):
            close_trade(trade_id, instrument, f"Older than {MAX_TRADE_AGE_HOURS}h", current_pl)
            print(f"🛑 Closed {instrument} (Trade {trade_id}) — older than {MAX_TRADE_AGE_HOURS}h")
            continue

        # Rule 2: Close if unrealized loss < threshold
        if current_pl < MAX_TRADE_LOSS:
            close_trade(trade_id, instrument, f"Loss below {MAX_TRADE_LOSS}", current_pl)
            print(f"🛑 Closed {instrument} (Trade {trade_id}) — loss {current_pl}")

    print("✅ Auto-close check complete.")

if __name__ == "__main__":
    auto_close()
