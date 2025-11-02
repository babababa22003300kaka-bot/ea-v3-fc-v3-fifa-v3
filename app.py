# app.py - الإصدار v13.0 (الحصن الأبدي) - نظام لا يموت

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

# --- 1. إعداد نظام تسجيل الأحداث (اللوجز) ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- 2. تحميل الإعدادات والتحقق من الملفات ---
CONFIG = None
CACHE_FILE = "/tmp/bot_cache.json"
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
is_first_run = True
telegram_app = None
playwright_page_global: Page = None
browser_instance: Browser = None
browser_context_global: BrowserContext = None
is_recycling = False
MAX_CACHE_SIZE = 5000
MEMORY_THRESHOLD_MB = 420

CHROMIUM_ARGS = ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-software-rasterizer", "--disable-extensions", "--js-flags=--max-old-space-size=128", "--renderer-process-limit=1"]

# --- 5. خادم الويب المحصّن (Flask) ---
app = Flask(__name__)
@app.route('/')
def heartbeat():
    status = "Online" if playwright_page_global and not playwright_page_global.is_closed() else "Emergency Mode (Browser Down)"
    return f"Bot is alive. Status: {status}. Monitoring {len(accounts_state_cache)} accounts."

@app.route('/health')
def health_check():
    is_healthy = playwright_page_global and not playwright_page_global.is_closed()
    return jsonify({
        "status": "ok" if is_healthy else "degraded",
        "browser_status": "online" if is_healthy else "offline",
        "cached_accounts": len(accounts_state_cache),
        "memory_mb": psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    }), 200 if is_healthy else 503

def run_flask_app():
    while True:
        try:
            logger.info("🚀 تشغيل خادم Flask...")
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
    global accounts_state_cache, is_first_run
    new_accounts_data = data.get("data", [])
    if not isinstance(new_accounts_data, list): return

    current_state = {
        account[2]: {"status": account[6], "id": account[0], "available": account[7], "taken": account[5]}
        for account in new_accounts_data if len(account) > 7 and account[2]
    }

    if is_first_run:
        accounts_state_cache = current_state
        is_first_run = False
        await send_telegram_notification(f"✅ *نظام الحصن الأبدي (v13.0) بدأ العمل!*\nتم تحميل الحالة الأولية لـ *{len(accounts_state_cache)}* حساب.")
        return

    changes_found = [
        f"🔥 *تحديث فوري للحالة!*\n\n📧 البريد: `{email}`\n📊 الحالة تغيرت من `{old_data['status']}` إلى `{new_data['status']}`"
        for email, new_data in current_state.items()
        if (old_data := accounts_state_cache.get(email)) and old_data["status"] != new_data["status"]
    ]

    if changes_found:
        await send_telegram_notification("\n\n---\n\n".join(changes_found))

    accounts_state_cache = current_state
    
    if len(accounts_state_cache) > MAX_CACHE_SIZE:
        accounts_state_cache = dict(list(accounts_state_cache.items())[-MAX_CACHE_SIZE:])
        logger.warning(f"♻️ تم تقليص ذاكرة الكاش إلى آخر {MAX_CACHE_SIZE} حساب.")

async def cache_backup_task():
    while True:
        await asyncio.sleep(3600)
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(accounts_state_cache, f)
            logger.info(f"✅ تم حفظ نسخة احتياطية من الذاكرة ({len(accounts_state_cache)} حساب).")
        except Exception as e:
            logger.error(f"❌ فشل في حفظ نسخة احتياطية من الذاكرة: {e}")

def load_cache_from_backup():
    global accounts_state_cache, is_first_run
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                accounts_state_cache = json.load(f)
            if accounts_state_cache:
                is_first_run = False
                logger.info(f"✅ تم استعادة الذاكرة من النسخة الاحتياطية ({len(accounts_state_cache)} حساب).")
    except Exception as e:
        logger.warning(f"⚠️ لم يتم استعادة الذاكرة من النسخة الاحتياطية: {e}")

# --- 7. أوامر التليجرام (محصنة بـ Decorator) ---
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
        "🛡️ *أهلاً بك في بوت الحصن الأبدي (v13.0)!*\n\n"
        "أنا مصمم للعمل بلا توقف. حتى لو فشل المتصفح، سأبقى متاحاً.\n\n"
        "*الأوامر المتاحة:*\n"
        "`/status` - عرض حالة النظام.\n"
        "`/accounts` - عرض قائمة الحسابات من الذاكرة.\n"
        "`/details [email]` - بحث شامل (ذاكرة + مباشر).\n"
        "`/system` - لوحة تحكم أداء النظام.",
        parse_mode="Markdown"
    )

@safe_handler
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    browser_status = "متصل ويعمل" if playwright_page_global and not playwright_page_global.is_closed() else "متوقف (وضع الطوارئ)"
    await update.message.reply_text(
        f"📊 *حالة النظام (الحصن الأبدي)*\n\n"
        f"🧠 *الذاكرة:* تحتوي على *{len(accounts_state_cache)}* حساب.\n"
        f"🖥️ *المتصفح:* *{browser_status}*.\n"
        f"🛡️ *الحماية:* نظام الحارس الخالد نشط.",
        parse_mode="Markdown"
    )

@safe_handler
async def accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not accounts_state_cache:
        await update.message.reply_text("⏳ الذاكرة فارغة حالياً، يرجى الانتظار لأول تحديث من الموقع أو استعادتها من النسخة الاحتياطية.")
        return
    report_lines = [f"📋 *قائمة الحسابات الحالية ({len(accounts_state_cache)}):*\n"]
    for email, data in accounts_state_cache.items():
        report_lines.append(f"- `{email}`: *{data.get('status', 'N/A')}*")
    full_report = "\n".join(report_lines)
    if len(full_report) > 4096:
        for i in range(0, len(full_report), 4096):
            await update.message.reply_text(full_report[i:i+4096], parse_mode="Markdown")
    else:
        await update.message.reply_text(full_report, parse_mode="Markdown")

@safe_handler
async def details_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ يرجى تحديد إيميل. مثال: `/details user@example.com`")
        return
    
    email_to_find = context.args[0].lower()
    msg = await update.message.reply_text(f"🔍 البحث عن `{email_to_find}`...")

    if email_to_find in accounts_state_cache:
        account_data = accounts_state_cache[email_to_find]
        await msg.edit_text(f"✅ *موجود في الذاكرة:*\n\n📧 البريد: `{email_to_find}`\n🆔 المعرف: `{account_data.get('id', 'N/A')}`\n📊 الحالة: *{account_data.get('status', 'غير معروف')}*", parse_mode="Markdown")
        return

    if playwright_page_global is None or playwright_page_global.is_closed():
        await msg.edit_text(f"⚠️ *الحساب غير موجود في الذاكرة.*\nالبحث المباشر غير متاح حالياً (صيانة أو متصفح غير جاهز).", parse_mode="Markdown")
        return

    if is_recycling:
        await msg.edit_text("⏳ *صيانة جارية...* يرجى المحاولة بعد 30 ثانية.", parse_mode="Markdown")
        return

    await msg.edit_text(f"⏳ لم يتم العثور عليه في الذاكرة. جاري البحث في *القائمة النشطة*...")
    result = await live_search_on_page(email_to_find, 1)
    if result:
        await msg.edit_text(f"🔥 *تم العثور عليه في القائمة النشطة:*\n\n📧 البريد: `{result['email']}`\n🆔 المعرف: `{result['id']}`\n📊 الحالة: *{result['status']}*", parse_mode="Markdown")
        return

    await msg.edit_text(f"⏳ لم يتم العثور عليه. جاري البحث في *الأرشيف الكامل*...")
    result = await live_search_on_page(email_to_find, 0)
    if result:
        await msg.edit_text(f"🗄️ *تم العثور عليه في الأرشيف الكامل:*\n\n📧 البريد: `{result['email']}`\n🆔 المعرف: `{result['id']}`\n📊 الحالة: *{result['status']}*", parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ لم يتم العثور على الحساب `{email_to_find}` في أي مكان.", parse_mode="Markdown")

@safe_handler
async def system_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(time.time() - process.create_time()))
    total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
    await update.message.reply_text(
        f"📊 *لوحة تحكم أداء النظام (الحصن الأبدي)*\n\n"
        f"🧠 *استهلاك الذاكرة (RAM):*\n"
        f"   - البوت الحالي: *{memory_usage_mb:.2f} / {total_memory_mb:.0f} ميجابايت*\n"
        f"   - النسبة: *{(memory_usage_mb / total_memory_mb) * 100:.2f}%*\n\n"
        f"⏳ *مدة التشغيل (Uptime):* *{uptime_str}*\n\n"
        f"🛡️ *حالة الحارس (Watchdog):*\n"
        f"   - أراقب الذاكرة كل 5 دقائق. سأقوم بإعادة التدوير إذا تجاوزت *{MEMORY_THRESHOLD_MB} ميجابايت*.",
        parse_mode="Markdown"
    )

async def live_search_on_page(email: str, big_update_value: int) -> dict | None:
    if playwright_page_global is None or playwright_page_global.is_closed(): return None
    search_script = f"""
        (async () => {{
            const forceUpdate = async (updateType) => {{
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
                const response = await fetch('/dataFunctions/updateSenderPage', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' }},
                    body: `date=0&bigUpdate=${{updateType}}&csrf_token=${{csrfToken}}`
                }});
                return response.json();
            }};
            const data = await forceUpdate({big_update_value});
            const accounts = data.data || [];
            const emailToFind = "{email.lower()}";
            const account = accounts.find(acc => acc && acc.length > 2 && acc[2] && acc[2].toLowerCase() === emailToFind);
            if (account) {{ return {{ id: account[0], email: account[2], status: account[6], available: account[7], taken: account[5] }}; }}
            return null;
        }})();
    """
    try:
        return await playwright_page_global.evaluate(search_script)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تنفيذ كود البحث المباشر: {e}")
        return None

# --- 8. نظام الدرع الألماسي (مضاد للانهيار) ---
async def setup_browser_with_retry(playwright_instance: Playwright, max_attempts=5) -> bool:
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"🔄 محاولة إعداد المتصفح ({attempt}/{max_attempts})...")
            await setup_browser_and_page(playwright_instance)
            logger.info("✅ تم إعداد المتصفح بنجاح!")
            return True
        except Exception as e:
            wait_time = min(60 * (2 ** (attempt - 1)), 300)
            logger.error(f"❌ فشل الإعداد: {e}. سأحاول مرة أخرى بعد {wait_time} ثانية...")
            if attempt < max_attempts:
                await send_telegram_notification(f"⚠️ *فشل إعداد المتصفح (محاولة {attempt}/{max_attempts})*\n`{e}`")
                await asyncio.sleep(wait_time)
            else:
                logger.critical("❌ فشلت كل المحاولات. التحول لوضع الطوارئ...")
                await send_telegram_notification("🚨 *تنبيه حرج!*\nفشل إعداد المتصفح بعد 5 محاولات. البوت يعمل بدون مراقبة مباشرة.")
                return False
    return False

async def recycle_browser_safe(playwright_instance: Playwright):
    global browser_instance, browser_context_global, playwright_page_global, is_recycling
    if is_recycling: return
    
    is_recycling = True
    playwright_page_global = None
    
    await send_telegram_notification("⏳ *صيانة تلقائية للذاكرة...*\nالبوت لا يزال يعمل والأوامر الأساسية متاحة.")
    
    if browser_context_global:
        try: await browser_context_global.close()
        except Exception as e: logger.error(f"⚠️ خطأ بسيط أثناء إغلاق السياق: {e}")
    if browser_instance:
        try: await browser_instance.close()
        except Exception as e: logger.error(f"⚠️ خطأ بسيط أثناء إغلاق المتصفح: {e}")
    
    success = await setup_browser_with_retry(playwright_instance, max_attempts=3)
    
    if not success:
        logger.critical("❌ لا يوجد متصفح متاح. البوت يعمل في وضع محدود.")
        await send_telegram_notification("🚨 *البوت في وضع الطوارئ!*\nلا يوجد متصفح. الأوامر الأساسية متاحة.")
    else:
        await send_telegram_notification("🟢 *اكتملت الصيانة بنجاح.*")
    
    is_recycling = False

async def immortal_ram_watchdog(playwright_instance: Playwright):
    while True:
        try:
            await ram_watchdog_core(playwright_instance)
        except Exception as e:
            logger.critical(f"🚨 Watchdog تعطل! {e}. إعادة تشغيل فورية...")
            await send_telegram_notification(f"🚨 *Watchdog تعطل!* `{e}`\nجاري إعادة التشغيل...")
            await asyncio.sleep(10)

async def ram_watchdog_core(playwright_instance: Playwright):
    await asyncio.sleep(300)
    process = psutil.Process(os.getpid())
    while True:
        memory_mb = process.memory_info().rss / (1024 ** 2)
        logger.info(f"📈 [RAM] {memory_mb:.1f}MB")
        if memory_mb > MEMORY_THRESHOLD_MB:
            logger.warning(f"⚠️ تجاوز الحد ({memory_mb:.2f}MB). تفعيل الصيانة...")
            await recycle_browser_safe(playwright_instance)
            await asyncio.sleep(3600)
        else:
            await asyncio.sleep(300)

async def periodic_reconnect(playwright_instance: Playwright):
    while True:
        await asyncio.sleep(600)
        if playwright_page_global is None or playwright_page_global.is_closed():
            logger.info("🔄 محاولة إعادة الاتصال الدورية...")
            success = await setup_browser_with_retry(playwright_instance, max_attempts=2)
            if success:
                await send_telegram_notification("✅ *تم استعادة الاتصال!* المراقبة المباشرة عادت للعمل.")
                break

# --- 9. منطق البوت الرئيسي (محصن ضد الانهيار) ---
async def setup_browser_and_page(playwright_instance: Playwright):
    global browser_instance, browser_context_global, playwright_page_global
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

async def main_bot_logic():
    global telegram_app
    
    load_cache_from_backup()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    telegram_app = application
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("accounts", accounts_command))
    application.add_handler(CommandHandler("details", details_command))
    application.add_handler(CommandHandler("system", system_command))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("🤖 بوت تليجرام نشط ويستمع للأوامر...")
    
    async with async_playwright() as p:
        asyncio.create_task(immortal_ram_watchdog(p))
        asyncio.create_task(cache_backup_task())

        browser_ready = await setup_browser_with_retry(p, max_attempts=5)
        
        if browser_ready:
            await send_telegram_notification("🛡️ *نظام الحصن الأبدي متصل بالكامل!*\nالمراقبة المباشرة نشطة والحماية من التوقف مفعّلة.")
        else:
            logger.warning("⚠️ البوت يعمل في وضع الطوارئ (بدون متصفح).")
            await send_telegram_notification("⚠️ *البوت يعمل في وضع الطوارئ*\nالأوامر الأساسية متاحة، لكن المراقبة المباشرة معطلة. سيتم المحاولة تلقائياً كل 10 دقائق.")
            asyncio.create_task(periodic_reconnect(p))
        
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

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))

    try:
        loop.run_until_complete(main_bot_logic())
    finally:
        logger.info("🏁 تم إيقاف حلقة الأحداث الرئيسية.")
        loop.close()
