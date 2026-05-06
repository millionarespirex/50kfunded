import telebot
import yfinance as yf
from flask import Flask
from threading import Thread

# CONFIGURATION
TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is alive!"

def run(): app.run(host='0.0.0.0', port=8080)

def analyze_market(ticker):
    df = yf.download(ticker, interval="5m", period="1d")
    current_price = df['Close'].iloc[-1]
    
    # Simple manual RSI-style bias
    avg_gain = df['Close'].diff().dropna().clip(lower=0).mean()
    avg_loss = (-df['Close'].diff().dropna().clip(upper=0)).mean()
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    bias = "BULLISH" if rsi > 50 else "BEARISH"
    tp1, tp_final, sl = (current_price + 17.5, current_price + 32.5, current_price - 15) if bias == "BULLISH" else (current_price - 17.5, current_price - 32.5, current_price + 15)

    return (f"📊 *Analysis for {ticker}*\nBias: {bias}\nEntry: {current_price:.2f}\n\n🎯 TP1: {tp1:.2f} (+$350)\n🎯 TP 2/3: {tp_final:.2f}\n🛑 SL: {sl:.2f}\n\n💼 Contracts: 2 Minis")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    markup.add(telebot.types.KeyboardButton('MNQ (Nasdaq)'), telebot.types.KeyboardButton('MES (S&P500)'))
    bot.send_message(message.chat.id, "Select asset:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    ticker_map = {"MNQ (Nasdaq)": "NQ=F", "MES (S&P500)": "ES=F"}
    if message.text in ticker_map:
        bot.send_message(message.chat.id, analyze_market(ticker_map[message.text]), parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
