# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    🎯 SERVICE TEMPLATE - قالب الخدمات                    ║
# ║              Universal Template for Adding New Services                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
Template لإضافة خدمة جديدة بدون تضارب نهائياً

📝 كيفية الاستخدام:
1. انسخ هذا الملف → `services/my_service.py`
2. غيّر اسم الـ Class → `MyService`
3. غيّر الـ States → حسب خدمتك
4. اكتب الـ handlers
5. سجّل في main.py

✅ مضمون 100% بدون تضارب!
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from database.operations import UserOperations
from utils.logger import log_user_action

# ═══════════════════════════════════════════════════════════════════════════
# STATES - حدد حالات خدمتك
# ═══════════════════════════════════════════════════════════════════════════

# مثال: خدمة شراء الكوينز
BUY_PLATFORM, BUY_AMOUNT, BUY_PAYMENT = range(3)


class BuyCoinsService:
    """
    مثال على خدمة جديدة - شراء الكوينز

    📝 لإنشاء خدمة جديدة:
    1. غيّر اسم الـ Class
    2. غيّر الـ States
    3. غيّر entry_points (/buy → /yourcommand)
    4. عدّل الـ handlers حسب احتياجك
    """

    # ═══════════════════════════════════════════════════════════════════════
    # ENTRY POINT - نقطة البداية
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def start_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        نقطة البداية - /buy

        هنا تبدأ الخدمة عند كتابة الأمر
        """
        user_id = update.effective_user.id

        print(f"💰 [BUY] Service started for user {user_id}")
        log_user_action(user_id, "Started buy coins service")

        # التحقق من التسجيل (اختياري)
        user_data = UserOperations.get_user_data(user_id)
        if not user_data or user_data.get("registration_step") != "completed":
            await update.message.reply_text(
                "❌ <b>يجب إكمال التسجيل أولاً!</b>\n\n🚀 /start للتسجيل",
                parse_mode="HTML",
            )
            return ConversationHandler.END

        # عرض الخيارات الأولى
        keyboard = [
            [InlineKeyboardButton("🎮 PlayStation", callback_data="buy_ps")],
            [InlineKeyboardButton("🎮 Xbox", callback_data="buy_xbox")],
            [InlineKeyboardButton("🖥️ PC", callback_data="buy_pc")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="buy_cancel")],
        ]

        await update.message.reply_text(
            "💰 <b>شراء الكوينز</b>\n\n🎮 اختر منصتك:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

        return BUY_PLATFORM

    # ═══════════════════════════════════════════════════════════════════════
    # STATE HANDLERS - معالجات الحالات
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def choose_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الحالة الأولى - اختيار المنصة"""
        query = update.callback_query
        await query.answer()

        # معالجة الإلغاء
        if query.data == "buy_cancel":
            await query.edit_message_text("❌ تم إلغاء عملية الشراء")
            return ConversationHandler.END

        user_id = query.from_user.id
        platform = query.data.replace("buy_", "")

        # حفظ البيانات في context
        context.user_data["buy_platform"] = platform

        print(f"🎮 [BUY] User {user_id} selected: {platform}")
        log_user_action(user_id, f"Selected platform: {platform}")

        # الانتقال للحالة التالية
        await query.edit_message_text(
            f"✅ اخترت: {platform}\n\n💰 أدخل الكمية (بالأرقام):",
            parse_mode="HTML",
        )

        return BUY_AMOUNT

    @staticmethod
    async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الحالة الثانية - إدخال الكمية"""
        user_id = update.effective_user.id
        text = update.message.text.strip()

        # التحقق من المدخلات
        if not text.isdigit():
            await update.message.reply_text("❌ أرقام فقط! أعد المحاولة:")
            return BUY_AMOUNT

        amount = int(text)

        # التحقق من الحدود
        if amount < 100:
            await update.message.reply_text("❌ الحد الأدنى: 100 كوين\nأعد المحاولة:")
            return BUY_AMOUNT

        # حفظ البيانات
        context.user_data["buy_amount"] = amount

        print(f"💰 [BUY] User {user_id} amount: {amount}")

        # الانتقال للحالة التالية
        await update.message.reply_text(
            f"✅ الكمية: {amount:,} كوين\n\n💳 أدخل طريقة الدفع:",
            parse_mode="HTML",
        )

        return BUY_PAYMENT

    @staticmethod
    async def enter_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الحالة الثالثة (الأخيرة) - إدخال الدفع"""
        user_id = update.effective_user.id
        payment = update.message.text.strip()

        # جلب البيانات المحفوظة
        platform = context.user_data.get("buy_platform", "unknown")
        amount = context.user_data.get("buy_amount", 0)

        # حفظ البيانات (في قاعدة بيانات مثلاً)
        # YourDatabase.save_buy_order(user_id, platform, amount, payment)

        # رسالة النجاح
        await update.message.reply_text(
            f"✅ <b>تم تأكيد طلب الشراء!</b>\n\n"
            f"🎮 المنصة: {platform}\n"
            f"💰 الكمية: {amount:,} كوين\n"
            f"💳 الدفع: {payment}\n\n"
            f"📞 سيتم التواصل معك قريباً!\n\n"
            f"🔹 /buy للشراء مرة أخرى",
            parse_mode="HTML",
        )

        log_user_action(
            user_id,
            f"Completed buy order: {amount} coins, platform: {platform}",
        )

        # مسح البيانات
        context.user_data.clear()
        print(f"✅ [BUY] Order completed for user {user_id}")

        # إنهاء المحادثة
        return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════════════
    # FALLBACKS - معالجات الإلغاء
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء العملية في أي وقت - /cancel"""
        user_id = update.effective_user.id

        print(f"❌ [BUY] User {user_id} cancelled")
        log_user_action(user_id, "Cancelled buy service")

        await update.message.reply_text(
            "❌ تم إلغاء عملية الشراء\n\n🔹 /buy للبدء من جديد"
        )

        context.user_data.clear()
        return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════════════
    # CONVERSATION HANDLER - التسجيل
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def get_conversation_handler():
        """
        إنشاء ConversationHandler للخدمة

        📝 هذا هو الجزء الوحيد اللي هتسجله في main.py
        """
        return ConversationHandler(
            # نقطة البداية - الأمر اللي يبدأ الخدمة
            entry_points=[CommandHandler("buy", BuyCoinsService.start_buy)],
            # الحالات - كل حالة ليها handlers خاصة
            states={
                BUY_PLATFORM: [
                    CallbackQueryHandler(
                        BuyCoinsService.choose_platform,
                        pattern="^buy_",  # فقط callbacks تبدأ بـ buy_
                    )
                ],
                BUY_AMOUNT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BuyCoinsService.enter_amount,
                    )
                ],
                BUY_PAYMENT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        BuyCoinsService.enter_payment,
                    )
                ],
            },
            # معالجات الإلغاء - تشتغل في أي حالة
            fallbacks=[CommandHandler("cancel", BuyCoinsService.cancel)],
            # اسم فريد للخدمة
            name="buy_coins_conversation",
            # حفظ الحالة (True = يحفظ الحالة حتى لو البوت توقف)
            persistent=False,
        )


# ═══════════════════════════════════════════════════════════════════════════
# كيفية التسجيل في main.py:
# ═══════════════════════════════════════════════════════════════════════════
"""
في ملف main.py، في method start_bot():

# 1. استورد الخدمة
from services.service_template import BuyCoinsService

# 2. سجّل الـ conversation
buy_conv = BuyCoinsService.get_conversation_handler()
self.app.add_handler(buy_conv)
print("✅ [4] Buy coins conversation registered")

✅ خلاص! مافيش تضارب أبداً!
"""
