# app.py - الإصدار النهائي v3.0 - مع لوحة تحكم تليجرام
# يجمع بين Playwright و Flask Heartbeat وأوامر التحكم

import asyncio
import json
import logging
import os
import threading
from flask import Flask
from playwright.async_api import async_playwright
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. إعداد نظام تسجيل الأحداث (اللوجز) ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. تحميل الإعدادات بذكاء (من متغيرات البيئة أو من ملف) ---
CONFIG = None
config_json_str = os.environ.get('CONFIG_JSON')

if config_json_str:
    logger.info("✅ تم العثور على إعدادات في متغيرات البيئة (Render Environment).")
    try:
        CONFIG = json.loads(config_json_str)
    except json.JSONDecodeError:
        logger.critical("❌ فشل في قراءة الإعدادات من متغير البيئة. الصيغة غير صحيحة.")
        exit()
else:
    logger.warning("⚠️ لم يتم العثور على متغير البيئة. جاري البحث عن ملف config.json محلي...")
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
        logger.info("✅ تم تحميل الإعدادات من ملف config.json المحلي.")
    except FileNotFoundError:
        logger.critical("❌ لم يتم العثور على إعدادات في أي مكان. لا يمكن المتابعة.")
        exit()
    except json.JSONDecodeError:
        logger.critical("❌ خطأ في قراءة ملف config.json. تأكد من أن صيغته صحيحة.")
        exit()

# --- 3. استخلاص المتغيرات العالمية والتحقق منها ---
TELEGRAM_BOT_TOKEN = CONFIG.get("telegram", {}).get("bot_token")
ADMIN_IDS = CONFIG.get("telegram", {}).get("admin_ids", [])
WEBSITE_URL = CONFIG.get("website", {}).get("urls", {}).get("sender_page")
COOKIES = list(CONFIG.get("website", {}).get("cookies", {}).items())

if not all([TELEGRAM_BOT_TOKEN, ADMIN_IDS, WEBSITE_URL, COOKIES]):
    logger.critical("❌ الإعدادات ناقصة! تأكد من وجود bot_token, admin_ids, sender_page, و cookies.")
    exit()

# --- 4. ذاكرة تخزين مؤقتة للحالة وتهيئة البوت ---
accounts_state_cache = {}
is_first_run = True
# ✨✨ تعديل: سنقوم بإنشاء البوت داخل دالة main_bot_logic
telegram_app = None

# --- 5. كود النبض (Heartbeat) لإبقاء الخدمة مستيقظة ---
app = Flask(__name__)

@app.route('/')
def heartbeat():
    """نقطة النهاية التي يتم استدعاؤها للحفاظ على الخدمة نشطة."""
    active_accounts_count = len(accounts_state_cache)
    return f"Bot is alive and monitoring {active_accounts_count} accounts."

def run_flask_app():
    """دالة لتشغيل تطبيق فلاسك في 'ثريد' منفصل."""
    app.run(host='0.0.0.0', port=10000)

# --- 6. دوال مساعدة (إرسال الإشعارات ومعالجة البيانات) ---
async def send_telegram_notification(message, chat_id=None):
    """إرسال إشعار إلى مسؤول معين أو جميع المسؤولين."""
    target_ids = [chat_id] if chat_id else ADMIN_IDS
    for cid in target_ids:
        try:
            # نستخدم telegram_app.bot لإرسال الرسائل
            await telegram_app.bot.send_message(
                chat_id=cid, text=message, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ فشل في إرسال رسالة إلى {cid}: {e}")

async def on_data_update(data):
    """يتم استدعاؤها من الجافا سكريبت عند وجود تحديث."""
    global accounts_state_cache, is_first_run
    logger.info("...[EVENT] تم استقبال تحديث للبيانات من الصفحة...")

    new_accounts_data = data.get("data", [])
    if not isinstance(new_accounts_data, list):
        logger.warning("⚠️ البيانات المستلمة ليست قائمة. التجاهل.")
        return

    current_state = {
        account[2]: {"status": account[6], "id": account[0]} for account in new_accounts_data if len(account) > 6 and account[2]
    }

    if is_first_run:
        accounts_state_cache = current_state
        is_first_run = False
        logger.info(f"✅ الحالة الأولية تم تحميلها لـ {len(accounts_state_cache)} حساب.")
        await send_telegram_notification(
            f"✅ *نظام المراقبة الفورية بدأ العمل!*\nتم تحميل الحالة الأولية لـ *{len(accounts_state_cache)}* حساب."
        )
        return

    changes_found = []
    for email, new_data in current_state.items():
        old_data = accounts_state_cache.get(email)
        if old_data and old_data["status"] != new_data["status"]:
            change_message = (
                f"🔥 *تحديث فوري للحالة!*\n\n"
                f"📧 البريد: `{email}`\n"
                f"🆔 المعرف: `{new_data['id']}`\n"
                f"📊 الحالة تغيرت من `{old_data['status']}` إلى `{new_data['status']}`"
            )
            changes_found.append(change_message)

    if changes_found:
        logger.info(f"🎉 تم العثور على {len(changes_found)} تغيير في الحالات!")
        full_report = "\n\n---\n\n".join(changes_found)
        await send_telegram_notification(full_report)

    accounts_state_cache = current_state

# --- 7. ✨✨ الأوامر الجديدة للتليجرام ✨✨ ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start: يعرض رسالة ترحيبية وقائمة الأوامر."""
    if update.effective_chat.id not in ADMIN_IDS: return
    
    welcome_message = (
        "👋 *أهلاً بك في بوت المراقبة الفورية!*\n\n"
        "هذا البوت يعمل الآن على السحابة ويقوم بمراقبة التغييرات في حالة الحسابات بشكل فوري.\n\n"
        "*الأوامر المتاحة:*\n"
        "`/status` - عرض حالة النظام وعدد الحسابات المراقبة.\n"
        "`/accounts` - عرض قائمة مختصرة بجميع الحسابات وحالاتها.\n"
        "`/details [email]` - عرض تفاصيل كاملة لحساب معين."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /status: يعرض حالة النظام."""
    if update.effective_chat.id not in ADMIN_IDS: return

    status_message = (
        f"🟢 *النظام يعمل بشكل طبيعي.*\n\n"
        f"🧠 الذاكرة تحتوي على *{len(accounts_state_cache)}* حساب.\n"
        f"🤖 أستمع للتحديثات بشكل فوري عبر تقنية حقن الجافا سكريبت."
    )
    await update.message.reply_text(status_message, parse_mode="Markdown")

async def accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /accounts: يعرض قائمة بجميع الحسابات وحالاتها."""
    if update.effective_chat.id not in ADMIN_IDS: return

    if not accounts_state_cache:
        await update.message.reply_text("⏳ الذاكرة فارغة حالياً، يرجى الانتظار لأول تحديث من الموقع.")
        return

    report = [f"📋 *قائمة الحسابات الحالية ({len(accounts_state_cache)}):*\n"]
    for email, data in accounts_state_cache.items():
        report.append(f"- `{email}`: *{data['status']}*")
    
    # تقسيم الرسالة إذا كانت طويلة جداً
    full_report = "\n".join(report)
    if len(full_report) > 4096:
        for i in range(0, len(full_report), 4096):
            await update.message.reply_text(full_report[i:i+4096], parse_mode="Markdown")
    else:
        await update.message.reply_text(full_report, parse_mode="Markdown")

async def details_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /details: يعرض تفاصيل حساب معين."""
    if update.effective_chat.id not in ADMIN_IDS: return

    if not context.args:
        await update.message.reply_text("⚠️ يرجى تحديد إيميل بعد الأمر. مثال: `/details user@example.com`")
        return

    email_to_find = context.args[0].lower()
    account_data = accounts_state_cache.get(email_to_find)

    if account_data:
        details_message = (
            f"🔍 *تفاصيل الحساب:*\n\n"
            f"📧 البريد: `{email_to_find}`\n"
            f"🆔 المعرف: `{account_data.get('id', 'N/A')}`\n"
            f"📊 الحالة الحالية: *{account_data.get('status', 'غير معروف')}*"
        )
        await update.message.reply_text(details_message, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ لم يتم العثور على الحساب `{email_to_find}` في الذاكرة الحالية.")

# --- 8. منطق البوت الرئيسي (Playwright) ---
async def main_bot_logic():
    """الوظيفة الرئيسية التي تشغل المتصفح، البوت، وكل شيء."""
    global telegram_app
    
    # ✨✨ تعديل: إنشاء تطبيق التليجرام هنا ✨✨
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    telegram_app = application # لكي تتمكن باقي الدوال من استخدامه
    
    # ✨✨ إضافة معالجات الأوامر الجديدة ✨✨
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("accounts", accounts_command))
    application.add_handler(CommandHandler("details", details_command))

    # تشغيل البوت في الخلفية
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("🤖 بوت تليجرام بدأ العمل ويستمع للأوامر...")

    async with async_playwright() as p:
        logger.info("🚀 تشغيل المتصفح في الخلفية...")
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser.new_context()

        playwright_cookies = [
            {"name": name, "value": value, "domain": ".utautotransfer.com", "path": "/"}
            for name, value in COOKIES
        ]
        await context.add_cookies(playwright_cookies)
        logger.info("🍪 تم وضع الكوكيز بنجاح.")

        page = await context.new_page()
        await page.expose_function("onDataUpdate", on_data_update)
        logger.info("🔗 تم ربط دالة البايثون بالصفحة.")

        try:
            with open("injector.js", "r", encoding="utf-8") as f:
                injector_script = f.read()
        except FileNotFoundError:
            logger.critical("❌ ملف injector.js غير موجود! لا يمكن المتابعة.")
            await send_telegram_notification("🔴 *خطأ فادح:*\nملف `injector.js` غير موجود. توقف النظام.")
            return

        await page.add_init_script(injector_script)
        logger.info("💉 تم تجهيز كود الحقن للعمل.")

        logger.info(f"🧭 جاري الانتقال إلى: {WEBSITE_URL}")
        try:
            await page.goto(WEBSITE_URL, timeout=120000)
        except Exception as e:
            logger.error(f"❌ فشل في تحميل الصفحة: {e}")
            await send_telegram_notification(f"🔴 *خطأ فادح:*\nفشل في تحميل صفحة الموقع.\n`{e}`")
            return

        logger.info("✅ تم تحميل الصفحة بنجاح. النظام الآن يستمع للتحديثات...")
        await send_telegram_notification(
            "🟢 *النظام متصل الآن!*\nأنا أستمع للتحديثات الفورية من الموقع."
        )

        while True:
            await asyncio.sleep(3600)

# --- 9. نقطة بداية التشغيل ---
if __name__ == "__main__":
    # تشغيل خدمة النبض في مسار منفصل
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("🌐 خدمة النبض (Heartbeat) بدأت العمل...")
    
    # تشغيل منطق البوت الرئيسي
    try:
        asyncio.run(main_bot_logic())
    except KeyboardInterrupt:
        logger.info("🛑 إيقاف النظام...")
    except Exception as e:
        logger.critical(f"❌ حدث خطأ فادح أدى إلى توقف البوت: {e}")
        # نحاول إرسال إشعار أخير
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))
        else:
            asyncio.run(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))

