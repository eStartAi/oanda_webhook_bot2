from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import sqlite3

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv("OANDA_API_TOKEN")
ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

app = Flask(__name__)

# Ensure SQLite DB exists
db = sqlite3.connect("trade_logs.db", check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    side TEXT,
    price REAL,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# --- JSON Healthcheck ---
@app.route("/", methods=["GET"])
def home():
    try:
        # Quick DB check
        cur = db.execute("SELECT COUNT(*) FROM trades")
        trade_count = cur.fetchone()[0]
    except Exception as e:
        trade_count = f"DB error: {e}"

    return jsonify({
        "status": "ok",
        "service": "OANDA Webhook Bot",
        "account_id": ACCOUNT_ID if ACCOUNT_ID else "❌ Not loaded",
        "env": {
            "OANDA_API_TOKEN": "✔️ Loaded" if API_TOKEN else "❌ Missing",
            "WEBHOOK_SECRET": "✔️ Loaded" if WEBHOOK_SECRET else "❌ Missing"
        },
        "trade_logs_count": trade_count
    }), 200

# --- Webhook Route ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Webhook Received:", data)

    # Verify secret
    if data.get("key") != WEBHOOK_SECRET:
        return jsonify({"status": "unauthorized"}), 403

    symbol, side, price = data.get("symbol"), data.get("side"), data.get("price")
    db.execute("INSERT INTO trades (symbol, side, price) VALUES (?, ?, ?)", (symbol, side, price))
    db.commit()

    return jsonify({"status": "ok", "message": f"Saved {side} {symbol} at {price}"}), 200

# --- Run App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Starting Webhook Bot on port {port}...")
    app.run(host="0.0.0.0", port=port)
