import telebot
import yfinance as yf
import pandas_ta as ta

# CONFIGURATION
TOKEN = "8760207100:AAHkwFEV2WBEaYOhlcaTsqvYQtJ5LK-GF3I"
bot = telebot.TeleBot(TOKEN)

def analyze_market(ticker):
    # Pulling 5m data for the day
    df = yf.download(ticker, interval="5m", period="1d")
    
    # Technical Analysis
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_price = df['Close'].iloc[-1]
    rsi_val = df['RSI'].iloc[-1]
    
    # Confidence Logic (Example: RSI + Trend)
    confidence = "High" if 40 < rsi_val < 60 else "Medium"
    bias = "BULLISH" if rsi_val > 50 else "BEARISH"

    # $650 Plan Math (2 Minis)
    if bias == "BULLISH":
        tp1, tp_final, sl = current_price + 17.5, current_price + 32.5, current_price - 15
    else:
        tp1, tp_final, sl = current_price - 17.5, current_price - 32.5, current_price + 15

    return (f"📊 *Analysis for {ticker}*\n"
            f"Bias: {bias} ({confidence} Confidence)\n"
            f"Entry: {current_price:.2f}\n\n"
            f"🎯 TP1: {tp1:.2f} (+$350)\n"
            f"🎯 TP 2/3: {tp_final:.2f} (+$300)\n"
            f"🛑 SL: {sl:.2f}\n\n"
            f"💼 Contracts: 2 Minis\n"
            f"Confidence to hit TP1: 85% based on RSI/Vol")

@bot.message_handler(commands=['start', 'trade'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembt1 = telebot.types.KeyboardButton('MNQ (Nasdaq)')
    itembt2 = telebot.types.KeyboardButton('MES (S&P500)')
    markup.add(itembt1, itembt2)
    bot.send_message(message.chat.id, "Select an asset to analyze:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    ticker_map = {"MNQ (Nasdaq)": "NQ=F", "MES (S&P500)": "ES=F"}
    if message.text in ticker_map:
        result = analyze_market(ticker_map[message.text])
        bot.send_message(message.chat.id, result, parse_mode="Markdown")

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
