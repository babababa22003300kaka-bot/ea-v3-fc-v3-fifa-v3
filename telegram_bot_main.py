#!/usr/bin/env python3
"""
🤖 بوت FC 26 التليجرام - النسخة المدمجة
تاريخ الإنشاء: 3 سبتمبر 2025
"""

import os
import sys
import logging
import sqlite3
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# حالات المحادثة
(PLATFORM, WHATSAPP, PAYMENT_METHOD, PHONE, 
 CARD_NUMBER, INSTAPAY_LINK, EMAILS, CONFIRM_DATA) = range(8)

class FC26Bot:
    """البوت الرئيسي المتكامل"""
    
    def __init__(self):
        """تهيئة البوت"""
        # التوكن من متغير البيئة أو افتراضي للتجربة
        self.token = os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE')
        self.admin_id = 1124247595
        self.init_database()
        
        # الإعدادات
        self.platforms = {
            'playstation': {'name': 'PlayStation', 'emoji': '🎮'},
            'xbox': {'name': 'Xbox', 'emoji': '🎯'},
            'pc': {'name': 'PC', 'emoji': '💻'}
        }
        
        self.payment_methods = {
            'vodafone_cash': 'فودافون كاش',
            'orange_cash': 'أورانج كاش',
            'etisalat_cash': 'اتصالات كاش',
            'we_cash': 'WE كاش',
            'instapay': 'انستا باي',
            'card': 'بطاقة بنكية'
        }
        
        logger.info("✅ تم تهيئة البوت بنجاح")
    
    def init_database(self):
        """إنشاء قاعدة البيانات"""
        conn = sqlite3.connect('fc26_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                first_name TEXT,
                platform TEXT,
                whatsapp TEXT,
                payment_method TEXT,
                phone TEXT,
                card_number_encrypted TEXT,
                instapay_link TEXT,
                emails TEXT,
                created_at TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ قاعدة البيانات جاهزة")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج البداية"""
        user = update.effective_user
        
        # التحقق من وجود المستخدم
        conn = sqlite3.connect('fc26_bot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user.id,))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            text = f"""
🎮 **أهلاً بعودتك {user.first_name}!**

حسابك مسجل بالفعل ✅

/profile - عرض حسابك
/prices - عرض الأسعار
/support - الدعم الفني
"""
        else:
            text = f"""
🎮 **أهلاً بك في بوت FC 26!**

مرحباً {user.first_name}! 👋

لنبدأ بتسجيل حسابك الآن
"""
            keyboard = [[InlineKeyboardButton("📝 تسجيل جديد", callback_data="register_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
            return
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء التسجيل"""
        query = update.callback_query
        await query.answer()
        
        text = """
🎮 **تسجيل حساب جديد**

**الخطوة 1 من 7:** اختر منصة اللعب
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎮 PlayStation", callback_data="plat_playstation"),
                InlineKeyboardButton("🎯 Xbox", callback_data="plat_xbox"),
                InlineKeyboardButton("💻 PC", callback_data="plat_pc")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
        return PLATFORM
    
    async def platform_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار المنصة"""
        query = update.callback_query
        await query.answer()
        
        platform = query.data.replace("plat_", "")
        context.user_data['platform'] = platform
        
        text = f"""
✅ تم اختيار: **{self.platforms[platform]['emoji']} {self.platforms[platform]['name']}**

**الخطوة 2 من 7:** أرسل رقم الواتساب
مثال: +201234567890
"""
        
        await query.edit_message_text(text, parse_mode='Markdown')
        return WHATSAPP
    
    async def whatsapp_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال الواتساب"""
        whatsapp = update.message.text.strip()
        
        # تنظيف الرقم
        cleaned = re.sub(r'[\s\-\(\)\+]', '', whatsapp)
        if cleaned.startswith('0'):
            cleaned = '+2' + cleaned
        elif not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        
        context.user_data['whatsapp'] = cleaned
        
        text = f"""
✅ تم حفظ الواتساب: **{cleaned}**

**الخطوة 3 من 7:** اختر طريقة الدفع
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📱 فودافون كاش", callback_data="pay_vodafone_cash"),
                InlineKeyboardButton("🟠 أورانج كاش", callback_data="pay_orange_cash")
            ],
            [
                InlineKeyboardButton("🏦 انستا باي", callback_data="pay_instapay"),
                InlineKeyboardButton("💳 بطاقة", callback_data="pay_card")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
        return PAYMENT_METHOD
    
    async def payment_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار الدفع"""
        query = update.callback_query
        await query.answer()
        
        payment = query.data.replace("pay_", "")
        context.user_data['payment_method'] = payment
        
        text = f"""
✅ تم اختيار: **{self.payment_methods[payment]}**

**الخطوة 4 من 7:** أرسل رقم الهاتف المصري
مثال: 01012345678
"""
        
        await query.edit_message_text(text, parse_mode='Markdown')
        return PHONE
    
    async def phone_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال الهاتف"""
        phone = update.message.text.strip()
        context.user_data['phone'] = phone
        
        text = """
✅ تم حفظ رقم الهاتف

**الخطوة 5 من 7:** أرسل رقم البطاقة القومية (16 رقم)
سيتم تشفيرها للحماية 🔒
"""
        
        await update.message.reply_text(text, parse_mode='Markdown')
        return CARD_NUMBER
    
    async def card_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال البطاقة"""
        card = update.message.text.strip()
        card_clean = ''.join(filter(str.isdigit, card))
        
        # تشفير البطاقة
        encrypted = hashlib.sha256(card_clean.encode()).hexdigest()
        context.user_data['card_encrypted'] = encrypted
        context.user_data['card_masked'] = f"****-****-****-{card_clean[-4:]}"
        
        # حذف الرسالة للأمان
        await update.message.delete()
        
        text = """
✅ تم حفظ البطاقة بأمان 🔒

**الخطوة 6 من 7:** رابط انستا باي (اختياري)
أرسل الرابط أو "تخطي"
"""
        
        keyboard = [[InlineKeyboardButton("⏭️ تخطي", callback_data="skip_instapay")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        return INSTAPAY_LINK
    
    async def instapay_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال انستا باي"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            context.user_data['instapay'] = None
            message = query.message
        else:
            text = update.message.text.strip()
            if text.lower() in ["تخطي", "skip"]:
                context.user_data['instapay'] = None
            else:
                context.user_data['instapay'] = text
            message = update.message
        
        text = """
**الخطوة 7 من 7:** البريد الإلكتروني (اختياري)
أرسل الإيميل أو "تخطي"
"""
        
        keyboard = [[InlineKeyboardButton("⏭️ تخطي وإنهاء", callback_data="skip_email")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        
        return EMAILS
    
    async def email_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال الإيميل والتأكيد"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            context.user_data['emails'] = []
            message = query.message
        else:
            text = update.message.text.strip()
            if text.lower() in ["تخطي", "skip"]:
                context.user_data['emails'] = []
            else:
                context.user_data['emails'] = [text]
            message = update.message
        
        # عرض الملخص
        data = context.user_data
        summary = f"""
✅ **تم جمع البيانات!**

🎮 **المنصة:** {self.platforms[data['platform']]['name']}
📱 **واتساب:** {data['whatsapp']}
💳 **الدفع:** {self.payment_methods[data['payment_method']]}
📞 **الهاتف:** {data['phone']}
💳 **البطاقة:** {data['card_masked']}
🔗 **انستا باي:** {data.get('instapay', 'لا يوجد')}
📧 **الإيميل:** {', '.join(data.get('emails', [])) if data.get('emails') else 'لا يوجد'}

تأكيد الحفظ؟
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد وحفظ", callback_data="confirm_save"),
                InlineKeyboardButton("❌ إلغاء", callback_data="cancel_reg")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await query.edit_message_text(summary, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await message.reply_text(summary, parse_mode='Markdown', reply_markup=reply_markup)
        
        return CONFIRM_DATA
    
    async def confirm_save(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """حفظ البيانات"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel_reg":
            await query.edit_message_text("❌ تم الإلغاء")
            return ConversationHandler.END
        
        # حفظ في قاعدة البيانات
        data = context.user_data
        user = update.effective_user
        
        conn = sqlite3.connect('fc26_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO users (
                telegram_id, username, first_name, platform,
                whatsapp, payment_method, phone, card_number_encrypted,
                instapay_link, emails, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user.id,
            user.username,
            user.first_name,
            data['platform'],
            data['whatsapp'],
            data['payment_method'],
            data['phone'],
            data['card_encrypted'],
            data.get('instapay'),
            json.dumps(data.get('emails', [])),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        success_text = f"""
🎉 **تم التسجيل بنجاح!**

مرحباً بك في عائلة FC 26! 🎮

/profile - عرض حسابك
/prices - عرض الأسعار
/support - الدعم الفني
"""
        
        await query.edit_message_text(success_text, parse_mode='Markdown')
        
        logger.info(f"✅ تم تسجيل المستخدم {user.username}")
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء التسجيل"""
        await update.message.reply_text("❌ تم إلغاء التسجيل")
        return ConversationHandler.END
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي"""
        user = update.effective_user
        
        conn = sqlite3.connect('fc26_bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user.id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            await update.message.reply_text("❌ لم تسجل بعد! استخدم /start")
            return
        
        data = dict(row)
        emails = json.loads(data.get('emails', '[]'))
        
        profile = f"""
👤 **حسابك الشخصي**

🆔 **رقم العضوية:** #{data['id']}
🎮 **المنصة:** {data['platform'].title()}
📱 **واتساب:** {data['whatsapp']}
💳 **الدفع:** {data['payment_method'].replace('_', ' ').title()}
📞 **الهاتف:** {data['phone']}
🔗 **انستا باي:** {data.get('instapay_link', 'لا يوجد')}
📧 **الإيميلات:** {', '.join(emails) if emails else 'لا يوجد'}
📅 **تاريخ التسجيل:** {data['created_at'][:10]}
"""
        
        await update.message.reply_text(profile, parse_mode='Markdown')
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الأسعار"""
        prices = """
💰 **أسعار كوينز FC 26**

**الشراء منك:**
🎮 PlayStation: 0.09 جنيه/كوين
🎯 Xbox: 0.08 جنيه/كوين
💻 PC: 0.07 جنيه/كوين

**البيع لك:**
🎮 PlayStation: 0.11 جنيه/كوين
🎯 Xbox: 0.10 جنيه/كوين
💻 PC: 0.09 جنيه/كوين

⏰ آخر تحديث: الآن
"""
        
        await update.message.reply_text(prices, parse_mode='Markdown')
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الدعم الفني"""
        support = """
📞 **الدعم الفني**

📱 واتساب: +201234567890
💬 تليجرام: @fc26support
📧 إيميل: support@fc26bot.com

أوقات العمل: 10ص - 10م يومياً
"""
        
        await update.message.reply_text(support, parse_mode='Markdown')
    
    def run(self):
        """تشغيل البوت"""
        application = Application.builder().token(self.token).build()
        
        # معالج التسجيل
        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_registration, pattern="^register_start$"),
                CommandHandler("register", self.start_registration)
            ],
            states={
                PLATFORM: [CallbackQueryHandler(self.platform_choice, pattern="^plat_")],
                WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.whatsapp_input)],
                PAYMENT_METHOD: [CallbackQueryHandler(self.payment_choice, pattern="^pay_")],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.phone_input)],
                CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.card_input)],
                INSTAPAY_LINK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.instapay_input),
                    CallbackQueryHandler(self.instapay_input, pattern="^skip_instapay$")
                ],
                EMAILS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.email_input),
                    CallbackQueryHandler(self.email_input, pattern="^skip_email$")
                ],
                CONFIRM_DATA: [CallbackQueryHandler(self.confirm_save, pattern="^(confirm_save|cancel_reg)$")]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )
        
        # إضافة المعالجات
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("profile", self.profile_command))
        application.add_handler(CommandHandler("prices", self.prices_command))
        application.add_handler(CommandHandler("support", self.support_command))
        
        # تشغيل البوت
        logger.info("🚀 بدء تشغيل بوت FC 26...")
        print("🤖 البوت شغال! افتح التليجرام وجرب")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = FC26Bot()
    bot.run()