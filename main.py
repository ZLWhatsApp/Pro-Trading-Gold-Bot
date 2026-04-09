import telebot
from telebot import types

TOKEN = '8722515105:AAHhqRcLd1GtcQJtQDmoTGHjsm5Q4jtO5os'
bot = telebot.TeleBot(TOKEN)

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
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("📊 توصيات الذهب", callback_data='gold')
        btn2 = types.InlineKeyboardButton("📉 تحليل الفوركس", callback_data='forex')
        btn3 = types.InlineKeyboardButton("🚀 توصيات كريبتو", callback_data='crypto')
        btn4 = types.InlineKeyboardButton("🎓 دروس تعليمية", callback_data='learn')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, f"مرحباً بك {message.from_user.first_name} في ( TitanSignals ) بوت التداول الاحترافي! 💎\nاختر خدمتك من الأسفل:", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_ch = types.InlineKeyboardButton("1️⃣ اشترك في القناة", url=f"https://t.me/{CHANNEL_ID[1:]}")
        btn_bot = types.InlineKeyboardButton("2️⃣ اشترك في البوت الداعم", url=OTHER_BOT_URL)
        btn_check = types.InlineKeyboardButton("✅ تم الاشتراك، تفعيل البوت", callback_data='check')
        markup.add(btn_ch, btn_bot, btn_check)
        bot.send_message(message.chat.id, "⚠️ **تنبيه هام!**\nعذراً عزيزي، يجب عليك الاشتراك أولاً في القنوات الرسمية لاستخدام خدمات البوت:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'check':
        if check_sub(call.from_user.id):
            bot.delete_message(call.message.chat.id, call.message.message_id)
            start(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد!", show_alert=True)
    
    elif call.data == 'gold':
        bot.send_message(call.message.chat.id, "🟡 **توصيات الذهب اليومية:**\nنحن نراقب السوق حالياً... سيتم النشر فور توفر فرصة قوية. 📈", parse_mode="Markdown")
    
    elif call.data == 'forex':
        bot.send_message(call.message.chat.id, "📉 **تحليل الفوركس:**\nيتم الآن تحديث التحليلات الفنية لأهم العملات. ترقبونا!", parse_mode="Markdown")
        
    elif call.data == 'crypto':
        bot.send_message(call.message.chat.id, "🚀 **توصيات كريبتو:**\nأفضل العملات الرقمية للاستثمار تجدها هنا قريباً جداً. 🔥", parse_mode="Markdown")
        
    elif call.data == 'learn':
        bot.send_message(call.message.chat.id, "🎓 **أكاديمية التعليم:**\nقريباً سنطلق شروحات حصرية من الصفر للاحتراف. تابعنا!", parse_mode="Markdown")

bot.infinity_polling()
