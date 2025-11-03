# app.py - الإصدار v14.0 (المحرك الدائم) - كفاءة استباقية واستقرار مطلق

import asyncio
import json
import logging
import os
import signal
import threading
import time
import psutil
from flask import Flask, jsonify
from playwright.async_api import async_playwright, Page, Browser, Playwright, BrowserContext
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from logging.handlers import RotatingFileHandler

# --- 1. إعداد نظام تسجيل الأحداث (اللوجز) ---
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
file_handler = RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# --- 2. تحميل الإعدادات والتحقق من الملفات ---
CONFIG = None
CACHE_FILE = os.path.join(os.path.dirname(__file__), "bot_cache.json")
try:
    if not os.path.exists("injector.js"):
        raise FileNotFoundError("ملف injector.js مفقود! لا يمكن تشغيل البوت.")
    
    config_json_str = os.environ.get('CONFIG_JSON')
    if config_json_str:
        CONFIG = json.loads(config_json_str)
        logger.info("✅ تم تحميل الإعدادات من متغيرات البيئة.")
    else:
        with open("config.json", "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
        logger.info("✅ تم تحميل الإعدادات من ملف config.json المحلي.")
except (FileNotFoundError, json.JSONDecodeError, TypeError) as e:
    logger.critical(f"❌ خطأ فادح في الإعدادات الأولية: {e}. لا يمكن المتابعة.")
    exit()

# --- 3. استخلاص المتغيرات العالمية ---
TELEGRAM_BOT_TOKEN = CONFIG.get("telegram", {}).get("bot_token")
ADMIN_IDS = CONFIG.get("telegram", {}).get("admin_ids", [])
WEBSITE_URL = CONFIG.get("website", {}).get("urls", {}).get("sender_page")
COOKIES = list(CONFIG.get("website", {}).get("cookies", {}).items())

if not all([TELEGRAM_BOT_TOKEN, ADMIN_IDS, WEBSITE_URL, COOKIES]):
    logger.critical("❌ الإعدادات ناقصة! تأكد من وجود كل المتغيرات المطلوبة.")
    exit()

# --- 4. متغيرات عالمية وحالة النظام ---
accounts_state_cache = {}
telegram_app = None
playwright_page_global: Page = None
browser_instance: Browser = None
browser_context_global: BrowserContext = None
is_swapping = False

CHROMIUM_ARGS = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-software-rasterizer", "--disable-extensions", "--js-flags=--max-old-space-size=128", "--renderer-process-limit=1"]

# --- 5. خادم الويب (Flask) ---
app = Flask(__name__)
@app.route('/')
def heartbeat():
    return f"Bot is alive (Perpetual Engine v14.0). Monitoring {len(accounts_state_cache)} accounts."

@app.route('/health')
def health_check():
    is_healthy = playwright_page_global and not playwright_page_global.is_closed()
    return jsonify({
        "status": "ok" if is_healthy else "degraded",
        "cached_accounts": len(accounts_state_cache),
        "memory_mb": psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    }), 200 if is_healthy else 503

def run_flask_app():
    while True:
        try:
            app.run(host='0.0.0.0', port=10000, use_reloader=False)
        except Exception as e:
            logger.error(f"🚨 انهار خادم Flask: {e}. إعادة التشغيل خلال 5 ثوانٍ...")
            time.sleep(5)

# --- 6. دوال مساعدة ومهام الخلفية ---
async def send_telegram_notification(message, chat_id=None):
    if not telegram_app: return
    target_ids = [chat_id] if chat_id else ADMIN_IDS
    for cid in target_ids:
        try:
            await telegram_app.bot.send_message(chat_id=cid, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"❌ فشل في إرسال رسالة إلى {cid}: {e}")

async def on_data_update(data):
    global accounts_state_cache
    new_accounts_data = data.get("data", [])
    if not isinstance(new_accounts_data, list): return

    current_state = {
        account[2]: {"status": account[6], "id": account[0], "available": account[7], "taken": account[5]}
        for account in new_accounts_data if len(account) > 7 and account[2]
    }

    # لا حاجة لـ is_first_run مع وجود النسخ الاحتياطي
    if not accounts_state_cache:
        await send_telegram_notification(f"✅ *نظام المحرك الدائم (v14.0) بدأ العمل!*\nتم تحميل الحالة الأولية لـ *{len(current_state)}* حساب.")

    changes_found = [
        f"🔥 *تحديث فوري للحالة!*\n\n📧 البريد: `{email}`\n📊 الحالة تغيرت من `{old_data['status']}` إلى `{new_data['status']}`"
        for email, new_data in current_state.items()
        if (old_data := accounts_state_cache.get(email)) and old_data["status"] != new_data["status"]
    ]

    if changes_found:
        await send_telegram_notification("\n\n---\n\n".join(changes_found))

    accounts_state_cache = current_state

def load_cache_from_backup():
    global accounts_state_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                accounts_state_cache = json.load(f)
            if accounts_state_cache:
                logger.info(f"✅ تم استعادة الذاكرة من النسخة الاحتياطية ({len(accounts_state_cache)} حساب).")
    except Exception as e:
        logger.warning(f"⚠️ لم يتم استعادة الذاكرة من النسخة الاحتياطية: {e}")

# --- 7. أوامر التليجرام (محصنة) ---
def safe_handler(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if update.effective_chat.id not in ADMIN_IDS: return
            await func(update, context)
        except Exception as e:
            logger.error(f"❌ خطأ في المعالج '{func.__name__}': {e}", exc_info=True)
            try:
                await update.message.reply_text("⚠️ حدث خطأ غير متوقع. تم إبلاغ المطور.")
            except: pass
    return wrapper

@safe_handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚙️ *أهلاً بك في بوت المحرك الدائم (v14.0)!*\n\n"
        "أنا أعمل الآن بنظام استباقي يمنع تراكم الذاكرة، مما يضمن استقراراً مطلقاً.\n\n"
        "*الأوامر المتاحة:*\n"
        "`/status` - عرض حالة النظام.\n"
        "`/accounts` - عرض قائمة الحسابات من الذاكرة.\n"
        "`/details [email]` - بحث شامل (ذاكرة + مباشر).\n"
        "`/system` - لوحة تحكم أداء النظام.",
        parse_mode="Markdown"
    )

# ... (هنا يجب وضع كل أوامرك الأخرى مثل status, accounts, details, system مع @safe_handler)

# --- 8. نظام المحرك الدائم (The Perpetual Engine) ---
async def gentle_page_swap(playwright_instance: Playwright):
    global playwright_page_global, is_swapping
    if is_swapping:
        logger.warning("🔄 عملية تبديل جارية بالفعل، تم تجاهل الطلب الجديد.")
        return

    is_swapping = True
    old_page = playwright_page_global
    
    try:
        logger.info("🔄 بدء عملية التبديل اللطيف للصفحة...")
        new_page = await browser_context_global.new_page()
        await new_page.expose_function("onDataUpdate", on_data_update)
        with open("injector.js", "r", encoding="utf-8") as f:
            await new_page.add_init_script(f.read())
        await new_page.goto(WEBSITE_URL, timeout=120000, wait_until="domcontentloaded")
        
        playwright_page_global = new_page
        logger.info("✅ تم التبديل إلى الصفحة الجديدة بنجاح.")
        
        if old_page:
            await old_page.close()
            logger.info("🚮 تم إغلاق الصفحة القديمة وتحرير ذاكرتها.")
            
    except Exception as e:
        logger.error(f"❌ فشل التبديل اللطيف للصفحة: {e}. سيتم الاعتماد على الصفحة القديمة إن أمكن.")
        if old_page and not old_page.is_closed():
            playwright_page_global = old_page
        else:
            logger.critical("🚨 كارثة: فشل التبديل والصفحة القديمة ماتت. تفعيل إعادة تشغيل كاملة...")
            await send_telegram_notification("🚨 *خطأ حرج!* فشل تبديل الصفحة والصفحة القديمة غير متاحة. جاري إعادة تشغيل كاملة...")
            await setup_browser_with_retry(playwright_instance, max_attempts=3)
    finally:
        is_swapping = False

async def perpetual_engine_task(playwright_instance: Playwright):
    logger.info("⚙️ المحرك الدائم بدأ العمل. سيتم تبديل الصفحة كل 15 دقيقة.")
    while True:
        await asyncio.sleep(15 * 60)
        logger.info("⚙️ [المحرك الدائم] حان وقت التبديل الوقائي للصفحة...")
        await send_telegram_notification("⚙️ *صيانة وقائية...* جاري تبديل الصفحة للحفاظ على الأداء (لا يوجد توقف).")
        await gentle_page_swap(playwright_instance)

# --- 9. منطق البوت الرئيسي ---
async def setup_browser_and_page(playwright_instance: Playwright):
    global browser_instance, browser_context_global, playwright_page_global
    logger.info("🚀 تشغيل المتصفح...")
    browser_instance = await playwright_instance.chromium.launch(headless=True, args=CHROMIUM_ARGS)
    browser_context_global = await browser_instance.new_context(java_script_enabled=True)
    
    async def resource_blocker(route):
        if route.request.resource_type in {"image", "media", "font", "stylesheet"}:
            await route.abort()
        else:
            await route.continue_()
    await browser_context_global.route("**/*", resource_blocker)

    await browser_context_global.add_cookies([{"name": k, "value": v, "domain": ".utautotransfer.com", "path": "/"} for k, v in COOKIES])
    
    page = await browser_context_global.new_page()
    await page.expose_function("onDataUpdate", on_data_update)
    with open("injector.js", "r", encoding="utf-8") as f:
        await page.add_init_script(f.read())
    await page.goto(WEBSITE_URL, timeout=120000, wait_until="domcontentloaded")
    
    playwright_page_global = page
    logger.info("✅ تم إعداد المتصفح والصفحة الأولية بنجاح.")

async def setup_browser_with_retry(playwright_instance: Playwright, max_attempts=5) -> bool:
    for attempt in range(1, max_attempts + 1):
        try:
            await setup_browser_and_page(playwright_instance)
            return True
        except Exception as e:
            wait_time = min(60 * (2 ** (attempt - 1)), 300)
            logger.error(f"❌ فشل الإعداد (محاولة {attempt}/{max_attempts}): {e}. سأحاول مرة أخرى بعد {wait_time} ثانية...")
            if attempt < max_attempts:
                await send_telegram_notification(f"⚠️ *فشل إعداد المتصفح (محاولة {attempt}/{max_attempts})*")
                await asyncio.sleep(wait_time)
            else:
                return False
    return False

async def main_bot_logic():
    global telegram_app
    load_cache_from_backup()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    telegram_app = application
    
    # ... (إضافة كل الأوامر المحصنة هنا)
    application.add_handler(CommandHandler("start", start_command))
    # ...

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("🤖 بوت تليجرام نشط ويستمع للأوامر...")
    
    async with async_playwright() as p:
        browser_ready = await setup_browser_with_retry(p, max_attempts=5)
        
        if browser_ready:
            asyncio.create_task(perpetual_engine_task(p))
            await send_telegram_notification("⚙️ *نظام المحرك الدائم متصل بالكامل!*\nالنظام الآن يقوم بصيانة نفسه بشكل دوري استباقي.")
        else:
            logger.critical("❌ فشل الإعداد الأولي للمتصفح. البوت سيتوقف.")
            await send_telegram_notification("🚨 *فشل كارثي!* لم يتمكن البوت من تشغيل المتصفح بعد عدة محاولات. توقف النظام.")
            return

        while True:
            await asyncio.sleep(3600)

# --- 10. الإغلاق النظيف ونقطة بداية التشغيل ---
async def shutdown(sig, loop):
    logger.info(f"تم استقبال إشارة إيقاف {sig.name}... جاري الإغلاق النظيف.")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    
    if browser_context_global: await browser_context_global.close()
    if browser_instance: await browser_instance.close()
    logger.info("✅ تم إغلاق المتصفح والسياق بنجاح.")

    await send_telegram_notification("🛑 *تم إيقاف نظام المحرك الدائم بأمان.*")
    await asyncio.sleep(2)
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if os.name != 'nt':
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))

    try:
        loop.run_until_complete(main_bot_logic())
    except KeyboardInterrupt:
        if os.name == 'nt':
            loop.run_until_complete(shutdown(signal.SIGINT, loop))
    finally:
        logger.info("🏁 تم إيقاف حلقة الأحداث الرئيسية.")
        loop.close()
