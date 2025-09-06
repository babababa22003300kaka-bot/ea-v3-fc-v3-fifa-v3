#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 FC 26 Trading Bot - النسخة الكاملة المتكاملة
البوت الكامل في ملف واحد مع نظام الرسائل الذكي
"""

import os
import logging
import sqlite3
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
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
    ENTERING_PHONE,
    ENTERING_PAYMENT_INFO,
    ENTERING_EMAILS,
    CONFIRMING_DATA
) = range(7)

# ================================ البيانات الثابتة ================================
GAMING_PLATFORMS = {
    'playstation': {'name': 'PlayStation 🎮', 'emoji': '🎮'},
    'xbox': {'name': 'Xbox 🎯', 'emoji': '🎯'},
    'pc': {'name': 'PC 💻', 'emoji': '💻'}
}

PAYMENT_METHODS = {
    'vodafone': {'name': 'فودافون كاش 📱', 'emoji': '📱'},
    'instapay': {'name': 'InstaPay 🏦', 'emoji': '🏦'},
    'visa': {'name': 'فيزا 💳', 'emoji': '💳'},
    'paypal': {'name': 'PayPal 💰', 'emoji': '💰'},
    'etisalat': {'name': 'اتصالات كاش 📲', 'emoji': '📲'},
    'orange': {'name': 'أورانج كاش 📳', 'emoji': '📳'},
    'other': {'name': 'طريقة أخرى 💸', 'emoji': '💸'}
}

MESSAGES = {
    'welcome': """🌟 أهلاً وسهلاً في بوت FC 26! 🎮

البوت الأول في مصر لتداول عملات FC 26 🇪🇬

✨ مميزاتنا:
• أسعار منافسة جداً 💰
• معاملات آمنة 100% 🔒
• دعم فني 24/7 📞
• سرعة في التنفيذ ⚡

اضغط على "تسجيل جديد" للبدء! 👇""",
    
    'choose_platform': """🎮 رائع! هيا نبدأ رحلتك!

الخطوة 1️⃣ من 6️⃣
اختر منصة اللعب المفضلة لديك:""",
    
    'enter_whatsapp': """📱 ممتاز! اختيار موفق!

الخطوة 2️⃣ من 6️⃣
الآن أرسل رقم الواتساب الخاص بك:

مثال: 01012345678
(يجب أن يبدأ بـ 010, 011, 012, أو 015)""",
    
    'choose_payment': """💳 تمام! الرقم صحيح ✅

الخطوة 3️⃣ من 6️⃣
اختر طريقة الدفع المفضلة:""",
    
    'enter_phone': """📞 رائع! طريقة دفع ممتازة!

الخطوة 4️⃣ من 6️⃣
أرسل رقم الهاتف (للتواصل):

مثال: 01234567890
(11 رقم يبدأ بـ 010/011/012/015)""",
    
    'enter_instapay': """🏦 تمام! البيانات آمنة معنا 🔐

الخطوة 5️⃣ من 6️⃣
أرسل رابط InstaPay الخاص بك (اختياري):

يمكنك:
• نسخ الرسالة كاملة من InstaPay
• أو كتابة "تخطي" للمتابعة""",
    
    'enter_payment_info': """💳 تمام! البيانات آمنة معنا 🔐

الخطوة 5️⃣ من 6️⃣
أرسل معلومات الدفع الخاصة بك (اختياري):

يمكنك كتابة "تخطي" للمتابعة""",
    
    'enter_emails': """📧 رائع! نحن في الخطوة الأخيرة!

الخطوة 6️⃣ من 6️⃣
أرسل بريدك الإلكتروني (اختياري):

يمكنك:
• إضافة عدة إيميلات (واحد في كل رسالة)
• أو كتابة "انتهى" لإكمال التسجيل""",
    
    'registration_complete': """🎉 مبروك! تم إنشاء حسابك بنجاح! 🎊

✅ ملخص بياناتك:
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {whatsapp}
💳 طريقة الدفع: {payment}
📞 الهاتف: {phone}
📧 الإيميل: {emails}
━━━━━━━━━━━━━━━━

🎁 هدية الترحيب:
• 100 نقطة ولاء 🏆
• خصم 10% على أول عملية 💸

مرحباً بك في عائلة FC 26! 🚀""",
    
    'welcome_back': """👋 أهلاً بعودتك!

كنا واقفين عند: {last_step}

هل تريد المتابعة من حيث توقفت؟""",
    
    'error_invalid_phone': """❌ رقم الهاتف غير صحيح!

يجب أن يكون:
• 11 رقم
• يبدأ بـ 010, 011, 012, أو 015

مثال: 01012345678

حاول مرة أخرى 👇""",
    
    'error_invalid_email': """❌ البريد الإلكتروني غير صحيح!

تأكد من كتابته بشكل صحيح:
مثال: example@gmail.com

حاول مرة أخرى 👇""",
    
    'data_saved': """💾 تم حفظ البيانات تلقائياً ✅

يمكنك العودة في أي وقت وسنكمل من نفس النقطة!"""
}

# ================================ نظام إدارة الرسائل الذكي ================================
class SmartMessageManager:
    """مدير الرسائل الذكي - رسالة واحدة نشطة فقط"""
    
    def __init__(self):
        self.user_active_messages: Dict[int, Dict[str, Any]] = {}
    
    async def disable_old_message(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, choice_made: str = None):
        """إلغاء تفعيل الرسالة القديمة وتحويلها لسجل تاريخي"""
        if user_id not in self.user_active_messages:
            return
        
        try:
            old_message_info = self.user_active_messages[user_id]
            
            if old_message_info.get('message_id') and old_message_info.get('chat_id'):
                old_text = old_message_info.get('text', '')
                
                if choice_made:
                    updated_text = f"{old_text}\n\n✅ **تم الاختيار:** {choice_made}"
                else:
                    updated_text = f"{old_text}\n\n✅ **تم**"
                
                try:
                    await context.bot.edit_message_text(
                        chat_id=old_message_info['chat_id'],
                        message_id=old_message_info['message_id'],
                        text=updated_text,
                        parse_mode='Markdown'
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
        """إرسال رسالة جديدة نشطة"""
        user_id = update.effective_user.id
        
        if disable_previous:
            await self.disable_old_message(user_id, context, choice_made)
        
        try:
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
            
            if reply_markup:
                self.user_active_messages[user_id] = {
                    'message_id': sent_message.message_id,
                    'chat_id': sent_message.chat_id,
                    'text': text
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
        """تحديث الرسالة الحالية"""
        if not update.callback_query:
            return await self.send_new_active_message(update, context, text, reply_markup)
        
        try:
            user_id = update.effective_user.id
            
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            if reply_markup:
                self.user_active_messages[user_id] = {
                    'message_id': update.callback_query.message.message_id,
                    'chat_id': update.callback_query.message.chat_id,
                    'text': text
                }
            else:
                if user_id in self.user_active_messages:
                    del self.user_active_messages[user_id]
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الرسالة: {e}")

# إنشاء المدير الذكي
smart_message_manager = SmartMessageManager()

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
                phone TEXT,
                payment_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الإيميلات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email TEXT,
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
            
            # تحديث بيانات التسجيل
            cursor.execute('''
                UPDATE registration_data 
                SET platform = ?, whatsapp = ?, payment_method = ?, phone = ?, payment_info = ?
                WHERE user_id = ?
            ''', (
                data.get('platform'),
                data.get('whatsapp'),
                data.get('payment_method'),
                data.get('phone'),
                data.get('payment_info'),
                user_id
            ))
            
            # حفظ الإيميلات
            emails = data.get('emails', [])
            cursor.execute('DELETE FROM email_data WHERE user_id = ?', (user_id,))
            for email in emails:
                cursor.execute('INSERT INTO email_data (user_id, email) VALUES (?, ?)', (user_id, email))
            
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
            cursor.execute('DELETE FROM email_data WHERE user_id = ?', (user_id,))
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

# ================================ المدققات ================================
class Validators:
    """مدققات البيانات"""
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """التحقق من رقم الهاتف"""
        phone = re.sub(r'[^\d]', '', phone)
        
        if len(phone) == 11 and phone[:3] in ['010', '011', '012', '015']:
            return True, phone
        return False, "رقم غير صحيح"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """التحقق من البريد الإلكتروني"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return True, email.lower()
        return False, "بريد غير صحيح"
    
    @staticmethod
    def extract_instapay_link(text: str) -> Optional[str]:
        """استخراج رابط InstaPay"""
        pattern = r'(https?://[^\s]+instapay[^\s]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # إذا لم نجد رابط، نرجع النص كما هو إذا كان قصيراً
        if len(text) < 100:
            return text
        return None

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
    def get_skip_keyboard():
        """لوحة التخطي"""
        keyboard = [[InlineKeyboardButton("⏭️ تخطي", callback_data="skip_step")]]
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
    def get_confirm_keyboard():
        """لوحة التأكيد"""
        keyboard = [
            [InlineKeyboardButton("✅ تأكيد وإنهاء", callback_data="confirm_registration")],
            [InlineKeyboardButton("✏️ تعديل", callback_data="edit_registration")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_emails_keyboard():
        """لوحة الإيميلات"""
        keyboard = [
            [InlineKeyboardButton("➕ إضافة إيميل آخر", callback_data="add_email")],
            [InlineKeyboardButton("✅ انتهى", callback_data="finish_emails")]
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
                CHOOSING_PAYMENT: "اختيار طريقة الدفع",
                ENTERING_PHONE: "إدخال رقم الهاتف",
                ENTERING_PAYMENT_INFO: "معلومات الدفع",
                ENTERING_EMAILS: "البريد الإلكتروني"
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
        """بدء التسجيل الجديد"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        username = query.from_user.username
        full_name = query.from_user.full_name
        
        # مسح أي بيانات تسجيل قديمة
        self.db.clear_temp_registration(telegram_id)
        
        user_id = self.db.create_user(telegram_id, username, full_name)
        
        context.user_data['registration'] = {
            'user_id': user_id,
            'telegram_id': telegram_id
        }
        
        await smart_message_manager.update_current_message(
            update, context, MESSAGES['choose_platform'],
            reply_markup=Keyboards.get_platform_keyboard()
        )
        
        return CHOOSING_PLATFORM
    
    async def handle_platform_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار المنصة"""
        query = update.callback_query
        await query.answer()
        
        platform_key = query.data.replace("platform_", "")
        platform_name = GAMING_PLATFORMS[platform_key]['name']
        
        context.user_data['registration']['platform'] = platform_key
        
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'platform_chosen', ENTERING_WHATSAPP,
            context.user_data['registration']
        )
        
        await smart_message_manager.send_new_active_message(
            update, context,
            f"✅ تم اختيار: {platform_name}\n\n" + MESSAGES['enter_whatsapp'],
            choice_made=platform_name
        )
        
        return ENTERING_WHATSAPP
    
    async def handle_whatsapp_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال واتساب"""
        whatsapp = update.message.text.strip()
        
        # تنظيف الرقم من أي رموز
        cleaned_phone = re.sub(r'[^\d]', '', whatsapp)
        
        # التحقق من صحة الرقم
        if len(cleaned_phone) == 11 and cleaned_phone[:3] in ['010', '011', '012', '015']:
            is_valid = True
            result = cleaned_phone
        else:
            is_valid = False
            result = "رقم غير صحيح"
        
        if not is_valid:
            await smart_message_manager.send_new_active_message(
                update, context, 
                f"❌ {result}\n\n" + MESSAGES['error_invalid_phone'],
                disable_previous=False
            )
            return ENTERING_WHATSAPP
        
        # التأكد من وجود registration في context
        if 'registration' not in context.user_data:
            context.user_data['registration'] = {
                'telegram_id': update.effective_user.id
            }
        
        # حفظ الرقم في السياق
        context.user_data['registration']['whatsapp'] = result
        
        # حفظ في قاعدة البيانات المؤقتة مع معالجة الأخطاء
        try:
            self.db.save_temp_registration(
                context.user_data['registration']['telegram_id'],
                'whatsapp_entered', 
                CHOOSING_PAYMENT,
                context.user_data['registration']
            )
        except Exception as e:
            logger.error(f"Error saving temp registration: {e}")
        
        # إرسال رسالة التأكيد مع لوحة المفاتيح للخطوة التالية
        await smart_message_manager.send_new_active_message(
            update, context,
            f"✅ تم حفظ الواتساب: {result}\n" + MESSAGES['data_saved'] +
            "\n\n" + MESSAGES['choose_payment'],
            reply_markup=Keyboards.get_payment_keyboard(),
            choice_made=f"واتساب: {result}"
        )
        
        return CHOOSING_PAYMENT
    
    async def handle_payment_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار طريقة الدفع"""
        query = update.callback_query
        await query.answer()
        
        payment_key = query.data.replace("payment_", "")
        payment_name = PAYMENT_METHODS[payment_key]['name']
        
        context.user_data['registration']['payment_method'] = payment_key
        
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'payment_chosen', ENTERING_PHONE,
            context.user_data['registration']
        )
        
        await smart_message_manager.send_new_active_message(
            update, context,
            f"✅ تم اختيار: {payment_name}\n\n" + MESSAGES['enter_phone'],
            choice_made=payment_name
        )
        
        return ENTERING_PHONE
    
    async def handle_phone_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال رقم الهاتف"""
        phone = update.message.text.strip()
        
        is_valid, result = Validators.validate_phone(phone)
        
        if not is_valid:
            await smart_message_manager.send_new_active_message(
                update, context,
                f"❌ {result}\n\n" + MESSAGES['error_invalid_phone'],
                disable_previous=False
            )
            return ENTERING_PHONE
        
        context.user_data['registration']['phone'] = result
        
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'phone_entered', ENTERING_PAYMENT_INFO,
            context.user_data['registration']
        )
        
        payment_method = context.user_data['registration'].get('payment_method')
        
        if payment_method == 'instapay':
            message = f"✅ تم حفظ الهاتف: {result}\n{MESSAGES['data_saved']}\n\n{MESSAGES['enter_instapay']}"
        else:
            message = f"✅ تم حفظ الهاتف: {result}\n{MESSAGES['data_saved']}\n\n{MESSAGES['enter_payment_info']}"
        
        await smart_message_manager.send_new_active_message(
            update, context, message,
            reply_markup=Keyboards.get_skip_keyboard(),
            choice_made=f"هاتف: {result}"
        )
        
        return ENTERING_PAYMENT_INFO
    
    async def handle_payment_info_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معلومات الدفع"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "skip_step":
                context.user_data['registration']['payment_info'] = None
                
                await smart_message_manager.send_new_active_message(
                    update, context,
                    "⏭️ تم تخطي معلومات الدفع\n\n" + MESSAGES['enter_emails'],
                    reply_markup=Keyboards.get_skip_keyboard(),
                    choice_made="تخطي معلومات الدفع"
                )
                return ENTERING_EMAILS
        
        payment_input = update.message.text.strip()
        
        if payment_input.lower() in ["تخطي", "skip"]:
            context.user_data['registration']['payment_info'] = None
            
            await smart_message_manager.send_new_active_message(
                update, context,
                "⏭️ تم التخطي\n\n" + MESSAGES['enter_emails'],
                reply_markup=Keyboards.get_skip_keyboard(),
                choice_made="تخطي"
            )
            return ENTERING_EMAILS
        
        payment_method = context.user_data['registration'].get('payment_method')
        
        if payment_method == 'instapay':
            extracted = Validators.extract_instapay_link(payment_input)
            context.user_data['registration']['payment_info'] = extracted or payment_input
            display_text = f"رابط InstaPay: {(extracted or payment_input)[:30]}..."
        else:
            context.user_data['registration']['payment_info'] = payment_input
            display_text = f"معلومات الدفع: {payment_input[:20]}..."
        
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'payment_info_entered', ENTERING_EMAILS,
            context.user_data['registration']
        )
        
        await smart_message_manager.send_new_active_message(
            update, context,
            "✅ تم الحفظ\n" + MESSAGES['data_saved'] + "\n\n" + MESSAGES['enter_emails'],
            reply_markup=Keyboards.get_skip_keyboard(),
            choice_made=display_text
        )
        
        return ENTERING_EMAILS
    
    async def handle_email_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال البريد الإلكتروني"""
        if 'emails' not in context.user_data['registration']:
            context.user_data['registration']['emails'] = []
        
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data in ["skip_step", "finish_emails"]:
                return await self.show_confirmation(update, context)
            
            elif query.data == "add_email":
                await smart_message_manager.update_current_message(
                    update, context, "📧 أرسل البريد الإلكتروني الإضافي:"
                )
                return ENTERING_EMAILS
        
        email_input = update.message.text.strip()
        
        if email_input.lower() in ["انتهى", "تخطي", "finish", "skip"]:
            return await self.show_confirmation(update, context)
        
        is_valid, result = Validators.validate_email(email_input)
        
        if not is_valid:
            await smart_message_manager.send_new_active_message(
                update, context, MESSAGES['error_invalid_email'],
                disable_previous=False
            )
            return ENTERING_EMAILS
        
        context.user_data['registration']['emails'].append(result)
        
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'emails_entered', ENTERING_EMAILS,
            context.user_data['registration']
        )
        
        emails_list = '\n'.join([f"• {e}" for e in context.user_data['registration']['emails']])
        
        await smart_message_manager.send_new_active_message(
            update, context,
            f"✅ تم إضافة: {result}\n\n📧 الإيميلات المسجلة:\n{emails_list}",
            reply_markup=Keyboards.get_emails_keyboard(),
            choice_made=f"إيميل: {result}"
        )
        
        return ENTERING_EMAILS
    
    async def show_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض التأكيد"""
        reg_data = context.user_data['registration']
        
        platform = GAMING_PLATFORMS.get(reg_data.get('platform'), {}).get('name', 'غير محدد')
        payment = PAYMENT_METHODS.get(reg_data.get('payment_method'), {}).get('name', 'غير محدد')
        emails = ', '.join(reg_data.get('emails', [])) or 'لا يوجد'
        
        summary = f"""
📊 **ملخص بياناتك:**
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {reg_data.get('whatsapp', 'غير محدد')}
💳 طريقة الدفع: {payment}
📞 الهاتف: {reg_data.get('phone', 'غير محدد')}"""
        
        if reg_data.get('payment_info'):
            if reg_data.get('payment_method') == 'instapay':
                summary += f"\n🏦 InstaPay: {reg_data['payment_info'][:30]}..."
            else:
                summary += f"\n💳 معلومات الدفع: {reg_data['payment_info'][:20]}..."
        
        summary += f"""
📧 الإيميلات: {emails}
━━━━━━━━━━━━━━━━
        """
        
        self.db.save_temp_registration(
            reg_data['telegram_id'], 'confirming',
            CONFIRMING_DATA, reg_data
        )
        
        await smart_message_manager.send_new_active_message(
            update, context, summary,
            reply_markup=Keyboards.get_confirm_keyboard(),
            choice_made="عرض الملخص"
        )
        
        return CONFIRMING_DATA
    
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد التسجيل"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_registration":
            reg_data = context.user_data['registration']
            
            success = self.db.complete_registration(reg_data['telegram_id'], reg_data)
            
            if success:
                completion_message = MESSAGES['registration_complete'].format(
                    platform=GAMING_PLATFORMS[reg_data['platform']]['name'],
                    whatsapp=reg_data['whatsapp'],
                    payment=PAYMENT_METHODS[reg_data['payment_method']]['name'],
                    phone=reg_data['phone'],
                    emails=', '.join(reg_data.get('emails', [])) or 'لا يوجد'
                )
                
                await smart_message_manager.update_current_message(
                    update, context, completion_message
                )
                
                await query.message.reply_text(
                    "يمكنك الآن استخدام جميع خدمات البوت! 🚀\n\n"
                    "استخدم الأوامر:\n"
                    "/profile - الملف الشخصي\n"
                    "/help - المساعدة"
                )
                
                context.user_data.clear()
                
                return ConversationHandler.END
            else:
                await smart_message_manager.update_current_message(
                    update, context,
                    "❌ حدث خطأ في حفظ البيانات. الرجاء المحاولة مرة أخرى."
                )
                return CONFIRMING_DATA
        
        elif query.data == "edit_registration":
            await smart_message_manager.update_current_message(
                update, context, "📝 سنبدأ من جديد...",
                reply_markup=Keyboards.get_platform_keyboard()
            )
            return CHOOSING_PLATFORM
    
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
                    CHOOSING_PAYMENT: MESSAGES['choose_payment'],
                    ENTERING_PHONE: MESSAGES['enter_phone'],
                    ENTERING_PAYMENT_INFO: self._get_payment_message(temp_data['data']),
                    ENTERING_EMAILS: MESSAGES['enter_emails']
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
                elif step in [ENTERING_PAYMENT_INFO, ENTERING_EMAILS]:
                    await smart_message_manager.update_current_message(
                        update, context, message,
                        reply_markup=Keyboards.get_skip_keyboard()
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
    
    def _get_payment_message(self, data):
        """رسالة معلومات الدفع"""
        if data.get('payment_method') == 'instapay':
            return MESSAGES['enter_instapay']
        else:
            return MESSAGES['enter_payment_info']
    
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
        
        user = self.db.get_user_by_telegram_id(telegram_id)
        
        if user and user.get('registration_status') == 'complete':
            # مستخدم مسجل - عرض القائمة الرئيسية مع النظام الذكي
            profile = self.db.get_user_profile(telegram_id)
            
            welcome_message = f"""
👋 أهلاً بعودتك!

🎮 بوت FC 26 - أفضل مكان لتداول العملات

كيف يمكنني مساعدتك اليوم؟
"""
            # أزرار تفاعلية
            keyboard = [
                [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile")],
                [InlineKeyboardButton("📞 الدعم", callback_data="support")],
                [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # استخدام النظام الذكي دائماً
            await smart_message_manager.send_new_active_message(
                update, context, welcome_message,
                reply_markup=reply_markup
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
        
        profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {profile.get('whatsapp', 'غير محدد')}
💳 طريقة الدفع: {profile.get('payment_method', 'غير محدد')}
📞 الهاتف: {profile.get('phone', 'غير محدد')}

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

🎮 بوت FC 26 - أفضل مكان لتداول العملات

كيف يمكنني مساعدتك اليوم؟
"""
            
            keyboard = [
                [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
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
            
            profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {profile.get('whatsapp', 'غير محدد')}
💳 طريقة الدفع: {profile.get('payment_method', 'غير محدد')}
📞 الهاتف: {profile.get('phone', 'غير محدد')}

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
                update, context, "🚧 قريباً... خدمة بيع العملات",
                choice_made="بيع العملات"
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

🎮 بوت FC 26 - أفضل مكان لتداول العملات

كيف يمكنني مساعدتك اليوم؟
"""
            
            keyboard = [
                [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
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
                ENTERING_PHONE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registration_handler.handle_phone_input
                    )
                ],
                ENTERING_PAYMENT_INFO: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registration_handler.handle_payment_info_input
                    ),
                    CallbackQueryHandler(
                        self.registration_handler.handle_payment_info_input,
                        pattern="^skip_step$"
                    )
                ],
                ENTERING_EMAILS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registration_handler.handle_email_input
                    ),
                    CallbackQueryHandler(
                        self.registration_handler.handle_email_input,
                        pattern="^(skip_step|add_email|finish_emails)$"
                    )
                ],
                CONFIRMING_DATA: [
                    CallbackQueryHandler(
                        self.registration_handler.handle_confirmation,
                        pattern="^(confirm_registration|edit_registration)$"
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
