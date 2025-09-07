#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 FC 26 Trading Bot - النسخة الكاملة المتكاملة
البوت الكامل في ملف واحد مع نظام الرسائل الذكي
مشروع لبيع كوينز FC 26
"""

import os
import logging
import sqlite3
import hashlib
import json
import re
import asyncio
import time
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# ================================ الإعدادات ================================
BOT_TOKEN = '7607085569:AAEDNKwt8j8B_CjG5gjKLJ8MLjrTRCCrx6k'
ADMIN_ID = 1124247595
DATABASE_PATH = 'fc26_bot.db'

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================ حالات التسجيل ================================
(
    CHOOSING_PLATFORM,
    ENTERING_WHATSAPP,
    CHOOSING_PAYMENT,
    ENTERING_PAYMENT_DETAILS
) = range(4)

# ================================ البيانات الثابتة ================================
GAMING_PLATFORMS = {
    'playstation': {'name': 'PlayStation 🎮', 'emoji': '🎮'},
    'xbox': {'name': 'Xbox ❎', 'emoji': '❎'},
    'pc': {'name': 'PC 💻', 'emoji': '💻'}
}

PAYMENT_METHODS = {
    'vodafone_cash': {'name': '⭕️ فودافون كاش', 'emoji': '⭕️'},
    'etisalat_cash': {'name': '🟢 اتصالات كاش', 'emoji': '🟢'},
    'orange_cash': {'name': '🍊 أورانج كاش', 'emoji': '🍊'},
    'we_cash': {'name': '🟣 وي كاش', 'emoji': '🟣'},
    'bank_wallet': {'name': '🏦 محفظة بنكية', 'emoji': '🏦'},
    'telda': {'name': '💳 تيلدا', 'emoji': '💳'},
    'instapay': {'name': '🔗 إنستا باي', 'emoji': '🔗'}
}

MESSAGES = {
    'welcome': """🌟 أهلاً وسهلاً في بوت FC 26! 🎮

البوت الأول في مصر لبيع كوينز FC 26 🇪🇬

✨ مميزاتنا:
• أسعار منافسة جداً 💰
• معاملات آمنة 100% 🔒
• دعم فني 24/7 📞
• سرعة في التنفيذ ⚡

اضغط على "تسجيل جديد" للبدء! 👇""",

    'choose_platform': """🎮 اختر منصة اللعب:""",

    'enter_whatsapp': """📱 **أرسل رقم الواتساب:**

📝 **القواعد:**
• 11 رقم بالضبط
• يبدأ بـ: 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ **مثال صحيح:** `01094591331`""",

    'choose_payment': """💳 اختر طريقة الدفع:""",



    'registration_complete': """🎉 مبروك! تم إنشاء حسابك بنجاح! 🎊

✅ ملخص بياناتك:
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {whatsapp}
💳 طريقة الدفع: {payment}
━━━━━━━━━━━━━━━━

مرحباً بك في عائلة FC 26! 🚀""",

    'welcome_back': """👋 أهلاً بعودتك!

كنا واقفين عند: {last_step}

هل تريد المتابعة من حيث توقفت؟""",





    'data_saved': """💾 تم حفظ البيانات تلقائياً ✅

يمكنك العودة في أي وقت وسنكمل من نفس النقطة!"""
}

# ================================ نظام إدارة الرسائل الذكي ================================
class SmartMessageManager:
    """مدير الرسائل الذكي - رسالة واحدة نشطة فقط مع حماية من Race Conditions"""

    def __init__(self):
        self.user_active_messages: Dict[int, Dict[str, Any]] = {}
        # إضافة قفل لكل مستخدم لمنع Race Conditions
        self.user_locks: Dict[int, asyncio.Lock] = {}

    async def get_or_create_lock(self, user_id: int) -> asyncio.Lock:
        """الحصول على قفل المستخدم أو إنشاء واحد جديد"""
        if user_id not in self.user_locks:
            self.user_locks[user_id] = asyncio.Lock()
        return self.user_locks[user_id]
    
    async def cleanup_user_data(self, user_id: int):
        """تنظيف بيانات المستخدم عند انتهاء المحادثة"""
        # حذف القفل إذا كان موجوداً
        if user_id in self.user_locks:
            del self.user_locks[user_id]
        
        # حذف الرسائل النشطة إذا كانت موجودة
        if user_id in self.user_active_messages:
            del self.user_active_messages[user_id]

    async def disable_old_message(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, choice_made: str = None):
        """إلغاء تفعيل الرسالة القديمة وتحويلها لسجل تاريخي"""
        # الحصول على القفل للمستخدم
        lock = await self.get_or_create_lock(user_id)
        
        async with lock:  # استخدام القفل لحماية العملية
            if user_id not in self.user_active_messages:
                return

            try:
                old_message_info = self.user_active_messages[user_id]

                if old_message_info.get('message_id') and old_message_info.get('chat_id'):
                    # إذا كانت الرسالة القديمة فيها أزرار، نحذفها ونضع "تم"
                    if old_message_info.get('has_keyboard', False):
                        try:
                            # تحديث الرسالة بدون أزرار وإضافة "تم"
                            await context.bot.edit_message_text(
                                chat_id=old_message_info['chat_id'],
                                message_id=old_message_info['message_id'],
                                text=old_message_info.get('text', '') + "\n\n✅ **تم**",
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            # إذا فشل التحديث، نحاول حذف الرسالة
                            try:
                                await context.bot.delete_message(
                                    chat_id=old_message_info['chat_id'],
                                    message_id=old_message_info['message_id']
                                )
                            except:
                                pass

                    del self.user_active_messages[user_id]
            except Exception as e:
                logger.debug(f"تعذر تعديل الرسالة القديمة: {e}")

    async def send_new_active_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        choice_made: str = None,
        disable_previous: bool = True,
        remove_keyboard: bool = True
    ):
        """إرسال رسالة جديدة نشطة مع حماية من Race Conditions"""
        user_id = update.effective_user.id
        
        # الحصول على القفل للمستخدم
        lock = await self.get_or_create_lock(user_id)

        if disable_previous:
            await self.disable_old_message(user_id, context, choice_made)

        async with lock:  # استخدام القفل لحماية عملية الإرسال والحفظ
            try:
                # التحقق من عدم وجود رسالة مطابقة نشطة بالفعل
                if user_id in self.user_active_messages:
                    existing_msg = self.user_active_messages[user_id]
                    if existing_msg.get('text') == text:
                        # نفس الرسالة موجودة بالفعل، لا نرسل مرة أخرى
                        logger.debug(f"تجاهل إرسال رسالة مكررة للمستخدم {user_id}")
                        return None
                
                if update.callback_query:
                    sent_message = await update.callback_query.message.reply_text(
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    # إزالة الكيبورد إذا لم يكن هناك reply_markup
                    final_markup = reply_markup if reply_markup else (ReplyKeyboardRemove() if remove_keyboard else None)
                    sent_message = await update.message.reply_text(
                        text=text,
                        reply_markup=final_markup,
                        parse_mode='Markdown'
                    )

                # حفظ معلومات الرسالة الجديدة
                self.user_active_messages[user_id] = {
                    'message_id': sent_message.message_id,
                    'chat_id': sent_message.chat_id,
                    'text': text,
                    'has_keyboard': reply_markup is not None,
                    'timestamp': datetime.now()  # إضافة timestamp للتتبع
                }

                return sent_message

            except Exception as e:
                logger.error(f"خطأ في إرسال رسالة: {e}")
                return None

    async def update_current_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ):
        """تحديث الرسالة الحالية مع حماية من Race Conditions"""
        if not update.callback_query:
            return await self.send_new_active_message(update, context, text, reply_markup)

        user_id = update.effective_user.id
        
        # الحصول على القفل للمستخدم
        lock = await self.get_or_create_lock(user_id)
        
        async with lock:  # استخدام القفل لحماية عملية التحديث
            try:
                # التحقق من عدم تكرار نفس الرسالة
                if user_id in self.user_active_messages:
                    old_msg = self.user_active_messages[user_id]
                    if old_msg.get('text') == text and old_msg.get('message_id') == update.callback_query.message.message_id:
                        # نفس الرسالة، لا نحدث
                        logger.debug(f"تجاهل تحديث رسالة مطابقة للمستخدم {user_id}")
                        return
                    
                    # التحقق من الـ timestamp لمنع التحديثات السريعة جداً
                    if 'timestamp' in old_msg:
                        time_diff = (datetime.now() - old_msg['timestamp']).total_seconds()
                        if time_diff < 0.5:  # أقل من نصف ثانية
                            logger.debug(f"تجاهل تحديث سريع جداً للمستخدم {user_id}")
                            return

                await update.callback_query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )

                # حفظ معلومات الرسالة المحدثة
                self.user_active_messages[user_id] = {
                    'message_id': update.callback_query.message.message_id,
                    'chat_id': update.callback_query.message.chat_id,
                    'text': text,
                    'has_keyboard': reply_markup is not None,
                    'timestamp': datetime.now()  # إضافة timestamp للتتبع
                }

            except Exception as e:
                # إذا كان الخطأ "لم يتغير النص"، نتجاهله
                if "message is not modified" in str(e).lower():
                    logger.debug(f"الرسالة لم تتغير للمستخدم {user_id}")
                else:
                    logger.debug(f"خطأ في تحديث الرسالة للمستخدم {user_id}: {e}")

# إنشاء المدير الذكي
smart_message_manager = SmartMessageManager()

# ================================ نظام الحماية المتقدم للواتساب ================================
class WhatsAppSecuritySystem:
    """نظام حماية متقدم للتحقق من أرقام الواتساب"""
    
    def __init__(self):
        # تتبع المحاولات لكل مستخدم
        self.user_attempts: Dict[int, List[datetime]] = defaultdict(list)
        self.failed_attempts: Dict[int, int] = defaultdict(int)
        self.blocked_users: Dict[int, datetime] = {}
        self.last_numbers: Dict[int, str] = {}
        
        # إعدادات الحماية
        self.MAX_ATTEMPTS_PER_MINUTE = 5
        self.MAX_FAILED_ATTEMPTS = 5
        self.BLOCK_DURATION_MINUTES = 15
        self.RATE_LIMIT_WINDOW = 60  # ثانية
        
        # شبكات الاتصال المصرية
        self.EGYPTIAN_NETWORKS = {
            '010': {'name': 'فودافون', 'emoji': '⭕️'},
            '011': {'name': 'اتصالات', 'emoji': '🟢'},
            '012': {'name': 'أورانج', 'emoji': '🍊'},
            '015': {'name': 'وي', 'emoji': '🟣'}
        }
    
    def is_user_blocked(self, user_id: int) -> Tuple[bool, Optional[int]]:
        """التحقق من حظر المستخدم"""
        if user_id in self.blocked_users:
            block_time = self.blocked_users[user_id]
            elapsed = (datetime.now() - block_time).total_seconds() / 60
            
            if elapsed < self.BLOCK_DURATION_MINUTES:
                remaining = self.BLOCK_DURATION_MINUTES - int(elapsed)
                return True, remaining
            else:
                # انتهت فترة الحظر
                del self.blocked_users[user_id]
                self.failed_attempts[user_id] = 0
        
        return False, None
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """فحص معدل الطلبات"""
        now = datetime.now()
        
        # تنظيف المحاولات القديمة
        if user_id in self.user_attempts:
            self.user_attempts[user_id] = [
                attempt for attempt in self.user_attempts[user_id]
                if (now - attempt).total_seconds() < self.RATE_LIMIT_WINDOW
            ]
        
        # فحص عدد المحاولات
        attempts_count = len(self.user_attempts[user_id])
        
        if attempts_count >= self.MAX_ATTEMPTS_PER_MINUTE:
            return False, f"⚠️ لقد تجاوزت الحد المسموح ({self.MAX_ATTEMPTS_PER_MINUTE} محاولات في الدقيقة)\\n\\n⏰ انتظر قليلاً ثم حاول مرة أخرى"
        
        # تسجيل المحاولة الجديدة
        self.user_attempts[user_id].append(now)
        return True, None
    
    def check_duplicate(self, user_id: int, phone: str) -> bool:
        """فحص الأرقام المكررة"""
        if user_id in self.last_numbers:
            if self.last_numbers[user_id] == phone:
                return True
        return False
    
    def analyze_input(self, text: str) -> Dict[str, Any]:
        """تحليل المدخل بشكل تفصيلي"""
        analysis = {
            'original': text,
            'has_letters': False,
            'has_symbols': False,
            'has_spaces': False,
            'has_arabic_numbers': False,
            'extracted_digits': '',
            'all_chars': [],
            'invalid_chars': []
        }
        
        # استخراج الأرقام فقط
        digits_only = re.sub(r'[^\d]', '', text)
        analysis['extracted_digits'] = digits_only
        
        # تحليل كل حرف
        for char in text:
            analysis['all_chars'].append(char)
            
            # فحص الأحرف
            if char.isalpha():
                analysis['has_letters'] = True
                analysis['invalid_chars'].append(char)
            
            # فحص الرموز
            elif not char.isdigit() and not char.isspace():
                analysis['has_symbols'] = True
                analysis['invalid_chars'].append(char)
            
            # فحص المسافات
            elif char.isspace():
                analysis['has_spaces'] = True
                analysis['invalid_chars'].append(char)
            
            # فحص الأرقام العربية
            elif char in '٠١٢٣٤٥٦٧٨٩':
                analysis['has_arabic_numbers'] = True
                analysis['invalid_chars'].append(char)
        
        return analysis
    
    def validate_whatsapp(self, text: str, user_id: int) -> Dict[str, Any]:
        """التحقق الشامل من رقم الواتساب"""
        result = {
            'is_valid': False,
            'cleaned_number': '',
            'error_type': None,
            'error_message': '',
            'network_info': None,
            'analysis': None
        }
        
        # التحليل التفصيلي للمدخل
        analysis = self.analyze_input(text)
        result['analysis'] = analysis
        
        # 1. فحص وجود أحرف أو رموز
        if analysis['has_letters'] or analysis['has_symbols'] or analysis['has_spaces'] or analysis['has_arabic_numbers']:
            invalid_chars_display = ''.join(set(analysis['invalid_chars']))
            result['error_type'] = 'invalid_chars'
            result['error_message'] = f"""❌ **رقم الواتساب يجب أن يكون أرقام فقط**

📍 **المدخل الخاطئ:** `{text}`
🚫 **الأحرف/الرموز الغير مسموحة:** `{invalid_chars_display}`
📊 **الأرقام المستخرجة:** `{analysis['extracted_digits'] or 'لا توجد أرقام'}`

✅ **مثال صحيح:** `01094591331`

💡 **تلميح:** استخدم الأرقام الإنجليزية فقط (0-9) بدون مسافات أو رموز"""
            return result
        
        cleaned = analysis['extracted_digits']
        
        # 2. فحص الطول
        if len(cleaned) < 11:
            result['error_type'] = 'too_short'
            result['error_message'] = f"""❌ **طول الرقم غير صحيح**

📏 **المطلوب:** 11 رقم بالضبط
📍 **أنت أدخلت:** {len(cleaned)} رقم فقط
🔢 **الرقم المدخل:** `{cleaned}`

✅ **مثال صحيح:** `01094591331`"""
            return result
        
        elif len(cleaned) > 11:
            result['error_type'] = 'too_long'
            result['error_message'] = f"""❌ **طول الرقم غير صحيح**

📏 **المطلوب:** 11 رقم بالضبط
📍 **أنت أدخلت:** {len(cleaned)} رقم (أكثر من المطلوب)
🔢 **الرقم المدخل:** `{cleaned}`

✅ **مثال صحيح:** `01094591331`"""
            return result
        
        # 3. فحص البداية
        prefix = cleaned[:3]
        if prefix not in self.EGYPTIAN_NETWORKS:
            result['error_type'] = 'invalid_prefix'
            result['error_message'] = f"""❌ **بداية الرقم غير صحيحة**

📍 **يجب أن يبدأ بـ:** 010 / 011 / 012 / 015
🚫 **رقمك يبدأ بـ:** `{prefix}`
🔢 **الرقم المدخل:** `{cleaned}`

📱 **الشبكات المدعومة:**
⭕️ **010** - فودافون
🟢 **011** - اتصالات  
🍊 **012** - أورانج
🟣 **015** - وي

✅ **مثال صحيح:** `01094591331`"""
            return result
        
        # النجاح!
        network = self.EGYPTIAN_NETWORKS[prefix]
        result['is_valid'] = True
        result['cleaned_number'] = cleaned
        result['network_info'] = network
        
        # حفظ الرقم لمنع التكرار
        self.last_numbers[user_id] = cleaned
        
        return result
    
    def record_failure(self, user_id: int):
        """تسجيل محاولة فاشلة"""
        self.failed_attempts[user_id] += 1
        
        if self.failed_attempts[user_id] >= self.MAX_FAILED_ATTEMPTS:
            self.blocked_users[user_id] = datetime.now()
            return True  # تم الحظر
        
        return False
    
    def reset_user_failures(self, user_id: int):
        """إعادة تعيين المحاولات الفاشلة عند النجاح"""
        self.failed_attempts[user_id] = 0
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]
    
    def get_remaining_attempts(self, user_id: int) -> int:
        """الحصول على عدد المحاولات المتبقية"""
        return self.MAX_FAILED_ATTEMPTS - self.failed_attempts.get(user_id, 0)

# إنشاء نظام الحماية
whatsapp_security = WhatsAppSecuritySystem()

# ================================ نظام التشفير المتقدم ================================
class EncryptionSystem:
    """نظام تشفير متقدم للبيانات الحساسة"""
    
    def __init__(self):
        # استخدام مفتاح ثابت آمن (في الإنتاج يجب استخدام مفتاح من متغيرات البيئة)
        self.master_key = b'FC26_BOT_SECURE_ENCRYPTION_KEY_2025_PRODUCTION'
        self._init_cipher()
    
    def _init_cipher(self):
        """تهيئة نظام التشفير"""
        # إنشاء KDF للحصول على مفتاح قوي
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'FC26_SALT_2025',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """تشفير البيانات"""
        if not data:
            return ""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"خطأ في التشفير: {e}")
            return data  # إرجاع البيانات بدون تشفير في حالة الخطأ
    
    def decrypt(self, encrypted_data: str) -> str:
        """فك تشفير البيانات"""
        if not encrypted_data:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"خطأ في فك التشفير: {e}")
            return encrypted_data  # إرجاع البيانات كما هي في حالة الخطأ

# إنشاء نظام التشفير
encryption_system = EncryptionSystem()

# ================================ نظام التحقق من طرق الدفع ================================
class PaymentValidationSystem:
    """نظام التحقق المتقدم من طرق الدفع"""
    
    def __init__(self):
        # تتبع المحاولات لكل مستخدم
        self.user_attempts: Dict[int, List[datetime]] = defaultdict(list)
        self.failed_attempts: Dict[int, int] = defaultdict(int)
        self.blocked_users: Dict[int, datetime] = {}
        
        # إعدادات الحماية
        self.MAX_ATTEMPTS_PER_MINUTE = 8
        self.MAX_FAILED_ATTEMPTS = 4
        self.BLOCK_DURATION_MINUTES = 10
        self.RATE_LIMIT_WINDOW = 60  # ثانية
        
        # قواعد التحقق لكل طريقة دفع
        self.PAYMENT_RULES = {
            'vodafone_cash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'فودافون كاش',
                'example': '01012345678',
                'network': 'جميع الشبكات'
            },
            'etisalat_cash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'اتصالات كاش',
                'example': '01112345678',
                'network': 'جميع الشبكات'
            },
            'orange_cash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'أورانج كاش',
                'example': '01212345678',
                'network': 'جميع الشبكات'
            },
            'we_cash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'وي كاش',
                'example': '01512345678',
                'network': 'جميع الشبكات'
            },
            'bank_wallet': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'محفظة بنكية',
                'example': '01012345678',
                'network': 'جميع الشبكات المصرية'
            },
            'telda': {
                'type': 'card',
                'length': 16,
                'name': 'تيلدا',
                'example': '1234567890123456'
            },
            'instapay': {
                'type': 'link',
                'name': 'إنستا باي',
                'keywords': ['instapay', 'ipn.eg'],
                'example': 'https://instapay.com/username'
            }
        }
    
    def is_user_blocked(self, user_id: int) -> Tuple[bool, Optional[int]]:
        """التحقق من حظر المستخدم"""
        if user_id in self.blocked_users:
            block_time = self.blocked_users[user_id]
            elapsed = (datetime.now() - block_time).total_seconds() / 60
            
            if elapsed < self.BLOCK_DURATION_MINUTES:
                remaining = self.BLOCK_DURATION_MINUTES - int(elapsed)
                return True, remaining
            else:
                # انتهت فترة الحظر
                del self.blocked_users[user_id]
                self.failed_attempts[user_id] = 0
        
        return False, None
    
    def check_rate_limit(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """فحص معدل الطلبات"""
        now = datetime.now()
        
        # تنظيف المحاولات القديمة
        if user_id in self.user_attempts:
            self.user_attempts[user_id] = [
                attempt for attempt in self.user_attempts[user_id]
                if (now - attempt).total_seconds() < self.RATE_LIMIT_WINDOW
            ]
        
        # فحص عدد المحاولات
        attempts_count = len(self.user_attempts[user_id])
        
        if attempts_count >= self.MAX_ATTEMPTS_PER_MINUTE:
            return False, f"⚠️ لقد تجاوزت الحد المسموح ({self.MAX_ATTEMPTS_PER_MINUTE} محاولات في الدقيقة)\\n\\n⏰ انتظر قليلاً ثم حاول مرة أخرى"
        
        # تسجيل المحاولة الجديدة
        self.user_attempts[user_id].append(now)
        return True, None
    
    def validate_wallet(self, text: str, payment_method: str) -> Dict[str, Any]:
        """التحقق من رقم المحفظة الإلكترونية"""
        result = {
            'is_valid': False,
            'cleaned_data': '',
            'error_message': '',
            'network': ''
        }
        
        # تنظيف الرقم من الرموز
        cleaned = re.sub(r'[^\d]', '', text)
        
        rules = self.PAYMENT_RULES[payment_method]
        
        # فحص وجود أحرف أو رموز
        if re.search(r'[a-zA-Z]', text):
            result['error_message'] = f"""❌ **رقم {rules['name']} غير صحيح**

📍 **يجب أن يكون:**
• أرقام فقط (بدون حروف أو رموز)
• 11 رقم بالضبط
• يبدأ بـ {'/'.join(rules['prefix'])} فقط

✅ **مثال صحيح:** `{rules['example']}`"""
            
            if payment_method == 'bank_wallet':
                result['error_message'] += "\n\n📍 **تنبيه:** المحفظة البنكية تقبل جميع الشبكات المصرية (010/011/012/015)"
            
            return result
        
        # فحص الطول
        if len(cleaned) != rules['length']:
            result['error_message'] = f"""❌ **رقم {rules['name']} غير صحيح**

📏 **الطول المطلوب:** {rules['length']} رقم
📍 **أنت أدخلت:** {len(cleaned)} رقم

✅ **مثال صحيح:** `{rules['example']}`"""
            return result
        
        # فحص البداية
        prefix = cleaned[:3]
        if prefix not in rules['prefix']:
            result['error_message'] = f"""❌ **رقم {rules['name']} غير صحيح**

📍 **يجب أن يبدأ بـ:** {'/'.join(rules['prefix'])} فقط
🚫 **رقمك يبدأ بـ:** `{prefix}`

✅ **مثال صحيح:** `{rules['example']}`"""
            
            if payment_method == 'bank_wallet':
                result['error_message'] += "\n\n📍 **تنبيه:** المحفظة البنكية تقبل جميع الشبكات المصرية (010/011/012/015)"
            
            return result
        
        # النجاح
        result['is_valid'] = True
        result['cleaned_data'] = cleaned
        result['network'] = rules['network']
        
        return result
    
    def validate_telda(self, text: str) -> Dict[str, Any]:
        """التحقق من رقم كارت تيلدا"""
        result = {
            'is_valid': False,
            'cleaned_data': '',
            'error_message': ''
        }
        
        # السماح بالمسافات والشرطات ثم إزالتها
        cleaned = re.sub(r'[\s\-]', '', text)
        
        # إزالة أي شيء غير الأرقام
        digits_only = re.sub(r'[^\d]', '', cleaned)
        
        # فحص وجود أحرف
        if re.search(r'[a-zA-Z]', text):
            result['error_message'] = """❌ **رقم كارت تيلدا غير صحيح**

📍 **يجب أن يكون:**
• 16 رقم بالضبط
• أرقام فقط (يُسمح بالمسافات والشرطات)
• بدون حروف أو رموز غريبة

✅ **أمثلة صحيحة:**
• `1234567890123456`
• `1234-5678-9012-3456`
• `1234 5678 9012 3456`"""
            return result
        
        # فحص الطول
        if len(digits_only) != 16:
            result['error_message'] = f"""❌ **رقم كارت تيلدا غير صحيح**

📏 **المطلوب:** 16 رقم بالضبط
📍 **أنت أدخلت:** {len(digits_only)} رقم

✅ **أمثلة صحيحة:**
• `1234567890123456`
• `1234-5678-9012-3456`
• `1234 5678 9012 3456`"""
            return result
        
        # النجاح
        result['is_valid'] = True
        result['cleaned_data'] = digits_only
        
        return result
    
    def validate_instapay(self, text: str) -> Dict[str, Any]:
        """التحقق من رابط إنستاباي واستخراج الرابط الصحيح فقط"""
        result = {
            'is_valid': False,
            'cleaned_data': '',
            'error_message': ''
        }
        
        # تنظيف النص
        text = text.strip()
        
        # البحث عن روابط InstaPay أو IPN في النص
        import re
        
        # نمط للبحث عن روابط ipn.eg أو instapay
        # يبحث عن روابط كاملة مثل https://ipn.eg/S/username/instapay/ABC123
        url_patterns = [
            r'https?://ipn\.eg/[^\s]+',  # روابط ipn.eg
            r'https?://instapay\.com/[^\s]+',  # روابط instapay.com
            r'ipn\.eg/[^\s]+',  # روابط ipn.eg بدون https
            r'instapay\.com/[^\s]+',  # روابط instapay.com بدون https
        ]
        
        # البحث عن أول رابط مطابق
        for pattern in url_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                found_url = match.group(0)
                # إضافة https:// إذا لم يكن موجوداً
                if not found_url.startswith('http'):
                    found_url = f"https://{found_url}"
                result['is_valid'] = True
                result['cleaned_data'] = found_url
                return result
        
        # إذا لم يتم العثور على رابط، نتحقق من النص بشكل عام
        if any(keyword in text.lower() for keyword in ['instapay', 'ipn.eg', 'ipn']):
            # إذا كان النص يحتوي على كلمات مفتاحية لكن ليس بتنسيق رابط صحيح
            # نحاول تنظيف النص وأخذ أول رابط
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if 'https://' in line or 'http://' in line:
                    # استخراج الرابط من السطر
                    url_match = re.search(r'https?://[^\s]+', line)
                    if url_match:
                        result['is_valid'] = True
                        result['cleaned_data'] = url_match.group(0)
                        return result
        
        # فشل التحقق
        result['error_message'] = """❌ **رابط إنستاباي غير صحيح**

📍 **يجب إدخال رابط كامل فقط**
• لا يُقبل اسم المستخدم بدون رابط
• يجب أن يحتوي على instapay أو ipn.eg

✅ **أمثلة صحيحة:**
• `https://ipn.eg/S/username/instapay/ABC123`
• `https://instapay.com/username`
• `ipn.eg/S/ABC123`
• `instapay.com/username`"""
        
        return result
    
    def record_failure(self, user_id: int):
        """تسجيل محاولة فاشلة"""
        self.failed_attempts[user_id] += 1
        
        if self.failed_attempts[user_id] >= self.MAX_FAILED_ATTEMPTS:
            self.blocked_users[user_id] = datetime.now()
            return True  # تم الحظر
        
        return False
    
    def reset_user_failures(self, user_id: int):
        """إعادة تعيين المحاولات الفاشلة عند النجاح"""
        self.failed_attempts[user_id] = 0
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]
    
    def get_remaining_attempts(self, user_id: int) -> int:
        """الحصول على عدد المحاولات المتبقية"""
        return self.MAX_FAILED_ATTEMPTS - self.failed_attempts.get(user_id, 0)

# إنشاء نظام التحقق من طرق الدفع
payment_validation = PaymentValidationSystem()

# ================================ قاعدة البيانات ================================
class Database:
    """مدير قاعدة البيانات"""

    def __init__(self):
        self.init_database()

    def get_connection(self):
        """إنشاء اتصال جديد"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """تهيئة قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                registration_status TEXT DEFAULT 'incomplete',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول بيانات التسجيل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration_data (
                user_id INTEGER PRIMARY KEY,
                platform TEXT,
                whatsapp TEXT,
                payment_method TEXT,
                payment_details TEXT,
                payment_details_type TEXT,
                payment_network TEXT,
                phone TEXT,
                payment_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')



        # جدول التسجيل المؤقت
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_registration (
                telegram_id INTEGER PRIMARY KEY,
                step_name TEXT,
                step_number INTEGER,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # جدول المحفظة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet (
                user_id INTEGER PRIMARY KEY,
                coin_balance REAL DEFAULT 0,
                loyalty_points INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # جدول المعاملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount REAL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        conn.commit()
        conn.close()

    def create_user(self, telegram_id: int, username: str, full_name: str) -> int:
        """إنشاء مستخدم جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, full_name)
                VALUES (?, ?, ?)
            ''', (telegram_id, username, full_name))

            if cursor.rowcount == 0:
                cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
                user_id = cursor.fetchone()['user_id']
            else:
                user_id = cursor.lastrowid

                # إنشاء سجلات فارغة
                cursor.execute('INSERT INTO registration_data (user_id) VALUES (?)', (user_id,))
                cursor.execute('INSERT INTO wallet (user_id) VALUES (?)', (user_id,))

            conn.commit()
            conn.close()
            return user_id

        except Exception as e:
            conn.close()
            logger.error(f"خطأ في إنشاء المستخدم: {e}")
            return None

    def save_temp_registration(self, telegram_id: int, step_name: str, step_number: int, data: dict):
        """حفظ التسجيل المؤقت"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO temp_registration (telegram_id, step_name, step_number, data)
            VALUES (?, ?, ?, ?)
        ''', (telegram_id, step_name, step_number, json.dumps(data)))

        conn.commit()
        conn.close()

    def get_temp_registration(self, telegram_id: int) -> Optional[dict]:
        """استرجاع التسجيل المؤقت"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM temp_registration WHERE telegram_id = ?
        ''', (telegram_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'step_name': row['step_name'],
                'step_number': row['step_number'],
                'data': json.loads(row['data'])
            }
        return None

    def clear_temp_registration(self, telegram_id: int):
        """حذف التسجيل المؤقت"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
        conn.commit()
        conn.close()

    def complete_registration(self, telegram_id: int, data: dict) -> bool:
        """إكمال التسجيل"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # الحصول على معرف المستخدم
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                return False

            user_id = user['user_id']

            # محاولة إضافة الحقول الجديدة إذا لم تكن موجودة (مع حماية من الأخطاء)
            try:
                cursor.execute("ALTER TABLE registration_data ADD COLUMN payment_details TEXT")
            except sqlite3.OperationalError:
                pass  # العمود موجود بالفعل
            except Exception as e:
                logger.debug(f"Column payment_details may already exist: {e}")
                pass
            
            try:
                cursor.execute("ALTER TABLE registration_data ADD COLUMN payment_details_type TEXT")
            except sqlite3.OperationalError:
                pass  # العمود موجود بالفعل
            except Exception as e:
                logger.debug(f"Column payment_details_type may already exist: {e}")
                pass
            
            try:
                cursor.execute("ALTER TABLE registration_data ADD COLUMN payment_network TEXT")
            except sqlite3.OperationalError:
                pass  # العمود موجود بالفعل
            except Exception as e:
                logger.debug(f"Column payment_network may already exist: {e}")
                pass
            
            # تحديث بيانات التسجيل
            cursor.execute('''
                UPDATE registration_data
                SET platform = ?, whatsapp = ?, payment_method = ?
                WHERE user_id = ?
            ''', (
                data.get('platform'),
                data.get('whatsapp'),
                data.get('payment_method'),
                user_id
            ))
            
            # محاولة تحديث الحقول الجديدة إذا كانت موجودة
            if data.get('payment_details'):
                try:
                    cursor.execute('''
                        UPDATE registration_data
                        SET payment_details = ?, payment_details_type = ?, payment_network = ?
                        WHERE user_id = ?
                    ''', (
                        data.get('payment_details'),
                        data.get('payment_details_type'),
                        data.get('payment_network'),
                        user_id
                    ))
                except:
                    pass



            # تحديث حالة التسجيل
            cursor.execute('''
                UPDATE users SET registration_status = 'complete' WHERE user_id = ?
            ''', (user_id,))

            # إضافة نقاط الترحيب
            cursor.execute('''
                UPDATE wallet SET loyalty_points = loyalty_points + 100 WHERE user_id = ?
            ''', (user_id,))

            conn.commit()
            conn.close()

            # حذف البيانات المؤقتة
            self.clear_temp_registration(telegram_id)

            return True

        except Exception as e:
            conn.close()
            logger.error(f"خطأ في إكمال التسجيل: {e}")
            return False

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[dict]:
        """الحصول على المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    def get_user_profile(self, telegram_id: int) -> Optional[dict]:
        """الحصول على الملف الشخصي"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.*, r.*, w.*
            FROM users u
            LEFT JOIN registration_data r ON u.user_id = r.user_id
            LEFT JOIN wallet w ON u.user_id = w.user_id
            WHERE u.telegram_id = ?
        ''', (telegram_id,))

        row = cursor.fetchone()

        if row:
            profile = dict(row)

            # عدد المعاملات
            cursor.execute('''
                SELECT COUNT(*) as transaction_count
                FROM transactions WHERE user_id = ?
            ''', (profile['user_id'],))

            profile['transaction_count'] = cursor.fetchone()['transaction_count']
            profile['level_name'] = self._get_level_name(profile.get('loyalty_points', 0))

            conn.close()
            return profile

        conn.close()
        return None

    def _get_level_name(self, points: int) -> str:
        """تحديد اسم المستوى"""
        if points >= 5000:
            return 'أسطورة 👑'
        elif points >= 1000:
            return 'خبير 💎'
        elif points >= 500:
            return 'محترف ⚡'
        elif points >= 100:
            return 'نشط 🔥'
        else:
            return 'مبتدئ 🌱'

    def delete_user_account(self, telegram_id: int) -> bool:
        """حذف حساب المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                return False

            user_id = user['user_id']

            # حذف من جميع الجداول
            cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM wallet WHERE user_id = ?', (user_id,))

            cursor.execute('DELETE FROM registration_data WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            logger.error(f"خطأ في حذف الحساب: {e}")
            return False







# ================================ لوحات المفاتيح ================================
class Keyboards:
    """لوحات المفاتيح"""

    @staticmethod
    def get_start_keyboard():
        """لوحة البداية"""
        keyboard = [
            [InlineKeyboardButton("🆕 تسجيل جديد", callback_data="register_new")],
            [InlineKeyboardButton("📞 الدعم الفني", callback_data="support")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_platform_keyboard():
        """لوحة المنصات"""
        keyboard = []
        for key, platform in GAMING_PLATFORMS.items():
            keyboard.append([
                InlineKeyboardButton(platform['name'], callback_data=f"platform_{key}")
            ])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_payment_keyboard():
        """لوحة طرق الدفع"""
        keyboard = []
        for key, method in PAYMENT_METHODS.items():
            keyboard.append([
                InlineKeyboardButton(method['name'], callback_data=f"payment_{key}")
            ])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_continue_keyboard():
        """لوحة الاستكمال"""
        keyboard = [
            [InlineKeyboardButton("✅ أكمل من حيث توقفت", callback_data="continue_registration")],
            [InlineKeyboardButton("🔄 ابدأ من جديد", callback_data="restart_registration")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_delete_keyboard():
        """لوحة حذف الحساب"""
        keyboard = [
            [InlineKeyboardButton("✅ نعم، احذف حسابي", callback_data="confirm_delete")],
            [InlineKeyboardButton("❌ لا، تراجع", callback_data="cancel_delete")]
        ]
        return InlineKeyboardMarkup(keyboard)

# ================================ معالج التسجيل الذكي ================================
class SmartRegistrationHandler:
    """معالج التسجيل مع النظام الذكي"""

    def __init__(self):
        self.db = Database()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بداية التسجيل"""
        telegram_id = update.effective_user.id
        username = update.effective_user.username

        # التحقق من وجود تسجيل سابق غير مكتمل
        temp_data = self.db.get_temp_registration(telegram_id)

        if temp_data:
            # استعادة البيانات المحفوظة
            context.user_data['registration'] = temp_data['data']
            step = temp_data['step_number']

            step_names = {
                ENTERING_WHATSAPP: "إدخال واتساب",
                CHOOSING_PAYMENT: "اختيار طريقة الدفع"
            }
            last_step = step_names.get(step, "غير معروف")

            message = MESSAGES['welcome_back'].format(last_step=last_step)

            # إضافة أزرار للاختيار بين المتابعة أو البدء من جديد
            keyboard = [
                [InlineKeyboardButton("✅ متابعة من حيث توقفت", callback_data="continue_registration")],
                [InlineKeyboardButton("🔄 البدء من جديد", callback_data="restart_registration")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # إرسال رسالة مع الأزرار
            await smart_message_manager.send_new_active_message(
                update, context,
                message + "\n\nماذا تريد أن تفعل؟",
                reply_markup=reply_markup
            )

            # لا نرسل رسالة الخطوة مباشرة، بل ننتظر اختيار المستخدم
            return ConversationHandler.END


        # مستخدم جديد
        await smart_message_manager.send_new_active_message(
            update, context, MESSAGES['welcome'],
            reply_markup=Keyboards.get_start_keyboard()
        )

        return ConversationHandler.END

    async def handle_registration_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء التسجيل الجديد مع حماية من الضغط المتكرر"""
        query = update.callback_query
        
        # الرد على الـ callback query بسرعة
        await query.answer()
        
        telegram_id = query.from_user.id
        username = query.from_user.username
        full_name = query.from_user.full_name
        
        # التحقق من عدم وجود تسجيل قيد المعالجة
        if 'registration' in context.user_data and context.user_data['registration'].get('in_progress'):
            logger.debug(f"تجاهل محاولة بدء تسجيل مكرر للمستخدم {telegram_id}")
            return

        # وضع علامة أن التسجيل قيد المعالجة
        context.user_data['registration'] = {
            'in_progress': True,
            'telegram_id': telegram_id
        }

        # مسح أي بيانات تسجيل قديمة
        self.db.clear_temp_registration(telegram_id)

        user_id = self.db.create_user(telegram_id, username, full_name)

        # تحديث بيانات التسجيل
        context.user_data['registration'].update({
            'user_id': user_id,
            'in_progress': False  # إلغاء العلامة بعد اكتمال المعالجة
        })

        await smart_message_manager.update_current_message(
            update, context, MESSAGES['choose_platform'],
            reply_markup=Keyboards.get_platform_keyboard()
        )

        return CHOOSING_PLATFORM

    async def handle_platform_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار المنصة مع حماية من الضغط المتكرر"""
        query = update.callback_query
        
        # الرد على الـ callback query بسرعة لمنع ظهور رمز التحميل
        await query.answer()
        
        # التحقق من أن البيانات صحيحة
        if not query.data.startswith("platform_"):
            return
        
        platform_key = query.data.replace("platform_", "")
        
        # التحقق من صحة المنصة
        if platform_key not in GAMING_PLATFORMS:
            await query.answer("❌ منصة غير صحيحة", show_alert=True)
            return
        
        platform_name = GAMING_PLATFORMS[platform_key]['name']

        # التحقق من وجود بيانات التسجيل
        if 'registration' not in context.user_data:
            context.user_data['registration'] = {
                'telegram_id': query.from_user.id
            }
        
        # التحقق من عدم تكرار نفس الاختيار
        if context.user_data['registration'].get('platform') == platform_key:
            logger.debug(f"تجاهل اختيار منصة مكرر: {platform_key}")
            return

        context.user_data['registration']['platform'] = platform_key

        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'platform_chosen', ENTERING_WHATSAPP,
            context.user_data['registration']
        )

        # استخدام update_current_message لتحديث الرسالة الحالية بدلاً من إرسال جديدة
        await smart_message_manager.update_current_message(
            update, context,
            f"✅ تم اختيار: {platform_name}\n\n" + MESSAGES['enter_whatsapp']
        )

        return ENTERING_WHATSAPP

    async def handle_whatsapp_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال واتساب مع نظام الحماية المتقدم"""
        user_id = update.effective_user.id
        whatsapp_input = update.message.text.strip()
        
        # 1. فحص الحظر
        is_blocked, remaining_minutes = whatsapp_security.is_user_blocked(user_id)
        if is_blocked:
            await smart_message_manager.send_new_active_message(
                update, context,
                f"""🚫 **أنت محظور مؤقتاً**

⏰ **المدة المتبقية:** {remaining_minutes} دقيقة

📝 **السبب:** تجاوز عدد المحاولات الخاطئة المسموح بها

💡 **نصيحة:** تأكد من إدخال رقم واتساب صحيح عند المحاولة مرة أخرى""",
                disable_previous=False
            )
            return ENTERING_WHATSAPP
        
        # 2. فحص معدل الطلبات
        rate_ok, rate_message = whatsapp_security.check_rate_limit(user_id)
        if not rate_ok:
            await smart_message_manager.send_new_active_message(
                update, context,
                rate_message,
                disable_previous=False
            )
            return ENTERING_WHATSAPP
        
        # 3. فحص التكرار
        if whatsapp_security.check_duplicate(user_id, whatsapp_input):
            await smart_message_manager.send_new_active_message(
                update, context,
                f"""⚠️ **لقد أدخلت هذا الرقم بالفعل**

🔢 **الرقم:** `{whatsapp_input}`

💡 **نصيحة:** إذا كان الرقم صحيحاً، انتظر رسالة التأكيد
إذا كنت تريد تغييره، أدخل رقماً مختلفاً""",
                disable_previous=False
            )
            return ENTERING_WHATSAPP
        
        # 4. التحقق الشامل من الرقم
        validation = whatsapp_security.validate_whatsapp(whatsapp_input, user_id)
        
        if not validation['is_valid']:
            # تسجيل المحاولة الفاشلة
            was_blocked = whatsapp_security.record_failure(user_id)
            remaining = whatsapp_security.get_remaining_attempts(user_id)
            
            # إضافة معلومات المحاولات المتبقية للرسالة
            error_msg = validation['error_message']
            
            if was_blocked:
                error_msg += f"""

🚫 **تم حظرك مؤقتاً لمدة {whatsapp_security.BLOCK_DURATION_MINUTES} دقيقة**
السبب: تجاوز عدد المحاولات الخاطئة"""
            elif remaining > 0:
                error_msg += f"""

⚠️ **تحذير:** لديك {remaining} محاولات متبقية"""
            
            await smart_message_manager.send_new_active_message(
                update, context,
                error_msg,
                disable_previous=False
            )
            
            # تسجيل المحاولة في السجلات
            logger.warning(f"محاولة فاشلة من المستخدم {user_id}: {validation['error_type']} - Input: {whatsapp_input}")
            
            return ENTERING_WHATSAPP
        
        # 5. النجاح! إعادة تعيين المحاولات الفاشلة
        whatsapp_security.reset_user_failures(user_id)
        
        # التأكد من وجود registration في context
        if 'registration' not in context.user_data:
            context.user_data['registration'] = {
                'telegram_id': user_id
            }
        
        # حفظ الرقم المنظف في السياق
        cleaned_number = validation['cleaned_number']
        network_info = validation['network_info']
        
        context.user_data['registration']['whatsapp'] = cleaned_number
        context.user_data['registration']['whatsapp_network'] = network_info['name']
        
        # حفظ في قاعدة البيانات المؤقتة
        try:
            self.db.save_temp_registration(
                context.user_data['registration']['telegram_id'],
                'whatsapp_entered',
                CHOOSING_PAYMENT,
                context.user_data['registration']
            )
        except Exception as e:
            logger.error(f"Error saving temp registration: {e}")
        
        # رسالة النجاح المفصلة
        success_message = f"""✅ **تم حفظ رقم الواتساب بنجاح!**

📱 **الرقم:** `{cleaned_number}`
🌐 **الشبكة:** {network_info['emoji']} {network_info['name']}
💾 **تم الحفظ التلقائي** ✅

━━━━━━━━━━━━━━━━
⏭️ **الخطوة التالية:** اختر طريقة الدفع المفضلة"""
        
        # إرسال رسالة النجاح مع خيارات الدفع
        await smart_message_manager.send_new_active_message(
            update, context,
            success_message + "\n\n" + MESSAGES['choose_payment'],
            reply_markup=Keyboards.get_payment_keyboard(),
            choice_made=f"واتساب: {cleaned_number}"
        )
        
        # تسجيل النجاح
        logger.info(f"تم حفظ رقم واتساب للمستخدم {user_id}: {cleaned_number} - شبكة: {network_info['name']}")
        
        return CHOOSING_PAYMENT

    async def handle_payment_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار طريقة الدفع مع حماية من الضغط المتكرر"""
        query = update.callback_query
        
        # الرد على الـ callback query بسرعة
        await query.answer()
        
        # التحقق من أن البيانات صحيحة
        if not query.data.startswith("payment_"):
            return
        
        payment_key = query.data.replace("payment_", "")
        
        # التحقق من صحة طريقة الدفع
        if payment_key not in PAYMENT_METHODS:
            await query.answer("❌ طريقة دفع غير صحيحة", show_alert=True)
            return
        
        payment_name = PAYMENT_METHODS[payment_key]['name']
        
        # التحقق من وجود بيانات التسجيل
        if 'registration' not in context.user_data:
            await query.answer("❌ يجب البدء من جديد", show_alert=True)
            return ConversationHandler.END
        
        # التحقق من عدم تكرار نفس الاختيار
        if context.user_data['registration'].get('payment_method') == payment_key:
            logger.debug(f"تجاهل اختيار طريقة دفع مكررة: {payment_key}")
            return

        context.user_data['registration']['payment_method'] = payment_key
        
        # حفظ في قاعدة البيانات المؤقتة
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'payment_method_chosen',
            ENTERING_PAYMENT_DETAILS,
            context.user_data['registration']
        )
        
        # عرض التعليمات حسب نوع طريقة الدفع
        instructions = self.get_payment_instructions(payment_key)
        
        await smart_message_manager.update_current_message(
            update, context,
            instructions
        )
        
        return ENTERING_PAYMENT_DETAILS
    
    def get_payment_instructions(self, payment_key: str) -> str:
        """الحصول على التعليمات المناسبة لكل طريقة دفع"""
        
        if payment_key == 'vodafone_cash':
            return """⭕️ **فودافون كاش**

📱 **أدخل رقم:**

📝 **القواعد:**
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ **مثال صحيح:** `01012345678`"""
        
        elif payment_key == 'etisalat_cash':
            return """🟢 **اتصالات كاش**

📱 **أدخل رقم:**

📝 **القواعد:**
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ **مثال صحيح:** `01112345678`"""
        
        elif payment_key == 'orange_cash':
            return """🍊 **أورانج كاش**

📱 **أدخل رقم:**

📝 **القواعد:**
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ **مثال صحيح:** `01212345678`"""
        
        elif payment_key == 'we_cash':
            return """🟣 **وي كاش**

📱 **أدخل رقم:**

📝 **القواعد:**
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ **مثال صحيح:** `01512345678`"""
        
        elif payment_key == 'bank_wallet':
            return """🏦 **محفظة بنكية**

📱 **أدخل رقم المحفظة البنكية:**

📝 **القواعد:**
• 11 رقم بالضبط
• يقبل جميع الشبكات: 010/011/012/015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ **أمثلة صحيحة:**
• `01012345678` - فودافون ⭕
• `01112345678` - اتصالات 🟢
• `01212345678` - أورانج 🍊
• `01512345678` - وي 🟣

📌 **ملاحظة مهمة:** المحفظة البنكية تقبل جميع الشبكات المصرية
✅ **يمكنك استخدام أي رقم من الشبكات الأربعة**"""
        
        elif payment_key == 'telda':
            return """💳 **تيلدا**

💳 **أدخل رقم كارت تيلدا:**

📝 **القواعد:**
• 16 رقم بالضبط
• أرقام فقط
• يُسمح بالمسافات والشرطات (سيتم إزالتها تلقائياً)

✅ **أمثلة صحيحة:**
• `1234567890123456`
• `1234-5678-9012-3456`
• `1234 5678 9012 3456`"""
        
        elif payment_key == 'instapay':
            return """🔗 **إنستا باي**

🔗 **أدخل رابط إنستاباي كامل:**

📝 **القواعد:**
• يجب إدخال رابط كامل فقط
• لا يُقبل اسم المستخدم بدون رابط
• يجب أن يحتوي على instapay أو ipn.eg

✅ **أمثلة صحيحة:**
• `https://ipn.eg/S/username/instapay/ABC123`
• `https://instapay.com/username`
• `ipn.eg/S/ABC123`
• `instapay.com/username`"""
        
        return "طريقة دفع غير معروفة"
    
    async def handle_payment_details_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج إدخال بيانات طريقة الدفع مع التشفير"""
        user_id = update.effective_user.id
        payment_input = update.message.text.strip()
        
        # التحقق من وجود بيانات التسجيل
        if 'registration' not in context.user_data or 'payment_method' not in context.user_data['registration']:
            await smart_message_manager.send_new_active_message(
                update, context,
                "❌ حدث خطأ. يرجى البدء من جديد بكتابة /start",
                disable_previous=False
            )
            return ConversationHandler.END
        
        payment_method = context.user_data['registration']['payment_method']
        
        # 1. فحص الحظر
        is_blocked, remaining_minutes = payment_validation.is_user_blocked(user_id)
        if is_blocked:
            await smart_message_manager.send_new_active_message(
                update, context,
                f"""🚫 **أنت محظور مؤقتاً**

⏰ **المدة المتبقية:** {remaining_minutes} دقيقة

📝 **السبب:** تجاوز عدد المحاولات الخاطئة المسموح بها

💡 **نصيحة:** تأكد من إدخال البيانات الصحيحة عند المحاولة مرة أخرى""",
                disable_previous=False
            )
            return ENTERING_PAYMENT_DETAILS
        
        # 2. فحص معدل الطلبات
        rate_ok, rate_message = payment_validation.check_rate_limit(user_id)
        if not rate_ok:
            await smart_message_manager.send_new_active_message(
                update, context,
                rate_message,
                disable_previous=False
            )
            return ENTERING_PAYMENT_DETAILS
        
        # 3. التحقق حسب نوع طريقة الدفع
        validation_result = None
        payment_type = None
        
        if payment_method in ['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash', 'bank_wallet']:
            validation_result = payment_validation.validate_wallet(payment_input, payment_method)
            payment_type = 'wallet'
        elif payment_method == 'telda':
            validation_result = payment_validation.validate_telda(payment_input)
            payment_type = 'card'
        elif payment_method == 'instapay':
            validation_result = payment_validation.validate_instapay(payment_input)
            payment_type = 'link'
        
        # 4. معالجة النتيجة
        if not validation_result['is_valid']:
            # تسجيل المحاولة الفاشلة
            was_blocked = payment_validation.record_failure(user_id)
            remaining = payment_validation.get_remaining_attempts(user_id)
            
            # إضافة معلومات المحاولات المتبقية للرسالة
            error_msg = validation_result['error_message']
            
            if was_blocked:
                error_msg += f"""

🚫 **تم حظرك مؤقتاً لمدة {payment_validation.BLOCK_DURATION_MINUTES} دقيقة**
السبب: تجاوز عدد المحاولات الخاطئة"""
            elif remaining > 0:
                error_msg += f"""

⚠️ **تحذير:** لديك {remaining} محاولات متبقية"""
            
            await smart_message_manager.send_new_active_message(
                update, context,
                error_msg,
                disable_previous=False
            )
            
            # تسجيل المحاولة في السجلات (بدون البيانات الحساسة)
            logger.warning(f"محاولة فاشلة من المستخدم {user_id} لطريقة دفع: {payment_method}")
            
            return ENTERING_PAYMENT_DETAILS
        
        # 5. النجاح! إعادة تعيين المحاولات الفاشلة
        payment_validation.reset_user_failures(user_id)
        
        # 6. تشفير البيانات الحساسة
        encrypted_data = encryption_system.encrypt(validation_result['cleaned_data'])
        
        # 7. حفظ البيانات المشفرة
        context.user_data['registration']['payment_details'] = encrypted_data
        context.user_data['registration']['payment_details_type'] = payment_type
        
        if payment_type == 'wallet':
            context.user_data['registration']['payment_network'] = validation_result.get('network', '')
        
        # 8. حفظ في قاعدة البيانات المؤقتة
        try:
            self.db.save_temp_registration(
                context.user_data['registration']['telegram_id'],
                'payment_details_entered',
                ConversationHandler.END,
                context.user_data['registration']
            )
        except Exception as e:
            logger.error(f"Error saving temp registration: {e}")
        
        # 9. إعداد رسالة النجاح
        payment_name = PAYMENT_METHODS[payment_method]['name']
        
        if payment_type == 'wallet':
            success_message = f"""✅ **تم حفظ {payment_name}!**

📱 **الرقم:** `{validation_result['cleaned_data']}`

━━━━━━━━━━━━━━━━"""
        elif payment_type == 'card':
            # عرض رقم الكارت كامل للعميل بدون إخفاء
            success_message = f"""✅ **تم حفظ كارت تيلدا!**

💳 **رقم الكارت:** `{validation_result['cleaned_data']}`

━━━━━━━━━━━━━━━━"""
        elif payment_type == 'link':
            success_message = f"""✅ **تم حفظ رابط إنستاباي!**

🔗 **الرابط:** `{validation_result['cleaned_data']}`

━━━━━━━━━━━━━━━━"""
        
        # 10. إرسال رسالة النجاح ثم الانتقال للتأكيد النهائي
        await smart_message_manager.send_new_active_message(
            update, context,
            success_message,
            choice_made=f"{payment_name}: تم الحفظ"
        )
        
        # تسجيل النجاح (بدون البيانات الحساسة)
        logger.info(f"تم حفظ بيانات دفع للمستخدم {user_id}: نوع {payment_method}")
        
        # الانتقال للتأكيد النهائي
        return await self.show_confirmation(update, context)



    async def show_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض التأكيد والحفظ التلقائي مع فك تشفير البيانات"""
        reg_data = context.user_data['registration']
        telegram_id = reg_data['telegram_id']
        
        # الحصول على اسم المستخدم
        if update.callback_query:
            username = update.callback_query.from_user.username
        else:
            username = update.effective_user.username
        
        # إضافة @ للمستخدم إذا كان موجود
        username_display = f"@{username}" if username else "غير محدد"

        # حفظ البيانات مباشرة
        success = self.db.complete_registration(telegram_id, reg_data)

        if success:
            platform = GAMING_PLATFORMS.get(reg_data.get('platform'), {}).get('name', 'غير محدد')
            payment_method = reg_data.get('payment_method', '')
            payment_name = PAYMENT_METHODS.get(payment_method, {}).get('name', 'غير محدد')
            
            # فك تشفير بيانات الدفع إذا كانت موجودة
            payment_details_display = ""
            if 'payment_details' in reg_data:
                try:
                    decrypted_data = encryption_system.decrypt(reg_data['payment_details'])
                    payment_type = reg_data.get('payment_details_type', '')
                    
                    if payment_type == 'wallet':
                        payment_details_display = f"""
💰 **بيانات الدفع:**
• الرقم: `{decrypted_data}`"""
                    elif payment_type == 'card':
                        # عرض رقم الكارت كامل للعميل بدون إخفاء
                        payment_details_display = f"""
💰 **بيانات الدفع:**
• رقم الكارت: `{decrypted_data}`"""
                    elif payment_type == 'link':
                        payment_details_display = f"""
💰 **بيانات الدفع:**
• الرابط: `{decrypted_data}`"""
                except:
                    payment_details_display = ""
            
            # رسالة النجاح مع اسم المستخدم ومعرف التليجرام
            success_message = f"""
✅ **تم حفظ بياناتك بنجاح!**

📊 **ملخص البيانات المحفوظة:**
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {reg_data.get('whatsapp', 'غير محدد')}
💳 طريقة الدفع: {payment_name}{payment_details_display}
━━━━━━━━━━━━━━━━

👤 **اسم المستخدم:** {username_display}
🆔 **معرف التليجرام:** `{telegram_id}`

🎉 مرحباً بك في عائلة FC 26! 🚀
"""

            # استخدام update_current_message إذا كان من callback
            if update.callback_query:
                await smart_message_manager.update_current_message(
                    update, context, success_message
                )
            else:
                await smart_message_manager.send_new_active_message(
                    update, context, success_message
                )
            
            # مسح البيانات المؤقتة
            context.user_data.clear()
            
            # تنظيف بيانات المستخدم في SmartMessageManager
            await smart_message_manager.cleanup_user_data(telegram_id)
            
            return ConversationHandler.END
        else:
            # في حالة الفشل
            error_message = "❌ حدث خطأ في حفظ البيانات. الرجاء المحاولة مرة أخرى."
            
            if update.callback_query:
                await smart_message_manager.update_current_message(
                    update, context, error_message
                )
            else:
                await smart_message_manager.send_new_active_message(
                    update, context, error_message
                )
            
            return ConversationHandler.END



    async def handle_continue_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """استكمال التسجيل"""
        query = update.callback_query
        await query.answer()

        telegram_id = query.from_user.id

        if query.data == "continue_registration":
            temp_data = self.db.get_temp_registration(telegram_id)

            if temp_data:
                context.user_data['registration'] = temp_data['data']
                step = temp_data['step_number']

                step_messages = {
                    ENTERING_WHATSAPP: MESSAGES['enter_whatsapp'],
                    CHOOSING_PAYMENT: MESSAGES['choose_payment']
                }

                message = step_messages.get(step, "")

                # عرض الرسالة المناسبة حسب الخطوة
                if step == CHOOSING_PAYMENT:
                    await smart_message_manager.update_current_message(
                        update, context, message,
                        reply_markup=Keyboards.get_payment_keyboard()
                    )
                elif step == CHOOSING_PLATFORM:
                    await smart_message_manager.update_current_message(
                        update, context, message,
                        reply_markup=Keyboards.get_platform_keyboard()
                    )
                elif step == ENTERING_WHATSAPP:
                    # للواتساب نرسل الرسالة بدون لوحة مفاتيح
                    await smart_message_manager.update_current_message(
                        update, context, message
                    )

                else:
                    await smart_message_manager.update_current_message(
                        update, context, message
                    )

                return step

        elif query.data == "restart_registration":
            self.db.clear_temp_registration(telegram_id)

            await smart_message_manager.update_current_message(
                update, context, MESSAGES['choose_platform'],
                reply_markup=Keyboards.get_platform_keyboard()
            )

            context.user_data['registration'] = {'telegram_id': telegram_id}

            return CHOOSING_PLATFORM



    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء التسجيل"""
        context.user_data.clear()

        await smart_message_manager.send_new_active_message(
            update, context,
            "تم إلغاء عملية التسجيل. يمكنك البدء من جديد بكتابة /start"
        )

        return ConversationHandler.END

# ================================ البوت الرئيسي ================================
class FC26SmartBot:
    """البوت الذكي الكامل"""

    def __init__(self):
        self.db = Database()
        self.registration_handler = SmartRegistrationHandler()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية مع النظام الذكي الموحد"""
        telegram_id = update.effective_user.id
        
        # إذا كان هناك callback_query، نتجاهل الطلب (منع التكرار)
        if update.callback_query:
            return

        user = self.db.get_user_by_telegram_id(telegram_id)

        if user and user.get('registration_status') == 'complete':
            # مستخدم مسجل - عرض القائمة الرئيسية مع النظام الذكي
            welcome_message = f"""
👋 أهلاً بعودتك!

🎮 بوت FC 26 - أفضل مكان لبيع كوينز

كيف يمكنني مساعدتك اليوم؟
"""
            # أزرار تفاعلية
            keyboard = [
                [InlineKeyboardButton("💸 بيع كوينز", callback_data="sell_coins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile")],
                [InlineKeyboardButton("📞 الدعم", callback_data="support")],
                [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # استخدام النظام الذكي دائماً
            await smart_message_manager.send_new_active_message(
                update, context, welcome_message,
                reply_markup=reply_markup,
                disable_previous=True  # تعطيل الرسالة السابقة
            )
        else:
            # مستخدم جديد - استخدام النظام الذكي للتسجيل
            await self.registration_handler.start(update, context)

    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي مع النظام الذكي"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)

        if not profile:
            await smart_message_manager.send_new_active_message(
                update, context,
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return

        # الحصول على معلومات الشبكة إذا كان الرقم موجود
        whatsapp_display = profile.get('whatsapp', 'غير محدد')
        network_display = ""
        
        if whatsapp_display != 'غير محدد' and len(whatsapp_display) >= 3:
            prefix = whatsapp_display[:3]
            if prefix in whatsapp_security.EGYPTIAN_NETWORKS:
                network = whatsapp_security.EGYPTIAN_NETWORKS[prefix]
                network_display = f" ({network['emoji']} {network['name']})"
        
        profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {whatsapp_display}{network_display}
💳 طريقة الدفع: {profile.get('payment_method', 'غير محدد')}

━━━━━━━━━━━━━━━━
🔐 بياناتك محمية
"""

        # أزرار العودة
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await smart_message_manager.send_new_active_message(
            update, context, profile_text,
            reply_markup=reply_markup
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المساعدة"""
        help_text = """
🆘 **المساعدة والأوامر**
━━━━━━━━━━━━━━━━

📢 الأوامر المتاحة:

/start - البداية والقائمة الرئيسية
/profile - عرض ملفك الشخصي
/delete - حذف حسابك
/help - هذه الرسالة

🔗 للدعم والمساعدة:
@FC26Support
"""
        # أزرار مفيدة
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
            [InlineKeyboardButton("👤 ملفي الشخصي", callback_data="profile")],
            [InlineKeyboardButton("📞 الدعم الفني", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await smart_message_manager.send_new_active_message(
            update, context, help_text,
            reply_markup=reply_markup
        )

    async def delete_account_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حذف الحساب مع النظام الذكي"""
        warning = """
⚠️ **تحذير مهم!**
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك؟

سيتم حذف:
• جميع بياناتك 🗑️

لا يمكن التراجع! ⛔
"""
        await smart_message_manager.send_new_active_message(
            update, context, warning,
            reply_markup=Keyboards.get_delete_keyboard()
        )

    async def handle_delete_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد حذف الحساب مع النظام الذكي"""
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_delete":
            telegram_id = query.from_user.id

            success = self.db.delete_user_account(telegram_id)

            if success:
                await smart_message_manager.update_current_message(
                    update, context,
                    "✅ تم حذف حسابك بنجاح.\n\nيمكنك التسجيل مرة أخرى بكتابة /start"
                )
            else:
                await smart_message_manager.update_current_message(
                    update, context,
                    "❌ حدث خطأ. حاول لاحقاً."
                )

        elif query.data == "cancel_delete":
            # العودة للقائمة الرئيسية
            welcome_message = f"""
✅ تم الإلغاء. سعداء لبقائك معنا! 😊

🎮 بوت FC 26 - أفضل مكان  لبيع كوينز

كيف يمكنني مساعدتك اليوم؟
"""

            keyboard = [
                [InlineKeyboardButton("💸 بيع كوينز", callback_data="sell_coins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile")],
                [InlineKeyboardButton("📞 الدعم", callback_data="support")],
                [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await smart_message_manager.update_current_message(
                update, context, welcome_message,
                reply_markup=reply_markup
            )

    async def handle_menu_buttons(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أزرار القائمة التفاعلية مع النظام الذكي"""
        query = update.callback_query
        await query.answer()

        if query.data == "profile":
            # استخدام النظام الذكي لعرض الملف الشخصي
            telegram_id = query.from_user.id
            profile = self.db.get_user_profile(telegram_id)

            if not profile:
                await smart_message_manager.update_current_message(
                    update, context,
                    "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
                )
                return

            # الحصول على معلومات الشبكة إذا كان الرقم موجود
            whatsapp_display = profile.get('whatsapp', 'غير محدد')
            network_display = ""
            
            if whatsapp_display != 'غير محدد' and len(whatsapp_display) >= 3:
                prefix = whatsapp_display[:3]
                if prefix in whatsapp_security.EGYPTIAN_NETWORKS:
                    network = whatsapp_security.EGYPTIAN_NETWORKS[prefix]
                    network_display = f" ({network['emoji']} {network['name']})"
            
            profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {whatsapp_display}{network_display}
💳 طريقة الدفع: {profile.get('payment_method', 'غير محدد')}

━━━━━━━━━━━━━━━━
🔐 بياناتك محمية
"""

            # أزرار العودة
            keyboard = [
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await smart_message_manager.update_current_message(
                update, context, profile_text,
                reply_markup=reply_markup
            )

        elif query.data == "delete_account":
            warning = """
⚠️ **تحذير مهم!**
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك؟

سيتم حذف:
• جميع بياناتك 🗑️

لا يمكن التراجع! ⛔
"""

            await smart_message_manager.update_current_message(
                update, context, warning,
                reply_markup=Keyboards.get_delete_keyboard()
            )

        elif query.data == "sell_coins":
            await smart_message_manager.update_current_message(
                update, context, "🚧 قريباً... خدمة بيع كوينز",
                choice_made="بيع كوينز"
            )

        elif query.data == "support":
            await smart_message_manager.update_current_message(
                update, context, "📞 للدعم: @FC26Support",
                choice_made="الدعم الفني"
            )

        elif query.data == "main_menu":
            # العودة للقائمة الرئيسية باستخدام النظام الذكي
            welcome_message = f"""
👋 أهلاً بعودتك!

🎮 بوت FC 26 - أفضل مكان  لبيع كوينز

كيف يمكنني مساعدتك اليوم؟
"""

            keyboard = [
                [InlineKeyboardButton("💸 بيع كوينز", callback_data="sell_coins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile")],
                [InlineKeyboardButton("📞 الدعم", callback_data="support")],
                [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await smart_message_manager.update_current_message(
                update, context, welcome_message,
                reply_markup=reply_markup
            )

    async def handle_text_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل النصية - نعيد توجيههم للأوامر"""
        # إزالة أي كيبورد موجود
        await update.message.reply_text(
            "👋 استخدم الأوامر التالية:\n\n"
            "/start - البداية\n"
            "/profile - الملف الشخصي\n"
            "/help - المساعدة",
            reply_markup=ReplyKeyboardRemove()
        )

    def get_registration_conversation(self):
        """معالج المحادثة للتسجيل"""
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    self.registration_handler.handle_registration_start,
                    pattern="^register_new$"
                ),
                CallbackQueryHandler(
                    self.registration_handler.handle_continue_registration,
                    pattern="^(continue_registration|restart_registration)$"
                )
            ],
            states={
                CHOOSING_PLATFORM: [
                    CallbackQueryHandler(
                        self.registration_handler.handle_platform_choice,
                        pattern="^platform_"
                    )
                ],
                ENTERING_WHATSAPP: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registration_handler.handle_whatsapp_input
                    )
                ],
                CHOOSING_PAYMENT: [
                    CallbackQueryHandler(
                        self.registration_handler.handle_payment_choice,
                        pattern="^payment_"
                    )
                ],
                ENTERING_PAYMENT_DETAILS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registration_handler.handle_payment_details_input
                    )
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.registration_handler.cancel),
                CommandHandler('start', self.registration_handler.start)
            ],
            allow_reentry=True
        )

    def run(self):
        """تشغيل البوت"""
        app = Application.builder().token(BOT_TOKEN).build()

        # معالج التسجيل (يجب أن يكون أولاً ليأخذ الأولوية)
        app.add_handler(self.get_registration_conversation())

        # الأوامر
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("profile", self.profile_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("delete", self.delete_account_command))

        # الأزرار
        app.add_handler(CallbackQueryHandler(
            self.handle_delete_confirmation,
            pattern="^(confirm_delete|cancel_delete)$"
        ))

        # أزرار القائمة الرئيسية (محدثة بدون الأزرار المحذوفة)
        app.add_handler(CallbackQueryHandler(
            self.handle_menu_buttons,
            pattern="^(profile|delete_account|sell_coins|support|main_menu)$"
        ))

        # الرسائل النصية (يجب أن يكون آخراً)
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_messages
        ))

        # التشغيل
        logger.info("🚀 بدء تشغيل FC 26 Smart Bot...")
        logger.info("✨ النظام الذكي للرسائل مفعّل")
        logger.info("📱 البوت جاهز: https://t.me/FC26_Trading_Bot")

        app.run_polling(allowed_updates=Update.ALL_TYPES)

# ================================ نقطة البداية ================================
if __name__ == "__main__":
    bot = FC26SmartBot()
    bot.run()
