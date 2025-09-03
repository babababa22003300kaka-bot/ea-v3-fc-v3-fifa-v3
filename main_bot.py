#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Bot - البوت الرئيسي
نظام تسجيل متقدم مع حفظ تلقائي
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# استيراد الإعدادات والمعالجات
from bot.config import BOT_TOKEN, ADMIN_ID
from bot.database.models import Database
from bot.handlers.registration import RegistrationHandler, get_registration_conversation
from bot.keyboards.registration import get_start_keyboard, get_main_menu_keyboard

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FC26Bot:
    """البوت الرئيسي لـ FC 26"""
    
    def __init__(self):
        self.db = Database()
        self.registration_handler = RegistrationHandler()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        telegram_id = update.effective_user.id
        username = update.effective_user.username
        
        # التحقق من وجود المستخدم
        user = self.db.get_user_by_telegram_id(telegram_id)
        
        if user and user.get('registration_status') == 'complete':
            # مستخدم مسجل
            profile = self.db.get_user_profile(telegram_id)
            
            welcome_back_message = f"""
👋 أهلاً بعودتك {username or 'صديقنا العزيز'}!

💰 رصيدك: {profile.get('coin_balance', 0)} عملة
🏆 المستوى: {profile.get('level_name', 'مبتدئ')}
⭐ نقاط الولاء: {profile.get('loyalty_points', 0)}

اختر من القائمة للمتابعة 👇
"""
            await update.message.reply_text(
                welcome_back_message,
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # مستخدم جديد أو لم يكمل التسجيل
            await self.registration_handler.start(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_text = """
📖 **دليل استخدام البوت:**

🔹 /start - البداية والتسجيل
🔹 /help - عرض المساعدة
🔹 /profile - عرض الملف الشخصي
🔹 /wallet - عرض المحفظة
🔹 /prices - أسعار العملات
🔹 /buy - شراء عملات
🔹 /sell - بيع عملات
🔹 /offers - العروض المتاحة
🔹 /support - الدعم الفني
🔹 /cancel - إلغاء العملية الحالية

💡 **نصائح:**
• أكمل تسجيلك للحصول على 100 نقطة ترحيبية
• تابع العروض اليومية للحصول على خصومات
• ارفع مستواك للحصول على مميزات إضافية
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text(
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return
        
        profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🆔 المعرف: {profile.get('user_id')}
🎮 المنصة: {profile.get('gaming_platform', 'غير محدد')}
📱 واتساب: {profile.get('whatsapp_number', 'غير محدد')}
💳 طريقة الدفع: {profile.get('payment_method', 'غير محدد')}

💰 **المحفظة:**
• العملات: {profile.get('coin_balance', 0)}
• الرصيد النقدي: {profile.get('cash_balance', 0):.2f} جنيه
• نقاط الولاء: {profile.get('loyalty_points', 0)}

🏆 **المستوى:**
• المستوى الحالي: {profile.get('level_name', 'مبتدئ')}
• نقاط الخبرة: {profile.get('experience_points', 0)}
• عدد المعاملات: {profile.get('transaction_count', 0)}

📅 تاريخ التسجيل: {profile.get('created_at', 'غير محدد')}
"""
        await update.message.reply_text(profile_text, parse_mode='Markdown')
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المحفظة"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text(
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return
        
        wallet_text = f"""
💰 **محفظتك الإلكترونية**
━━━━━━━━━━━━━━━━

🪙 عملات FC 26: {profile.get('coin_balance', 0)}
💵 الرصيد النقدي: {profile.get('cash_balance', 0):.2f} جنيه
⭐ نقاط الولاء: {profile.get('loyalty_points', 0)}

📊 **الإحصائيات:**
• إجمالي المشتريات: {profile.get('total_purchased', 0)}
• إجمالي المبيعات: {profile.get('total_sold', 0)}
• الرصيد المجمد: {profile.get('frozen_balance', 0):.2f} جنيه

💡 استخدم نقاط الولاء للحصول على خصومات!
"""
        await update.message.reply_text(wallet_text, parse_mode='Markdown')
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الأسعار"""
        prices_text = """
💹 **أسعار FC 26 اليوم**
━━━━━━━━━━━━━━━━

📈 سعر الشراء: 1.20 جنيه للعملة
📉 سعر البيع: 1.15 جنيه للعملة

🎯 **العروض الخاصة:**
• شراء 1000 عملة = خصم 5%
• شراء 5000 عملة = خصم 10%
• شراء 10000 عملة = خصم 15%

⏰ آخر تحديث: منذ 5 دقائق

📊 لعرض الرسم البياني: /chart
"""
        await update.message.reply_text(prices_text, parse_mode='Markdown')
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """لوحة الإدارة"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
        
        # إحصائيات
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE registration_status = 'complete'")
        registered_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        conn.close()
        
        admin_text = f"""
🔧 **لوحة الإدارة**
━━━━━━━━━━━━━━━━

👥 **المستخدمون:**
• الإجمالي: {total_users}
• المسجلون: {registered_users}
• غير مكتملي التسجيل: {total_users - registered_users}

💳 **المعاملات:**
• الإجمالي: {total_transactions}

⚙️ **الأوامر الإدارية:**
/broadcast - رسالة جماعية
/users - قائمة المستخدمين
/stats - إحصائيات مفصلة
/backup - نسخة احتياطية
"""
        await update.message.reply_text(admin_text, parse_mode='Markdown')
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة المعالجات
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("profile", self.profile_command))
        app.add_handler(CommandHandler("wallet", self.wallet_command))
        app.add_handler(CommandHandler("prices", self.prices_command))
        app.add_handler(CommandHandler("admin", self.admin_command))
        
        # إضافة معالج التسجيل
        app.add_handler(get_registration_conversation())
        
        # تشغيل البوت
        logger.info("🚀 بدء تشغيل FC 26 Bot...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = FC26Bot()
    bot.run()