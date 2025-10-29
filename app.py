# app.py - الإصدار النهائي للنشر على Render
# يجمع بين Playwright و Flask Heartbeat وقراءة الإعدادات الذكية

import asyncio
import json
import logging
import os
import threading
from flask import Flask
from playwright.async_api import async_playwright
from telegram import Bot

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
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

# --- 5. كود النبض (Heartbeat) لإبقاء الخدمة مستيقظة ---
app = Flask(__name__)

@app.route('/')
def heartbeat():
    """نقطة النهاية التي يتم استدعاؤها للحفاظ على الخدمة نشطة."""
    active_accounts_count = len(accounts_state_cache)
    return f"Bot is alive and monitoring {active_accounts_count} accounts."

def run_flask_app():
    """دالة لتشغيل تطبيق فلاسك في 'ثريد' منفصل."""
    # Render يختار البورت تلقائياً، لذلك نستخدم بورت شائع
    app.run(host='0.0.0.0', port=10000)

# --- 6. دوال مساعدة (إرسال الإشعارات ومعالجة البيانات) ---
async def send_telegram_notification(message):
    """إرسال إشعار إلى جميع المسؤولين."""
    for chat_id in ADMIN_IDS:
        try:
            await telegram_bot.send_message(
                chat_id=chat_id, text=message, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ فشل في إرسال رسالة إلى {chat_id}: {e}")

async def on_data_update(data):
    """يتم استدعاؤها من الجافا سكريبت عند وجود تحديث."""
    global accounts_state_cache, is_first_run
    logger.info("...[EVENT] تم استقبال تحديث للبيانات من الصفحة...")

    new_accounts_data = data.get("data", [])
    if not isinstance(new_accounts_data, list):
        logger.warning("⚠️ البيانات المستلمة ليست قائمة. التجاهل.")
        return

    current_state = {
        account[2]: account[6] for account in new_accounts_data if len(account) > 6 and account[2]
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
    for email, new_status in current_state.items():
        old_status = accounts_state_cache.get(email)
        if old_status is not None and old_status != new_status:
            change_message = (
                f"🔥 *تحديث فوري للحالة!*\n\n"
                f"📧 البريد: `{email}`\n"
                f"📊 الحالة تغيرت من `{old_status}` إلى `{new_status}`"
            )
            changes_found.append(change_message)

    if changes_found:
        logger.info(f"🎉 تم العثور على {len(changes_found)} تغيير في الحالات!")
        full_report = "\n\n---\n\n".join(changes_found)
        await send_telegram_notification(full_report)

    accounts_state_cache = current_state

# --- 7. منطق البوت الرئيسي (Playwright) ---
async def main_bot_logic():
    """الوظيفة الرئيسية التي تشغل المتصفح وتحقن الكود."""
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

# --- 8. نقطة بداية التشغيل ---
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
        asyncio.run(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))
