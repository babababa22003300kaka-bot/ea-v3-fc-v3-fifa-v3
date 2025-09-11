import asyncio
import hashlib
import logging
import os
import re
import sqlite3
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from cryptography.fernet import Fernet
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)


# ================================ إدارة الرسائل المركزية  ================================
class MessageManager:
    @staticmethod
    async def send_or_edit_message(
        update: Update, text: str, reply_markup=None, parse_mode="Markdown"
    ):
        """
        دالة مركزية لإرسال أو تعديل الرسائل
        تضمن وجود رسالة واحدة نشطة فقط
        """
        try:
            if update.callback_query:
                # إذا كان التفاعل من زر، نعدل نفس الرسالة
                await update.callback_query.edit_message_text(
                    text=text, reply_markup=reply_markup, parse_mode=parse_mode
                )
            else:
                # إذا كان التفاعل من رسالة نصية أو أمر، نرسل رسالة جديدة
                await update.message.reply_text(
                    text=text, reply_markup=reply_markup, parse_mode=parse_mode
                )
        except Exception as e:
            logger.error(f"خطأ في MessageManager: {e}")
            # في حالة فشل التعديل، نرسل رسالة جديدة
            if update.effective_chat:
                try:
                    if update.callback_query:
                        await update.callback_query.message.reply_text(
                            text=text, reply_markup=reply_markup, parse_mode=parse_mode
                        )
                    else:
                        await update.message.reply_text(
                            text=text, reply_markup=reply_markup, parse_mode=parse_mode
                        )
                except:
                    pass


# إنشاء مدير الرسائل العام
message_manager = MessageManager()


# ================================ نظام الحماية الشامل ================================
class SecurityManager:
    def __init__(self):
        self.failed_attempts = defaultdict(lambda: {"count": 0, "blocked_until": None})
        self.user_requests = defaultdict(list)
        self.encryption_key = self._get_or_create_key()
        self.cipher = Fernet(self.encryption_key)

    def _get_or_create_key(self):
        """إنشاء أو جلب مفتاح التشفير"""
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def encrypt_data(self, data):
        """تشفير البيانات الحساسة"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        """فك تشفير البيانات"""
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except:
            return encrypted_data

    def check_rate_limit(self, user_id, max_requests=20):
        """فحص معدل الطلبات - مكافحة الإغراق"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # تنظيف الطلبات القديمة
        self.user_requests[user_id] = [
            req_time
            for req_time in self.user_requests[user_id]
            if req_time > minute_ago
        ]

        # التحقق من تجاوز الحد المسموح
        if len(self.user_requests[user_id]) >= max_requests:
            return False

        # إضافة الطلب الحالي
        self.user_requests[user_id].append(now)
        return True

    def record_failed_attempt(self, user_id, action="general"):
        """تسجيل محاولة فاشلة"""
        key = f"{user_id}_{action}"
        self.failed_attempts[key]["count"] += 1

        if self.failed_attempts[key]["count"] >= 5:
            # قفل لمدة 15 دقيقة
            self.failed_attempts[key]["blocked_until"] = datetime.now() + timedelta(
                minutes=15
            )
            return True  # مقفل
        return False  # غير مقفل

    def is_blocked(self, user_id, action="general"):
        """فحص إذا كان المستخدم مقفل"""
        key = f"{user_id}_{action}"
        blocked_until = self.failed_attempts[key]["blocked_until"]

        if blocked_until and datetime.now() < blocked_until:
            remaining = blocked_until - datetime.now()
            return True, remaining.seconds // 60  # مقفل مع الدقائق المتبقية

        # إذا انتهت فترة القفل، إعادة تعيين العداد
        if blocked_until and datetime.now() >= blocked_until:
            self.failed_attempts[key] = {"count": 0, "blocked_until": None}

        return False, 0

    def reset_failed_attempts(self, user_id, action="general"):
        """إعادة تعيين المحاولات الفاشلة بعد نجاح العملية"""
        key = f"{user_id}_{action}"
        self.failed_attempts[key] = {"count": 0, "blocked_until": None}


# إنشاء مدير الأمان العام
security_manager = SecurityManager()


# ================================ ديكوريتر الحماية ================================
def security_check(func):
    """ديكوريتر للحماية من الإغراق والهجمات"""

    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id

        # فحص معدل الطلبات
        if not security_manager.check_rate_limit(user_id):
            await update.message.reply_text(
                "🚫 **تم اكتشاف نشاط مشبوه**\n\n"
                "⚠️ تم تجاوز الحد المسموح من الطلبات\n"
                "يرجى الانتظار دقيقة واحدة قبل المحاولة مرة أخرى\n\n"
                "🔒 **هذا الإجراء لحماية النظام من الاستغلال**",
                parse_mode="Markdown",
            )
            return

        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"خطأ في {func.__name__}: {e}")
            await update.message.reply_text(
                "❌ **حدث خطأ مؤقت**\n\n"
                "يرجى المحاولة مرة أخرى خلال دقائق\n"
                "إذا استمرت المشكلة، تواصل مع الدعم",
                parse_mode="Markdown",
            )

    return wrapper


# ================================ إعدادات البوت ================================
BOT_TOKEN = "7607085569:AAEDNKwt8j8B_CjG5gjKLJ8MLjrTRCCrx6k"
ADMIN_ID = 1124247595

# إعداد التسجيل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ================================ خطوات التسجيل ================================
class RegistrationSteps:
    PLATFORM = 1
    WHATSAPP = 2
    PAYMENT = 3
    COMPLETE = 4


# ================================ منصات اللعب ================================
class Platforms:
    DATA = {"PlayStation": "🎮 PlayStation", "Xbox": "❎ Xbox", "PC": "💻 PC"}

    @classmethod
    def get_keyboard(cls):
        return [
            [
                InlineKeyboardButton(
                    "🎮 PlayStation", callback_data="platform_PlayStation"
                )
            ],
            [InlineKeyboardButton("❎ Xbox", callback_data="platform_Xbox")],
            [InlineKeyboardButton("💻 PC", callback_data="platform_PC")],
        ]


# ================================ طرق الدفع ================================
class PaymentMethods:
    DATA = {
        "vodafone_cash": "⭕️ فودافون كاش",
        "etisalat_cash": "🟢 اتصالات كاش",
        "orange_cash": "🍊 أورانج كاش",
        "we_cash": "🟣 وي كاش",
        "bank_wallet": "🏦 محفظة بنكية",
        "telda": "💳 تيلدا",
        "instapay": "🔗 إنستا باي",
    }

    @classmethod
    def get_keyboard(cls):
        return [
            [
                InlineKeyboardButton(
                    "⭕️ فودافون كاش", callback_data="payment_vodafone_cash"
                )
            ],
            [
                InlineKeyboardButton(
                    "🟢 اتصالات كاش", callback_data="payment_etisalat_cash"
                )
            ],
            [
                InlineKeyboardButton(
                    "🍊 أورانج كاش", callback_data="payment_orange_cash"
                )
            ],
            [InlineKeyboardButton("🟣 وي كاش", callback_data="payment_we_cash")],
            [
                InlineKeyboardButton(
                    "🏦 محفظة بنكية", callback_data="payment_bank_wallet"
                )
            ],
            [InlineKeyboardButton("💳 تيلدا", callback_data="payment_telda")],
            [InlineKeyboardButton("🔗 إنستا باي", callback_data="payment_instapay")],
        ]


# ================================ قاعدة البيانات ================================
class Database:
    DB_NAME = "fc26_users.db"

    @classmethod
    def init_db(cls):
        """تهيئة قاعدة البيانات"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                platform TEXT,
                whatsapp TEXT,
                payment_method TEXT,
                payment_data TEXT,
                step INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    @classmethod
    def get_user(cls, user_id):
        """جلب بيانات المستخدم"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    @classmethod
    def create_user(cls, user_id, username):
        """إنشاء مستخدم جديد"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, username, step) VALUES (?, ?, ?)",
            (user_id, username, RegistrationSteps.PLATFORM),
        )
        conn.commit()
        conn.close()

    @classmethod
    def update_user_step(cls, user_id, step):
        """تحديث خطوة المستخدم"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET step = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (step, user_id),
        )
        conn.commit()
        conn.close()

    @classmethod
    def update_user_field(cls, user_id, field, value):
        """تحديث حقل معين للمستخدم مع التشفير للبيانات الحساسة"""
        # البيانات الحساسة التي تحتاج تشفير
        sensitive_fields = ["whatsapp", "payment_data", "username"]

        if field in sensitive_fields and value:
            value = security_manager.encrypt_data(value)

        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE users SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
            (value, user_id),
        )
        conn.commit()
        conn.close()

    @classmethod
    def get_user_decrypted(cls, user_id):
        """جلب بيانات المستخدم مع فك التشفير"""
        user = cls.get_user(user_id)
        if not user:
            return None

        # فك تشفير البيانات الحساسة
        user_list = list(user)
        sensitive_indices = [1, 3, 5]  # username, whatsapp, payment_data

        for i in sensitive_indices:
            if user_list[i]:
                user_list[i] = security_manager.decrypt_data(user_list[i])

        return tuple(user_list)

    @classmethod
    def delete_user(cls, user_id):
        """حذف المستخدم"""
        conn = sqlite3.connect(cls.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()


# ================================ التحقق من البيانات ================================
class Validators:
    @staticmethod
    def validate_phone_number(phone):
        """التحقق من صحة رقم الهاتف المصري (11 رقم - أرقام فقط)"""
        # إزالة جميع المسافات والرموز
        phone = re.sub(r"[^\d]", "", phone)

        # التحقق من أن النص يحتوي على أرقام فقط
        if not phone.isdigit():
            return False

        # التحقق من الطول والبداية
        if len(phone) == 11 and phone.startswith(("010", "011", "012", "015")):
            return True
        return False

    @staticmethod
    def validate_card_number(card):
        """التحقق من صحة رقم البطاقة (16 رقم - أرقام فقط مع السماح بالمسافات والنقوش)"""
        # إزالة جميع المسافات والرموز trừ الأرقام
        card_digits_only = re.sub(r"[^\d]", "", card)

        # التحقق من أن النص يحتوي على أرقام فقط بعد التنظيف
        if not card_digits_only.isdigit():
            return False

        # التحقق من أن الطول هو 16 رقم بالضبط بعد التنظيف
        if len(card_digits_only) == 16:
            return True
        return False

    @staticmethod
    def extract_instapay_link(text):
        """استخلاص رابط إنستا باي من النص - روابط فقط"""
        patterns = [
            r"(https://ipn\.eg/S/[^\s]+)",
            r"(https://[^\s]*instapay[^\s]*)",
            r"(https://[^\s]*\.instapay[^\s]*)",
            r"(ipn\.eg/[^\s]+)",
            r"(instapay\.com/[^\s]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                link = match.group(1)
                if not link.startswith("https://"):
                    link = "https://" + link
                return link

        # فقط روابط إنستا باي - من غير اسماء مستخدمين
        return None


# ================================ رسائل النظام ================================
class Messages:
    WELCOME = (
        "🎮 **مرحباً بك في FC 26 - EA SPORTS**\n\n"
        "📝 **إعداد الملف الشخصي**\n\n"
        "🎯 **اختر منصة اللعب:**"
    )

    WHATSAPP_REQUEST = (
        "📱 **رقم الواتساب**\n\n"
        "يرجى إدخال رقم الواتساب:\n"
        "📍 **أرقام فقط** (بدون حروف أو رموز)\n"
        "📍 **11 رقم** يبدأ بـ 010/011/012/015"
    )

    PAYMENT_REQUEST = "💳 **طريقة الدفع المفضلة:**\n\nاختر طريقة الدفع:"

    COMPLETION_SUCCESS = (
        "🎉 **تم حفظ بياناتك بنجاح!**\n\n"
        "✅ **مرحباً بك في عالم FC 26**\n\n"
        "🔒 *بياناتك محمية بأعلى معايير الأمان والتشفير العالمي*\n\n"
        "يمكنك الآن الاستمتاع بجميع المميزات!"
    )

    @staticmethod
    def get_whatsapp_saved(whatsapp):
        return f"✅ **تم حفظ رقم الواتساب:** `{whatsapp}`\n\n"

    @staticmethod
    def get_platform_saved(platform):
        return f"✅ **تم اختيار المنصة:** {Platforms.DATA[platform]}\n\n"

    @staticmethod
    def get_payment_saved(payment_method):
        return f"✅ **تم اختيار:** {PaymentMethods.DATA[payment_method]}\n\n"


# ================================ معالج المنصات ================================
class PlatformHandler:
    @staticmethod
    async def show_platform_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """عرض اختيار المنصة - رسالة واحدة فقط"""
        keyboard = Platforms.get_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message_manager.send_or_edit_message(
            update, Messages.WELCOME, reply_markup=reply_markup
        )

    @staticmethod
    async def handle_platform_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالج اختيار المنصة - تحديث نفس الرسالة"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        platform = query.data.replace("platform_", "")

        # حفظ المنصة
        Database.update_user_field(user_id, "platform", platform)
        Database.update_user_step(user_id, RegistrationSteps.WHATSAPP)

        # تحديث نفس الرسالة بالخطوة التالية
        await message_manager.send_or_edit_message(
            update, Messages.get_platform_saved(platform) + Messages.WHATSAPP_REQUEST
        )


# ================================ معالج الواتساب ================================
class WhatsAppHandler:
    @staticmethod
    @security_check
    async def handle_whatsapp_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج إدخال رقم الواتساب - رسالة واحدة فقط"""
        user_id = update.effective_user.id
        original_input = update.message.text

        # فحص الحظر
        is_blocked, remaining_minutes = security_manager.is_blocked(
            user_id, "whatsapp_input"
        )
        if is_blocked:
            await message_manager.send_or_edit_message(
                update,
                f"🔒 **تم قفل هذه الميزة مؤقتاً**\n\n"
                f"⏱️ **الوقت المتبقي:** {remaining_minutes} دقيقة\n\n"
                f"**السبب:** محاولات متكررة خاطئة\n"
                f"يرجى الانتظار حتى انتهاء فترة القفل",
            )
            return

        # تنظيف المدخل من أي شيء غير الأرقام
        whatsapp = re.sub(r"[^\d]", "", original_input)

        user = Database.get_user_decrypted(user_id)
        if not user or user[6] != RegistrationSteps.WHATSAPP:
            return

        # فحص إذا كان المدخل الأصلي يحتوي على حروف
        if original_input != whatsapp:
            # تسجيل محاولة فاشلة
            is_locked = security_manager.record_failed_attempt(
                user_id, "whatsapp_input"
            )
            error_msg = (
                "❌ **رقم الواتساب يجب أن يكون أرقام فقط**\n\n"
                f"📍 **المدخل الخاطئ:** `{original_input}`\n"
                f"📍 **المطلوب:**\n"
                f"• أرقام فقط (بدون حروف أو رموز)\n"
                f"• 11 رقم بالضبط\n"
                f"• يبدأ بـ 010 أو 011 أو 012 أو 015\n\n"
                f"✅ **مثال صحيح:** 01094591331"
            )

            if is_locked:
                error_msg += "\n\n🔒 **تحذير: تم قفل هذه الميزة لمدة 15 دقيقة بسبب المحاولات المتكررة**"

            await message_manager.send_or_edit_message(update, error_msg)
            return

        if not Validators.validate_phone_number(whatsapp):
            # تسجيل محاولة فاشلة
            is_locked = security_manager.record_failed_attempt(
                user_id, "whatsapp_input"
            )
            error_msg = (
                "❌ **رقم الواتساب غير صحيح**\n\n"
                "📍 **المطلوب:**\n"
                "• أرقام فقط (بدون حروف أو رموز)\n"
                "• 11 رقم بالضبط\n"
                "• يبدأ بـ 010 أو 011 أو 012 أو 015\n\n"
                "✅ **مثال صحيح:** 01094591331"
            )

            if is_locked:
                error_msg += "\n\n🔒 **تحذير: تم قفل هذه الميزة لمدة 15 دقيقة بسبب المحاولات المتكررة**"

            await message_manager.send_or_edit_message(update, error_msg)
            return

        # نجاح العملية - إعادة تعيين المحاولات الفاشلة
        security_manager.reset_failed_attempts(user_id, "whatsapp_input")

        # حفظ رقم الواتساب (سيتم تشفيره تلقائياً)
        Database.update_user_field(user_id, "whatsapp", whatsapp)
        Database.update_user_step(user_id, RegistrationSteps.PAYMENT)

        # عرض طرق الدفع
        keyboard = PaymentMethods.get_keyboard()
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message_manager.send_or_edit_message(
            update,
            Messages.get_whatsapp_saved(whatsapp) + Messages.PAYMENT_REQUEST,
            reply_markup=reply_markup,
        )


# ================================ معالج طرق الدفع ================================
class PaymentHandler:
    PAYMENT_INSTRUCTIONS = {
        "vodafone_cash": "يرجى إدخال رقم محفظة فودافون كاش (أرقام فقط - 11 رقم):",
        "etisalat_cash": "يرجى إدخال رقم محفظة اتصالات كاش (أرقام فقط - 11 رقم):",
        "orange_cash": "يرجى إدخال رقم محفظة أورانج كاش (أرقام فقط - 11 رقم):",
        "we_cash": "يرجى إدخال رقم محفظة وي كاش (أرقام فقط - 11 رقم):",
        "bank_wallet": "يرجى إدخال رقم المحفظة البنكية (أرقام فقط - 11 رقم):",
        "telda": "يرجى إدخال رقم كارت تيلدا (16 رقم - يُسمح بالمسافات أو علامات الناقص بين الأرقام):",
        "instapay": "يرجى إدخال رابط إنستا باي صحيح:\nمثال: https://instapay.com/username",
    }

    @staticmethod
    async def handle_payment_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالج اختيار طريقة الدفع - رسالة واحدة فقط"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        payment_method = query.data.replace("payment_", "")

        # حفظ طريقة الدفع
        Database.update_user_field(user_id, "payment_method", payment_method)

        instruction = PaymentHandler.PAYMENT_INSTRUCTIONS.get(
            payment_method, "يرجى إدخال البيانات:"
        )

        # تحديث نفس الرسالة
        await message_manager.send_or_edit_message(
            update, Messages.get_payment_saved(payment_method) + instruction
        )

    @staticmethod
    async def handle_payment_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج بيانات الدفع - رسالة واحدة فقط"""
        user_id = update.effective_user.id
        original_input = update.message.text

        user = Database.get_user_decrypted(user_id)
        if not user or user[6] != RegistrationSteps.PAYMENT:
            return

        payment_method = user[4]  # payment_method field

        # استخراج البيانات المنظفة حسب طريقة الدفع
        if payment_method in [
            "vodafone_cash",
            "etisalat_cash",
            "orange_cash",
            "we_cash",
            "bank_wallet",
        ]:
            # تنظيف البيانات من أي شيء غير الأرقام
            payment_data_cleaned = re.sub(r"[^\d]", "", original_input)

            # التحقق إذا كان المدخل الأصلي يحتوي على حروف
            if original_input != payment_data_cleaned and payment_data_cleaned:
                await message_manager.send_or_edit_message(
                    update,
                    f"❌ **يجب إدخال أرقام فقط**\n\n"
                    f"📍 **المدخل الخاطئ:** `{original_input}`\n"
                    f"📍 **تم استخراج الأرقام فقط:** `{payment_data_cleaned}`\n\n"
                    f"**❗ يرجى إدخال أرقام فقط بدون حروف أو رموز**",
                )
                return

            payment_data = payment_data_cleaned
        elif payment_method == "telda":
            # بالنسبة لتيلدا، نبعت البيانات الأصلية للتحقق مع استخراج الأرقام في التحقق
            payment_data = original_input
        else:
            payment_data = original_input

        # التحقق من صحة البيانات
        valid, error_message, final_data = await PaymentHandler._validate_payment_data(
            payment_method, payment_data, update
        )

        if not valid:
            await message_manager.send_or_edit_message(update, error_message)
            return

        # 🔥 الجزء المهم: حفظ البيانات وإكمال التسجيل 🔥
        Database.update_user_field(user_id, "payment_data", final_data)
        Database.update_user_step(user_id, RegistrationSteps.COMPLETE)

        # 🔥 إكمال التسجيل وعرض الملخص الكامل 🔥
        await RegistrationHandler.complete_registration(update, context)

    @staticmethod
    async def _validate_payment_data(payment_method, payment_data, update):
        """التحقق من صحة بيانات الدفع - مع إصلاح تيلدا لـ 16 رقم"""
        if payment_method in [
            "vodafone_cash",
            "etisalat_cash",
            "orange_cash",
            "we_cash",
            "bank_wallet",
        ]:
            # جميع المحافظ تتطلب 11 رقم - أرقام فقط
            if Validators.validate_phone_number(payment_data):
                return True, "", payment_data
            else:
                method_name = PaymentMethods.DATA[payment_method]
                return (
                    False,
                    f"❌ رقم {method_name} غير صحيح\n\n📍 يجب أن يكون:\n• أرقام فقط (بدون حروف أو رموز)\n• 11 رقم يبدأ بـ 010/011/012/015",
                    payment_data,
                )

        elif payment_method == "telda":
            # تيلدا يتطلب 16 رقم - أرقام فقط مع السماح بالمسافات والنقوش
            # استخراج الأرقام فقط من الإدخال
            telda_digits_only = re.sub(r"[^\d]", "", payment_data)

            if Validators.validate_card_number(payment_data):
                # إرجاع الأرقام المنظفة فقط (بدون مسافات أو نقوش)
                return True, "", telda_digits_only
            else:
                return (
                    False,
                    "❌ رقم كارت تيلدا غير صحيح\n\n📍 يجب أن يكون:\n• أرقام فقط (بدون حروف)\n• 16 رقم بالضبط\n• يُسمح بالمسافات أو علامات الناقص بين الأرقام",
                    payment_data,
                )

        elif payment_method == "instapay":
            extracted_link = Validators.extract_instapay_link(payment_data)
            if extracted_link:
                if extracted_link.startswith("https://"):
                    await message_manager.send_or_edit_message(
                        update,
                        f"✅ **تم استخلاص الرابط تلقائياً:**\n\n🔗 `{extracted_link}`",
                    )
                return True, "", extracted_link
            else:
                return (
                    False,
                    "❌ يرجى إدخال رابط إنستا باي صحيح\nمثال: https://instapay.com/username\n\nيرجى المحاولة مرة أخرى:",
                    payment_data,
                )

        return False, "❌ بيانات غير صحيحة", payment_data


# ================================ معالج التسجيل ================================
class RegistrationHandler:
    @staticmethod
    async def complete_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إكمال التسجيل - رسالة واحدة فقط"""
        user_id = update.effective_user.id
        user = Database.get_user_decrypted(user_id)  # استخدام البيانات المفكوكة

        if not user:
            return

        # عرض البيانات كاملة وواضحة للعميل
        whatsapp = user[3] or "غير محدد"
        payment_data = user[5] or "غير محدد"

        # عرض بيانات الدفع حسب النوع - كاملة وواضحة
        if user[4] == "instapay" and payment_data != "غير محدد":
            payment_display = f"🔗 رابط إنستا باي: {payment_data}"
        else:
            payment_display = f"`{payment_data}`"

        # عرض البيانات الكاملة للعميل
        profile_summary = (
            "🎉 **تم حفظ بياناتك بنجاح!** 🎉\n\n"
            "📋 **ملخص البيانات المحفوظة:**\n\n"
            f"  **الاسم:** {user[1]}\n"
            f"🎮 **المنصة:** {Platforms.DATA.get(user[2], 'غير محدد')}\n"
            f"📱 **الواتساب:** `{whatsapp}`\n"
            f"💳 **طريقة الدفع:** {PaymentMethods.DATA.get(user[4], 'غير محدد')}\n"
            f"💰 **بيانات الدفع:** {payment_display}\n"
            f"📅 **تاريخ التسجيل:** {user[7][:10] if user[7] else 'اليوم'}\n\n"
            "✅ **مرحباً بك في عالم FC 26**\n\n"
            "🔒 *بياناتك محمية بأعلى معايير الأمان والتشفير العالمي*"
        )

        keyboard = [
            [InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_profile")],
            [InlineKeyboardButton("🎮 بدء اللعب", callback_data="start_game")],
            [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message_manager.send_or_edit_message(
            update, profile_summary, reply_markup=reply_markup
        )


# ================================ معالج الملف الشخصي ================================
class ProfileHandler:
    @staticmethod
    async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي - رسالة واحدة فقط"""
        user_id = (
            update.effective_user.id
            if update.callback_query
            else update.effective_user.id
        )
        user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير

        if not user:
            await PlatformHandler.show_platform_selection(update, context)
            return

        keyboard = [
            [InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_profile")],
            [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account")],
            [InlineKeyboardButton("🎮 بدء اللعب", callback_data="start_game")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # عرض البيانات كاملة وواضحة للعميل
        whatsapp = user[3] or "غير محدد"
        payment_data = user[5] or "غير محدد"

        # عرض بيانات الدفع حسب النوع - كاملة وواضحة
        if user[4] == "instapay" and payment_data != "غير محدد":
            payment_display = f"🔗 رابط إنستا باي: {payment_data}"
        else:
            payment_display = f"`{payment_data}`"

        profile_text = (
            f"👤 **الملف الشخصي**\n\n"
            f"  **الاسم:** {user[1]}\n"
            f"🎮 **المنصة:** {Platforms.DATA.get(user[2], user[2] or 'غير محدد')}\n"
            f"📱 **الواتساب:** `{whatsapp}`\n"
            f"💳 **طريقة الدفع:** {PaymentMethods.DATA.get(user[4], user[4] or 'غير محدد')}\n"
            f"💰 **بيانات الدفع:** {payment_display}\n"
            f"📅 **تاريخ التسجيل:** {user[7][:10] if user[7] else 'غير محدد'}\n\n"
            f"✅ **الحالة:** مكتمل"
        )

        await message_manager.send_or_edit_message(
            update, profile_text, reply_markup=reply_markup
        )


# ================================ الأوامر ================================
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر عرض الملف الشخصي /profile - رسالة واحدة فقط"""
    user_id = update.effective_user.id
    user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير

    if not user:
        await message_manager.send_or_edit_message(
            update,
            "❌ **لم يتم العثور على حسابك!**\n\n" "يرجى التسجيل أولاً باستخدام /start",
        )
        return

    if user[6] != RegistrationSteps.COMPLETE:
        await message_manager.send_or_edit_message(
            update,
            "⚠️ **لم تكمل التسجيل بعد!**\n\n" "يرجى إكمال التسجيل باستخدام /start",
        )
        return

    # عرض الملف الشخصي
    await ProfileHandler.show_profile(update, context)


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر حذف الحساب /delete - رسالة واحدة فقط"""
    user_id = update.effective_user.id
    user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير

    if not user:
        await message_manager.send_or_edit_message(
            update, "❌ **لم يتم العثور على حسابك!**\n\n" "لا يوجد حساب للحذف."
        )
        return

    # رسالة تأكيد الحذف
    keyboard = [
        [
            InlineKeyboardButton(
                "⚠️ نعم، احذف حسابي نهائياً", callback_data="confirm_delete"
            )
        ],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_delete")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message_manager.send_or_edit_message(
        update,
        "🚨 **تحذير: حذف الحساب**\n\n"
        "⚠️ **هذا الإجراء خطير ولا يمكن التراجع عنه!**\n\n"
        "سيتم حذف جميع بياناتك:\n"
        "• المعلومات الشخصية\n"
        "• بيانات المنصة والدفع\n"
        "• تاريخ التسجيل\n"
        "• جميع الإعدادات\n\n"
        "🔴 **هل أنت متأكد 100% من حذف حسابك؟**",
        reply_markup=reply_markup,
    )


async def sell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر بيع الكوينز /sell - رسالة واحدة فقط"""
    user_id = update.effective_user.id
    user = Database.get_user_decrypted(user_id)  # استخدام البيانات المفكوكة

    if not user:
        await message_manager.send_or_edit_message(
            update,
            "❌ **لم يتم العثور على حسابك!**\n\n" "يرجى التسجيل أولاً باستخدام /start",
        )
        return

    if user[6] != RegistrationSteps.COMPLETE:
        await message_manager.send_or_edit_message(
            update,
            "⚠️ **لم تكمل التسجيل بعد!**\n\n" "يرجى إكمال التسجيل باستخدام /start",
        )
        return

    # عرض خيارات البيع
    keyboard = [
        [InlineKeyboardButton("🎮 بيع كوينز FC 26", callback_data="sell_fc26")],
        [InlineKeyboardButton("📞 التحدث مع الدعم", callback_data="contact_support")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # عرض معلومات المستخدم كاملة وواضحة
    whatsapp = user[3] or "غير محدد"
    payment_method_display = PaymentMethods.DATA.get(user[4], "غير محدد")

    # عرض بيانات الدفع كاملة حسب النوع
    if user[4] == "instapay" and user[5] != "غير محدد":
        payment_data_display = f"🔗 رابط إنستا باي: {user[5]}"
    else:
        payment_data_display = user[5] or "غير محدد"

    await message_manager.send_or_edit_message(
        update,
        "💰 **بيع الكوينز - FC 26**\n\n"
        "👤 **معلوماتك:**\n"
        f"📱 الواتساب: `{whatsapp}`\n"
        f"💳 طريقة الدفع: {payment_method_display}\n"
        f"💰 بيانات الدفع: {payment_data_display}\n"
        f"🎮 المنصة: {Platforms.DATA.get(user[2], 'غير محدد')}\n\n"
        "🔥 **خدماتنا:**\n"
        "• بيع كوينز FC 26 بأفضل الأسعار\n"
        "• دفع فوري وآمن\n"
        "• دعم فني 24/7\n"
        "• ضمان المعاملة\n\n"
        "اختر الخدمة المطلوبة:",
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة /help - رسالة واحدة فقط"""
    help_text = (
        "🤖 **أوامر البوت - FC 26**\n\n"
        "📋 **الأوامر المتاحة:**\n\n"
        "🏠 `/start` - بدء البوت أو التسجيل\n"
        "👤 `/profile` - عرض الملف الشخصي\n"
        "🗑️ `/delete` - حذف الحساب نهائياً\n"
        "💰 `/sell` - بيع الكوينز\n"
        "❓ `/help` - عرض هذه الرسالة\n\n"
        "🎮 **خدماتنا:**\n"
        "• تسجيل احترافي بالمنصة المفضلة\n"
        "• بيع وشراء الكوينز بأمان\n"
        "• دعم جميع طرق الدفع المصرية\n"
        "• دعم فني 24/7\n\n"
        "💡 **للمساعدة:** تواصل معنا عبر الواتساب"
    )

    await message_manager.send_or_edit_message(update, help_text)


# ================================ المعالجات الرئيسية ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البداية - رسالة واحدة فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.first_name or "مستخدم"

    user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير

    if user and user[6] == RegistrationSteps.COMPLETE:
        await ProfileHandler.show_profile(update, context)
    else:
        Database.create_user(user_id, username)
        await PlatformHandler.show_platform_selection(update, context)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج عام للاستعلامات المرجعية - رسالة واحدة فقط"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("platform_"):
        await PlatformHandler.handle_platform_selection(update, context)
    elif query.data.startswith("payment_"):
        await PaymentHandler.handle_payment_selection(update, context)
    elif query.data == "show_profile":
        await ProfileHandler.show_profile(update, context)
    elif query.data == "edit_profile":
        await PlatformHandler.show_platform_selection(update, context)
    elif query.data == "start_game":
        await message_manager.send_or_edit_message(
            update, "🎮 **قريباً... ميزة بدء اللعب!**"
        )
    elif query.data == "delete_account":
        keyboard = [
            [InlineKeyboardButton("✅ نعم، احذف", callback_data="confirm_delete")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="show_profile")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message_manager.send_or_edit_message(
            update,
            "⚠️ **تأكيد الحذف**\n\nهل أنت متأكد من حذف حسابك؟",
            reply_markup=reply_markup,
        )
    elif query.data == "confirm_delete":
        user_id = query.from_user.id
        Database.delete_user(user_id)
        await message_manager.send_or_edit_message(
            update, "✅ **تم حذف حسابك بنجاح!**\n\nيمكنك البدء من جديد بأمر /start"
        )
    elif query.data == "cancel_delete":
        await message_manager.send_or_edit_message(
            update,
            "✅ **تم إلغاء عملية حذف الحساب**\n\n"
            "حسابك آمن ولم يتم حذف أي بيانات.\n"
            "يمكنك المتابعة في استخدام البوت بشكل طبيعي.\n\n"
            "للوصول لحسابك: /profile",
        )
    elif query.data == "contact_support":
        user_id = query.from_user.id
        user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير
        whatsapp = user[3] if user else "غير محدد"

        await message_manager.send_or_edit_message(
            update,
            "📞 **التواصل مع الدعم**\n\n"
            "🔥 **للمعاملات السريعة:**\n"
            f"واتساب العميل: `{whatsapp}`\n"
            "واتساب الدعم: `01094591331`\n\n"
            "⚡ **أوقات العمل:**\n"
            "• 24 ساعة يومياً\n"
            "• 7 أيام في الأسبوع\n"
            "• رد سريع خلال دقائق\n\n"
            "💬 **اكتب رسالتك وسنرد عليك فوراً**",
        )
    elif query.data == "main_menu":
        # العودة للقائمة الرئيسية
        keyboard = [
            [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
            [InlineKeyboardButton("💰 بيع الكوينز", callback_data="sell_coins_menu")],
            [InlineKeyboardButton("🎮 بدء اللعب", callback_data="start_game")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message_manager.send_or_edit_message(
            update,
            "🏠 **القائمة الرئيسية - FC 26**\n\n"
            "مرحباً بك في بوت FC 26\n"
            "اختر الخدمة المطلوبة:",
            reply_markup=reply_markup,
        )
    elif query.data == "sell_coins_menu":
        # نفس محتوى أمر /sell المحدث
        keyboard = [
            [InlineKeyboardButton("🎮 بيع كوينز FC 26", callback_data="sell_fc26")],
            [
                InlineKeyboardButton(
                    "📞 التواصل مع الدعم", callback_data="contact_support"
                )
            ],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message_manager.send_or_edit_message(
            update,
            "💰 **بيع الكوينز - FC 26**\n\n"
            "🔥 **خدماتنا:**\n"
            "• بيع كوينز FC 26 بأفضل الأسعار\n"
            "• دفع فوري وآمن\n"
            "• دعم فني 24/7\n"
            "• ضمان المعاملة\n\n"
            "اختر الخدمة المطلوبة:",
            reply_markup=reply_markup,
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل النصية - رسالة واحدة فقط"""
    user_id = update.effective_user.id
    user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير

    if not user:
        await start(update, context)
        return

    current_step = user[6]

    if current_step == RegistrationSteps.WHATSAPP:
        await WhatsAppHandler.handle_whatsapp_input(update, context)
    elif current_step == RegistrationSteps.PAYMENT:
        await PaymentHandler.handle_payment_data(update, context)


# ================================ حالات محادثة البيع ================================


class SellStates:
    CHOOSE_TYPE = 1
    ENTER_AMOUNT = 2
    CONFIRM_SALE = 3


# ================================ معالج محادثة البيع ================================
class SellConversationHandler:
    @staticmethod
    def parse_amount(text: str):
        """
        تحليل كمية الكوينز - أرقام فقط (3-5 أرقام)
        """
        if not text or not isinstance(text, str):
            return None

        # تنظيف النص من أي شيء غير الأرقام
        text = text.strip()

        # التحقق من وجود k أو m - ممنوع
        if "k" in text.lower() or "m" in text.lower():
            return "invalid_format"

        try:
            # التحقق من أن النص أرقام فقط
            if not text.isdigit():
                return None

            number = int(text)

            # التحقق من عدد الأرقام (3-5 أرقام)
            if len(text) < 3 or len(text) > 5:
                return "invalid_length"

            return number

        except (ValueError, TypeError):
            return None

    @staticmethod
    def format_amount(amount: int) -> str:
        """
        تنسيق عرض الكمية حسب القواعد المحددة
        """
        if not isinstance(amount, (int, float)):
            return "0"

        amount = int(amount)

        if 100 <= amount <= 999:
            # من 100 إلى 999: عرض بصيغة K
            return f"{amount} K"
        elif 1000 <= amount <= 20000:
            # من 1,000 إلى 20,000: عرض بصيغة M مع الفاصلة العربية
            formatted = f"{amount:,}".replace(",", "٬")
            return f"{formatted} M"
        else:
            # للقيم خارج النطاق (إن وجدت)
            return str(amount)

    @staticmethod
    def calculate_price(amount, transfer_type="normal"):
        """حساب السعر حسب الكمية ونوع التحويل"""
        # السعر الأساسي لكل 1000 كوين
        base_price_per_1000 = 5  # 5 جنيه لكل 1000 كوين

        # خصم حسب الكمية
        if amount >= 1000000:  # 1M أو أكثر
            discount = 0.15  # خصم 15%
        elif amount >= 500000:  # 500K أو أكثر
            discount = 0.10  # خصم 10%
        elif amount >= 100000:  # 100K أو أكثر
            discount = 0.05  # خصم 5%
        else:
            discount = 0

        # رسوم إضافية للتحويل الفوري
        if transfer_type == "instant":
            instant_multiplier = 1.35  # زيادة 35%
        else:
            instant_multiplier = 1.0

        # حساب السعر  النهائي
        price_per_1000 = base_price_per_1000 * (1 - discount) * instant_multiplier
        total_price = (amount / 1000) * price_per_1000

        return int(total_price)


async def sell_coins_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بداية محادثة البيع - رسالة واحدة فقط"""
    user_id = update.callback_query.from_user.id
    user = Database.get_user_decrypted(user_id)  # استخدام النسخة المفكوكة التشفير

    if not user or user[6] != RegistrationSteps.COMPLETE:
        await message_manager.send_or_edit_message(
            update, "❌ **يجب إكمال التسجيل أولاً**\n\nاستخدم /start للتسجيل"
        )
        return ConversationHandler.END

    # عرض خيارات نوع التحويل
    keyboard = [
        [
            InlineKeyboardButton(
                "⚡ تحويل فوري (خلال ساعة)", callback_data="type_instant"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 تحويل عادي (خلال 24 ساعة)", callback_data="type_normal"
            )
        ],
        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_sell")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message_manager.send_or_edit_message(
        update,
        "💰 **بيع كوينز FC 26**\n\n"
        "🎯 **اختر نوع التحويل:**\n\n"
        "⚡ **تحويل فوري:** خلال ساعة واحدة (سعر أعلى)\n"
        "📅 **تحويل عادي:** خلال 24 ساعة (سعر عادي)\n\n"
        "💡 **الأسعار تختلف حسب الكمية ونوع التحويل**",
        reply_markup=reply_markup,
    )

    return SellStates.CHOOSE_TYPE


async def sell_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع التحويل - رسالة واحدة فقط"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_sell":
        await message_manager.send_or_edit_message(
            update,
            "✅ **تم إلغاء عملية البيع**\n\nيمكنك العودة في أي وقت باستخدام /sell",
        )
        return ConversationHandler.END

    # حفظ نوع التحويل
    transfer_type = "instant" if query.data == "type_instant" else "normal"
    context.user_data["transfer_type"] = transfer_type

    type_name = "⚡ فوري" if transfer_type == "instant" else "📅 عادي"

    await message_manager.send_or_edit_message(
        update,
        f"✅ **تم اختيار التحويل {type_name}**\n\n"
        "💰 **أدخل كمية الكوينز للبيع:**\n\n"
        "📝 **قواعد الإدخال:**\n"
        "• أرقام فقط (بدون حروف أو رموز)\n"
        "• الحد الأدنى: 3 أرقام (مثال: 100k)\n"
        "• الحد الأقصى: 5 أرقام (مثال: 20,000m)\n"
        "• ممنوع استخدام k أو m\n\n"
        "💡 **أمثلات صحيحة:** 500، 1,500، 20,000\n\n"
        "اكتب الكمية بالأرقام العادية:",
    )

    return SellStates.ENTER_AMOUNT


async def sell_amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال كمية الكوينز - أرقام فقط (3-5 أرقام) - رسالة واحدة فقط"""
    user_id = update.effective_user.id
    amount_text = update.message.text

    # 1. تحليل الكمية المدخلة
    amount = SellConversationHandler.parse_amount(amount_text)

    # 2. التحقق من الصيغة الخاطئة (k أو m)
    if amount == "invalid_format":
        await message_manager.send_or_edit_message(
            update,
            "❌ **صيغة غير صحيحة!**\n\n"
            "🚫 **ممنوع استخدام k أو m**\n\n"
            "✅ **المطلوب:** أرقام فقط (3-5 أرقام)\n"
            "📝 **مثال صحيح:** 500 أو 1,500 أو 20,000\n\n"
            "يرجى إدخال الكمية بالأرقام العادية فقط:",
        )
        return SellStates.ENTER_AMOUNT

    # 3. التحقق من طول الرقم
    if amount == "invalid_length":
        await message_manager.send_or_edit_message(
            update,
            "❌ **عدد الأرقام غير صحيح!**\n\n"
            "📍 **المطلوب:**\n"
            "• الحد الأدنى: 3 أرقام (مثال: 100k)\n"
            "• الحد الأقصى: 5 أرقام (مثال: 20,000m)\n\n"
            f"أنت أدخلت: {len(amount_text)} أرقام\n\n"
            "📝 **أمثلات صحيحة:** 500k، 1,500m، 20,000m\n\n"
            "يرجى إدخال رقم بين 3-5 أرقام:",
        )
        return SellStates.ENTER_AMOUNT

    # 4. التحقق من صحة الصيغة العامة
    if amount is None:
        await message_manager.send_or_edit_message(
            update,
            "❌ **صيغة غير صحيحة!**\n\n"
            "✅ **المطلوب:** أرقام فقط (3-5 أرقام)\n"
            "🚫 **ممنوع:** حروف، رموز، k، m\n\n"
            "📝 **أمثلات صحيحة:**\n"
            "• 500 (الف)\n"
            "• 1,500 (مليون ونص)\n"
            "• 20,000(20 مليون)\n\n"
            "يرجى المحاولة مرة أخرى:",
        )
        return SellStates.ENTER_AMOUNT

    # 5. تعريف الحدود الفعلية
    MIN_SELL_AMOUNT = 100  # 100 كوين (3 أرقام)
    MAX_SELL_AMOUNT = 20000  # 20000 كوين (5 أرقام)

    # 6. التحقق من الحدود
    if amount < MIN_SELL_AMOUNT:
        await message_manager.send_or_edit_message(
            update,
            f"❌ **الكمية قليلة جداً!**\n\n"
            f"📍 **الحد الأدنى:** {MIN_SELL_AMOUNT:,} كوين\n"
            f"أنت أدخلت: {amount:,} كوين\n\n"
            "يرجى إدخال كمية أكبر:",
        )
        return SellStates.ENTER_AMOUNT

    if amount > MAX_SELL_AMOUNT:
        await message_manager.send_or_edit_message(
            update,
            f"❌ **الكمية كبيرة جداً!**\n\n"
            f"📍 **الحد الأقصى:** {MAX_SELL_AMOUNT:,} كوين\n"
            f"أنت أدخلت: {amount:,} كوين\n\n"
            "لبيع كميات أكبر، يرجى التواصل مع الدعم.",
        )
        return SellStates.ENTER_AMOUNT

    # حفظ الكمية وحساب السعر
    context.user_data["amount"] = amount
    transfer_type = context.user_data.get("transfer_type", "normal")
    price = SellConversationHandler.calculate_price(amount, transfer_type)

    # عرض تأكيد البيع مباشرة بدون أزرار
    user = Database.get_user_decrypted(user_id)
    whatsapp = user[3] or "غير محدد"
    payment_method = PaymentMethods.DATA.get(user[4], "غير محدد")

    formatted_amount = SellConversationHandler.format_amount(amount)
    type_name = "⚡ فوري" if transfer_type == "instant" else "📅 عادي"

    # رسالة التأكيد المباشر
    await message_manager.send_or_edit_message(
        update,
        "🎉 **تم تأكيد طلب البيع بنجاح!**\n\n"
        f"📊 **تفاصيل الطلب:**\n"
        f"💰 الكمية: {formatted_amount} كوينز\n"
        f"💵 السعر: {price} جنيه  \n"
        f"⏰ نوع التحويل: {type_name}\n\n"
        "👤 **بياناتك:**\n"
        f"📱 الواتساب: `{whatsapp}`\n"
        f"💳 طريقة الدفع: {payment_method}\n\n"
        "📞 **الخطوات التالية:**\n"
        "1️⃣ سيتم التواصل معك خلال دقائق\n"
        "2️⃣ تسليم الكوينز للممثل\n"
        "3️⃣ استلام المبلغ فوراً\n\n"
        "✅ **تم حفظ طلبك في النظام**\n"
        f"🆔 **رقم الطلب:** #{user_id}{amount}\n\n"
        "💬 **للاستفسار:** /sell\n"
        "🏠 **القائمة الرئيسية:** /start",
    )

    # مسح بيانات المحادثة وإنهاء المحادثة
    context.user_data.clear()
    return ConversationHandler.END


async def sell_conversation_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء محادثة البيع - رسالة واحدة فقط"""
    await message_manager.send_or_edit_message(
        update, "✅ **تم إلغاء عملية البيع**\n\nيمكنك البدء من جديد باستخدام /sell"
    )
    context.user_data.clear()
    return ConversationHandler.END


# ================================ الدالة الرئيسية ================================


def run_bot_in_thread():
    """دالة تشغيل البوت في خيط منفصل"""
    try:
        print("🚀 Starting FC 26 Bot in separate thread...")

        # حذف webhook أولاً
        webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        try:
            response = requests.post(webhook_url)
            print(f"✅ Webhook cleared: {response.json()}")
        except Exception as e:
            print(f"⚠️ Webhook clear warning: {e}")

        # تهيئة قاعدة البيانات
        Database.init_db()
        print("✅ Database initialized")

        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()

        # إعداد محادثة البيع
        sell_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(sell_coins_start, pattern="^sell_fc26$")
            ],
            states={
                SellStates.CHOOSE_TYPE: [
                    CallbackQueryHandler(
                        sell_type_chosen,
                        pattern="^(type_instant|type_normal|cancel_sell)$",
                    )
                ],
                SellStates.ENTER_AMOUNT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, sell_amount_entered)
                ],
            },
            fallbacks=[CommandHandler("cancel", sell_conversation_cancel)],
        )

        # إضافة المعالجات
        application.add_handler(sell_conversation)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("delete", delete_command))
        application.add_handler(CommandHandler("sell", sell_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )

        print("🔄 Starting polling in separate thread...")

        # تشغيل البوت مع معالجة الحلقة الحدثية بشكل صحيح
        asyncio.set_event_loop(asyncio.new_event_loop())
        application.run_polling(drop_pending_updates=True)

    except Exception as e:
        print(f"❌ خطأ في خيط البوت: {e}")
        logger.error(f"Bot thread error: {e}")


def main():
    """الدالة الرئيسية مع العزل المطلق"""
    print("🚀 Starting FC 26 System with Thread Isolation...")

    # For Windows, we need to set the event loop policy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # تشغيل البوت مباشرة في الخيط الرئيسي
    try:
        print("🚀 Starting FC 26 Bot...")

        # حذف webhook أولاً
        webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
        try:
            response = requests.post(webhook_url)
            print(f"✅ Webhook cleared: {response.json()}")
        except Exception as e:
            print(f"⚠️ Webhook clear warning: {e}")

        # تهيئة قاعدة البيانات
        Database.init_db()
        print("✅ Database initialized")

        # إنشاء التطبيق
        application = Application.builder().token(BOT_TOKEN).build()

        # إعداد محادثة البيع
        sell_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(sell_coins_start, pattern="^sell_fc26$")
            ],
            states={
                SellStates.CHOOSE_TYPE: [
                    CallbackQueryHandler(
                        sell_type_chosen,
                        pattern="^(type_instant|type_normal|cancel_sell)$",
                    )
                ],
                SellStates.ENTER_AMOUNT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, sell_amount_entered)
                ],
            },
            fallbacks=[CommandHandler("cancel", sell_conversation_cancel)],
        )

        # إضافة المعالجات
        application.add_handler(sell_conversation)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("profile", profile_command))
        application.add_handler(CommandHandler("delete", delete_command))
        application.add_handler(CommandHandler("sell", sell_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )

        print("🔄 Starting polling...")
        print("✅ Bot is running! Press Ctrl+C to stop.")

        # تشغيل البوت
        application.run_polling(drop_pending_updates=True)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down FC 26 System...")
        print("✅ System stopped successfully!")
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        logger.error(f"Bot error: {e}")


if __name__ == "__main__":
    main()
