import telebot
import yfinance as yf
from flask import Flask
from threading import Thread

# CONFIGURATION
TOKEN = "8760207100:AAHkwFEV2WBEaYOhlcaTsqvYQtJ5LK-GF3I"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home(): return "Bot is alive!"

def run(): app.run(host='0.0.0.0', port=8080)

def analyze_market(ticker):
    try:
        # Pulling 1 day of 15m data for a better trend view
        df = yf.download(ticker, interval="15m", period="1d")
        if df.empty: return "Market data currently unavailable. Try again in a minute."
        
        current_price = float(df['Close'].iloc[-1])
        open_price = float(df['Open'].iloc[0])
        
        # Super simple bias: Is today green or red?
        bias = "BULLISH" if current_price > open_price else "BEARISH"
        
        # $650 Plan Math (approx 32.5 points on NQ)
        if bias == "BULLISH":
            tp1, tp_final, sl = current_price + 17.5, current_price + 32.5, current_price - 20
        else:
            tp1, tp_final, sl = current_price - 17.5, current_price - 32.5, current_price + 20

        return (f"📊 *Analysis for {ticker}*\n"
                f"Bias: {bias}\n"
                f"Entry: {current_price:.2f}\n\n"
                f"🎯 TP1: {tp1:.2f} (+$350)\n"
                f"🎯 TP 2/3: {tp_final:.2f} (+$300)\n"
                f"🛑 SL: {sl:.2f}\n\n"
                f"💼 Contracts: 2 Minis")
    except Exception as e:
        return f"Error fetching data: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(telebot.types.KeyboardButton('MNQ (Nasdaq)'), telebot.types.KeyboardButton('MES (S&P500)'))
    bot.send_message(message.chat.id, "Select asset to analyze:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    ticker_map = {"MNQ (Nasdaq)": "NQ=F", "MES (S&P500)": "ES=F"}
    if message.text in ticker_map:
        bot.send_message(message.chat.id, "Analyzing live markets... 📈")
        result = analyze_market(ticker_map[message.text])
        bot.send_message(message.chat.id, result, parse_mode="Markdown")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()
