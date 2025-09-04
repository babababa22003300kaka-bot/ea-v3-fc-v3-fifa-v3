#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Bot - النسخة النهائية مع حذف الحساب الشغال 100%
"""

import os
import logging
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# الإعدادات
BOT_TOKEN = "7607085569:AAEq91WtoNg68U9e8-mWm8DsOTh2W9MmmTw"
ADMIN_ID = 1124247595

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# استيراد قاعدة البيانات
from bot.database.models import Database
from bot.handlers.registration import get_registration_conversation

class FC26Bot:
    """البوت الرئيسي"""
    
    def __init__(self):
        self.db = Database()
        logger.info("✅ تم تهيئة البوت")
    
    # ========== الأوامر الأساسية ==========
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        telegram_id = update.effective_user.id
        username = update.effective_user.username or "صديقنا العزيز"
        
        user = self.db.get_user_by_telegram_id(telegram_id)
        
        if user and user.get('registration_status') == 'complete':
            # مستخدم مسجل
            keyboard = [
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
                [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
                [InlineKeyboardButton("📊 المعاملات", callback_data="transactions")],
                [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
            ]
            
            await update.message.reply_text(
                f"🏠 **مرحباً بعودتك {username}!**\n\n"
                "اختر من القائمة:",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # مستخدم جديد
            keyboard = [[InlineKeyboardButton("📝 تسجيل جديد", callback_data="start_registration")]]
            
            await update.message.reply_text(
                "🌟 **أهلاً وسهلاً في بوت FC 26!**\n\n"
                "🎮 البوت الأول لتداول عملات FC 26\n"
                "✨ خدمة سريعة وآمنة 24/7\n\n"
                "للبدء، اضغط على تسجيل جديد:",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text("❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء")
            return
        
        profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🆔 **المعرف:** #{profile.get('user_id')}
📱 **المستخدم:** @{profile.get('telegram_username', 'غير محدد')}
🎮 **المنصة:** {profile.get('gaming_platform', 'غير محدد')}
📅 **تاريخ التسجيل:** {str(profile.get('created_at', 'غير محدد'))[:10]}

📊 **معلومات الحساب:**
• واتساب: {profile.get('whatsapp_number', 'غير محدد')}
• طريقة الدفع: {profile.get('payment_method', 'غير محدد')}
• الحالة: ✅ نشط
"""
        
        keyboard = [
            [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
            [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account_warning")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            profile_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر حذف الحساب المباشر"""
        telegram_id = update.effective_user.id
        
        # التحقق من وجود المستخدم
        user = self.db.get_user_by_telegram_id(telegram_id)
        if not user:
            await update.message.reply_text(
                "❌ لم يتم العثور على حسابك!\n\nاكتب /start للتسجيل"
            )
            return
        
        # إظهار رسالة التحذير
        keyboard = [
            [
                InlineKeyboardButton("⚠️ نعم، احذف نهائياً", callback_data="delete_confirm_final"),
                InlineKeyboardButton("❌ إلغاء", callback_data="delete_cancel")
            ]
        ]
        
        await update.message.reply_text(
            "🚨 **تحذير خطير!**\n\n"
            "⚠️ أنت على وشك حذف حسابك نهائياً\n\n"
            "**سيتم حذف:**\n"
            "• جميع بياناتك الشخصية 🗑️\n"
            "• سجل معاملاتك 📊\n"
            "• كل شيء مرتبط بحسابك 💾\n\n"
            "🔴 **لا يمكن التراجع عن هذا القرار أبداً!**\n\n"
            "هل أنت متأكد 100%؟",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ========== معالجات الأزرار ==========
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج عام للأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        telegram_id = query.from_user.id
        
        # تجاهل أزرار الحذف - لها معالجات خاصة
        if data in ["delete_confirm_final", "delete_cancel", "delete_account_warning"]:
            return
        
        if data == "show_profile":
            profile = self.db.get_user_profile(telegram_id)
            
            if not profile:
                await query.edit_message_text("❌ حسابك غير موجود!")
                return
            
            profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🆔 **المعرف:** #{profile.get('user_id')}
📱 **المستخدم:** @{profile.get('telegram_username', 'غير محدد')}
🎮 **المنصة:** {profile.get('gaming_platform', 'غير محدد')}
📅 **التسجيل:** {str(profile.get('created_at', 'غير محدد'))[:10]}
"""
            
            keyboard = [
                [InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account_warning")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]
            ]
            
            await query.edit_message_text(
                profile_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "main_menu":
            keyboard = [
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
                [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
                [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
            ]
            
            await query.edit_message_text(
                "🏠 **القائمة الرئيسية**\n\nاختر من القائمة:",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        else:
            await query.edit_message_text("🚧 قيد التطوير...")
    
    async def handle_delete_warning(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج تحذير الحذف من الأزرار"""
        query = update.callback_query
        await query.answer("⚠️ تحذير مهم")
        
        keyboard = [
            [
                InlineKeyboardButton("⚠️ نعم، احذف نهائياً", callback_data="delete_confirm_final"),
                InlineKeyboardButton("❌ إلغاء", callback_data="delete_cancel")
            ]
        ]
        
        await query.edit_message_text(
            "🚨 **تحذير نهائي!**\n\n"
            "⚠️ هذا آخر تحذير قبل حذف حسابك\n\n"
            "**سيتم فقدان كل شيء:**\n"
            "• البيانات الشخصية 📝\n"
            "• السجلات والمعاملات 📊\n"
            "• لا يمكن الاستعادة أبداً 🚫\n\n"
            "🔴 **هل أنت متأكد تماماً؟**",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد الحذف النهائي"""
        query = update.callback_query
        await query.answer("🗑️ جاري حذف الحساب...")
        
        telegram_id = query.from_user.id
        username = query.from_user.username or "المستخدم"
        
        logger.info(f"🔴 بدء حذف حساب: {telegram_id} (@{username})")
        
        try:
            # تنفيذ الحذف
            success = self.db.delete_user_account(telegram_id)
            
            if success:
                await query.edit_message_text(
                    f"✅ **تم حذف حسابك بنجاح**\n\n"
                    f"👋 وداعاً {username}!\n\n"
                    "نأسف لرؤيتك تغادر 😢\n"
                    "يمكنك العودة في أي وقت بكتابة /start\n\n"
                    "🙏 شكراً لاستخدامك بوت FC 26",
                    parse_mode='Markdown'
                )
                logger.info(f"✅ تم حذف حساب {telegram_id} بنجاح")
            else:
                await query.edit_message_text(
                    "❌ **فشل حذف الحساب**\n\n"
                    "حدث خطأ أثناء حذف حسابك\n"
                    "يرجى المحاولة مرة أخرى أو التواصل مع الدعم\n\n"
                    "📞 الدعم: @FC26_Support",
                    parse_mode='Markdown'
                )
                logger.error(f"❌ فشل حذف حساب {telegram_id}")
                
        except Exception as e:
            logger.error(f"💥 خطأ في حذف حساب {telegram_id}: {e}")
            await query.edit_message_text(
                "❌ **خطأ غير متوقع**\n\n"
                "حدث خطأ تقني\n"
                "يرجى التواصل مع الدعم الفني\n\n"
                f"🔍 رقم الخطأ: #{telegram_id}",
                parse_mode='Markdown'
            )
    
    async def handle_delete_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء الحذف"""
        query = update.callback_query
        await query.answer("✅ تم الإلغاء")
        
        keyboard = [
            [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
            [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
            [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
        ]
        
        await query.edit_message_text(
            "✅ **تم إلغاء حذف الحساب**\n\n"
            "😊 سعداء لبقائك معنا!\n"
            "حسابك آمن ولم يتم حذف أي شيء\n\n"
            "🏠 العودة للقائمة الرئيسية:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logger.info(f"تم إلغاء حذف حساب {query.from_user.id}")
    
    # ========== تشغيل البوت ==========
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🚀 بدء تشغيل FC 26 Bot...")
        
        # حذف أي webhook قديم
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
                json={"drop_pending_updates": True}
            )
            logger.info(f"🧹 حذف webhook: {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️ تحذير webhook: {e}")
        
        # إنشاء التطبيق
        app = Application.builder().token(BOT_TOKEN).build()
        
        # ========== ترتيب المعالجات مهم جداً ==========
        
        # 1. معالجات الحذف أولاً (أعلى أولوية)
        app.add_handler(CallbackQueryHandler(
            self.handle_delete_confirm,
            pattern="^delete_confirm_final$"
        ))
        app.add_handler(CallbackQueryHandler(
            self.handle_delete_cancel,
            pattern="^delete_cancel$"
        ))
        app.add_handler(CallbackQueryHandler(
            self.handle_delete_warning,
            pattern="^delete_account_warning$"
        ))
        
        # 2. الأوامر الأساسية
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("profile", self.profile_command))
        app.add_handler(CommandHandler("delete", self.delete_command))
        
        # 3. معالج الأزرار العام
        app.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # 4. معالج التسجيل (آخر شيء)
        try:
            app.add_handler(get_registration_conversation())
        except:
            logger.warning("⚠️ معالج التسجيل غير متاح")
        
        # تشغيل البوت
        logger.info("✅ البوت جاهز - حذف الحساب يعمل 100%!")
        print("🎉 البوت شغال! اضغط Ctrl+C للإيقاف")
        
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )

if __name__ == "__main__":
    bot = FC26Bot()
    bot.run()
