import telebot
import requests
import json
import os
import time
from telebot import types

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_KEY = os.environ.get("API_KEY")
ADMIN_ID = 6788585905

bot = telebot.TeleBot(BOT_TOKEN)

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_user(user_id, referred_by=None):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"referrals": 0, "referred_by": str(referred_by)}
        if referred_by and str(referred_by) in users:
            users[str(referred_by)]["referrals"] += 1
        with open("users.json", "w") as f:
            json.dump(users, f)

def get_total_users():
    users = load_users()
    return len(users)

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    referred_by = None
    if len(args) > 1:
        try:
            referred_by = int(args[1])
        except:
            pass
    save_user(message.chat.id, referred_by)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💱 Convert Currency", callback_data="help_currency"),
        types.InlineKeyboardButton("📈 Crypto Rates", callback_data="help_crypto"),
        types.InlineKeyboardButton("🏦 Top Rates", callback_data="top_rates"),
        types.InlineKeyboardButton("👥 Refer Friends", callback_data="refer"),
        types.InlineKeyboardButton("📢 Share Bot", callback_data="share"),
        types.InlineKeyboardButton("💬 Feedback", callback_data="feedback")
    )
    bot.reply_to(message,
        "👋 Welcome to *Currency & Crypto Bot*!\n\n"
        "I can help you:\n"
        "💱 Convert any currency\n"
        "📈 Check crypto prices\n"
        "🏦 See live exchange rates\n"
        "👥 Earn rewards by referring friends\n\n"
        "Choose an option below or type:\n"
        "`100 USD to EUR`",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message,
        "📖 *Available Commands:*\n\n"
        "💱 Currency: `100 USD to EUR`\n"
        "📈 Crypto: `/crypto BTC`\n"
        "🏦 Top Rates: `/rates`\n"
        "👥 Referrals: `/referral`\n"
        "📢 Share: `/share`\n"
        "💬 Feedback: `/feedback your message`\n\n"
        "💡 Crypto: BTC ETH USDT BNB SOL XRP DOGE",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['crypto'])
def crypto(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Example: `/crypto BTC`", parse_mode="Markdown")
        return
    symbol = args[1].upper()
    coin_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "tether",
        "BNB": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin"
    }
    if symbol not in coin_map:
        bot.reply_to(message, "❌ Supported coins: BTC ETH USDT BNB SOL XRP ADA DOGE")
        return
    try:
        coin_id = coin_map[symbol]
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url).json()
        price = response[coin_id]["usd"]
        change = response[coin_id]["usd_24h_change"]
        emoji = "📈" if change > 0 else "📉"
        bot.reply_to(message,
            f"🪙 *{symbol} Price*\n\n"
            f"💵 Price: `${price:,.4f}`\n"
            f"{emoji} 24h Change: `{change:.2f}%`\n\n"
            f"_USDT BEP20 = USDT = ~$1.00_",
            parse_mode="Markdown"
        )
    except:
        bot.reply_to(message, "❌ Could not fetch price. Try again later.")

@bot.message_handler(commands=['rates'])
def rates(message):
    try:
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
        response = requests.get(url).json()
        r = response["conversion_rates"]
        msg = "🏦 *Live Rates (1 USD)*\n\n"
        for c in ["EUR", "GBP", "NGN", "GHS", "KES", "ZAR", "CAD", "AUD", "JPY", "INR"]:
            if c in r:
                msg += f"`{c}`: {r[c]:,.2f}\n"
        bot.reply_to(message, msg, parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Could not fetch rates. Try again later.")

@bot.message_handler(commands=['referral'])
def referral(message):
    users = load_users()
    user_data = users.get(str(message.chat.id), {"referrals": 0})
    ref_count = user_data.get("referrals", 0)
    ref_link = f"https://t.me/mycurrency123_bot?start={message.chat.id}"
    bot.reply_to(message,
        f"👥 *Your Referral Stats*\n\n"
        f"🔗 Your link:\n`{ref_link}`\n\n"
        f"✅ People referred: *{ref_count}*\n\n"
        f"Share and grow! 🚀",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['share'])
def share(message):
    bot.reply_to(message,
        "📢 *Share this bot!*\n\n"
        "👉 https://t.me/mycurrency123_bot\n\n"
        "Help friends convert currencies and track crypto! 🚀",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['feedback'])
def feedback(message):
    text = message.text.replace('/feedback', '').strip()
    if not text:
        bot.reply_to(message, "Example: `/feedback The bot is great!`", parse_mode="Markdown")
        return
    bot.send_message(ADMIN_ID, f"💬 *Feedback from* `{message.chat.id}`:\n\n{text}", parse_mode="Markdown")
    bot.reply_to(message, "✅ Thanks for your feedback!")

@bot.message_handler(commands=['users'])
def count_users(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, f"👥 Total users: *{get_total_users()}*", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Not authorized!")

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id == ADMIN_ID:
        text = message.text.replace('/broadcast ', '').strip()
        users = load_users()
        success = 0
        for user_id in users.keys():
            try:
                bot.send_message(int(user_id), text)
                success += 1
            except:
                pass
        bot.reply_to(message, f"✅ Sent to {success} users!")
    else:
        bot.reply_to(message, "❌ Not authorized!")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "help_currency":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "💱 Type:\n`100 USD to EUR`\n`50 GBP to NGN`", parse_mode="Markdown")
    elif call.data == "help_crypto":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📈 Type:\n`/crypto BTC`\n`/crypto USDT`", parse_mode="Markdown")
    elif call.data == "top_rates":
        bot.answer_callback_query(call.id)
        rates(call.message)
    elif call.data == "refer":
        bot.answer_callback_query(call.id)
        referral(call.message)
    elif call.data == "share":
        bot.answer_callback_query(call.id)
        share(call.message)
    elif call.data == "feedback":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Send:\n`/feedback your message here`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def convert(message):
    save_user(message.chat.id)
    try:
        parts = message.text.upper().split()
        amount = float(parts[0])
        from_currency = parts[1]
        to_currency = parts[3]
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}"
        response = requests.get(url).json()
        if response["result"] == "success":
            result = response["conversion_result"]
            bot.reply_to(message, f"💱 *{amount} {from_currency} = {result:,.2f} {to_currency}*", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Invalid currencies.\nTry: `100 USD to EUR`", parse_mode="Markdown")
    except:
        bot.reply_to(message, "⚠️ Format: `100 USD to EUR`", parse_mode="Markdown")

while True:
    try:
        bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
