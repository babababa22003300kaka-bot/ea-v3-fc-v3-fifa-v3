# app.py - الإصدار النهائي v7.0 - مع إعادة تدوير ذكية للمتصفح

import asyncio
import json
import logging
import os
import threading
import time
from flask import Flask
from playwright.async_api import async_playwright, Page, Browser
from telegram import Update, Bot
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

# --- 4. متغيرات عالمية وذاكرة التخزين المؤقت ---
accounts_state_cache = {}
is_first_run = True
telegram_app = None
playwright_page_global: Page = None
browser_instance: Browser = None # ✨ متغير جديد للاحتفاظ بالمتصفح

# --- 5. كود النبض (Heartbeat) ---
app = Flask(__name__)
@app.route('/')
def heartbeat():
    active_accounts_count = len(accounts_state_cache)
    return f"Bot is alive and monitoring {active_accounts_count} accounts."

def run_flask_app():
    app.run(host='0.0.0.0', port=10000)

# --- 6. دوال مساعدة ---
async def send_telegram_notification(message, chat_id=None):
    target_ids = [chat_id] if chat_id else ADMIN_IDS
    for cid in target_ids:
        try:
            await telegram_app.bot.send_message(
                chat_id=cid, text=message, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ فشل في إرسال رسالة إلى {cid}: {e}")

async def on_data_update(data):
    global accounts_state_cache, is_first_run
    logger.info("...[EVENT] تم استقبال تحديث للبيانات من الصفحة...")
    # (باقي الكود كما هو بدون تغيير)
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


# --- 7. أوامر التليجرام ---
# (كل الأوامر كما هي بدون تغيير)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    welcome_message = (
        "👋 *أهلاً بك في بوت المراقبة الفورية (v7.0 - إعادة تدوير ذكية)!*\n\n"
        "هذا البوت يعمل الآن على السحابة ويراقب التغييرات بشكل فوري.\n\n"
        "*الأوامر المتاحة:*\n"
        "`/status` - عرض حالة النظام وعدد الحسابات.\n"
        "`/accounts` - عرض قائمة مختصرة بجميع الحسابات وحالاتها.\n"
        "`/details [email]` - بحث مزدوج (نشط وأرشيف) عن حساب معين."
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ADMIN_IDS: return
    status_message = (
        f"🟢 *النظام يعمل بشكل طبيعي.*\n\n"
        f"🧠 الذاكرة تحتوي على *{len(accounts_state_cache)}* حساب.\n"
        f"🤖 أستمع للتحديثات بشكل فوري عبر تقنية حقن الجافا سكريبت."
    )
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
    if playwright_page_global is None:
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
                if (account) {{
                    return {{ id: account[0], email: account[2], status: account[6], available: account[7], taken: account[5] }};
                }}
                return null;
            }});
        }})();
    """
    try:
        result = await playwright_page_global.evaluate(search_script)
        return result
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
        details_message = (
            f"✅ *تم العثور عليه في الذاكرة:*\n\n"
            f"📧 البريد: `{email_to_find}`\n"
            f"🆔 المعرف: `{account_data.get('id', 'N/A')}`\n"
            f"📊 الحالة: *{account_data.get('status', 'غير معروف')}*"
        )
        await msg.edit_text(details_message, parse_mode="Markdown")
        return
    await msg.edit_text(f"⏳ لم يتم العثور عليه في الذاكرة. جاري البحث في *القائمة النشطة*...")
    result = await live_search_on_page(email_to_find, 1)
    if result:
        details_message = (
            f"🔥 *تم العثور عليه في القائمة النشطة:*\n\n"
            f"📧 البريد: `{result['email']}`\n"
            f"🆔 المعرف: `{result['id']}`\n"
            f"📊 الحالة: *{result['status']}*\n"
            f"💰 المتاح: *{result.get('available', 'N/A')}*\n"
            f"💸 المسحوب: *{result.get('taken', 'N/A')}*"
        )
        await msg.edit_text(details_message, parse_mode="Markdown")
        return
    await msg.edit_text(f"⏳ لم يتم العثور عليه. جاري البحث في *الأرشيف الكامل*...")
    result = await live_search_on_page(email_to_find, 0)
    if result:
        details_message = (
            f"🗄️ *تم العثور عليه في الأرشيف الكامل:*\n\n"
            f"📧 البريد: `{result['email']}`\n"
            f"🆔 المعرف: `{result['id']}`\n"
            f"📊 الحالة: *{result['status']}*\n"
            f"💰 المتاح: *{result.get('available', 'N/A')}*\n"
            f"💸 المسحوب: *{result.get('taken', 'N/A')}*"
        )
        await msg.edit_text(details_message, parse_mode="Markdown")
    else:
        await msg.edit_text(f"❌ لم يتم العثور على الحساب `{email_to_find}` في أي مكان.")


# --- 8. ✨✨ منطق إعادة التدوير الذكي ✨✨ ---
async def smart_recycler():
    """
    هذه الدالة تعمل في الخلفية وتقوم بإعادة تشغيل المتصفح كل 6 ساعات
    لتحرير الذاكرة ومنع مشكلة "Ran out of memory".
    """
    global browser_instance, playwright_page_global
    
    # انتظر قليلاً في البداية للسماح للنظام بالاستقرار
    await asyncio.sleep(300) 
    
    while True:
        # انتظر لمدة 6 ساعات
        logger.info(f"♻️ [Recycler] سأقوم بإعادة تدوير المتصفح خلال 6 ساعات لتنظيف الذاكرة.")
        await asyncio.sleep(6 * 60 * 60)
        
        logger.warning("♻️ [Recycler] حان وقت إعادة التدوير! جاري إغلاق المتصفح الحالي...")
        await send_telegram_notification("⏳ *صيانة دورية:*\nجاري إعادة تشغيل المتصفح لتنظيف الذاكرة (تستغرق ~30 ثانية).")
        
        if browser_instance:
            try:
                await browser_instance.close()
                logger.info("♻️ [Recycler] تم إغلاق المتصفح بنجاح.")
            except Exception as e:
                logger.error(f"♻️ [Recycler] خطأ أثناء إغلاق المتصفح: {e}")

        # إعادة تهيئة المتصفح والصفحة
        # هذا الجزء هو نسخة مصغرة من بداية `main_bot_logic`
        try:
            async with async_playwright() as p:
                logger.info("🚀 [Recycler] تشغيل متصفح جديد...")
                browser_instance = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
                context = await browser_instance.new_context()

                playwright_cookies = [
                    {"name": name, "value": value, "domain": ".utautotransfer.com", "path": "/"}
                    for name, value in COOKIES
                ]
                await context.add_cookies(playwright_cookies)
                
                page = await context.new_page()
                playwright_page_global = page
                
                await page.expose_function("onDataUpdate", on_data_update)
                
                with open("injector.js", "r", encoding="utf-8") as f:
                    injector_script = f.read()
                await page.add_init_script(injector_script)
                
                await page.goto(WEBSITE_URL, timeout=120000)
                
                logger.info("✅ [Recycler] تمت إعادة الاتصال بنجاح!")
                await send_telegram_notification("🟢 *اكتملت الصيانة.*\nالنظام عاد للعمل بشكل طبيعي.")

        except Exception as e:
            logger.critical(f"❌ [Recycler] فشل فادح أثناء إعادة التدوير: {e}")
            await send_telegram_notification(f"🚨 *خطأ فادح أثناء الصيانة:*\nفشل النظام في إعادة تشغيل المتصفح. `{e}`")
            # انتظر فترة أطول قبل المحاولة مرة أخرى
            await asyncio.sleep(60 * 15)


# --- 9. منطق البوت الرئيسي (Playwright) ---
async def main_bot_logic():
    """الوظيفة الرئيسية التي تشغل كل شيء معاً."""
    global telegram_app, playwright_page_global, browser_instance
    
    # تهيئة وتشغيل بوت التليجرام
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    telegram_app = application
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("accounts", accounts_command))
    application.add_handler(CommandHandler("details", details_command))

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    logger.info("🤖 بوت تليجرام بدأ العمل ويستمع للأوامر...")

    # تشغيل "إعادة التدوير الذكية" في الخلفية
    asyncio.create_task(smart_recycler())

    # تشغيل المتصفح لأول مرة
    async with async_playwright() as p:
        logger.info("🚀 تشغيل المتصفح لأول مرة...")
        browser_instance = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = await browser_instance.new_context()

        playwright_cookies = [
            {"name": name, "value": value, "domain": ".utautotransfer.com", "path": "/"}
            for name, value in COOKIES
        ]
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
            await page.goto(WEBSITE_URL, timeout=120000)
        except Exception as e:
            logger.error(f"❌ فشل في تحميل الصفحة: {e}")
            await send_telegram_notification(f"🔴 *خطأ فادح:*\nفشل في تحميل صفحة الموقع.\n`{e}`")
            return

        logger.info("✅ تم تحميل الصفحة بنجاح. النظام الآن يستمع للتحديثات...")
        await send_telegram_notification(
            "🟢 *النظام متصل الآن!*\nأنا أستمع للتحديثات الفورية من الموقع."
        )

        # حلقة لا نهائية لإبقاء السكربت الرئيسي يعمل
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
        logger.critical(f"❌ حدث خطأ فادح أدى إلى توقف البوت: {e}")
        # محاولة إرسال إشعار أخير
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))
        else:
            asyncio.run(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))

