# ShinuaBack
Shinua backend for communicating with DB - telegram bot and FastAPI

## Backend

### Project setup
```bash
# Install dependencies
$ cd backend
$ pip install -r requirements.txt

# Install backend module
$ pip install -e .
```

### Install wkhtmltopdf
An external binary is needed to generate PDFs. You can download it from [here](https://wkhtmltopdf.org/downloads.html). Make sure to add it to your PATH.

### Run server
```bash
$ uvicorn main:app --host 0.0.0.0 --reload
```
# ShinuaBot
Telegram bot written in python to help collect shinua pickup data.

### Project setup
Replace TELEGRAM_BOT_TOKEN with your bot token (you can get it from @BotFather)

### Telegram Channel
The bot is currently under the following telegram channel: t.me/shinua_havrati_bot

```bash
# Install dependencies
$ cd bot
$ pip install -r requirements.txt

# Install bot module
$ pip install -e .
```
### Run bot
```bash
$ python bot.py
```
### Start new pickup
enter the telegram channel and write התחל
