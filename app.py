# main.py (أو app.py) - v2.0 - جاهز للنشر على Render (خطة مجانية)

import asyncio
import json
import logging
import threading
from flask import Flask
from playwright.async_api import async_playwright
from telegram import Bot

# --- إعدادات اللوجر ---
# هذا الجزء يقوم بإعداد نظام تسجيل الأحداث (اللوجز) لعرض معلومات التشغيل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- تحميل الإعدادات من ملف config.json ---
# يتم تحميل الإعدادات الحساسة مثل توكن البوت والكوكيز من ملف خارجي
try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
except FileNotFoundError:
    logger.critical("❌ ملف config.json غير موجود! يرجى إنشاؤه ووضع الإعدادات بداخله.")
    exit()
except json.JSONDecodeError:
    logger.critical("❌ خطأ في قراءة ملف config.json. تأكد من أن صيغته صحيحة.")
    exit()

# --- متغيرات عالمية أساسية ---
# يتم استخلاص المتغيرات المهمة من ملف الإعدادات لسهولة الوصول إليها
TELEGRAM_BOT_TOKEN = CONFIG.get("telegram", {}).get("bot_token")
ADMIN_IDS = CONFIG.get("telegram", {}).get("admin_ids", [])
WEBSITE_URL = CONFIG.get("website", {}).get("urls", {}).get("sender_page")
COOKIES = list(CONFIG.get("website", {}).get("cookies", {}).items())

# --- التحقق من وجود الإعدادات الأساسية ---
if not all([TELEGRAM_BOT_TOKEN, ADMIN_IDS, WEBSITE_URL, COOKIES]):
    logger.critical("❌ الإعدادات في config.json ناقصة! تأكد من وجود bot_token, admin_ids, sender_page, و cookies.")
    exit()

# --- ذاكرة تخزين مؤقتة للحالة ---
# هذا القاموس سيحتفظ بآخر حالة معروفة لكل حساب لتتم مقارنتها مع التحديثات الجديدة
accounts_state_cache = {}
is_first_run = True

# --- تهيئة بوت التليجرام ---
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)


# --- ✨✨ كود النبض (Heartbeat) لإبقاء الخدمة مستيقظة على Render ---
# هذا الجزء ينشئ موقع ويب صغير جداً، وظيفته الوحيدة هي الرد على "الزيارات"
# التي تأتي من خدمة مثل Uptime Robot، لمنع Render من "تنويم" الخدمة المجانية.
app = Flask(__name__)

@app.route('/')
def heartbeat():
    """
    نقطة النهاية (endpoint) التي يتم استدعاؤها للحفاظ على الخدمة نشطة.
    """
    # يمكنك عرض عدد الحسابات الحالية كمعلومة إضافية
    active_accounts_count = len(accounts_state_cache)
    return f"Bot is alive and monitoring {active_accounts_count} accounts."

def run_flask_app():
    """
    دالة لتشغيل تطبيق فلاسك في "ثريد" منفصل.
    """
    # Render يختار البورت تلقائياً، لذلك نستخدم بورت شائع مثل 10000
    # ولا داعي للقلق من تعارضه مع خدمات أخرى.
    app.run(host='0.0.0.0', port=10000)

# --------------------------------------------------------------------


async def send_telegram_notification(message):
    """
    دالة مسؤولة عن إرسال إشعارات التليجرام إلى جميع المسؤولين.
    """
    for chat_id in ADMIN_IDS:
        try:
            await telegram_bot.send_message(
                chat_id=chat_id, text=message, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"❌ فشل في إرسال رسالة إلى {chat_id}: {e}")


async def on_data_update(data):
    """
    هذه هي الدالة السحرية! يتم استدعاؤها تلقائياً من كود الجافا سكريبت
    المحقون في الصفحة كلما حدث تحديث للبيانات.
    """
    global accounts_state_cache, is_first_run
    logger.info("...[EVENT] تم استقبال تحديث للبيانات من الصفحة...")

    new_accounts_data = data.get("data", [])
    if not new_accounts_data:
        logger.warning("⚠️ التحديث المستلم لا يحتوي على بيانات حسابات (data is empty).")
        return

    # بناء الحالة الحالية من البيانات الجديدة
    current_state = {
        account[2]: account[6] for account in new_accounts_data if len(account) > 6 and account[2]
    }

    # في أول تشغيل، يتم فقط ملء الذاكرة بدون إرسال إشعارات
    if is_first_run:
        accounts_state_cache = current_state
        is_first_run = False
        logger.info(f"✅ الحالة الأولية تم تحميلها لـ {len(accounts_state_cache)} حساب.")
        await send_telegram_notification(
            f"✅ *نظام المراقبة الفورية بدأ العمل!*\nتم تحميل الحالة الأولية لـ *{len(accounts_state_cache)}* حساب."
        )
        return

    # مقارنة الحالة الحالية بالحالة المخزنة في الذاكرة لاكتشاف التغييرات
    changes_found = []
    for email, new_status in current_state.items():
        old_status = accounts_state_cache.get(email)
        # إرسال إشعار فقط إذا كان الحساب موجوداً من قبل وحالته تغيرت
        if old_status is not None and old_status != new_status:
            change_message = (
                f"🔥 *تحديث فوري للحالة!*\n\n"
                f"📧 البريد: `{email}`\n"
                f"📊 الحالة تغيرت من `{old_status}` إلى `{new_status}`"
            )
            changes_found.append(change_message)

    if changes_found:
        logger.info(f"🎉 تم العثور على {len(changes_found)} تغيير في الحالات!")
        # إرسال الإشعارات المجمعة
        full_report = "\n\n---\n\n".join(changes_found)
        await send_telegram_notification(full_report)

    # تحديث الذاكرة بالحالة الجديدة لتكون جاهزة للمقارنة القادمة
    accounts_state_cache = current_state


async def main_bot_logic():
    """
    الوظيفة الرئيسية التي تشغل متصفح Playwright وتحقن الكود.
    """
    async with async_playwright() as p:
        logger.info("🚀 تشغيل المتصفح في الخلفية...")
        # يمكن تغيير headless إلى False لرؤية المتصفح وهو يعمل أثناء الاختبار
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()

        # ضبط الكوكيز لتسجيل الدخول تلقائياً
        playwright_cookies = [
            {"name": name, "value": value, "domain": ".utautotransfer.com", "path": "/"}
            for name, value in COOKIES
        ]
        await context.add_cookies(playwright_cookies)
        logger.info("🍪 تم وضع الكوكيز بنجاح.")

        page = await context.new_page()

        # ربط دالة البايثون `on_data_update` لتكون متاحة للاستدعاء من الجافا سكريبت
        await page.expose_function("onDataUpdate", on_data_update)
        logger.info("🔗 تم ربط دالة البايثون بالصفحة.")

        # قراءة كود الحقن من ملف injector.js
        try:
            with open("injector.js", "r", encoding="utf-8") as f:
                injector_script = f.read()
        except FileNotFoundError:
            logger.critical("❌ ملف injector.js غير موجود! لا يمكن المتابعة.")
            return

        # حقن الكود الذي "يتجسس" على البيانات في كل مرة يتم فيها تحميل الصفحة
        await page.add_init_script(injector_script)
        logger.info("💉 تم تجهيز كود الحقن للعمل.")

        logger.info(f"🧭 جاري الانتقال إلى: {WEBSITE_URL}")
        try:
            await page.goto(WEBSITE_URL, timeout=90000) # زيادة مهلة الانتظار
        except Exception as e:
            logger.error(f"❌ فشل في تحميل الصفحة: {e}")
            await send_telegram_notification(f"🔴 *خطأ فادح:*\nفشل في تحميل صفحة الموقع. قد تكون الكوكيز غير صالحة أو الموقع لا يعمل.\n`{e}`")
            return

        logger.info("✅ تم تحميل الصفحة بنجاح. النظام الآن يستمع للتحديثات...")
        await send_telegram_notification(
            "🟢 *النظام متصل الآن!*\nأنا أستمع للتحديثات الفورية من الموقع."
        )

        # حلقة لا نهائية لإبقاء السكربت يعمل
        while True:
            await asyncio.sleep(3600) # ينام لمدة ساعة، لكنه يظل يستمع للأحداث


if __name__ == "__main__":
    # تشغيل موقع فلاسك في "ثريد" منفصل لضمان عدم توقف البوت الرئيسي
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # هذا يجعل الثريد يتوقف عند توقف البرنامج الرئيسي
    flask_thread.start()
    logger.info("🌐 خدمة النبض (Heartbeat) بدأت العمل...")
    
    # تشغيل منطق البوت الرئيسي
    try:
        asyncio.run(main_bot_logic())
    except KeyboardInterrupt:
        logger.info("🛑 إيقاف النظام...")
    except Exception as e:
        logger.critical(f"❌ حدث خطأ فادح أدى إلى توقف البوت: {e}")
        # حاول إرسال إشعار أخير إذا أمكن
        asyncio.run(send_telegram_notification(f"🚨 *توقف النظام!* 🚨\nحدث خطأ فادح: `{e}`"))

