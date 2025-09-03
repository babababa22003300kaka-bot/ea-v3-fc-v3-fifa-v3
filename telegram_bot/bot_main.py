#!/usr/bin/env python3
"""
🤖 بوت FC 26 التليجرام - النسخة الأولى
تاريخ الإنشاء: 3 سبتمبر 2025
المطور: GenSpark AI
"""

import os
import sys
import logging
from pathlib import Path

# إضافة المسار للـ system path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

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

from config.bot_config import BotConfig
from handlers.registration_handler import RegistrationHandler
from handlers.profile_handler import ProfileManager
from database.db_manager import DatabaseManager
from utils.validators import InputValidator

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FC26TelegramBot:
    """البوت الرئيسي لـ FC 26"""
    
    def __init__(self):
        """تهيئة البوت"""
        self.config = BotConfig()
        self.db = DatabaseManager()
        self.registration = RegistrationHandler(self.db)
        self.profile_manager = ProfileManager(self.db)
        self.validator = InputValidator()
        
        # توكن البوت
        self.token = os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE')
        
        logger.info("✅ تم تهيئة بوت FC 26 بنجاح")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر البداية /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # التحقق من وجود المستخدم
        existing_user = await self.db.get_user_by_telegram_id(user.id)
        
        if existing_user:
            # مستخدم مسجل
            welcome_back = f"""
🎮 **أهلاً بعودتك {user.first_name}!**

مرحباً بك مجدداً في بوت FC 26 الرسمي 🏆

📊 **حسابك:**
🎮 المنصة: {existing_user.get('platform', 'غير محدد')}
📱 واتساب: {existing_user.get('whatsapp', 'غير محدد')}

**ماذا تريد أن تفعل اليوم؟**
"""
            keyboard = [
                [
                    InlineKeyboardButton("👤 حسابي", callback_data="my_profile"),
                    InlineKeyboardButton("💰 شراء كوينز", callback_data="buy_coins")
                ],
                [
                    InlineKeyboardButton("💸 بيع كوينز", callback_data="sell_coins"),
                    InlineKeyboardButton("📊 الأسعار", callback_data="prices")
                ],
                [
                    InlineKeyboardButton("📞 الدعم", callback_data="support"),
                    InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")
                ]
            ]
        else:
            # مستخدم جديد
            welcome_back = f"""
🎮 **أهلاً بك في بوت FC 26!**

مرحباً {user.first_name}! 👋

أنا البوت الرسمي لشراء وبيع كوينز FC 26 ⚽

**المميزات:**
✅ أسعار تنافسية
✅ تحويل فوري
✅ دعم 24/7
✅ أمان 100%

**لنبدأ بتسجيل حسابك الآن!**
"""
            keyboard = [
                [InlineKeyboardButton("📝 تسجيل جديد", callback_data="register_start")],
                [InlineKeyboardButton("📚 كيف يعمل البوت؟", callback_data="how_it_works")],
                [InlineKeyboardButton("📞 الدعم الفني", callback_data="support")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # حفظ معلومات المستخدم في السياق
        context.user_data['telegram_id'] = user.id
        context.user_data['username'] = user.username
        context.user_data['first_name'] = user.first_name
        
        await update.message.reply_text(
            welcome_back,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # تسجيل النشاط
        await self.db.log_activity(user.id, "start_command", f"User {user.username} started bot")
        
        logger.info(f"👤 User {user.username} ({user.id}) started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج أمر المساعدة /help"""
        help_text = """
📚 **دليل استخدام بوت FC 26**

**الأوامر المتاحة:**
/start - البدء أو العودة للقائمة الرئيسية
/register - تسجيل حساب جديد
/profile - عرض حسابك
/prices - عرض الأسعار الحالية
/buy - شراء كوينز
/sell - بيع كوينز
/support - التواصل مع الدعم
/help - عرض هذه الرسالة

**كيفية التسجيل:**
1️⃣ اضغط /register أو "تسجيل جديد"
2️⃣ اختر منصة اللعب (PlayStation/Xbox/PC)
3️⃣ أدخل رقم الواتساب
4️⃣ اختر طريقة الدفع
5️⃣ أدخل بقية البيانات المطلوبة
6️⃣ راجع البيانات واحفظها

**ملاحظات مهمة:**
• جميع بياناتك محمية ومشفرة 🔒
• التحويلات فورية أو خلال 30 دقيقة
• الأسعار محدثة يومياً
• الدعم متاح 24/7

**للمساعدة السريعة:**
📞 واتساب: +201234567890
💬 تليجرام: @fc26support
"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الأسعار الحالية"""
        prices_text = """
💰 **أسعار كوينز FC 26 اليوم**

**أسعار الشراء (نشتري منك):**
🎮 PlayStation: 0.09 جنيه/كوين
🎯 Xbox: 0.08 جنيه/كوين  
💻 PC: 0.07 جنيه/كوين

**أسعار البيع (تشتري منا):**
🎮 PlayStation: 0.11 جنيه/كوين
🎯 Xbox: 0.10 جنيه/كوين
💻 PC: 0.09 جنيه/كوين

**العروض الخاصة:**
🎁 خصم 5% للكميات > 10,000 كوين
🎁 خصم 10% للكميات > 50,000 كوين

⏰ آخر تحديث: منذ 5 دقائق
📊 السعر العالمي: $0.0001/كوين

_الأسعار قابلة للتغيير حسب السوق_
"""
        
        keyboard = [
            [
                InlineKeyboardButton("💰 شراء الآن", callback_data="buy_coins"),
                InlineKeyboardButton("💸 بيع الآن", callback_data="sell_coins")
            ],
            [InlineKeyboardButton("🔄 تحديث الأسعار", callback_data="refresh_prices")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            prices_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "register_start":
            # بدء عملية التسجيل
            await self.registration.start_registration(update, context)
            
        elif query.data == "my_profile":
            await self.profile_manager.show_profile(update, context)
            
        elif query.data == "buy_coins":
            await query.edit_message_text("🚧 نظام الشراء قيد التطوير...")
            
        elif query.data == "sell_coins":
            await query.edit_message_text("🚧 نظام البيع قيد التطوير...")
            
        elif query.data == "prices":
            await self.prices_command(update, context)
            
        elif query.data == "support":
            support_text = """
📞 **الدعم الفني**

**طرق التواصل:**
📱 واتساب: +201234567890
💬 تليجرام: @fc26support
📧 إيميل: support@fc26bot.com

**أوقات العمل:**
السبت - الخميس: 10 ص - 10 م
الجمعة: 2 م - 10 م

أرسل رسالتك وسنرد عليك في أقرب وقت!
"""
            await query.edit_message_text(support_text, parse_mode='Markdown')
            
        elif query.data == "settings":
            await query.edit_message_text("⚙️ الإعدادات قيد التطوير...")
    
    def run(self):
        """تشغيل البوت"""
        try:
            # إنشاء التطبيق
            application = Application.builder().token(self.token).build()
            
            # إضافة المعالجات
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("prices", self.prices_command))
            
            # معالج التسجيل (ConversationHandler)
            registration_conv = self.registration.get_conversation_handler()
            application.add_handler(registration_conv)
            
            # معالج الأزرار
            application.add_handler(CallbackQueryHandler(self.button_callback))
            
            # معالج الرسائل العامة
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.registration.handle_message))
            
            # بدء البوت
            logger.info("🚀 Starting FC 26 Bot...")
            print("🤖 بوت FC 26 شغال دلوقتي!")
            print("📱 افتح التليجرام وابحث عن البوت")
            print("⛔ للإيقاف: Ctrl+C")
            
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"❌ خطأ في تشغيل البوت: {e}")
            raise

def main():
    """نقطة البداية"""
    bot = FC26TelegramBot()
    bot.run()

if __name__ == "__main__":
    main()