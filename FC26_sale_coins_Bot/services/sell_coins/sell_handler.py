# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎯 FC26 COIN SELLING HANDLER - معالج بيع الكوينز            ║
# ║                    Main Coin Selling Handler                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from typing import Dict, List, Optional
import re
import logging

from .sell_pricing import CoinSellPricing, Platform
from .sell_messages import SellMessages
from .sell_keyboards import SellKeyboards

# استيراد الأدوات المساعدة من البوت الرئيسي
from utils.logger import log_user_action
from database.operations import UserOperations

logger = logging.getLogger(__name__)

class SellCoinsHandler:
    """معالج خدمة بيع الكوينز الرئيسي"""
    
    def __init__(self):
        """تهيئة معالج البيع"""
        self.user_sessions = {}  # جلسات المستخدمين النشطة
        self.pending_sales = {}  # البيوعات المعلقة
    
    def get_handlers(self) -> List:
        """جلب جميع معالجات خدمة البيع"""
        return [
            CommandHandler("sell", self.handle_sell_command),
            CallbackQueryHandler(self.handle_platform_selection, pattern="^sell_platform_"),
            CallbackQueryHandler(self.handle_package_selection, pattern="^sell_package_"),
            CallbackQueryHandler(self.handle_custom_amount, pattern="^sell_custom_"),
            CallbackQueryHandler(self.handle_price_confirmation, pattern="^sell_confirm_"),
            CallbackQueryHandler(self.handle_sale_instructions, pattern="^sell_ready_"),
            CallbackQueryHandler(self.handle_payment_selection, pattern="^sell_payment_"),
            CallbackQueryHandler(self.handle_navigation, pattern="^sell_back_"),
            CallbackQueryHandler(self.handle_help, pattern="^sell_help"),
            CallbackQueryHandler(self.handle_cancel, pattern="^sell_cancel"),
            CallbackQueryHandler(self.handle_support, pattern="^sell_support"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input)
        ]
    
    async def handle_sell_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر /sell"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Started coin selling service")
        
        # التحقق من تسجيل المستخدم
        user_data = UserOperations.get_user_data(user_id)
        if not user_data:
            await update.message.reply_text(
                "❌ <b>يجب التسجيل أولاً!</b>\n\n🚀 استخدم /start للتسجيل قبل بيع الكوينز",
                parse_mode="HTML"
            )
            return
        
        # بدء جلسة بيع جديدة
        self.user_sessions[user_id] = {
            'step': 'platform_selection',
            'platform': None,
            'coins': None,
            'price': None,
            'started_at': update.message.date
        }
        
        # عرض رسالة الترحيب
        welcome_message = SellMessages.get_welcome_sell_message()
        keyboard = SellKeyboards.get_main_sell_keyboard()
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_platform_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار المنصة"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        # استخراج المنصة من callback_data
        platform = query.data.replace("sell_platform_", "")
        
        # حفظ المنصة في الجلسة
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        
        self.user_sessions[user_id].update({
            'step': 'package_selection',
            'platform': platform
        })
        
        log_user_action(user_id, f"Selected platform: {platform}")
        
        # عرض باقات المنصة
        packages_message = SellMessages.get_packages_message(platform)
        keyboard = SellKeyboards.get_platform_packages_keyboard(platform)
        
        await query.edit_message_text(
            packages_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_package_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار الباقة"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        # استخراج البيانات من callback_data
        # تنسيق: sell_package_{platform}_{coins}
        parts = query.data.split("_")
        if len(parts) >= 4:
            platform = parts[2]
            coins = int(parts[3])
            
            # حساب السعر
            price = CoinSellPricing.get_price(platform, coins)
            if not price:
                await query.edit_message_text(
                    SellMessages.get_error_message('system_error'),
                    reply_markup=SellKeyboards.get_error_keyboard(),
                    parse_mode="HTML"
                )
                return
            
            # حفظ البيانات في الجلسة
            self.user_sessions[user_id].update({
                'step': 'price_confirmation',
                'coins': coins,
                'price': price
            })
            
            log_user_action(user_id, f"Selected package: {coins} coins for {price} EGP")
            
            # عرض تأكيد السعر
            confirmation_message = SellMessages.get_price_confirmation_message(platform, coins, price)
            keyboard = SellKeyboards.get_price_confirmation_keyboard(platform, coins, price)
            
            await query.edit_message_text(
                confirmation_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    
    async def handle_custom_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب كمية مخصصة"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        # استخراج المنصة
        platform = query.data.replace("sell_custom_", "")
        
        # تحديث الجلسة
        self.user_sessions[user_id].update({
            'step': 'custom_amount_input',
            'platform': platform
        })
        
        log_user_action(user_id, f"Requested custom amount for {platform}")
        
        # عرض رسالة طلب الكمية المخصصة
        custom_message = SellMessages.get_custom_amount_message(platform)
        keyboard = SellKeyboards.get_custom_amount_cancel_keyboard(platform)
        
        await query.edit_message_text(
            custom_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة النص المُدخل (للكمية المخصصة)"""
        user_id = update.effective_user.id
        
        # التحقق من وجود جلسة نشطة
        if user_id not in self.user_sessions:
            return
        
        session = self.user_sessions[user_id]
        
        # التحقق من الخطوة الحالية
        if session.get('step') != 'custom_amount_input':
            return
        
        text = update.message.text.strip()
        platform = session.get('platform')
        
        # التحقق من صحة الإدخال
        try:
            coins = int(text)
        except ValueError:
            await update.message.reply_text(
                SellMessages.get_error_message('invalid_amount'),
                parse_mode="HTML"
            )
            return
        
        # التحقق من صحة الكمية
        is_valid, validation_message = CoinSellPricing.validate_coin_amount(coins)
        if not is_valid:
            await update.message.reply_text(
                validation_message,
                parse_mode="HTML"
            )
            return
        
        # حساب السعر للكمية المخصصة
        price = CoinSellPricing.calculate_custom_price(platform, coins)
        if not price:
            await update.message.reply_text(
                SellMessages.get_error_message('system_error'),
                parse_mode="HTML"
            )
            return
        
        # تحديث الجلسة
        session.update({
            'step': 'price_confirmation',
            'coins': coins,
            'price': price
        })
        
        log_user_action(user_id, f"Entered custom amount: {coins} coins for {price} EGP")
        
        # عرض تأكيد السعر
        confirmation_message = SellMessages.get_price_confirmation_message(platform, coins, price)
        keyboard = SellKeyboards.get_price_confirmation_keyboard(platform, coins, price)
        
        await update.message.reply_text(
            confirmation_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_price_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة تأكيد السعر"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        # استخراج البيانات من callback_data
        # تنسيق: sell_confirm_{platform}_{coins}_{price}
        parts = query.data.split("_")
        if len(parts) >= 5:
            platform = parts[2]
            coins = int(parts[3])
            price = int(parts[4])
            
            # تحديث الجلسة
            self.user_sessions[user_id].update({
                'step': 'sale_instructions',
                'platform': platform,
                'coins': coins,
                'price': price
            })
            
            log_user_action(user_id, f"Confirmed sale: {coins} coins for {price} EGP")
            
            # عرض تعليمات البيع
            instructions_message = SellMessages.get_sale_instructions_message(platform, coins)
            keyboard = SellKeyboards.get_sale_instructions_keyboard(platform, coins)
            
            await query.edit_message_text(
                instructions_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    
    async def handle_sale_instructions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الموافقة على تعليمات البيع"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        session = self.user_sessions.get(user_id, {})
        
        # إنشاء طلب بيع
        sale_id = self._create_sale_request(user_id, session)
        
        log_user_action(user_id, f"Started sale process, sale_id: {sale_id}")
        
        # عرض اختيار طريقة الدفع
        payment_message = "💳 <b>اختر طريقة الدفع المفضلة:</b>\n\n" + \
                         "ستستلم أموالك على الطريقة المختارة فور إتمام البيع"
        keyboard = SellKeyboards.get_payment_method_keyboard()
        
        await query.edit_message_text(
            payment_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_payment_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار طريقة الدفع"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        # استخراج طريقة الدفع
        payment_method = query.data.replace("sell_payment_", "")
        
        # حفظ طريقة الدفع في الجلسة
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['payment_method'] = payment_method
        
        log_user_action(user_id, f"Selected payment method: {payment_method}")
        
        # عرض رسالة نجاح البدء
        success_message = """✅ <b>تم بدء عملية البيع بنجاح!</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 <b>الخطوات التالية:</b>

1️⃣ سيتواصل معك فريق الدعم خلال 5 دقائق
2️⃣ سيتم إرشادك لتنفيذ التعليمات  
3️⃣ ستستلم أموالك فور التأكد من الكوينز

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ <b>وقت الاستجابة:</b> 5-10 دقائق كحد أقصى
📞 <b>للاستعجال:</b> تواصل مع الدعم الفني

🎉 <b>شكراً لثقتك في FC26!</b>"""

        keyboard = SellKeyboards.get_sale_progress_keyboard()
        
        await query.edit_message_text(
            success_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_navigation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة التنقل بين الصفحات"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        action = query.data.replace("sell_back_", "")
        
        if action == "main":
            # العودة للقائمة الرئيسية
            welcome_message = SellMessages.get_welcome_sell_message()
            keyboard = SellKeyboards.get_main_sell_keyboard()
            
            await query.edit_message_text(
                welcome_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
        elif action == "platforms":
            # العودة لاختيار المنصة
            platform_message = SellMessages.get_platform_selection_message()
            keyboard = SellKeyboards.get_main_sell_keyboard()
            
            await query.edit_message_text(
                platform_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
        elif action.startswith("packages_"):
            # العودة لباقات المنصة
            platform = action.replace("packages_", "")
            packages_message = SellMessages.get_packages_message(platform)
            keyboard = SellKeyboards.get_platform_packages_keyboard(platform)
            
            await query.edit_message_text(
                packages_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب المساعدة"""
        query = update.callback_query
        await query.answer()
        
        help_message = SellMessages.get_help_message()
        keyboard = SellKeyboards.get_help_keyboard()
        
        await query.edit_message_text(
            help_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إلغاء البيع"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        # إزالة الجلسة
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        log_user_action(user_id, "Cancelled coin selling")
        
        cancel_message = SellMessages.get_error_message('sale_cancelled')
        keyboard = SellKeyboards.get_error_keyboard()
        
        await query.edit_message_text(
            cancel_message,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة طلب الدعم الفني"""
        query = update.callback_query
        await query.answer()
        
        support_message = """📞 <b>الدعم الفني FC26</b>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 <b>متوفر 24/7 لخدمتك</b>

📱 <b>طرق التواصل:</b>
• الدردشة المباشرة في البوت
• واتساب: متوفر في ملفك الشخصي
• رسائل خاصة

⚡ <b>استجابة سريعة:</b> خلال دقائق معدودة

نحن هنا لمساعدتك! 🤝"""
        
        await query.edit_message_text(
            support_message,
            parse_mode="HTML"
        )
    
    def _create_sale_request(self, user_id: int, session: Dict) -> str:
        """إنشاء طلب بيع جديد"""
        import time
        
        sale_id = f"SALE_{user_id}_{int(time.time())}"
        
        # حفظ طلب البيع
        self.pending_sales[sale_id] = {
            'user_id': user_id,
            'platform': session.get('platform'),
            'coins': session.get('coins'),
            'price': session.get('price'),
            'status': 'pending',
            'created_at': time.time()
        }
        
        return sale_id
    
    def get_user_session(self, user_id: int) -> Optional[Dict]:
        """جلب جلسة المستخدم"""
        return self.user_sessions.get(user_id)
    
    def clear_user_session(self, user_id: int):
        """مسح جلسة المستخدم"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]