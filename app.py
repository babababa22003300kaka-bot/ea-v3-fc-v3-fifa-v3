# main.py

import asyncio
import json
import logging
from playwright.async_api import async_playwright
from telegram import Bot
from telegram.ext import Application, CommandHandler

# --- إعدادات اللوجر ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- تحميل الإعدادات ---
try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    logger.critical("❌ config.json not found! Please create it.")
    exit()

# --- متغيرات عالمية ---
TELEGRAM_BOT_TOKEN = CONFIG["telegram"]["bot_token"]
ADMIN_IDS = CONFIG["telegram"]["admin_ids"]
WEBSITE_URL = CONFIG["website"]["urls"]["sender_page"]
COOKIES = list(CONFIG["website"]["cookies"].items())

# ذاكرة لتخزين آخر حالة للحسابات
# { "email@example.com": "STATUS" }
accounts_state_cache = {}
is_first_run = True

# --- بوت التليجرام ---
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_telegram_notification(message):
    """إرسال إشعار إلى جميع المسؤولين"""
    for chat_id in ADMIN_IDS:
        try:
            await telegram_bot.send_message(
                chat_id=chat_id, text=message, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")


async def on_data_update(data):
    """
    هذه الدالة يتم استدعاؤها من الجافا سكريبت المحقون عند وجود تحديث.
    """
    global accounts_state_cache, is_first_run
    logger.info("Received data update from the page...")

    new_accounts_data = data.get("data", [])

    # بناء الحالة الحالية
    current_state = {
        account[2]: account[6] for account in new_accounts_data if len(account) > 6
    }

    if is_first_run:
        accounts_state_cache = current_state
        is_first_run = False
        logger.info(f"Initial state loaded for {len(accounts_state_cache)} accounts.")
        await send_telegram_notification(
            f"✅ *نظام المراقبة الفورية بدأ!*\nتم تحميل الحالة الأولية لـ *{len(accounts_state_cache)}* حساب."
        )
        return

    # مقارنة الحالة الحالية بالحالة المخزنة
    changes_found = []
    for email, status in current_state.items():
        if email in accounts_state_cache and accounts_state_cache[email] != status:
            old_status = accounts_state_cache[email]
            change_message = (
                f"🔥 *تحديث فوري للحالة!*\n\n"
                f"📧 البريد: `{email}`\n"
                f"📊 الحالة تغيرت من `{old_status}` إلى `{status}`"
            )
            changes_found.append(change_message)

    if changes_found:
        logger.info(f"Found {len(changes_found)} status changes!")
        # إرسال الإشعارات
        for change in changes_found:
            await send_telegram_notification(change)

    # تحديث الذاكرة
    accounts_state_cache = current_state


async def main():
    """الوظيفة الرئيسية لتشغيل المتصفح وحقن الكود"""
    async with async_playwright() as p:
        logger.info("🚀 Launching browser...")
        browser = await p.chromium.launch(headless=True)  # True = يعمل في الخلفية
        context = await browser.new_context()

        # تحويل الكوكيز إلى التنسيق الصحيح
        playwright_cookies = [
            {"name": name, "value": value, "domain": ".utautotransfer.com", "path": "/"}
            for name, value in COOKIES
        ]
        await context.add_cookies(playwright_cookies)
        logger.info("🍪 Cookies have been set.")

        page = await context.new_page()

        # ربط دالة البايثون بالجافا سكريبت
        await page.expose_function("onDataUpdate", on_data_update)
        logger.info("🔗 Python function 'onDataUpdate' is now exposed to the page.")

        # قراءة كود الحقن من الملف
        with open("injector.js", "r", encoding="utf-8") as f:
            injector_script = f.read()

        # حقن الكود عند كل تحميل للصفحة
        await page.add_init_script(injector_script)
        logger.info("💉 Injector script will be loaded on page navigation.")

        logger.info(f"Navigating to {WEBSITE_URL}...")
        await page.goto(WEBSITE_URL)

        logger.info("✅ Navigation complete. The system is now live and listening.")
        await send_telegram_notification(
            "🟢 *النظام متصل الآن!*\nأنا أستمع للتحديثات الفورية من الموقع."
        )

        # إبقاء السكربت يعمل في الخلفية
        while True:
            await asyncio.sleep(60)


if __name__ == "__main__":
    # تأكد من وجود admin_ids في ملف الإعدادات
    if not ADMIN_IDS:
        logger.critical(
            "❌ No admin_ids found in config.json. Please add your Telegram chat ID."
        )
        exit()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
