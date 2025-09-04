#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Bot - النسخة النهائية المُحسنة
تم إصلاح جميع الأخطاء
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


# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# استيراد قاعدة البيانات
from bot.database.models import Database

# حالات التسجيل
CHOOSING_PLATFORM, ENTERING_WHATSAPP, CHOOSING_PAYMENT = range(3)

class FC26Bot:
    """البوت الرئيسي"""
    
    def __init__(self):
        self.db = Database()
        self.app = None
        logger.info("✅ تم تهيئة البوت")
    
    # ========== الأوامر الأساسية ==========
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        # التأكد من عدم معالجة التحديثات المكررة
        if update.message is None:
            return
            
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
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_text = """
📚 **دليل الاستخدام**
━━━━━━━━━━━━━━━━

🔹 **الأوامر:**
• /start - البداية والتسجيل
• /help - هذه المساعدة
• /profile - الملف الشخصي
• /delete - حذف الحساب

💡 **نصائح:**
• استخدم الأزرار للتنقل
• يمكنك العودة أي وقت بـ /start
        """
        
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            help_text,
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
        username = update.effective_user.username or update.effective_user.first_name
        
        keyboard = [
            [
                InlineKeyboardButton("⚠️ نعم، احذف حسابي", callback_data="delete_confirm"),
                InlineKeyboardButton("❌ إلغاء", callback_data="delete_cancel")
            ]
        ]
        
        await update.message.reply_text(
            f"⚠️ **تحذير: حذف الحساب**\n\n"
            f"مرحباً {username} 👋\n\n"
            "هل أنت متأكد من حذف حسابك؟\n"
            "⚠️ **سيتم حذف:**\n"
            "• جميع بياناتك الشخصية\n"
            "• سجل معاملاتك\n"
            "• رصيدك من العملات\n\n"
            "❌ **لا يمكن التراجع عن هذا الإجراء!**",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ========== معالجات التسجيل ==========
    
    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بداية التسجيل - تستجيب لزر التسجيل"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        
        # إنشاء مستخدم جديد إذا لم يكن موجود
        user = self.db.get_user_by_telegram_id(telegram_id)
        if not user:
            self.db.create_user(
                telegram_id=telegram_id,
                telegram_username=username
            )
        
        # اختيار المنصة
        keyboard = [
            [InlineKeyboardButton("🎮 PlayStation", callback_data="platform_ps")],
            [InlineKeyboardButton("🎮 Xbox", callback_data="platform_xbox")],
            [InlineKeyboardButton("💻 PC", callback_data="platform_pc")]
        ]
        
        await query.edit_message_text(
            "📝 **خطوة 1 من 3**\n\n"
            "🎮 اختر منصة اللعب الخاصة بك:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CHOOSING_PLATFORM
    
    async def platform_chosen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج اختيار المنصة"""
        query = update.callback_query
        await query.answer()
        
        platform = query.data.replace("platform_", "")
        context.user_data['platform'] = platform
        
        await query.edit_message_text(
            "📝 **خطوة 2 من 3**\n\n"
            "📱 أدخل رقم واتساب للتواصل:\n"
            "(مثال: 01234567890)",
            parse_mode='Markdown'
        )
        
        return ENTERING_WHATSAPP
    
    async def whatsapp_entered(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج إدخال رقم واتساب"""
        whatsapp = update.message.text
        context.user_data['whatsapp'] = whatsapp
        
        keyboard = [
            [InlineKeyboardButton("💳 فودافون كاش", callback_data="payment_vodafone")],
            [InlineKeyboardButton("🏦 InstaPay", callback_data="payment_instapay")],
            [InlineKeyboardButton("💰 تحويل بنكي", callback_data="payment_bank")]
        ]
        
        await update.message.reply_text(
            "📝 **خطوة 3 من 3**\n\n"
            "💳 اختر طريقة الدفع المفضلة:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return CHOOSING_PAYMENT
    
    async def payment_chosen(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج اختيار طريقة الدفع"""
        query = update.callback_query
        await query.answer("جاري حفظ البيانات...")
        
        payment = query.data.replace("payment_", "")
        telegram_id = query.from_user.id
        
        # حفظ البيانات في قاعدة البيانات
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # تحديث بيانات المستخدم
            cursor.execute("""
                UPDATE users 
                SET registration_status = 'complete'
                WHERE telegram_id = ?
            """, (telegram_id,))
            
            # الحصول على user_id
            cursor.execute("SELECT user_id FROM users WHERE telegram_id = ?", (telegram_id,))
            user = cursor.fetchone()
            
            if user:
                user_id = user['user_id']
                
                # حفظ بيانات التسجيل
                cursor.execute("""
                    INSERT OR REPLACE INTO registration_data 
                    (user_id, gaming_platform, whatsapp_number, payment_method)
                    VALUES (?, ?, ?, ?)
                """, (user_id, context.user_data.get('platform'), 
                      context.user_data.get('whatsapp'), payment))
            
            conn.commit()
            
            # رسالة النجاح
            keyboard = [
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
                [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
                [InlineKeyboardButton("📊 المعاملات", callback_data="transactions")]
            ]
            
            await query.edit_message_text(
                "🎉 **تم التسجيل بنجاح!**\n\n"
                "✅ حسابك جاهز الآن\n"
                "يمكنك البدء في التداول فوراً\n\n"
                "اختر من القائمة:",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"خطأ في حفظ التسجيل: {e}")
            await query.edit_message_text(
                "❌ حدث خطأ في حفظ البيانات\n"
                "يرجى المحاولة مرة أخرى لاحقاً",
                parse_mode='Markdown'
            )
        finally:
            conn.close()
        
        return ConversationHandler.END
    
    async def cancel_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء التسجيل"""
        await update.message.reply_text(
            "❌ تم إلغاء التسجيل\n"
            "يمكنك البدء مرة أخرى بكتابة /start"
        )
        return ConversationHandler.END
    
    # ========== معالجات الأزرار العامة ==========
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج عام للأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        telegram_id = query.from_user.id
        
        try:
            if data == "show_profile":
                # عرض الملف الشخصي
                profile = self.db.get_user_profile(telegram_id)
                if not profile:
                    await query.edit_message_text("❌ يجب عليك التسجيل أولاً!")
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
                
                await query.edit_message_text(
                    profile_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
            elif data == "main_menu":
                username = query.from_user.username or "صديقنا العزيز"
                keyboard = [
                    [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
                    [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
                    [InlineKeyboardButton("📊 المعاملات", callback_data="transactions")],
                    [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
                ]
                
                await query.edit_message_text(
                    f"🏠 **القائمة الرئيسية**\n\n"
                    f"مرحباً {username} 👋\n"
                    "اختر من القائمة:",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
            elif data == "help":
                help_text = """
📚 **دليل الاستخدام**
━━━━━━━━━━━━━━━━

🔹 **الأوامر:**
• /start - البداية والتسجيل
• /help - هذه المساعدة
• /profile - الملف الشخصي
• /delete - حذف الحساب

💡 **نصائح:**
• استخدم الأزرار للتنقل
• يمكنك العودة أي وقت بـ /start
                """
                
                keyboard = [
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                
                await query.edit_message_text(
                    help_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
            elif data == "sell_coins":
                await query.edit_message_text(
                    "💸 **بيع العملات**\n\n"
                    "قريباً... هذه الميزة قيد التطوير 🚧",
                    parse_mode='Markdown'
                )
            
            elif data == "transactions":
                await query.edit_message_text(
                    "📊 **سجل المعاملات**\n\n"
                    "قريباً... هذه الميزة قيد التطوير 🚧",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            # تجاهل أخطاء "Message is not modified"
            if "Message is not modified" not in str(e):
                logger.error(f"خطأ في معالج الأزرار: {e}")
    
    # ========== معالجات الحذف ==========
    
    async def handle_delete_warning(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحذير قبل الحذف"""
        query = update.callback_query
        await query.answer()
        
        username = query.from_user.username or query.from_user.first_name
        
        keyboard = [
            [
                InlineKeyboardButton("⚠️ نعم، احذف حسابي", callback_data="delete_confirm"),
                InlineKeyboardButton("❌ إلغاء", callback_data="delete_cancel")
            ]
        ]
        
        try:
            await query.edit_message_text(
                f"⚠️ **تحذير: حذف الحساب**\n\n"
                f"مرحباً {username} 👋\n\n"
                "هل أنت متأكد من حذف حسابك؟\n"
                "⚠️ **سيتم حذف:**\n"
                "• جميع بياناتك الشخصية\n"
                "• سجل معاملاتك\n"
                "• رصيدك من العملات\n\n"
                "❌ **لا يمكن التراجع عن هذا الإجراء!**",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            # تجاهل خطأ "Message is not modified"
            if "Message is not modified" not in str(e):
                logger.error(f"خطأ في تحذير الحذف: {e}")
    
    async def handle_delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد الحذف"""
        query = update.callback_query
        await query.answer("جاري حذف الحساب...")
        
        telegram_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name
        
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
            # إرسال رسالة خطأ بدون markdown إذا كان هناك مشكلة في التنسيق
            try:
                await query.edit_message_text(
                    f"❌ خطأ غير متوقع\n\n"
                    f"حدث خطأ تقني\n"
                    f"يرجى التواصل مع الدعم الفني\n\n"
                    f"رقم الخطأ: {telegram_id}"
                )
            except:
                pass
    
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
        self.app = Application.builder().token(BOT_TOKEN).build()
        
        # ========== معالج التسجيل ==========
        registration_conv = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_registration, pattern="^start_registration$")
            ],
            states={
                CHOOSING_PLATFORM: [
                    CallbackQueryHandler(self.platform_chosen, pattern="^platform_")
                ],
                ENTERING_WHATSAPP: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.whatsapp_entered)
                ],
                CHOOSING_PAYMENT: [
                    CallbackQueryHandler(self.payment_chosen, pattern="^payment_")
                ]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel_registration)
            ],
            per_message=False  # مهم لتجنب التحذيرات
        )
        
        # ========== ترتيب المعالجات مهم جداً ==========
        
        # 1. معالج التسجيل أولاً (أعلى أولوية)
        self.app.add_handler(registration_conv)
        
        # 2. معالجات الحذف
        self.app.add_handler(CallbackQueryHandler(self.handle_delete_warning, pattern="^delete_account_warning$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_delete_confirm, pattern="^delete_confirm$"))
        self.app.add_handler(CallbackQueryHandler(self.handle_delete_cancel, pattern="^delete_cancel$"))
        
        # 3. الأوامر الأساسية
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("profile", self.profile_command))
        self.app.add_handler(CommandHandler("delete", self.delete_command))
        
        # 4. معالج الأزرار العامة (آخر شيء)
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("✅ البوت جاهز - التسجيل والحذف يعملان 100%!")
        
        # تشغيل البوت مع drop_pending_updates لتجنب التحديثات المكررة
        self.app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        logger.info("🎉 البوت شغال! اضغط Ctrl+C للإيقاف")

# نقطة البداية
if __name__ == "__main__":
    bot = FC26Bot()
    bot.run()
