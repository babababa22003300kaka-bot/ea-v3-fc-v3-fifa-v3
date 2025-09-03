#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Bot - البوت الرئيسي
نظام أزرار تفاعلية فقط - بدون كيبورد
نسخة محدثة ومبسطة
"""

import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from bot.keyboards.registration import get_start_keyboard, get_main_menu_keyboard, get_delete_account_keyboard

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
        self.delete_user_state = {}  # لتتبع حالة حذف المستخدم
        
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

🔹 **الأوامر المتاحة:**
• /sell - بيع عملات  
• /profile - الملف الشخصي
• /wallet - المحفظة
• /delete - حذف حسابك
• /help - المساعدة

أو استخدم الأزرار التفاعلية:
"""
            await update.message.reply_text(
                welcome_back_message,
                reply_markup=get_main_menu_keyboard(),
                parse_mode='Markdown'
            )
        else:
            # مستخدم جديد أو لم يكمل التسجيل
            await self.registration_handler.start(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_text = """
📖 **دليل استخدام البوت**
━━━━━━━━━━━━━━━━

🔹 **الأوامر الأساسية:**
• /start - البداية والتسجيل
• /help - عرض هذه المساعدة

💰 **التداول:**
• /sell - بيع عملات FC 26
• /prices - أسعار العملات

👤 **الحساب:**
• /profile - عرض الملف الشخصي
• /wallet - عرض المحفظة
• /transactions - سجل المعاملات
• /delete - حذف حسابك

⚙️ **أخرى:**
• /settings - الإعدادات
• /support - الدعم الفني
• /cancel - إلغاء العملية الحالية

🔧 **أوامر الأدمن:**
• /admin - لوحة الإدارة
• /deleteuser - حذف مستخدم محدد

💡 **نصائح:**
• أكمل تسجيلك للحصول على 100 نقطة ترحيبية
• ارفع مستواك للحصول على مميزات إضافية

⚡ يمكنك استخدام الأزرار التفاعلية أو كتابة الأوامر مباشرة
"""
        
        # إضافة أوامر الأدمن إذا كان المستخدم أدمن
        if update.effective_user.id == ADMIN_ID:
            help_text += """
━━━━━━━━━━━━━━━━
🔧 **أوامر الأدمن الخاصة:**
• /deleteuser [telegram_id] - حذف مستخدم بمعرفه
• /broadcast - رسالة جماعية
• /stats - إحصائيات مفصلة
• /backup - نسخة احتياطية
"""
        
        await update.message.reply_text(
            help_text, 
            parse_mode='Markdown',
            reply_markup=get_main_menu_keyboard()
        )
    
    async def sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر بيع العملات"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text(
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return
        
        balance = profile.get('coin_balance', 0)
        
        if balance == 0:
            await update.message.reply_text(
                "❌ ليس لديك عملات للبيع!\n\nرصيدك الحالي: 0 عملة",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        sell_message = f"""
💸 **بيع عملات FC 26**
━━━━━━━━━━━━━━━━

💰 رصيدك الحالي: {balance:,} عملة
📊 سعر البيع: 1.15 جنيه للعملة
💵 القيمة الإجمالية: {balance * 1.15:,.2f} جنيه

اختر الكمية المراد بيعها:
"""
        
        # إنشاء أزرار ديناميكية حسب الرصيد
        keyboard = []
        
        if balance >= 100:
            keyboard.append([
                InlineKeyboardButton("100 عملة (115 جنيه)", callback_data="sell_100")
            ])
        if balance >= 500:
            keyboard[-1].append(
                InlineKeyboardButton("500 عملة (575 جنيه)", callback_data="sell_500")
            )
        if balance >= 1000:
            keyboard.append([
                InlineKeyboardButton("1000 عملة (1150 جنيه)", callback_data="sell_1000")
            ])
        if balance >= 5000:
            keyboard[-1].append(
                InlineKeyboardButton("5000 عملة (5750 جنيه)", callback_data="sell_5000")
            )
        
        keyboard.append([
            InlineKeyboardButton(f"💯 بيع الكل ({balance} عملة)", callback_data="sell_all")
        ])
        keyboard.append([
            InlineKeyboardButton("💎 كمية مخصصة", callback_data="sell_custom")
        ])
        keyboard.append([
            InlineKeyboardButton("🔙 رجوع للقائمة", callback_data="back_to_menu")
        ])
        
        await update.message.reply_text(
            sell_message,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text(
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء",
                reply_markup=get_start_keyboard()
            )
            return
        
        # حساب مستوى المستخدم
        points = profile.get('loyalty_points', 0)
        if points >= 5000:
            level = "👑 أسطورة"
            next_level = "المستوى الأقصى"
            progress = 100
        elif points >= 1000:
            level = "💎 خبير"
            next_level = "👑 أسطورة (5000 نقطة)"
            progress = int((points - 1000) / 40)
        elif points >= 500:
            level = "⚡ محترف"
            next_level = "💎 خبير (1000 نقطة)"
            progress = int((points - 500) / 5)
        elif points >= 100:
            level = "🔥 نشط"
            next_level = "⚡ محترف (500 نقطة)"
            progress = int((points - 100) / 4)
        else:
            level = "🌱 مبتدئ"
            next_level = "🔥 نشط (100 نقطة)"
            progress = int(points)
        
        # شريط التقدم
        progress_bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        
        profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🆔 **معرف المستخدم:** #{profile.get('user_id')}
📱 **تيليجرام:** @{profile.get('telegram_username', 'غير محدد')}
🆔 **Telegram ID:** `{telegram_id}`
🎮 **المنصة:** {profile.get('platform', 'غير محدد')}
📅 **تاريخ التسجيل:** {profile.get('created_at', 'غير محدد')[:10]}

💰 **المعلومات المالية:**
• الرصيد: {profile.get('coin_balance', 0):,} عملة
• القيمة: {profile.get('coin_balance', 0) * 1.15:,.2f} جنيه
• نقاط الولاء: {points:,} نقطة

🏆 **المستوى والتقدم:**
• المستوى الحالي: {level}
• المستوى التالي: {next_level}
• التقدم: [{progress_bar}] {progress}%

📊 **الإحصائيات:**
• عمليات البيع: {profile.get('sell_count', 0)}
• إجمالي المعاملات: {profile.get('transaction_count', 0)}
"""
        
        keyboard = [
            [InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_profile"),
             InlineKeyboardButton("🔐 الأمان", callback_data="security")],
            [InlineKeyboardButton("💳 المحفظة", callback_data="wallet"),
             InlineKeyboardButton("📊 المعاملات", callback_data="transactions")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        
        await update.message.reply_text(
            profile_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المحفظة"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text(
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return
        
        balance = profile.get('coin_balance', 0)
        points = profile.get('loyalty_points', 0)
        
        wallet_text = f"""
💳 **محفظتك الإلكترونية**
━━━━━━━━━━━━━━━━

💰 **الرصيد الحالي:**
• عملات FC 26: {balance:,} عملة
• القيمة بسعر البيع: {balance * 1.15:,.2f} جنيه

⭐ **نقاط الولاء:**
• النقاط المتاحة: {points:,} نقطة
• القيمة: {points * 0.01:.2f} جنيه

📈 **آخر 5 معاملات:**
جاري التحميل...

💡 **نصائح:**
• احصل على 50 نقطة يومياً بتسجيل الدخول
• استخدم النقاط للحصول على خصومات
"""
        
        keyboard = [
            [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
            [InlineKeyboardButton("💱 تحويل عملات", callback_data="transfer")],
            [InlineKeyboardButton("📊 كل المعاملات", callback_data="all_transactions")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        
        await update.message.reply_text(
            wallet_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر حذف الحساب"""
        telegram_id = update.effective_user.id
        
        # عرض رسالة التحذير
        warning_message = """
⚠️ **تحذير مهم جداً!**
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك نهائياً؟

**سيتم حذف:**
• جميع بياناتك الشخصية 🗑️
• رصيدك من العملات 💰
• نقاط الولاء المتراكمة ⭐
• سجل معاملاتك بالكامل 📊

⛔ **لا يمكن التراجع عن هذا الإجراء نهائياً!**

هل تريد المتابعة؟
"""
        await update.message.reply_text(
            warning_message,
            reply_markup=get_delete_account_keyboard(),
            parse_mode='Markdown'
        )
    
    async def deleteuser_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر حذف مستخدم محدد (للأدمن فقط)"""
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ هذا الأمر للمشرفين فقط!")
            return
        
        # التحقق من وجود معرف المستخدم
        if len(context.args) == 0:
            # طلب معرف المستخدم
            await update.message.reply_text(
                """🔧 **حذف مستخدم محدد**
━━━━━━━━━━━━━━━━

استخدم الأمر بالشكل التالي:
`/deleteuser [telegram_id]`

مثال:
`/deleteuser 123456789`

أو أرسل معرف التيليجرام الآن:""",
                parse_mode='Markdown'
            )
            # حفظ الحالة لانتظار الرد
            self.delete_user_state[update.effective_user.id] = True
            return
        
        try:
            target_telegram_id = int(context.args[0])
            
            # البحث عن المستخدم
            user = self.db.get_user_by_telegram_id(target_telegram_id)
            
            if not user:
                await update.message.reply_text(
                    f"❌ لم يتم العثور على مستخدم بالمعرف: {target_telegram_id}"
                )
                return
            
            # عرض معلومات المستخدم وطلب التأكيد
            confirm_text = f"""
⚠️ **تأكيد حذف المستخدم**
━━━━━━━━━━━━━━━━

🆔 **معرف المستخدم:** #{user.get('user_id')}
📱 **اسم المستخدم:** @{user.get('telegram_username', 'غير محدد')}
🆔 **Telegram ID:** `{target_telegram_id}`
📅 **تاريخ التسجيل:** {user.get('created_at', 'غير محدد')[:10]}

هل تريد حذف هذا المستخدم نهائياً؟
"""
            
            keyboard = [
                [InlineKeyboardButton("⚠️ نعم، احذف المستخدم", callback_data=f"admin_delete_{target_telegram_id}")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_admin_delete")]
            ]
            
            await update.message.reply_text(
                confirm_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ معرف غير صحيح! يجب أن يكون رقماً."
            )
    
    async def transactions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض المعاملات"""
        telegram_id = update.effective_user.id
        profile = self.db.get_user_profile(telegram_id)
        
        if not profile:
            await update.message.reply_text(
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return
        
        transactions_text = """
📊 **سجل المعاملات**
━━━━━━━━━━━━━━━━

📅 **آخر المعاملات:**
• لا توجد معاملات حتى الآن

📈 **إحصائيات:**
• إجمالي البيع: 0 عملة
• صافي الربح: 0 جنيه

🔍 المعاملات ستظهر هنا عند إجراء عمليات
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 تقرير شهري", callback_data="monthly_report")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        
        await update.message.reply_text(
            transactions_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الأسعار"""
        prices_text = """
💹 **أسعار FC 26 اللحظية**
━━━━━━━━━━━━━━━━

📊 **الأسعار الحالية:**
• سعر البيع: 1.15 جنيه/عملة

📈 **مؤشر السوق:**
• الاتجاه: مستقر 📊
• حجم التداول: 125,000 عملة

⏰ **آخر تحديث:** منذ دقيقتين
"""
        
        keyboard = [
            [InlineKeyboardButton("💸 بيع الآن", callback_data="sell_now")],
            [InlineKeyboardButton("📊 الرسم البياني", callback_data="price_chart")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        
        await update.message.reply_text(
            prices_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الإعدادات"""
        settings_text = """
⚙️ **الإعدادات**
━━━━━━━━━━━━━━━━

🔧 **إعدادات الحساب:**
• اللغة: العربية 🇪🇬
• المنطقة الزمنية: Cairo (GMT+2)

🔔 **الإشعارات:**
• إشعارات الأسعار: ✅ مفعل
• إشعارات المعاملات: ✅ مفعل

🔐 **الأمان:**
• التحقق الثنائي: ❌ معطل

اختر ما تريد تعديله:
"""
        
        keyboard = [
            [InlineKeyboardButton("🌍 اللغة", callback_data="set_language"),
             InlineKeyboardButton("🔔 الإشعارات", callback_data="set_notifications")],
            [InlineKeyboardButton("🔐 الأمان", callback_data="set_security")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        
        await update.message.reply_text(
            settings_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الدعم الفني"""
        support_text = """
📞 **الدعم الفني**
━━━━━━━━━━━━━━━━

🆘 **طرق التواصل:**

📱 **واتساب:**
• رقم الدعم: 01234567890
• متاح 24/7

💬 **تيليجرام:**
• الدعم المباشر: @FC26_Support

📧 **البريد الإلكتروني:**
• support@fc26bot.com

❓ **الأسئلة الشائعة:**
• كيف أبيع عملات؟
• كيف أحول لصديق؟
• كيف أستخدم النقاط؟

اختر طريقة التواصل:
"""
        
        keyboard = [
            [InlineKeyboardButton("💬 دردشة مباشرة", url="https://t.me/FC26_Support")],
            [InlineKeyboardButton("❓ الأسئلة الشائعة", callback_data="faq")],
            [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
        ]
        
        await update.message.reply_text(
            support_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل النصية"""
        user_id = update.effective_user.id
        
        # التحقق من حالة انتظار معرف المستخدم للحذف
        if user_id == ADMIN_ID and self.delete_user_state.get(user_id):
            try:
                target_telegram_id = int(update.message.text.strip())
                
                # البحث عن المستخدم
                user = self.db.get_user_by_telegram_id(target_telegram_id)
                
                if not user:
                    await update.message.reply_text(
                        f"❌ لم يتم العثور على مستخدم بالمعرف: {target_telegram_id}"
                    )
                else:
                    # عرض معلومات المستخدم وطلب التأكيد
                    confirm_text = f"""
⚠️ **تأكيد حذف المستخدم**
━━━━━━━━━━━━━━━━

🆔 **معرف المستخدم:** #{user.get('user_id')}
📱 **اسم المستخدم:** @{user.get('telegram_username', 'غير محدد')}
🆔 **Telegram ID:** `{target_telegram_id}`

هل تريد حذف هذا المستخدم نهائياً؟
"""
                    
                    keyboard = [
                        [InlineKeyboardButton("⚠️ نعم، احذف المستخدم", callback_data=f"admin_delete_{target_telegram_id}")],
                        [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_admin_delete")]
                    ]
                    
                    await update.message.reply_text(
                        confirm_text,
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                
                # إلغاء حالة الانتظار
                self.delete_user_state[user_id] = False
                
            except ValueError:
                await update.message.reply_text(
                    "❌ معرف غير صحيح! يجب أن يكون رقماً."
                )
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار التفاعلية"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        
        # معالجة حذف الحساب الشخصي
        if query.data == "confirm_delete":
            success = self.db.delete_user_account(telegram_id)
            
            if success:
                await query.edit_message_text(
                    "✅ تم حذف حسابك بنجاح.\n\nنأسف لرؤيتك تغادر 😢\nيمكنك التسجيل مرة أخرى في أي وقت بكتابة /start"
                )
            else:
                await query.edit_message_text(
                    "❌ حدث خطأ في حذف الحساب. الرجاء المحاولة لاحقاً."
                )
        
        elif query.data == "cancel_delete":
            await query.edit_message_text(
                "✅ تم إلغاء عملية حذف الحساب.\n\nسعداء لبقائك معنا! 😊",
                reply_markup=get_main_menu_keyboard()
            )
        
        # معالجة حذف المستخدم من قبل الأدمن
        elif query.data.startswith("admin_delete_"):
            if telegram_id != ADMIN_ID:
                await query.answer("❌ غير مصرح لك!", show_alert=True)
                return
            
            target_id = int(query.data.replace("admin_delete_", ""))
            success = self.db.delete_user_account(target_id)
            
            if success:
                await query.edit_message_text(
                    f"✅ تم حذف المستخدم {target_id} بنجاح من قاعدة البيانات."
                )
            else:
                await query.edit_message_text(
                    f"❌ فشل حذف المستخدم {target_id}. قد يكون غير موجود."
                )
        
        elif query.data == "cancel_admin_delete":
            await query.edit_message_text(
                "✅ تم إلغاء عملية حذف المستخدم."
            )
        
        # معالجة زر حذف من القائمة
        elif query.data == "delete_account":
            warning_message = """
⚠️ **تحذير مهم جداً!**
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك نهائياً؟

**سيتم حذف:**
• جميع بياناتك الشخصية 🗑️
• رصيدك من العملات 💰
• نقاط الولاء المتراكمة ⭐

⛔ **لا يمكن التراجع عن هذا الإجراء!**
"""
            await query.edit_message_text(
                warning_message,
                reply_markup=get_delete_account_keyboard(),
                parse_mode='Markdown'
            )
        
        # معالجة البيع
        elif query.data == "sell_coins" or query.data == "sell_now":
            profile = self.db.get_user_profile(telegram_id)
            balance = profile.get('coin_balance', 0) if profile else 0
            
            if balance == 0:
                await query.edit_message_text(
                    "❌ ليس لديك عملات للبيع!",
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                sell_message = f"""
💸 **بيع عملات FC 26**
━━━━━━━━━━━━━━━━

💰 رصيدك: {balance} عملة
📊 السعر: 1.15 جنيه/عملة
"""
                keyboard = [
                    [InlineKeyboardButton(f"بيع الكل ({balance} عملة)", callback_data="sell_all")],
                    [InlineKeyboardButton("💎 كمية مخصصة", callback_data="sell_custom")],
                    [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]
                ]
                await query.edit_message_text(
                    sell_message,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        # معالجة البروفايل
        elif query.data == "profile":
            profile = self.db.get_user_profile(telegram_id)
            
            if not profile:
                await query.edit_message_text(
                    "❌ يجب عليك التسجيل أولاً!"
                )
                return
            
            profile_text = f"""
👤 **الملف الشخصي**
━━━━━━━━━━━━━━━━

🆔 معرف: #{profile.get('user_id')}
💰 الرصيد: {profile.get('coin_balance', 0)} عملة
⭐ النقاط: {profile.get('loyalty_points', 0)}
🏆 المستوى: {profile.get('level_name', 'مبتدئ')}
"""
            
            keyboard = [
                [InlineKeyboardButton("💳 المحفظة", callback_data="wallet")],
                [InlineKeyboardButton("📊 المعاملات", callback_data="transactions")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]
            ]
            
            await query.edit_message_text(
                profile_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        # الرجوع للقائمة الرئيسية
        elif query.data == "back_to_menu":
            profile = self.db.get_user_profile(telegram_id)
            
            if profile:
                menu_text = f"""
🏠 **القائمة الرئيسية**
━━━━━━━━━━━━━━━━

💰 رصيدك: {profile.get('coin_balance', 0)} عملة
⭐ نقاطك: {profile.get('loyalty_points', 0)}

اختر من القائمة أو استخدم الأوامر:
"""
            else:
                menu_text = """
🏠 **القائمة الرئيسية**

مرحباً بك! اختر من القائمة:
"""
            
            await query.edit_message_text(
                menu_text,
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard()
            )
        
        # باقي الأزرار - قيد التطوير
        else:
            await query.edit_message_text(
                "🚧 هذه الخدمة قيد التطوير...\n\nجاري العمل عليها وستكون متاحة قريباً!",
                reply_markup=get_main_menu_keyboard()
            )
    
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

💳 **المعاملات:**
• الإجمالي: {total_transactions}

⚙️ **الأوامر الإدارية:**
• /deleteuser [id] - حذف مستخدم محدد
• /broadcast - رسالة جماعية
• /users - قائمة المستخدمين
• /stats - إحصائيات مفصلة
• /backup - نسخة احتياطية
"""
        
        keyboard = [
            [InlineKeyboardButton("👥 المستخدمون", callback_data="admin_users"),
             InlineKeyboardButton("🗑️ حذف مستخدم", callback_data="admin_delete_user")],
            [InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 إغلاق", callback_data="close")]
        ]
        
        await update.message.reply_text(
            admin_text, 
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة معالجات الأوامر
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("sell", self.sell_command))
        app.add_handler(CommandHandler("profile", self.profile_command))
        app.add_handler(CommandHandler("wallet", self.wallet_command))
        app.add_handler(CommandHandler("delete", self.delete_command))
        app.add_handler(CommandHandler("deleteuser", self.deleteuser_command))
        app.add_handler(CommandHandler("transactions", self.transactions_command))
        app.add_handler(CommandHandler("prices", self.prices_command))
        app.add_handler(CommandHandler("settings", self.settings_command))
        app.add_handler(CommandHandler("support", self.support_command))
        app.add_handler(CommandHandler("admin", self.admin_command))
        
        # إضافة معالج الرسائل النصية
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # إضافة معالج الأزرار التفاعلية
        app.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # إضافة معالج التسجيل
        app.add_handler(get_registration_conversation())
        
        # تشغيل البوت
        logger.info("🚀 بدء تشغيل FC 26 Bot...")
        logger.info("✅ النسخة المبسطة - بدون شراء أو عروض أو إحالات")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = FC26Bot()
    bot.run()