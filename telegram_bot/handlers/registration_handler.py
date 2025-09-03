"""
📝 معالج التسجيل التفاعلي
نظام تسجيل متدرج وسلس للمستخدمين الجدد
"""

import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

logger = logging.getLogger(__name__)

# حالات المحادثة
(
    PLATFORM,
    WHATSAPP,
    PAYMENT_METHOD,
    PHONE,
    CARD_NUMBER,
    INSTAPAY_LINK,
    EMAILS,
    CONFIRM_DATA
) = range(8)

class RegistrationHandler:
    """معالج عملية التسجيل الكاملة"""
    
    def __init__(self, db_manager):
        """تهيئة معالج التسجيل"""
        self.db = db_manager
        self.temp_data = {}
        
    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء عملية التسجيل"""
        query = update.callback_query
        if query:
            await query.answer()
            
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # تهيئة بيانات المستخدم المؤقتة
        context.user_data['registration'] = {
            'telegram_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'step': 1,
            'start_time': datetime.now().isoformat()
        }
        
        # رسالة البداية مع اختيار المنصة
        welcome_text = """
🎮 **تسجيل حساب جديد - الخطوة 1 من 7**

رائع! هنبدأ تسجيل حسابك خطوة بخطوة 📝

**أولاً، اختر منصة اللعب المفضلة:**
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎮 PlayStation", callback_data="platform_playstation"),
                InlineKeyboardButton("🎯 Xbox", callback_data="platform_xbox"),
                InlineKeyboardButton("💻 PC", callback_data="platform_pc")
            ],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_registration")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        logger.info(f"🎮 User {user.username} started registration")
        
        # حفظ النشاط
        await self.db.log_activity(user.id, "registration_started", "Started registration process")
        
        return PLATFORM
    
    async def platform_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار المنصة"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel_registration":
            await query.edit_message_text("❌ تم إلغاء التسجيل. يمكنك البدء مجدداً في أي وقت بالضغط على /start")
            return ConversationHandler.END
        
        # حفظ المنصة المختارة
        platform = query.data.replace("platform_", "")
        context.user_data['registration']['platform'] = platform
        context.user_data['registration']['step'] = 2
        
        # حفظ تلقائي للخطوة
        await self._auto_save_step(context.user_data['registration'])
        
        # رسالة طلب رقم الواتساب
        platform_emoji = {"playstation": "🎮", "xbox": "🎯", "pc": "💻"}
        platform_name = {"playstation": "PlayStation", "xbox": "Xbox", "pc": "PC"}
        
        whatsapp_text = f"""
✅ تم اختيار منصة: **{platform_emoji[platform]} {platform_name[platform]}**

📱 **الخطوة 2 من 7: رقم الواتساب**

من فضلك أرسل رقم الواتساب الخاص بك
يجب أن يكون بالصيغة الدولية

**مثال:**
• +201234567890 ✅
• 01234567890 ✅
• 201234567890 ✅

_رقم الواتساب مهم للتواصل معك بخصوص الطلبات_
"""
        
        keyboard = [[InlineKeyboardButton("❌ إلغاء", callback_data="cancel_registration")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            whatsapp_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        return WHATSAPP
    
    async def whatsapp_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة رقم الواتساب"""
        message = update.message
        whatsapp = message.text.strip()
        
        # التحقق من صحة الرقم
        from utils.validators import InputValidator
        validator = InputValidator()
        
        is_valid, cleaned_number, error_msg = validator.validate_whatsapp(whatsapp)
        
        if not is_valid:
            await message.reply_text(
                f"❌ {error_msg}\n\nحاول مرة أخرى أو اضغط /cancel للإلغاء",
                parse_mode='Markdown'
            )
            return WHATSAPP
        
        # حفظ الرقم
        context.user_data['registration']['whatsapp'] = cleaned_number
        context.user_data['registration']['step'] = 3
        
        # حفظ تلقائي
        await self._auto_save_step(context.user_data['registration'])
        
        # رسالة اختيار طريقة الدفع
        payment_text = f"""
✅ تم حفظ رقم الواتساب: **{cleaned_number}**

💳 **الخطوة 3 من 7: طريقة الدفع المفضلة**

اختر طريقة الدفع التي تناسبك:
"""
        
        keyboard = [
            [
                InlineKeyboardButton("📱 فودافون كاش", callback_data="pay_vodafone_cash"),
                InlineKeyboardButton("🟠 أورانج كاش", callback_data="pay_orange_cash")
            ],
            [
                InlineKeyboardButton("🟢 اتصالات كاش", callback_data="pay_etisalat_cash"),
                InlineKeyboardButton("🟡 WE كاش", callback_data="pay_we_cash")
            ],
            [
                InlineKeyboardButton("🏦 انستا باي", callback_data="pay_instapay"),
                InlineKeyboardButton("💳 بطاقة بنكية", callback_data="pay_card")
            ],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_registration")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            payment_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        return PAYMENT_METHOD
    
    async def payment_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار طريقة الدفع"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel_registration":
            await query.edit_message_text("❌ تم إلغاء التسجيل")
            return ConversationHandler.END
        
        payment_method = query.data.replace("pay_", "")
        context.user_data['registration']['payment_method'] = payment_method
        context.user_data['registration']['step'] = 4
        
        # حفظ تلقائي
        await self._auto_save_step(context.user_data['registration'])
        
        # رسالة طلب رقم الهاتف
        payment_names = {
            "vodafone_cash": "فودافون كاش",
            "orange_cash": "أورانج كاش",
            "etisalat_cash": "اتصالات كاش",
            "we_cash": "WE كاش",
            "instapay": "انستا باي",
            "card": "بطاقة بنكية"
        }
        
        phone_text = f"""
✅ تم اختيار: **{payment_names.get(payment_method, payment_method)}**

📞 **الخطوة 4 من 7: رقم الهاتف**

أرسل رقم هاتفك المصري (11 رقم)
يجب أن يبدأ بـ: 010, 011, 012, 015

**مثال:** 01012345678
"""
        
        await query.edit_message_text(phone_text, parse_mode='Markdown')
        
        return PHONE
    
    async def phone_number(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة رقم الهاتف"""
        message = update.message
        phone = message.text.strip()
        
        # التحقق من صحة الرقم
        from utils.validators import InputValidator
        validator = InputValidator()
        
        is_valid, error_msg = validator.validate_egyptian_phone(phone)
        
        if not is_valid:
            await message.reply_text(f"❌ {error_msg}\n\nحاول مرة أخرى")
            return PHONE
        
        context.user_data['registration']['phone'] = phone
        context.user_data['registration']['step'] = 5
        
        # حفظ تلقائي
        await self._auto_save_step(context.user_data['registration'])
        
        # رسالة طلب رقم البطاقة
        card_text = """
✅ تم حفظ رقم الهاتف

💳 **الخطوة 5 من 7: رقم البطاقة القومية**

أرسل رقم البطاقة القومية (16 رقم)
سيتم تشفيره وحمايته بالكامل 🔒

**ملاحظة:** يمكنك كتابة الرقم بأي صيغة:
• 1234567890123456
• 1234-5678-9012-3456
"""
        
        await message.reply_text(card_text, parse_mode='Markdown')
        
        return CARD_NUMBER
    
    async def card_number_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة رقم البطاقة"""
        message = update.message
        card = message.text.strip()
        
        # إزالة الشرطات والمسافات
        card_clean = ''.join(filter(str.isdigit, card))
        
        if len(card_clean) != 16:
            await message.reply_text(
                f"❌ رقم البطاقة يجب أن يكون 16 رقم!\nأنت أدخلت: {len(card_clean)} رقم\n\nحاول مرة أخرى"
            )
            return CARD_NUMBER
        
        # حفظ البطاقة (سيتم تشفيرها عند الحفظ في قاعدة البيانات)
        context.user_data['registration']['card_number'] = card_clean
        context.user_data['registration']['step'] = 6
        
        # حذف رسالة البطاقة للأمان
        await message.delete()
        
        # حفظ تلقائي
        await self._auto_save_step(context.user_data['registration'])
        
        # رسالة طلب رابط انستا باي
        instapay_text = """
✅ تم حفظ رقم البطاقة بشكل آمن 🔒

🔗 **الخطوة 6 من 7: رابط انستا باي (اختياري)**

إذا كان لديك حساب انستا باي، أرسل الرابط
أو اكتب **"تخطي"** للمتابعة

**مثال:** https://instapay.eg/username
"""
        
        keyboard = [[InlineKeyboardButton("⏭️ تخطي", callback_data="skip_instapay")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message.reply_text(
            instapay_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        return INSTAPAY_LINK
    
    async def instapay_link_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة رابط انستا باي"""
        # معالجة الزر أو النص
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "skip_instapay":
                context.user_data['registration']['instapay_link'] = None
                message_obj = query.message
        else:
            message = update.message
            text = message.text.strip()
            
            if text.lower() in ["تخطي", "skip", "لا", "no"]:
                context.user_data['registration']['instapay_link'] = None
            else:
                # تنظيف الرابط
                if not text.startswith("http"):
                    text = f"https://instapay.eg/{text}"
                context.user_data['registration']['instapay_link'] = text
            
            message_obj = message
        
        context.user_data['registration']['step'] = 7
        
        # حفظ تلقائي
        await self._auto_save_step(context.user_data['registration'])
        
        # رسالة طلب الإيميلات
        emails_text = """
📧 **الخطوة 7 من 7: البريد الإلكتروني (اختياري)**

يمكنك إضافة بريد إلكتروني أو أكثر
أرسلهم مفصولين بفاصلة

**مثال:** email1@gmail.com, email2@yahoo.com

أو اضغط **"تخطي"** للإنهاء
"""
        
        keyboard = [[InlineKeyboardButton("⏭️ تخطي وإنهاء", callback_data="skip_emails")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await query.edit_message_text(
                emails_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await message_obj.reply_text(
                emails_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        return EMAILS
    
    async def emails_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الإيميلات وعرض التأكيد"""
        # معالجة الزر أو النص
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "skip_emails":
                context.user_data['registration']['emails'] = []
                message_obj = query.message
        else:
            message = update.message
            text = message.text.strip()
            
            if text.lower() in ["تخطي", "skip", "لا", "no"]:
                context.user_data['registration']['emails'] = []
            else:
                # معالجة الإيميلات
                emails = [e.strip() for e in text.split(',')]
                valid_emails = []
                
                for email in emails:
                    if '@' in email and '.' in email:
                        valid_emails.append(email.lower())
                
                context.user_data['registration']['emails'] = valid_emails[:6]  # حد أقصى 6
            
            message_obj = message
        
        context.user_data['registration']['step'] = 8
        
        # حفظ تلقائي
        await self._auto_save_step(context.user_data['registration'])
        
        # عرض ملخص البيانات للتأكيد
        reg_data = context.user_data['registration']
        
        # إخفاء رقم البطاقة
        card_masked = reg_data['card_number'][:4] + "****" + reg_data['card_number'][-4:]
        
        summary_text = f"""
✅ **تم جمع جميع البيانات!**

📊 **ملخص بياناتك:**

🎮 **المنصة:** {reg_data['platform'].title()}
📱 **واتساب:** {reg_data['whatsapp']}
💳 **طريقة الدفع:** {reg_data['payment_method'].replace('_', ' ').title()}
📞 **الهاتف:** {reg_data['phone']}
💳 **البطاقة:** {card_masked}
🔗 **انستا باي:** {reg_data.get('instapay_link', 'لا يوجد')}
📧 **الإيميلات:** {', '.join(reg_data.get('emails', [])) if reg_data.get('emails') else 'لا يوجد'}

**هل تريد حفظ هذه البيانات؟**
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد وحفظ", callback_data="confirm_save"),
                InlineKeyboardButton("✏️ تعديل", callback_data="edit_data")
            ],
            [InlineKeyboardButton("❌ إلغاء", callback_data="cancel_registration")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await query.edit_message_text(
                summary_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await message_obj.reply_text(
                summary_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        return CONFIRM_DATA
    
    async def confirm_save(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد وحفظ البيانات"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel_registration":
            await query.edit_message_text("❌ تم إلغاء التسجيل")
            return ConversationHandler.END
        
        if query.data == "edit_data":
            await query.edit_message_text("✏️ ميزة التعديل قيد التطوير...")
            return ConversationHandler.END
        
        if query.data == "confirm_save":
            # حفظ البيانات في قاعدة البيانات
            reg_data = context.user_data['registration']
            reg_data['created_at'] = datetime.now().isoformat()
            
            try:
                user_id = await self.db.save_user(reg_data)
                
                success_text = f"""
🎉 **تهانينا! تم تسجيل حسابك بنجاح!**

✅ أصبحت الآن عضواً في عائلة FC 26

**معلوماتك:**
🆔 رقم العضوية: #{user_id}
🎮 المنصة: {reg_data['platform'].title()}
📱 واتساب: {reg_data['whatsapp']}

**ماذا الآن؟**
• يمكنك شراء أو بيع الكوينز مباشرة
• تابع العروض اليومية
• احصل على خصومات حصرية

**للبدء:**
/prices - عرض الأسعار
/buy - شراء كوينز
/sell - بيع كوينز
/profile - عرض حسابك

مرحباً بك في عالم FC 26! 🎮⚽
"""
                
                keyboard = [
                    [
                        InlineKeyboardButton("💰 شراء كوينز", callback_data="buy_coins"),
                        InlineKeyboardButton("💸 بيع كوينز", callback_data="sell_coins")
                    ],
                    [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
                ]
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    success_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                # تسجيل النشاط
                await self.db.log_activity(
                    reg_data['telegram_id'],
                    "registration_completed",
                    f"User completed registration successfully"
                )
                
                logger.info(f"✅ User {reg_data['username']} completed registration")
                
            except Exception as e:
                logger.error(f"Error saving user: {e}")
                await query.edit_message_text(
                    "❌ حدث خطأ في حفظ البيانات. الرجاء المحاولة مرة أخرى."
                )
            
            return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء التسجيل"""
        await update.message.reply_text(
            "❌ تم إلغاء التسجيل. يمكنك البدء مجدداً بالضغط على /start"
        )
        return ConversationHandler.END
    
    async def _auto_save_step(self, data):
        """حفظ تلقائي لكل خطوة"""
        try:
            # حفظ البيانات مؤقتاً في قاعدة البيانات
            await self.db.save_temp_registration(data)
            logger.info(f"📝 Auto-saved step {data.get('step')} for user {data.get('telegram_id')}")
        except Exception as e:
            logger.error(f"Error auto-saving: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج عام للرسائل"""
        await update.message.reply_text(
            "للبدء في استخدام البوت، اضغط /start"
        )
    
    def get_conversation_handler(self):
        """إرجاع معالج المحادثة"""
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start_registration, pattern="^register_start$"),
                CommandHandler("register", self.start_registration)
            ],
            states={
                PLATFORM: [CallbackQueryHandler(self.platform_choice, pattern="^platform_|cancel_registration$")],
                WHATSAPP: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.whatsapp_number)],
                PAYMENT_METHOD: [CallbackQueryHandler(self.payment_choice, pattern="^pay_|cancel_registration$")],
                PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.phone_number)],
                CARD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.card_number_input)],
                INSTAPAY_LINK: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.instapay_link_input),
                    CallbackQueryHandler(self.instapay_link_input, pattern="^skip_instapay$")
                ],
                EMAILS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.emails_input),
                    CallbackQueryHandler(self.emails_input, pattern="^skip_emails$")
                ],
                CONFIRM_DATA: [CallbackQueryHandler(self.confirm_save, pattern="^confirm_save|edit_data|cancel_registration$")]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )