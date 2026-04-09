import telebot
from telebot import types
import sqlite3
import logging
from datetime import datetime
import threading
import time

# ================== الإعدادات الأساسية ==================
TOKEN = '8722515105:AAHhqRcLd1GtcQJtQDmoTGHjsm5Q4jtO5os'  # يفضل تغييره فوراً!
CHANNEL_ID = '@gold_whatsap'  # معرف القناة
OTHER_BOT_URL = 'http://t.me/StarsMakeBot?start=83jyHqQkM'  # بوت الربح
ADMIN_ID = 123456789  # ضع معرفك هنا (يمكن الحصول عليه من @userinfobot)

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

# ================== قاعدة البيانات ==================
def init_db():
    conn = sqlite3.connect('titan_signals.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  last_name TEXT,
                  registered_at TEXT,
                  last_active TEXT,
                  notifications INTEGER DEFAULT 1)''')
    c.execute('''CREATE TABLE IF NOT EXISTS signals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  type TEXT,
                  content TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

def add_user(user_id, username, first_name, last_name):
    conn = sqlite3.connect('titan_signals.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, registered_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, username, first_name, last_name, datetime.now().isoformat(), datetime.now().isoformat()))
    c.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def update_user_activity(user_id):
    conn = sqlite3.connect('titan_signals.db')
    c = conn.cursor()
    c.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (datetime.now().isoformat(), user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('titan_signals.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]

# ================== التحقق من الاشتراك ==================
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"خطأ في التحقق من العضوية: {e}")
        return False

# ================== لوحة التحكم الرئيسية ==================
def main_menu(chat_id, user_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📊 توصيات الذهب", callback_data='gold')
    btn2 = types.InlineKeyboardButton("📉 تحليل الفوركس", callback_data='forex')
    btn3 = types.InlineKeyboardButton("🚀 توصيات كريبتو", callback_data='crypto')
    btn4 = types.InlineKeyboardButton("🎓 دروس تعليمية", callback_data='learn')
    btn5 = types.InlineKeyboardButton("ℹ️ عن البوت", callback_data='about')
    btn6 = types.InlineKeyboardButton("📢 قناة التوصيات", url=f"https://t.me/{CHANNEL_ID[1:]}")
    btn7 = types.InlineKeyboardButton("⭐ بوت النجوم", url=OTHER_BOT_URL)
    markup.add(btn1, btn2, btn3, btn4)
    markup.add(btn5, btn6, btn7)
    
    text = f"✨ **مرحباً بك {message.from_user.first_name} في (TitanSignals)** ✨\n\n" \
           "🔹 **بوت التداول الاحترافي الأول عربياً**\n" \
           "🔹 نقدم لك توصيات وتحليلات دقيقة للذهب والفوركس والعملات الرقمية\n\n" \
           "📌 **اختر الخدمة التي تريدها من الأسفل:**"
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ================== رسالة الاشتراك الإجباري ==================
def subscription_required(chat_id, message_id=None):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_ch = types.InlineKeyboardButton("📢 القناة الرسمية", url=f"https://t.me/{CHANNEL_ID[1:]}")
    btn_bot = types.InlineKeyboardButton("⭐ بوت الربح", url=OTHER_BOT_URL)
    btn_check = types.InlineKeyboardButton("✅ تأكيد الاشتراك", callback_data='check_sub')
    markup.add(btn_ch, btn_bot)
    markup.add(btn_check)
    
    text = "⚠️ **تنبيه هام جداً!**\n\n" \
           "عذراً، لا يمكنك استخدام خدمات البوت إلا بعد الاشتراك في القناة الرسمية.\n" \
           "📌 اضغط على **القناة الرسمية** وانضم إليها، ثم اضغط **تأكيد الاشتراك**.\n\n" \
           "🎁 **بوت النجوم**: احصل على أرباح يومية من خلال بوت الربح التابع لنا."
    
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ================== أوامر البوت ==================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
    
    if check_sub(user_id):
        main_menu(message.chat.id, user_id)
    else:
        subscription_required(message.chat.id)

@bot.message_handler(commands=['help'])
def help_command(message):
    text = "📖 **قائمة المساعدة والأوامر المتاحة:**\n\n" \
           "/start - بدء البوت وعرض القائمة الرئيسية\n" \
           "/services - عرض الخدمات المتاحة\n" \
           "/about - معلومات عن البوت\n" \
           "/check - التحقق من الاشتراك يدوياً\n" \
           "/contact - التواصل مع الدعم\n\n" \
           "🔔 **ملاحظة:** جميع الخدمات متاحة فقط بعد الاشتراك في قناتنا."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['services'])
def services(message):
    if not check_sub(message.from_user.id):
        subscription_required(message.chat.id)
        return
    main_menu(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['about'])
def about(message):
    text = "🌟 **عن بوت TitanSignals** 🌟\n\n" \
           "✅ بوت احترافي متخصص في مجال التداول والأسواق المالية.\n" \
           "✅ نقدم توصيات يومية دقيقة للذهب، الفوركس، والعملات الرقمية.\n" \
           "✅ محتوى تعليمي مجاني لمساعدتك على فهم أسواق المال.\n" \
           "✅ يتم تحديث التوصيات بشكل لحظي عبر القناة الخاصة.\n\n" \
           "📢 **للتواصل مع المطور:** @TitanSupport\n" \
           "⭐ **شارك البوت مع أصدقائك:**\n" \
           f"https://t.me/{bot.get_me().username}"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['check'])
def check_subscription(message):
    user_id = message.from_user.id
    if check_sub(user_id):
        bot.send_message(message.chat.id, "✅ **تم التحقق!** أنت مشترك في القناة، يمكنك استخدام جميع الخدمات.", parse_mode="Markdown")
        main_menu(message.chat.id, user_id)
    else:
        subscription_required(message.chat.id)

@bot.message_handler(commands=['contact'])
def contact(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📞 تواصل مع الدعم", url="https://t.me/TitanSupport")
    markup.add(btn)
    bot.send_message(message.chat.id, "📧 **للاستفسارات أو المشاكل:**\nاضغط على الزر أدناه للتواصل مع فريق الدعم.", reply_markup=markup, parse_mode="Markdown")

# ================== الأزرار التفاعلية ==================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    update_user_activity(user_id)
    
    # تأكيد الاشتراك
    if call.data == 'check_sub':
        if check_sub(user_id):
            bot.answer_callback_query(call.id, "✅ تم التحقق! مرحباً بك في البوت.")
            # تعديل الرسالة الحالية لعرض القائمة الرئيسية
            main_menu(call.message.chat.id, user_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد! اشترك ثم اضغط تأكيد.", show_alert=True)
        return
    
    # التحقق من الاشتراك قبل أي خدمة أخرى
    if not check_sub(user_id):
        bot.answer_callback_query(call.id, "⚠️ يجب الاشتراك في القناة أولاً!", show_alert=True)
        subscription_required(call.message.chat.id, call.message.message_id)
        return
    
    # خدمة توصيات الذهب
    if call.data == 'gold':
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 الرجوع للقائمة", callback_data='main')
        btn_contact = types.InlineKeyboardButton("📩 طلب توصية خاصة", callback_data='special_signal')
        markup.add(btn_back, btn_contact)
        
        text = "🟡 **توصيات الذهب اليومية** 🟡\n\n" \
               "**تحليل السوق:**\n" \
               "• الذهب يتداول حالياً عند مستوى 2045$ للأونصة.\n" \
               "• المقاومة الرئيسية: 2060$ - الدعم: 2025$.\n" \
               "• الاتجاه العام: صاعد على المدى المتوسط.\n\n" \
               "📊 **التوصية:**\n" \
               "شراء من منطقة 2035-2040$ بهدف 2055$ ووقف خسارة 2020$.\n\n" \
               "⏰ **مدة الصفقة:** 4-8 ساعات.\n\n" \
               "⚠️ *ملاحظة: هذه التوصية لأغراض تعليمية، إدارة رأس المال ضرورية.*"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # خدمة تحليل الفوركس
    elif call.data == 'forex':
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 الرجوع للقائمة", callback_data='main')
        btn_pairs = types.InlineKeyboardButton("🔁 أزواج أخرى", callback_data='forex_pairs')
        markup.add(btn_back, btn_pairs)
        
        text = "📉 **تحليل زوج EUR/USD** 📉\n\n" \
               "• السعر الحالي: 1.0895\n" \
               "• المتوسطات المتحركة: إشارة شراء ضعيفة\n" \
               "• مؤشر RSI: 54 (محايد)\n" \
               "• الدعم: 1.0850 / المقاومة: 1.0950\n\n" \
               "**التوصية:** الانتظار حتى كسر 1.0900 ثم شراء بهدف 1.0960.\n\n" \
               "📌 **إدارة المخاطرة:** لا تخاطر بأكثر من 2% من رأس المال."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # خدمة الكريبتو
    elif call.data == 'crypto':
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("🔙 الرجوع للقائمة", callback_data='main')
        btn_signal = types.InlineKeyboardButton("📊 توصية سريعة", callback_data='crypto_signal')
        markup.add(btn_back, btn_signal)
        
        text = "🚀 **توصيات العملات الرقمية** 🚀\n\n" \
               "**بيتكوين (BTC):**\n" \
               "• السعر: 43,200$\n" \
               "• الحجم: مرتفع، اختراق قادم متوقع.\n" \
               "• الهدف القادم: 45,000$ ثم 48,000$.\n\n" \
               "**إيثريوم (ETH):**\n" \
               "• السعر: 2,280$\n" \
               "• دعم قوي عند 2,200$ - شراء مع وقف 2,150$.\n\n" \
               "⚠️ **تنبيه:** سوق الكريبتو شديد التقلب، استخدم أوامر وقف الخسارة."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # الدروس التعليمية
    elif call.data == 'learn':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("📘 أساسيات التداول", callback_data='lesson1')
        btn2 = types.InlineKeyboardButton("📙 التحليل الفني", callback_data='lesson2')
        btn3 = types.InlineKeyboardButton("📗 إدارة المخاطر", callback_data='lesson3')
        btn_back = types.InlineKeyboardButton("🔙 رجوع", callback_data='main')
        markup.add(btn1, btn2, btn3, btn_back)
        
        text = "🎓 **أكاديمية Titan التعليمية** 🎓\n\n" \
               "اختر الدرس الذي تريد قراءته الآن:\n" \
               "• **أساسيات التداول** - للمبتدئين\n" \
               "• **التحليل الفني** - الشموع والمؤشرات\n" \
               "• **إدارة المخاطر** - كيف تحمي رأس مالك"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # معلومات عن البوت
    elif call.data == 'about':
        about(call.message)
        # لا نعدل الرسالة، نرسل رسالة جديدة ونحذف القديمة اختيارياً
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # العودة للقائمة الرئيسية
    elif call.data == 'main':
        main_menu(call.message.chat.id, user_id, call.message.message_id)
    
    # الدروس التفصيلية
    elif call.data == 'lesson1':
        text = "📘 **أساسيات التداول للمبتدئين**\n\n" \
               "1️⃣ **ما هو التداول؟**\n" \
               "شراء وبيع الأصول المالية بهدف الربح من تقلبات الأسعار.\n\n" \
               "2️⃣ **أنواع الأسواق:**\n" \
               "- سوق الأسهم\n" \
               "- سوق الفوركس (العملات)\n" \
               "- السلع (الذهب، النفط)\n" \
               "- العملات الرقمية\n\n" \
               "3️⃣ **خطوات البدء:**\n" \
               "• تعلم الأساسيات\n" \
               "• اختيار وسيط موثوق\n" \
               "• البدء بحساب تجريبي\n" \
               "• إدارة المخاطر\n\n" \
               "🔹 **نصيحة:** لا تستثمر أموالاً لا يمكنك تحمل خسارتها."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data='learn'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == 'lesson2':
        text = "📙 **التحليل الفني - دليل سريع**\n\n" \
               "📊 **ما هو التحليل الفني؟**\n" \
               "دراسة تحركات الأسعار السابقة لتوقع المستقبل.\n\n" \
               "🕯️ **أنماط الشموع اليابانية:**\n" \
               "- شمعة المطرقة (Hammer): إشارة انعكاس صاعد\n" \
               "- شمعة النجم الثاقب (Shooting Star): إشارة هبوط\n\n" \
               "📈 **المؤشرات الشائعة:**\n" \
               "- المتوسطات المتحركة (MA)\n" \
               "- مؤشر القوة النسبية (RSI)\n" \
               "- مذبذب MACD\n\n" \
               "💡 **نصيحة:** اجمع بين أكثر من مؤشر لتأكيد الإشارات."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data='learn'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    elif call.data == 'lesson3':
        text = "📗 **إدارة المخاطر - أساس النجاح**\n\n" \
               "⚠️ **قواعد ذهبية:**\n" \
               "1. لا تخاطر بأكثر من 1-2% من رأس المال في الصفقة الواحدة.\n" \
               "2. استخدم أوامر وقف الخسارة (Stop Loss) دائماً.\n" \
               "3. نسبة المخاطرة إلى المكافأة لا تقل عن 1:2.\n" \
               "4. نوّع محفظتك ولا تضع كل الأموال في أصل واحد.\n" \
               "5. تحكم في عواطفك: الجشع والخوف أعداء التداول.\n\n" \
               "📐 **مثال:**\n" \
               "رأس المال: 1000$ - المخاطرة 2% = 20$ كحد أقصى للخسارة."
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data='learn'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    
    # طلب توصية خاصة
    elif call.data == 'special_signal':
        bot.answer_callback_query(call.id, "📩 سيتم التواصل معك قريباً عبر الدعم.", show_alert=True)
        # إرسال إشعار للمطور
        bot.send_message(ADMIN_ID, f"🔔 مستخدم {call.from_user.first_name} (ID: {user_id}) طلب توصية خاصة.")
    
    elif call.data == 'forex_pairs':
        text = "📉 **أزواج أخرى يمكن تحليلها:**\n\n" \
               "• GBP/USD - إشارة شراء محتملة\n" \
               "• USD/JPY - اتجاه هابط\n" \
               "• AUD/USD - تماسك جانبي\n\n" \
               "للاستفسار عن تحليل زوج معين، تواصل مع الدعم."
        bot.answer_callback_query(call.id, "سيتم إضافة المزيد قريباً", show_alert=True)
    
    elif call.data == 'crypto_signal':
        text = "⚡ **توصية سريعة على عملة Solana (SOL):**\n" \
               "• السعر الحالي: 98.5$\n" \
               "• نقطة الدخول: 97-99$\n" \
               "• الهدف الأول: 105$ - الثاني: 112$\n" \
               "• وقف الخسارة: 93$\n\n" \
               "⏳ صلاحية التوصية: 24 ساعة."
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# ================== الأوامر الإدارية (للمطور فقط) ==================
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ هذا الأمر للمطور فقط.")
        return
    text = message.text.replace('/broadcast', '').strip()
    if not text:
        bot.reply_to(message, "⚠️ الرجاء إدخال نص الإشعار بعد الأمر.\nمثال: /broadcast مرحباً جميعاً")
        return
    users = get_all_users()
    success = 0
    fail = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 **إشعار عام من الإدارة:**\n{text}", parse_mode="Markdown")
            success += 1
        except:
            fail += 1
        threading.Event().wait(0.05)  # تأخير بسيط لتجنب الحظر
    bot.reply_to(message, f"✅ تم الإرسال إلى {success} مستخدم.\n❌ فشل: {fail}")

@bot.message_handler(commands=['stats'])
def stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ هذا الأمر للمطور فقط.")
        return
    conn = sqlite3.connect('titan_signals.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE notifications = 1")
    notified = c.fetchone()[0]
    conn.close()
    bot.reply_to(message, f"📊 **إحصائيات البوت:**\n👥 إجمالي المستخدمين: {total}\n🔔 مفعّل الإشعارات: {notified}")

# ================== تشغيل البوت ==================
if __name__ == "__main__":
    print("🚀 تم تشغيل البوت بنجاح...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            logging.error(f"خطأ في الاتصال: {e}")
            time.sleep(5)
