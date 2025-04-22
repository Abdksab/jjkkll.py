import telebot
import requests
import os
import traceback
import sqlite3
from datetime import datetime
from telebot.types import (InputMediaPhoto, InputMediaVideo, 
                          InlineKeyboardMarkup, InlineKeyboardButton)

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

token = "8107738054:AAEjK8PS4PvzVaqgxXK4oXTAup1j1ICyEv4" #توكنك
admin = 7991664348  #ايديك

bot = telebot.TeleBot(token)
info = bot.get_me()
abuhamza = f"- @{info.username}"

headers = {
    "x-rapidapi-key": "18ed5e66a7msh9f4b2dcea69f606p1dc970jsnd09db62aaec1",
    "x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
    "Content-Type": "application/json"
}

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

def init_db():
    conn = sqlite3.connect('abuhamza.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY, 
                      username TEXT,
                      first_name TEXT,
                      last_name TEXT,
                      join_date TIMESTAMP,
                      is_banned BOOLEAN DEFAULT 0)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      date DATE UNIQUE,
                      new_users INTEGER DEFAULT 0)''')
    
    conn.commit()
    conn.close()

init_db()

def expand_url(short_url):
    try:
        response = requests.head(short_url, allow_redirects=True)
        return response.url
    except:
        return None

def fetch_media_direct(url):
    response = requests.post(
        "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink",
        json={"url": url},
        headers=headers
    )
    return response.json()

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def register_user(user):
    conn = sqlite3.connect('abuhamza.sqlite3')
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user.id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                      (user.id, user.username, user.first_name, 
                       user.last_name, datetime.now(), 0))
        
        cursor.execute("SELECT * FROM stats WHERE date=?", (today,))
        if cursor.fetchone():
            cursor.execute("UPDATE stats SET new_users=new_users+1 WHERE date=?", (today,))
        else:
            cursor.execute("INSERT INTO stats (date, new_users) VALUES (?, 1)", (today,))
    
    conn.commit()
    conn.close()

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

def is_banned(user_id):
    conn = sqlite3.connect('abuhamza.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == admin:  
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("حظر", callback_data="ban_user"),
            InlineKeyboardButton("رفع حظر", callback_data="unban_user")
        )
        markup.row(
            InlineKeyboardButton("اذاعة", callback_data="broadcast")
        )
        markup.row(
            InlineKeyboardButton("الاحصائيات", callback_data="user_stats")
        )
        bot.send_message(message.chat.id, "مرحبا بك عزيزي الادمن في لوحة التحكم الخاصة بك \n\n• تحكم في بوتك من الازرار الموجودة بالاسفل", reply_markup=markup)

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    if is_banned(call.from_user.id):
        bot.send_message(call.chat.id, "⚠️ تم حظرك من استخدام البوت")
        return

    if call.data == "ban_user":
        msg = bot.send_message(call.message.chat.id, "أرسل آيدي المستخدم الذي تريد حظره")
        bot.register_next_step_handler(msg, process_ban)
    elif call.data == "unban_user":
        msg = bot.send_message(call.message.chat.id, "أرسل آيدي المستخدم الذي تريد رفع الحظر عنه")
        bot.register_next_step_handler(msg, process_unban)
    elif call.data == "broadcast":
        msg = bot.send_message(call.message.chat.id, "أرسل الرسالة التي تريد إرسالها للجميع")
        bot.register_next_step_handler(msg, process_broadcast)
    elif call.data == "user_stats":
        show_user_stats(call.message)

    elif call.data == "back":
        text = """*أهلاً بك في بوت التحميل*

_مع هذا البوت يمكنك تحميل الفيديوهات والصور من جميع المنصات بصيغ متعددة._

📌 *أرسل الرابط الآن للبدء*"""

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("حول البوت ❗", callback_data="about")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="Markdown", reply_markup=keyboard)

    elif call.data == "about":
        text = """‌\n
🪩*المنصات المدعومة* :

*1- يوتيوب
2- انستقرام
3- فيسبوك
4- تويتر
5- سناب شات
6- تيك توك
7- بينترست*

*يدعم تحميل الصور والفيديوهات* ✅

       --------------------------------------------------
       --------------------------------------------------

_طريقة الاستخدام_  :

📌 *فقط أرسل رابط المحتوى الذي تريد تحميله الى البوت*"""

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("🔙 رجوع", callback_data="back")
        )
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="Markdown", reply_markup=keyboard)

def process_ban(message):
    try:
        user_id = int(message.text)
        conn = sqlite3.connect('abuhamza.sqlite3')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"تم حظر المستخدم {user_id} بنجاح.")
    except:
        bot.send_message(message.chat.id, "تأكد من إدخال آيدي صحيح.")

def process_unban(message):
    try:
        user_id = int(message.text)
        conn = sqlite3.connect('abuhamza.sqlite3')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, f"تم رفع الحظر عن المستخدم {user_id} بنجاح.")
    except:
        bot.send_message(message.chat.id, "تأكد من إدخال آيدي صحيح.")

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

def process_broadcast(message):
    conn = sqlite3.connect('abuhamza.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_banned=0")
    users = cursor.fetchall()
    conn.close()
    
    for user in users:
        try:
            bot.send_message(user[0], message.text)
        except:
            pass
    
    bot.send_message(message.chat.id, f"تم إرسال الرسالة إلى {len(users)} مستخدم.")

def show_user_stats(message):
    conn = sqlite3.connect('abuhamza.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned=0")
    total_users = cursor.fetchone()[0]
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT SUM(new_users) FROM stats WHERE date=?", (today,))
    today_users = cursor.fetchone()[0] or 0
    
    month = datetime.now().strftime('%Y-%m')
    cursor.execute("SELECT SUM(new_users) FROM stats WHERE strftime('%Y-%m', date)=?", (month,))
    month_users = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT username, first_name, join_date FROM users WHERE is_banned=0 ORDER BY join_date DESC LIMIT 5")
    last_users = cursor.fetchall()
    
    conn.close()
    
    stats_text = f"""
*إحصائيات المستخدمين*

👥- *إجمالي المستخدمين* : {total_users}

📅- *اليوم* : {today_users}
🗓️- *هذا الشهر* : {month_users}

      ----------------------------------------------
               ----------------------------------------------

_آخر 5 مستخدمين انضمو للبوت_
"""
    for user in last_users:
        username = f"@{user[0]}" if user[0] else "بدون يوزر"
        stats_text += f"\n-[ {username} ~ {user[1]} ]"
    
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ تم حظرك من استخدام البوت")
        return
    
    register_user(message.from_user)
    
    welcome_text = f"""
*أهلاً بك في بوت التحميل*

_مع هذا البوت يمكنك تحميل الفيديوهات والصور من جميع المنصات بصيغ متعددة._

📌 *أرسل الرابط الآن للبدء*
المطور : @F_Q_2"""

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("حول البوت ❗", callback_data="about")
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=keyboard, disable_web_page_preview=True)

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def url(message):
    chat_id = message.chat.id
    url = message.text

    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ تم حظرك من استخدام البوت")
        return

    wait_msg = bot.send_message(chat_id, "*جاري فحص الاتصال بالخادم* 🪩", parse_mode="Markdown").message_id

    try:
        api_url = f"http://145.223.80.56:5003/get?q={url}"
        res = requests.get(api_url).json()

        if 'Download link' not in res:
            bot.delete_message(chat_id, wait_msg)
            handle_url(message)

        download_url = res['Download link']
        filename = os.path.join("downloads", os.path.basename(url) + ".mp4")

        with open(filename, 'wb') as f:
            f.write(requests.get(download_url).content)

        if os.path.getsize(filename) == 0:
            bot.edit_message_text("❌- الملف فارغ", chat_id, wait_msg)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("قناة التحديثات", url="https://t.me/FileeCode"))

            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video, caption=f"{abuhamza}", supports_streaming=True, reply_markup=keyboard)

        bot.delete_message(chat_id, wait_msg)
        os.remove(filename)

    except Exception as e:
        print(e)

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

if not os.path.exists("downloads"):
    os.makedirs("downloads")
    
def handle_url(message):
    chat_id = message.chat.id
    msg_id = message.message_id

    if is_banned(message.from_user.id):
        bot.send_message(message.chat.id, "⚠️ تم حظرك من استخدام البوت")
        return
    
    register_user(message.from_user)
    
    short_url = message.text.strip()
    bot.send_chat_action(message.chat.id, "upload_document")

    status_msg = bot.send_message(message.chat.id, "• *جاري فحص الرابط* ♻️", parse_mode="Markdown")

    full_url = expand_url(short_url)
    if not full_url:
        bot.send_message(message.chat.id, "تعذر فك اختصار الرابط.")
        return

    try:       
        bot.send_chat_action(message.chat.id, "upload_document")
        bot.edit_message_text(
            "• *جاري الاتصال بالخادم* ⏳", 
            parse_mode="Markdown",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )

        data = fetch_media_direct(full_url)
        media_list = data.get("medias", [])

        if not media_list:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                text=f"لم يتم العثور على وسائط.\n\nالاستجابة:\n```{data}```",
                parse_mode="Markdown"
            )
            return

        bot.send_chat_action(message.chat.id, "upload_document")
        bot.edit_message_text(
            "• *جاري استخراج الصور* 🛠",
            parse_mode="Markdown",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )

        photo_group = []
        audio_files = []

        for i, media in enumerate(media_list):
            url = media.get("url")
            type_ = media.get("type", "unknown")
            ext = media.get("extension", "")
            filename = f"media_{i}.{ext}"

            download_file(url, filename)

            if type_ == "image":
                photo_group.append(InputMediaPhoto(open(filename, 'rb')))
            elif type_ == "audio":
                audio_files.append(filename)

        bot.send_chat_action(message.chat.id, "upload_document")
        bot.edit_message_text(
            "• *جاري ارسال الصور* 🚀",
            parse_mode="Markdown",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("قناة التحديثات", url=f"https://t.me/FileeCode"))

        if photo_group:
            photo_group[0].caption = f"{abuhamza}"
            bot.send_media_group(message.chat.id, photo_group)

        for audio in audio_files:
            bot.send_audio(
                message.chat.id,
                open(audio, 'rb'),
                caption=abuhamza,
                reply_markup=markup
            )

        bot.delete_message(message.chat.id, status_msg.message_id)

        for i in range(len(media_list)):
            try:
                os.remove(f"media_{i}.{media_list[i].get('extension')}")
            except:
                pass

    except Exception as e:
        err = traceback.format_exc()
        bot.send_message(message.chat.id, f"حدث خطأ:\n```\n{err}\n```", parse_mode="Markdown")

#البوت كتابة المبرمج ابو حمزه

#يوزر المبرمج @FFJFF5

#قناة المبرمج @FileeCode

bot.infinity_polling()