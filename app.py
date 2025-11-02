# app.py - الإصدار v9.0 (إصدار الصقر) - إدارة ذاكرة ذكية ومراقبة مستمرة

import asyncio
import json
import logging
import os
import threading
import time
import psutil
from flask import Flask
from playwright.async_api import async_playwright, Page, Browser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. إعداد نظام تسجيل الأحداث (اللوجز) ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- 2. تحميل الإعدادات بذكاء ---
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
    except (FileNotFoundError, json.JSONDecodeError):
        logger.critical("❌ خطأ في تحميل ملف config.json. لا يمكن المتابعة.")
        exit()

# --- 3. استخلاص المتغيرات العالمية والتحقق منها ---
TELEGRAM_BOT_TOKEN = CONFIG.get("telegram", {}).get("bot_token")
ADMIN_IDS = CONFIG.get("telegram", {}).get("admin_ids", [])
WEBSITE_URL = CONFIG.get("website", {}).get("urls", {}).get("sender_page")
COOKIES = list(CONFIG.get("website", {}).get("cookies", {}).items())

if not all([TELEGRAM_BOT_TOKEN, ADMIN_IDS, WEBSITE_URL, COOKIES]):
    logger.critical("❌ الإعدادات ناقصة! تأكد من وجود bot_token, admin_ids, sender_page, و cookies.")
    exit()

# --- 4. متغيرات عالمية وذاكرة التخزين المؤقت ---
accounts_state_cache = {}
is_first_run = True
telegram_app = None
playwright_page_global: Page = None
browser_instance: Browser = None
MAX_CACHE_ENTRIES = 5000  # ✨ حد أقصى لذاكرة الكاش

# ✨ إعدادات تشغيل المتصفح "الرجيم" لتقليل استهلاك الذاكرة
CHROMIUM_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-extensions",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--renderer-process-limit=1",
    "--js-flags=--max-old-space-size=128"
]

# --- 5. كود النبض (Heartbeat) ---
app = Flask(__name__)
@app.route('/')
def heartbeat():
    return f"Bot is alive. Monitoring {len(accounts_state_cache)} accounts."

def run_flask_app():
    app.run(host='0.0.0.0', port=10000)

# --- 6. دوال مساعدة ---
async def send_telegram_notification(message, chat_id=None):
    target_ids = [chat_id] if chat_id else ADMIN_IDS
    for cid in target_ids:
        try:
            await telegram_app.bot.send_message(chat_id=cid, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"❌ فشل في إرسال رسالة إلى {cid}: {e}")

async def on_data_update(data):
    global accounts_state_cache, is_first_run
    logger.info("...[EVENT] تم استقبال تحديث للبيانات من الصفحة...")
    new_accounts_data = data.get("data", [])
    if not isinstance(new_accounts_data, list):
        logger.warning("⚠️ البيانات المستلمة ليست قائمة. التجاهل.")
        return

    current_state = {
        account[2]: {"status": account[6], "id": account[0], "available": account[7], "taken": account[5]}
        for account in new_accounts_data if len(account) > 7 and account[2]
    }

    if is_first_run:
        accounts_state_cache = current_state
        is_first_run = False
        logger.info(f"✅ الحالة الأولية تم تحميلها لـ {len(accounts_state_cache)} حساب.")
        await send_telegram_notification(f"✅ *نظام المراقبة (إصدار الصقر) بدأ العمل!*\nتم تحميل الحالة الأولية لـ *{len(accounts_state_cache)}* حساب.")
        return

    changes_found = []
    for email, new_data in current_state.items():
        old_data = accounts_state_cache.get(email)
        if old_data and old_data["status"] != new_data["status"]:
            change_message = (f"🔥 *تحديث فوري للحالة!*\n\n📧 البريد: `{email}`\n🆔 المعرف: `{new_data['id']}`\n📊 الحالة تغيرت من `{old_data['status']}` إلى `{new_data['status']}`")
            changes_found.append(change_message)

    if changes_found:
        logger.info(f"🎉 تم العثور على {len(changes_found)} تغيير في الحالات!")
        full_report = "\n\n---\n\n".join(changes_found)
        await send_telegram_notification(full_report)

    accounts_state_cache = current_state
    
    if len(accounts_state_cache) > MAX_CACHE_ENTRIES:
        accounts_state_cache = dict(list(accounts_state_cache.items())[-MAX_CACHE_ENTRIES:])
        logger.info(f"🧹 تم تنظيف الكاش للحفاظ على الذاكرة (أبقى على آخر {MAX_CACHE_ENTRIES} حساب).")

# --- 7. أوامر التليجرام ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    welcome_message = (
        "🦅 *أهلاً بك في بوت الصقر للمراقبة (v9.0)!*\n\n"
        "أنا أعمل الآن بنظام إدارة ذاكرة ذكي ومراقبة مستمرة.\n\n"
        "*الأوامر المتاحة:*\n"
        "`/status` - عرض حالة النظام وعدد الحسابات.\n"
        "`/accounts` - عرض قائمة مختصرة بجميع الحسابات وحالاتها.\n"
        "`/details [email]` - بحث مزدوج (نشط وأرشيف) عن حساب معين.\n"
        "`/system` - عرض لوحة تحكم أداء النظام (RAM, CPU)."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    status_message = (f"🟢 *النظام يعمل بشكل طبيعي.*\n\n🧠 الذاكرة تحتوي على *{len(accounts_state_cache)}* حساب.\n🦅 أراقب التحديثات وأحمي الذاكرة بشكل مستمر.")
    await update.message.reply_text(status_message, parse_mode="Markdown")

async def accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    if not accounts_state_cache:
        await update.message.reply_text("⏳ الذاكرة فارغة حالياً، يرجى الانتظار لأول تحديث من الموقع.")
        return
    report_lines = [f"📋 *قائمة الحسابات الحالية ({len(accounts_state_cache)}):*\n"]
    for email, data in accounts_state_cache.items():
        report_lines.append(f"- `{email}`: *{data['status']}*")
    full_report = "\n".join(report_lines)
    if len(full_report) > 4096:
        for i in range(0, len(full_report), 4096):
            await update.message.reply_text(full_report[i:i+4096], parse_mode="Markdown")
    else:
        await update.message.reply_text(full_report, parse_mode="Markdown")

async def live_search_on_page(email: str, big_update_value: int) -> dict | None:
    if playwright_page_global is None or playwright_page_global.is_closed():
        logger.error("❌ المتصفح غير جاهز للبحث المباشر.")
        return None
    logger.info(f"⚡️ Executing LIVE search for '{email}' with bigUpdate={big_update_value}...")
    search_script = f"""
        (() => {{
            const forceUpdate = async (updateType) => {{
                const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
                const response = await fetch('/dataFunctions/updateSenderPage', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest' }},
                    body: `date=0&bigUpdate=${{updateType}}&csrf_token=${{csrfToken}}`
                }});
                return response.json();
            }};
            return forceUpdate({big_update_value}).then(data => {{
                const accounts = data.data || [];
                const emailToFind = "{email.lower()}";
                const account = accounts.find(acc => acc && acc.length > 2 && acc[2] && acc[2].toLowerCase() === emailToFind);
                if (account) {{ return {{ id: account[0], email: account[2], status: account[6], available: account[7], taken: account[5] }}; }}
                return null;
            }});
        }})();
    """
    try:
        return await playwright_page_global.evaluate(search_script)
    except Exception as e:
        logger.error(f"❌ خطأ أثناء تنفيذ كود البحث المباشر: {e}")
        return None

async def details_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("⚠️ يرجى تحديد إيميل بعد الأمر. مثال: `/details user@example.com`")
        return
    email_to_find = context.args[0].lower()
    msg = await update.message.reply_text(f"🔍 البحث عن `{email_to_find}`...")
    if email_to_find in accounts_state_cache:
        account_data = accounts_state_cache[email_to_find]
        details_message = (f"✅ *تم العثور عليه في الذاكرة:*\n\n📧 البريد: `{email_to_find}`\n🆔 المعرف: `{account_data.get('id', 'N/A')}`\n📊 الحالة: *{account_data.get('status', 'غير معروف')}*")
        await msg.edit_text(details_message, parse_mode="Markdown")
        return
    await msg.edit_text(f"⏳ لم يتم العثور عليه في الذاكرة. جاري البحث في *القائمة النشطة*...")
    result = await live_search_on_page(email_to_find, 1)
    if result:
        details_message = (f"🔥 *تم العثور عليه في القائمة النشطة:*\n\n📧 البريد: `{result['email']}`\n🆔 المعرف: `{result['id']}`\n📊 الحالة: *{result['status']}*\n💰 المتاح: *{result.get('available', 'N/A')}*\n💸 المسحوب: *{result.get('taken', 'N/A')}*")
        await msg.edit_text(details_message, parse_mode="Markdown")
        return
    await msg.edit_text(f"⏳ لم يتم العثور عليه. جاري البحث في *الأرشيف الكامل*...")
    result = await live_search_on_page(email_to_find, 0)
    if result:
        details_message = (f"🗄️ *تم العثور عليه في الأرشيف الكامل:*\n\n📧 البريد: `{result['email']}`\n🆔 المعرف: `{result['id']}`\n📊 الحالة: *{result['status']}*\n💰 المتاح: *{result.get('available', 'N/A')}*\n💸 المسحوب: *{result.get('taken', 'N/A')}*")
        await msg.edit_text(details_message, parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ لم يتم العثور على الحساب `{email_to_find}` في أي مكان.")

async def system_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
    cpu_usage = process.cpu_percent(interval=0.1)
    uptime_seconds = time.time() - process.create_time()
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    total_memory_mb = psutil.virtual_memory().total / (1024 * 1024)
    system_report = (
        f"📊 *لوحة تحكم أداء النظام (إصدار الصقر)*\n\n"
        f"🧠 *استهلاك الذاكرة (RAM):*\n"
        f"   - البوت الحالي: *{memory_usage_mb:.2f} ميجابايت*\n"
        f"   - إجمالي المتاح: *{total_memory_mb:.2f} ميجابايت*\n"
        f"   - النسبة: *{(memory_usage_mb / total_memory_mb) * 100:.2f}%*\n\n"
        f"💻 *استهلاك المعالج (CPU):*\n"
        f"   - *{cpu_usage}%*\n\n"
        f"⏳ *مدة التشغيل (Uptime):*\n"
        f"   - *{uptime_str}* (ساعة:دقيقة:ثانية)\n\n"
        f"🦅 *حالة الحارس (Watchdog):*\n"
        f"   - أراقب الذاكرة كل دقيقتين. سأقوم بعمل `Refresh` تلقائي إذا تجاوزت *420 ميجابايت*."
    )
    await update.message.reply_text(system_report, parse_mode="Markdown")

# --- 8. نظام الحارس الذكي (Smart Watchdog) ---
async def light_refresh():
    if playwright_page_global and not playwright_page_global.is_closed():
        try:
            logger.warning("🔄 [Watchdog] تنفيذ Refresh خفيف للصفحة...")
            await playwright_page_global.reload(wait_until="domcontentloaded", timeout=60000)
            logger.info("✅ [Watchdog] تم تنفيذ Refresh خفيف بنجاح.")
        except Exception as e:
            logger.error(f"🚫 [Watchdog] فشل في عمل Refresh خفيف: {e}.")
    else:
        logger.error("🚫 [Watchdog] لا يمكن عمل Refresh لأن الصفحة مغلقة!")

async def ram_watchdog(threshold_mb=420):
    process = psutil.Process(os.getpid())
    while True:
        await asyncio.sleep(120)
        mem_usage = process.memory_info().rss / (1024 ** 2)
        logger.info(f"📈 [RAM] الاستهلاك الحالي: {mem_usage:.1f}MB")
        if mem_usage > threshold_mb:
            await send_telegram_notification(f"⚠️ *تحذير ذاكرة مرتفعة!*\nالاستهلاك الحالي: *{mem_usage:.1f}MB*.\n🦅 جاري تنفيذ `Refresh` خفيف لتنظيف الذاكرة...")
            await light_refresh()

# --- 9. منطق البوت الرئيسي (Playwright) ---
async def main_bot_logic():
    global telegram_app, playwright_page_global, browser_instance
    
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
    logger.info("🤖 بوت تليجرام بدأ العمل ويستمع للأوامر...")

    asyncio.create_task(ram_watchdog())

    async with async_playwright() as p:
        logger.info("🚀 تشغيل المتصفح بوضع 'الرجيم' لتقليل استهلاك الذاكرة...")
        browser_instance = await p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        
        context = await browser_instance.new_context(viewport={"width": 800, "height": 600}, java_script_enabled=True)
        
        await context.route("**/*", lambda route: route.abort() if route.request.resource_type in {"image", "font", "media", "stylesheet"} else route.continue_())
        logger.info("⛔️ تم منع تحميل الصور والخطوط لتسريع الأداء.")

        playwright_cookies = [{"name": name, "value": value, "domain": ".utautotransfer.com", "path": "/"} for name, value in COOKIES]
        await context.add_cookies(playwright_cookies)
        logger.info("🍪 تم وضع الكوكيز بنجاح.")

        page = await context.new_page()
        playwright_page_global = page
        
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
            await page.goto(WEBSITE_URL, timeout=120000, wait_until="domcontentloaded")
        except Exception as e:
            logger.error(f"❌ فشل في تحميل الصفحة: {e}")
            await send_telegram_notification(f"🔴 *خطأ فادح:*\nفشل في تحميل صفحة الموقع.\n`{e}`")
            return

        logger.info("✅ تم تحميل الصفحة بنجاح. النظام الآن تحت المراقبة المستمرة...")
        await send_telegram_notification("🦅 *نظام الصقر متصل الآن!*\nأنا أراقب التحديثات وأحمي الذاكرة بشكل مستمر.")

        while True:
            await asyncio.sleep(3600)

# --- 10. نقطة بداية التشغيل ---
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    logger.info("🌐 خدمة النبض (Heartbeat) بدأت العمل...")
    
    try:
        asyncio.run(main_bot_logic())
    except KeyboardInterrupt:
        logger.info("🛑 إيقاف النظام...")
    except Exception as e:
        logger.critical(f"❌ حدث خطأ فادح أدى إلى توقف البوت: {e}", exc_info=True)
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))
        else:
            asyncio.run(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))
