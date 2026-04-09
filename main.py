import telebot
from telebot import types

# التوكن الخاص بك الذي أرسلته
TOKEN = '8722515105:AAHhqRcLd1GtcQJtQDmoTGHjsm5Q4jtO5os'
bot = telebot.TeleBot(TOKEN)

# الروابط المطلوبة
CHANNEL_ID = '@gold_whatsap'
OTHER_BOT_URL = 'http://t.me/StarsMakeBot?start=83jyHqQkM'

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        # القائمة الرئيسية الاحترافية
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📊 توصيات الذهب", callback_data='gold')
        btn2 = types.InlineKeyboardButton("📉 تحليل الفوركس", callback_data='forex')
        btn3 = types.InlineKeyboardButton("🚀 توصيات كريبتو", callback_data='crypto')
        btn4 = types.InlineKeyboardButton("🎓 دروس تعليمية", callback_data='learn')
        markup.add(btn1, btn2, btn3, btn4)
        
        bot.send_message(message.chat.id, f"مرحباً بك {message.from_user.first_name} في بوت التداول الاحترافي! 💎\nاختر خدمتك من الأسفل:", reply_markup=markup)
    else:
        # رسالة الاشتراك الإجباري
        markup = types.InlineKeyboardMarkup()
        btn_ch = types.InlineKeyboardButton("1️⃣ اشترك في القناة", url=f"https://t.me/{CHANNEL_ID[1:]}")
        btn_bot = types.InlineKeyboardButton("2️⃣ اشترك في البوت الداعم", url=OTHER_BOT_URL)
        btn_check = types.InlineKeyboardButton("✅ تم الاشتراك، تفعيل البوت", callback_data='check')
        markup.add(btn_ch)
        markup.add(btn_bot)
        markup.add(btn_check)
        
        bot.send_message(message.chat.id, "⚠️ يجب عليك الاشتراك في القناة والبوت لاستخدام خدماتنا:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'check':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    elif call.data == 'gold':
        bot.answer_callback_query(call.id, "جاري تجهيز صفقات الذهب الحصرية... 🔥")

bot.infinity_polling()
