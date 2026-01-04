# 🚀 Ultra Gelişmiş Telegram Bot (pyTelegramBotAPI) - FULL DETAYLI SÜRÜM
import re
import time
import json
import os
import threading
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

# ==================== YAPILANDIRMA ====================
BOT_TOKEN = "8500439268:AAFYGuVk9sJjc0poBFztlrlrX49j3cczFFY"
ADMIN_ID = 5633974834  # Senin Telegram ID'n

# Bot Başlangıç Zamanı
bot_start_time = time.time()

# Logging (Loglama Sistemi)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# ==================== VERİ SAKLAMASI (DATA MANAGEMENT) ====================
DATA_FILE = "bot_data.json"

class DataManager:
    def __init__(self):
        self.data = {
            "afk_users": {},
            "group_settings": {},
            "user_stats": {},
            "warnings": {},
            "banned_words": [],
            "whitelisted_users": []
        }
        self.lock = threading.Lock()
        self.load_data()
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info("✅ Data uğurla yükləndi")
            except Exception as e:
                logger.error(f"❌ Data yüklənmə xətası: {e}")
                # Yedek al ve sıfırla
                if os.path.exists(DATA_FILE):
                    os.rename(DATA_FILE, f"{DATA_FILE}.bak_{int(time.time())}")
    
    def save_data(self):
        with self.lock:
            try:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"❌ Data saxlama xətası: {e}")
    
    def auto_save(self):
        """Her 5 dəqiqədə bir avtomatik saxla"""
        while True:
            time.sleep(300)
            self.save_data()

data_manager = DataManager()

# Arka planda otomatik kayıt thread'i
save_thread = threading.Thread(target=data_manager.auto_save, daemon=True)
save_thread.start()

# ==================== SÖYÜŞ VE KÜFÜR FİLTRESİ ====================
SWEAR_WORDS = [
    "sik", "göt", "qəhbə", "qehbe", "peyser", "anani", "anavi", 
    "şərəfsiz", "qandon", "ble", "varyoxunu", "soxum", "blə", 
    "pedafil", "trans", "bacini", "gij", "gic", "pox", "qələt", 
    "sikim", "sər", "blet", "blət", "amcıq", "mənə", "oç", "şərzə"
]

# ==================== SPAM KORUMASI ====================
spam_tracker = defaultdict(list)
SPAM_THRESHOLD = 5  # 10 saniyədə 5 mesaj
SPAM_TIME_WINDOW = 10

def is_spam(user_id):
    """Spam kontrol fonksiyonu"""
    now = time.time()
    # Süresi dolmuş kayıtları temizle
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if now - t < SPAM_TIME_WINDOW]
    spam_tracker[user_id].append(now)
    return len(spam_tracker[user_id]) > SPAM_THRESHOLD

# ==================== YARDIMCI FONKSİYONLAR ====================
def get_group_settings(chat_id):
    """Qrup parametrlərini çək və ya oluştur"""
    chat_id_str = str(chat_id)
    if chat_id_str not in data_manager.data["group_settings"]:
        data_manager.data["group_settings"][chat_id_str] = {
            "anti_link": True,
            "anti_swear": True,
            "anti_spam": True,
            "welcome": True,
            "afk_notify": True,
            "warn_limit": 3
        }
        data_manager.save_data()
    return data_manager.data["group_settings"][chat_id_str]

def is_admin(chat_id, user_id):
    """İstifadəçinin admin olub-olmadığını yoxla"""
    try:
        if user_id == ADMIN_ID: return True
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except:
        return False

# ==================== /START KOMANDASI ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user.first_name
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("✅ Məni qrupuna əlavə et", url=f"https://t.me/{bot.get_me().username}?startgroup=true"),
        InlineKeyboardButton("📚 Komandalar", callback_data="commands"),
        InlineKeyboardButton("⚙️ Parametrlər", callback_data="settings_main"),
        InlineKeyboardButton("📊 Statistika", callback_data="stats_info"),
        InlineKeyboardButton("🧑‍💻 Sahibim", url="https://t.me/Ragimovxh")
    )
    
    start_text = f"""✧══════════•❁❀❁•══════════✧
▻ <b>Salam {user}</b> 👋
▻ Mənim adım <b>ɴᴏ ʟɪɴᴋ 🙎</b>
▻ Mən <b>Ultra Güclü</b> Anti-Spam botuyam 🤖

<b>🎯 Funksiyalarım:</b>
┣ 🚫 Anti-Link Sistemi
┣ 🤬 Söyüş Filtrləməsi  
┣ ⚡ Anti-Spam Mühafizəsi
┣ 😴 AFK Sistemi
┣ 👋 Xoşgəlmə Mesajları
┣ ⚠️ Xəbərdarlıq Sistemi
┣ 📊 Statistika İzləmə
┗ 🔧 Qrup İdarəetməsi

<i>✨ Versiya: 2.0 Ultra</i>
✧══════════•❁❀❁•══════════✧"""
    
    # Resim URL
    photo_url = "https://freesorgupanel.neocities.org/IMG_20251230_164458_274.jpg"
    
    try:
        bot.send_photo(
            message.chat.id,
            photo=photo_url,
            caption=start_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Start komutunda hata: {e}")
        # Resim gitmezse yazı olarak at (Fallback)
        bot.send_message(message.chat.id, start_text, reply_markup=markup, parse_mode='HTML')

# ==================== GENEL BİLGİ KOMUTLARI ====================
@bot.message_handler(commands=['info'])
def info_command(message):
    user = message.from_user.first_name
    uptime = time.time() - bot_start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    info_text = f"""╔═══════════════════════════╗
║  ℹ️ <b>BOT MƏLUMATI</b>
╠═══════════════════════════╣
║ 
║ 🤖 Bot: <b>ɴᴏ ʟɪɴᴋ</b>
║ 👤 İstifadəçi: <b>{user}</b>
║ ⏱️ İş vaxtı: <b>{hours}s {minutes}dəq</b>
║ 🐍 Python: <b>3.10+</b>
║ 📚 Library: <b>pyTelegramBotAPI</b>
║ 👨‍💻 Developer: <b>@Ragimovxh</b>
║ 🌟 Version: <b>2.0 Ultra</b>
╚═══════════════════════════╝"""
    
    bot.reply_to(message, info_text, parse_mode='HTML')

@bot.message_handler(commands=['alive'])
def alive_command(message):
    start = time.time()
    msg = bot.reply_to(message, "🏓 Ping yoxlanır...")
    ping = int((time.time() - start) * 1000)
    
    uptime = time.time() - bot_start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    alive_text = f"""╔═══════════════════════════╗
║  ✅ <b>BOT AKTİVDİR</b>
╠═══════════════════════════╣
║
║ 🏓 <b>PING:</b> {ping} ms
║ ⏱️ <b>İŞ VAXI:</b> {hours}s {minutes}dəq
║ <b>📊 BOT STATİSTİKASI:</b>
║ ┣ 💬 Mesajlar: <code>{len(spam_tracker)}</code>
║ ┣ 👥 Qruplar: <code>{len(data_manager.data['group_settings'])}</code>
║ ┗ 😴 AFK: <code>{len(data_manager.data['afk_users'])}</code>
╚═══════════════════════════╝"""
    
    # Burada edit_message_text güvenlidir çünkü önceki mesaj yazıdır.
    bot.edit_message_text(
        alive_text,
        message.chat.id,
        msg.message_id,
        parse_mode='HTML'
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)
    
    total_messages = len(spam_tracker)
    afk_count = len(data_manager.data["afk_users"])
    
    if message.chat.type in ['group', 'supergroup']:
        user_key = f"{chat_id}_{user_id}"
        warns = data_manager.data["warnings"].get(user_key, 0)
        
        stats_text = f"""╔═══════════════════════════╗
║  📊 <b>ŞƏXSİ STATİSTİKA</b>
╠═══════════════════════════╣
║
║ 👤 İstifadəçi: <b>{message.from_user.first_name}</b>
║ 🆔 ID: <code>{message.from_user.id}</code>
║ ⚠️ Xəbərdarlıqlar: <code>{warns}</code>
║ 
║ <b>📈 QRUP STATİSTİKASI:</b>
║ 💬 Ümumi mesajlar: <code>{total_messages}</code>
║ 😴 AFK istifadəçilər: <code>{afk_count}</code>
╚═══════════════════════════╝"""
    else:
        stats_text = f"""╔═══════════════════════════╗
║  📊 <b>GLOBAL STATİSTİKA</b>
╠═══════════════════════════╣
║ 💬 Ümumi mesajlar: <code>{total_messages}</code>
║ 😴 AFK istifadəçilər: <code>{afk_count}</code>
║ 🏠 Qruplar: <code>{len(data_manager.data['group_settings'])}</code>
╚═══════════════════════════╝"""
    
    bot.reply_to(message, stats_text, parse_mode='HTML')

# ==================== AFK SİSTEMİ ====================
@bot.message_handler(commands=['afk'])
def set_afk(message):
    user_id = str(message.from_user.id)
    reason = message.text[5:].strip() if len(message.text) > 5 else "Səbəb göstərilməyib"
    
    data_manager.data["afk_users"][user_id] = {
        "reason": reason,
        "time": time.time(),
        "name": message.from_user.first_name,
        "username": message.from_user.username
    }
    data_manager.save_data()
    
    bot.reply_to(
        message, 
        f"😴 <b>{message.from_user.first_name}</b> AFK rejiminə keçdi\n"
        f"📝 Səbəb: <i>{reason}</i>",
        parse_mode='HTML'
    )

# ==================== YÖNETİCİ VE MODERASYON KOMUTLARI ====================

@bot.message_handler(commands=['settings'])
def settings_command(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ Bu komanda yalnız qruplarda işləyir!")
        return
    
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Bu komanda yalnız adminlər üçündür!")
        return
    
    settings = get_group_settings(message.chat.id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{'✅' if settings['anti_link'] else '❌'} Anti-Link", callback_data=f"toggle_anti_link_{message.chat.id}"),
        InlineKeyboardButton(f"{'✅' if settings['anti_swear'] else '❌'} Anti-Swear", callback_data=f"toggle_anti_swear_{message.chat.id}"),
        InlineKeyboardButton(f"{'✅' if settings['anti_spam'] else '❌'} Anti-Spam", callback_data=f"toggle_anti_spam_{message.chat.id}"),
        InlineKeyboardButton(f"{'✅' if settings['welcome'] else '❌'} Xoşgəlmə", callback_data=f"toggle_welcome_{message.chat.id}")
    )
    
    settings_text = f"""╔═══════════════════════════╗
║  ⚙️ <b>QRUP PARAMETRLƏRİ</b>
╠═══════════════════════════╣
║
║ 🚫 Anti-Link: <code>{'AKTİV' if settings['anti_link'] else 'DEAKTİV'}</code>
║ 🤬 Anti-Swear: <code>{'AKTİV' if settings['anti_swear'] else 'DEAKTİV'}</code>
║ ⚡ Anti-Spam: <code>{'AKTİV' if settings['anti_spam'] else 'DEAKTİV'}</code>
║ 👋 Xoşgəlmə: <code>{'AKTİV' if settings['welcome'] else 'DEAKTİV'}</code>
║ ⚠️ Xəbərdarlıq limiti: <code>{settings['warn_limit']}</code>
╚═══════════════════════════╝"""
    
    bot.send_message(message.chat.id, settings_text, reply_markup=markup, parse_mode='HTML')

# --- Ban Sistemi ---
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Yalnız adminlər!")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ban etmək üçün mesaja cavab verin!")
        return
    
    target = message.reply_to_message.from_user
    reason = message.text[5:].strip() if len(message.text) > 5 else "Səbəb yoxdur"
    
    try:
        bot.ban_chat_member(message.chat.id, target.id)
        bot.send_message(
            message.chat.id, 
            f"⛔ <b>{target.first_name}</b> qadağan edildi!\n📝 Səbəb: {reason}\n👮 Admin: {message.from_user.first_name}", 
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {str(e)}")

# --- Unban Sistemi ---
@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    target = message.reply_to_message.from_user
    try:
        bot.unban_chat_member(message.chat.id, target.id)
        bot.send_message(message.chat.id, f"✅ <b>{target.first_name}</b> banı açıldı!", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {str(e)}")

# --- Kick Sistemi (Ban + Unban) ---
@bot.message_handler(commands=['kick'])
def kick_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    target = message.reply_to_message.from_user
    try:
        bot.unban_chat_member(message.chat.id, target.id) # Unban üye zaten gruptaysa atar
        bot.send_message(message.chat.id, f"👢 <b>{target.first_name}</b> qrupdan atıldı!", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {str(e)}")

# --- Mute Sistemi ---
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Yalnız adminlər!")
        return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Mute etmək üçün mesaja cavab verin!")
        return
    
    target = message.reply_to_message.from_user
    duration = 3600 # Default 1 saat
    
    # Süre ayrıştırma (1m, 2h, 1d)
    args = message.text.split()
    if len(args) > 1:
        time_str = args[1]
        try:
            if time_str.endswith('m'): duration = int(time_str[:-1]) * 60
            elif time_str.endswith('h'): duration = int(time_str[:-1]) * 3600
            elif time_str.endswith('d'): duration = int(time_str[:-1]) * 86400
        except: pass
    
    try:
        permissions = ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(message.chat.id, target.id, until_date=time.time() + duration, permissions=permissions)
        
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        bot.send_message(
            message.chat.id, 
            f"🔇 <b>{target.first_name}</b> səssizləşdirildi!\n⏱️ Müddət: {hours}s {minutes}dəq\n👮 Admin: {message.from_user.first_name}", 
            parse_mode='HTML'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {str(e)}")

# --- Unmute Sistemi ---
@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    target = message.reply_to_message.from_user
    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_invite_users=True
        )
        bot.restrict_chat_member(message.chat.id, target.id, permissions=permissions)
        bot.send_message(message.chat.id, f"🔊 <b>{target.first_name}</b> səsi açıldı!", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Xəta: {str(e)}")

# --- Warn (Uyarı) Sistemi ---
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    target = message.reply_to_message.from_user
    chat_id = str(message.chat.id)
    user_id = str(target.id)
    user_key = f"{chat_id}_{user_id}"
    
    if user_key not in data_manager.data["warnings"]:
        data_manager.data["warnings"][user_key] = 0
    
    data_manager.data["warnings"][user_key] += 1
    data_manager.save_data()
    
    settings = get_group_settings(message.chat.id)
    warns = data_manager.data["warnings"][user_key]
    
    warn_text = f"⚠️ <b>XƏBƏRDARLIQ</b>\n\n👤 İstifadəçi: <b>{target.first_name}</b>\n📊 Xəbərdarlıq: <code>{warns}/{settings['warn_limit']}</code>"
    
    if warns >= settings['warn_limit']:
        try:
            bot.ban_chat_member(message.chat.id, target.id, until_date=time.time()+3600)
            warn_text += f"\n\n⛔ Limitə çatdığı üçün 1 saat qadağan edildi!"
            data_manager.data["warnings"][user_key] = 0
        except Exception as e:
            warn_text += f"\n❌ Ban xətası: {e}"
    
    bot.send_message(message.chat.id, warn_text, parse_mode='HTML')

# --- Unwarn Sistemi ---
@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    
    target = message.reply_to_message.from_user
    chat_id = str(message.chat.id)
    user_id = str(target.id)
    user_key = f"{chat_id}_{user_id}"
    
    if user_key in data_manager.data["warnings"] and data_manager.data["warnings"][user_key] > 0:
        data_manager.data["warnings"][user_key] -= 1
        data_manager.save_data()
        warns = data_manager.data["warnings"][user_key]
        bot.send_message(message.chat.id, f"✅ <b>{target.first_name}</b> xəbərdarlığı silindi!\n📊 Cari: <code>{warns}</code>", parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ Bu istifadəçinin xəbərdarlığı yoxdur!")

# --- Pin / Unpin / Purge ---
@bot.message_handler(commands=['pin'])
def pin_message(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message: return
    try:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.send_message(message.chat.id, "📌 Mesaj pinləndi!")
    except: pass

@bot.message_handler(commands=['unpin'])
def unpin_message(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    try:
        bot.unpin_chat_message(message.chat.id)
        bot.send_message(message.chat.id, "📌 Pin götürüldü!")
    except: pass

@bot.message_handler(commands=['purge'])
def purge_messages(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Təmizləmək üçün bir mesaja cavab verin!")
        return
    
    start_id = message.reply_to_message.message_id
    end_id = message.message_id
    deleted = 0
    
    # Bilgi mesajı
    msg = bot.send_message(message.chat.id, "🗑️ Mesajlar silinir...")
    
    try:
        for msg_id in range(start_id, end_id + 1):
            try:
                bot.delete_message(message.chat.id, msg_id)
                deleted += 1
            except: pass
        
        bot.delete_message(message.chat.id, msg.message_id)
        bot.send_message(message.chat.id, f"✅ {deleted} mesaj silindi!").delete_after(3)
    except: pass

# --- Basit Toggle Komutları ---
@bot.message_handler(commands=['antilink', 'antiswear', 'antispam', 'welcome'])
def toggle_simple(message):
    if message.chat.type not in ['group', 'supergroup']: return
    if not is_admin(message.chat.id, message.from_user.id): return
    
    cmd = message.text.split()[0][1:] # komut adı (örn: antilink)
    setting_map = {
        'antilink': 'anti_link',
        'antiswear': 'anti_swear',
        'antispam': 'anti_spam',
        'welcome': 'welcome'
    }
    
    key = setting_map.get(cmd)
    if key:
        settings = get_group_settings(message.chat.id)
        # Eğer argüman varsa (on/off)
        args = message.text.split()
        if len(args) > 1:
            if args[1].lower() == 'on': settings[key] = True
            elif args[1].lower() == 'off': settings[key] = False
        else:
            settings[key] = not settings[key] # Toggle
            
        data_manager.save_data()
        status = "✅ AKTİV" if settings[key] else "❌ DEAKTİV"
        bot.reply_to(message, f"{cmd.upper()}: {status}")

# ==================== SAHİP KOMUTLARI (OWNER) ====================
@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID: return
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Mesaj yazın: /broadcast mesaj")
        return
    
    text = message.text.split(maxsplit=1)[1]
    count = 0
    for chat_id in data_manager.data["group_settings"].keys():
        try:
            bot.send_message(int(chat_id), text, parse_mode='HTML')
            count += 1
            time.sleep(0.1)
        except: pass
    
    bot.reply_to(message, f"✅ Broadcast tamamlandı: {count} qrup")

@bot.message_handler(commands=['globalstats'])
def global_stats(message):
    if message.from_user.id != ADMIN_ID: return
    total_groups = len(data_manager.data["group_settings"])
    total_afk = len(data_manager.data["afk_users"])
    total_warns = sum(data_manager.data["warnings"].values())
    bot.reply_to(message, f"🌍 <b>GLOBAL STATS</b>\n\n🏠 Groups: {total_groups}\n😴 AFK: {total_afk}\n⚠️ Warns: {total_warns}")

# ==================== CALLBACK HANDLER (HATA DÜZELTME YERİ) ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """
    Bu fonksiyon tüm buton tıklamalarını yönetir.
    ÖNEMLİ: Resimli mesajdan yazıya geçerken 'delete_message' kullanılır.
    """
    
    if call.data == "commands":
        # Eski (resimli) mesajı SİL
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        
        commands_text = """╔═══════════════════════════╗
║  📚 <b>KOMANDALAR LİSTİ</b>
╠═══════════════════════════╣
║
║ <b>👤 İSTİFADƏÇİ:</b>
║ • /start - Botu başlat
║ • /info - Bot məlumatı
║ • /alive - Bot statusu
║ • /stats - Statistika
║ • /afk [səbəb] - AFK rejimi
║
║ <b>👮 ADMİN:</b>
║ • /settings - Parametrlər
║ • /warn - Xəbərdarlıq ver
║ • /unwarn - Xəbərdarlıq sil
║ • /ban - Banla
║ • /unban - Banı aç
║ • /mute [vaxt] - Səssizləşdir
║ • /unmute - Səsi aç
║ • /kick - Qrupdan at
║ • /pin - Mesajı pinlə
║ • /purge - Mesajları sil
╚═══════════════════════════╝"""
        # Yeni (yazılı) mesaj GÖNDER
        bot.send_message(call.message.chat.id, commands_text, parse_mode='HTML')
        
    elif call.data == "settings_main":
        bot.answer_callback_query(call.id, "⚠️ Parametrləri qrupda /settings yazaraq dəyişin.", show_alert=True)
        
    elif call.data == "stats_info":
        total_msgs = len(spam_tracker)
        afk_count = len(data_manager.data["afk_users"])
        stats_txt = f"📊 Global Mesajlar: {total_msgs}\n😴 AFK Sayı: {afk_count}"
        bot.answer_callback_query(call.id, stats_txt, show_alert=True)

    # Ayarlar Toggle İşlemi (Sadece settings komutundan gelenler için)
    elif call.data.startswith('toggle_'):
        if not is_admin(call.message.chat.id, call.from_user.id):
            bot.answer_callback_query(call.id, "❌ Yalnız adminlər!", show_alert=True)
            return
            
        parts = call.data.split('_')
        setting = "_".join(parts[1:-1]) # anti_link
        chat_id = parts[-1]
        
        settings = get_group_settings(int(chat_id))
        
        if setting in settings:
            settings[setting] = not settings[setting]
            data_manager.save_data()
            bot.answer_callback_query(call.id, f"✅ Dəyişdirildi!")
            
            # Menüyü güncelle (Bu mesaj metin olduğu için edit çalışır)
            new_markup = InlineKeyboardMarkup(row_width=2)
            new_markup.add(
                InlineKeyboardButton(f"{'✅' if settings['anti_link'] else '❌'} Anti-Link", callback_data=f"toggle_anti_link_{chat_id}"),
                InlineKeyboardButton(f"{'✅' if settings['anti_swear'] else '❌'} Anti-Swear", callback_data=f"toggle_anti_swear_{chat_id}"),
                InlineKeyboardButton(f"{'✅' if settings['anti_spam'] else '❌'} Anti-Spam", callback_data=f"toggle_anti_spam_{chat_id}"),
                InlineKeyboardButton(f"{'✅' if settings['welcome'] else '❌'} Xoşgəlmə", callback_data=f"toggle_welcome_{chat_id}")
            )
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=new_markup)
            except: pass

# ==================== XOŞGƏLMƏ MESAJI ====================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    settings = get_group_settings(message.chat.id)
    if not settings["welcome"]: return
    
    for new_member in message.new_chat_members:
        if new_member.is_bot: continue
        
        welcome_text = f"""╔═══════════════════════════╗
║  🎉 <b>XOŞ GƏLMİSƏN</b> 🎉
╠═══════════════════════════╣
║ 👤 İstifadəçi: <b>{new_member.first_name}</b>
║ 🏠 Qrup: <b>{message.chat.title}</b>
╚═══════════════════════════╝"""
        try:
            bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')
        except: pass

# ==================== MESAJ FİLTRİ (EN ALTTA OLMALI) ====================
@bot.message_handler(func=lambda message: message.chat.type in ['group', 'supergroup'])
def message_filter(message):
    user_id = str(message.from_user.id)
    chat_id = str(message.chat.id)
    settings = get_group_settings(message.chat.id)
    
    # 1. AFK'dan Çıkış (Kullanıcı mesaj yazdı)
    if user_id in data_manager.data["afk_users"]:
        del data_manager.data["afk_users"][user_id]
        data_manager.save_data()
        bot.reply_to(message, f"👋 Xoş gəldin <b>{message.from_user.first_name}</b>, artıq AFK deyilsən!", parse_mode='HTML')
    
    # 2. AFK Kontrol (Birisi AFK birini etiketledi mi?)
    if message.reply_to_message:
        target_id = str(message.reply_to_message.from_user.id)
        if target_id in data_manager.data["afk_users"]:
            afk_data = data_manager.data["afk_users"][target_id]
            duration = int(time.time() - afk_data["time"])
            
            # Zaman formatı
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            
            afk_text = f"😴 <b>{afk_data['name']}</b> AFK-dadır.\n📝 Səbəb: {afk_data['reason']}\n⏱️ {hours}s {minutes}dəq"
            bot.reply_to(message, afk_text, parse_mode='HTML')

    # Adminler filtrelere takılmaz
    if is_admin(message.chat.id, message.from_user.id): return

    # 3. Spam Kontrolü
    if settings["anti_spam"] and is_spam(message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            warning = bot.send_message(message.chat.id, f"⚠️ <b>{message.from_user.first_name}</b>, spam etmə!", parse_mode='HTML')
            time.sleep(3) # Mesajı 3sn sonra sil
            bot.delete_message(message.chat.id, warning.message_id)
        except: pass
        return

    # Eğer mesaj metni yoksa (resim, sticker vb.) buradan sonrasını kontrol etme
    if not message.text: return
    
    text_lower = message.text.lower()

    # 4. Link Kontrolü
    if settings["anti_link"]:
        if re.search(r'(https?://|www\.|\.[a-z]{2,}|t\.me/)', text_lower):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, f"🚫 <b>{message.from_user.first_name}</b>, link paylaşma!", parse_mode='HTML')
                return
            except: pass

    # 5. Söyüş (Küfür) Kontrolü
    if settings["anti_swear"]:
        if any(swear in text_lower for swear in SWEAR_WORDS):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, f"🤬 <b>{message.from_user.first_name}</b>, mədəni ol!", parse_mode='HTML')
                
                # Otomatik Warn (Uyarı)
                user_key = f"{chat_id}_{user_id}"
                if user_key not in data_manager.data["warnings"]:
                    data_manager.data["warnings"][user_key] = 0
                data_manager.data["warnings"][user_key] += 1
                data_manager.save_data()
                
                if data_manager.data["warnings"][user_key] >= settings["warn_limit"]:
                    bot.ban_chat_member(message.chat.id, message.from_user.id, until_date=time.time()+3600)
                    bot.send_message(message.chat.id, f"⛔ Limit doldu, 1 saat banlandı!")
                    data_manager.data["warnings"][user_key] = 0
            except: pass

# ==================== BOT BAŞLATMA (MAIN) ====================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 BOT BAŞLADI - FULL DETAYLI MOD")
    logger.info("=" * 60)
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            logger.info("⛔ Bot dayandırıldı")
            data_manager.save_data()
            break
        except Exception as e:
            logger.error(f"❌ Kritik xəta: {e}")
            logger.info("🔄 Yeniden başlatılıyor...")
            time.sleep(5)
