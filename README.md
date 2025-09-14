# OANDA Webhook Bot

## Features
- Flask webhook server
- SQLite trade logging
- Modular utils (trade, risk, logger)
- Ready for Render deployment

## Usage
```bash
git clone <repo>
cd oanda_webhook_bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Deployment
- Use `render.yaml` for Render deployment.
# oanda_webhook_bot_Public
