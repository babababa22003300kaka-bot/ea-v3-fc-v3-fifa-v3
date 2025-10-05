# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💰 SELL COINS - CONVERSATION HANDLER                        ║
# ║                   خدمة بيع الكوينز - ConversationHandler                ║
# ║                  🔥 WITH MESSAGE TAGGING SYSTEM 🔥                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
خدمة بيع الكوينز باستخدام ConversationHandler
- معزولة تماماً عن باقي الخدمات
- بدون تضارب نهائياً
- 🏷️ نظام وسم الرسائل لمنع الردود المزدوجة
- 🔥 EXCLUSIVE CONSUMPTION MODE (block=True INSIDE)
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
from utils.message_tagger import MessageTagger  # 🔥 النظام الجديد

from .sell_pricing import CoinSellPricing

# ═══════════════════════════════════════════════════════════════════════════
# STATES
# ═══════════════════════════════════════════════════════════════════════════

SELL_PLATFORM, SELL_TYPE, SELL_AMOUNT = range(3)


class SellCoinsConversation:
    """معالج بيع الكوينز - ConversationHandler مع نظام الوسم"""

    # ═══════════════════════════════════════════════════════════════════════
    # ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def start_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء عملية البيع - /sell"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        log_user_action(user_id, "Started coin selling service")

        print(f"\n💰 [SELL] Service started for user {user_id}")

        # التحقق من التسجيل
        user_data = UserOperations.get_user_data(user_id)
        if not user_data or user_data.get("registration_step") != "completed":
            await update.message.reply_text(
                "❌ <b>يجب إكمال التسجيل أولاً!</b>\n\n🚀 /start للتسجيل",
                parse_mode="HTML",
            )
            return ConversationHandler.END

        # عرض اختيار المنصة
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎮 PlayStation", callback_data="sell_platform_playstation"
                )
            ],
            [InlineKeyboardButton("🎮 Xbox", callback_data="sell_platform_xbox")],
            [InlineKeyboardButton("🖥️ PC", callback_data="sell_platform_pc")],
            [InlineKeyboardButton("❌ إلغاء", callback_data="sell_cancel")],
        ]

        await update.message.reply_text(
            "💰 <b>بيع الكوينز</b>\n\n🎮 اختر منصتك:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

        return SELL_PLATFORM

    # ═══════════════════════════════════════════════════════════════════════
    # STATE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def choose_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار المنصة"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        if query.data == "sell_cancel":
            await query.edit_message_text("❌ تم إلغاء عملية البيع")
            return ConversationHandler.END

        user_id = query.from_user.id
        platform = query.data.replace("sell_platform_", "")

        print(f"🎮 [SELL] User {user_id} selected platform: {platform}")

        # حفظ المنصة
        context.user_data["sell_platform"] = platform
        log_user_action(user_id, f"Selected platform: {platform}")

        # عرض أنواع التحويل مع الأسعار
        transfer_message = CoinSellPricing.get_platform_pricing_message(platform)

        # جلب أسعار 1M
        normal_price = CoinSellPricing.get_price(platform, 1000000, "normal")
        instant_price = CoinSellPricing.get_price(platform, 1000000, "instant")

        normal_formatted = f"{normal_price:,} ج.م" if normal_price else "غير متاح"
        instant_formatted = f"{instant_price:,} ج.م" if instant_price else "غير متاح"

        keyboard = [
            [
                InlineKeyboardButton(
                    f"📅 تحويل عادي - {normal_formatted}",
                    callback_data=f"sell_type_normal",
                )
            ],
            [
                InlineKeyboardButton(
                    f"⚡ تحويل فوري - {instant_formatted}",
                    callback_data=f"sell_type_instant",
                )
            ],
            [InlineKeyboardButton("🔙 رجوع", callback_data="sell_back")],
        ]

        await query.edit_message_text(
            transfer_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

        return SELL_TYPE

    @staticmethod
    async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختيار نوع التحويل"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        if query.data == "sell_back":
            # رجوع لاختيار المنصة
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎮 PlayStation", callback_data="sell_platform_playstation"
                    )
                ],
                [InlineKeyboardButton("🎮 Xbox", callback_data="sell_platform_xbox")],
                [InlineKeyboardButton("🖥️ PC", callback_data="sell_platform_pc")],
                [InlineKeyboardButton("❌ إلغاء", callback_data="sell_cancel")],
            ]

            await query.edit_message_text(
                "💰 <b>بيع الكوينز</b>\n\n🎮 اختر منصتك:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )
            return SELL_PLATFORM

        user_id = query.from_user.id
        transfer_type = query.data.replace("sell_type_", "")
        platform = context.user_data.get("sell_platform", "unknown")

        print(f"⚡ [SELL] User {user_id} selected type: {transfer_type}")

        # حفظ النوع
        context.user_data["sell_type"] = transfer_type
        log_user_action(
            user_id, f"Selected transfer type: {transfer_type} for {platform}"
        )

        # طلب إدخال الكمية
        platform_name = {
            "playstation": "🎮 PlayStation",
            "xbox": "🎮 Xbox",
            "pc": "🖥️ PC",
        }.get(platform, platform)

        transfer_name = "⚡ فوري" if transfer_type == "instant" else "📅 عادي"

        await query.edit_message_text(
            f"✅ **تم اختيار {platform_name} - {transfer_name}**\n\n"
            f"💰 **أدخل كمية الكوينز للبيع:**\n\n"
            f"📝 **قواعد الإدخال:**\n"
            f"• أرقام فقط (بدون حروف أو رموز)\n"
            f"• الحد الأدنى: 50 كوين\n"
            f"• الحد الأقصى: 20,000 كوين\n\n"
            f"💡 **مثال:** 500 أو 1500 أو 5000\n\n"
            f"اكتب الكمية بالأرقام:\n\n"
            f"❌ للإلغاء: /cancel",
            parse_mode="Markdown",
        )

        return SELL_AMOUNT

    @staticmethod
    async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إدخال الكمية"""
        # 🏷️ وسم الرسالة - الأهم!
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        text = update.message.text.strip()

        print(f"💰 [SELL] Amount input from user {user_id}: {text}")

        # التحقق من الصيغة
        if not text.isdigit():
            print(f"   ❌ [SELL] Invalid format: {text}")
            await update.message.reply_text(
                "❌ **صيغة غير صحيحة!**\n\n"
                "✅ **المطلوب:** أرقام فقط\n"
                "🚫 **ممنوع:** حروف، رموز، k، m\n\n"
                "يرجى إدخال الكمية بالأرقام:",
                parse_mode="Markdown",
            )
            return SELL_AMOUNT

        amount = int(text)

        # التحقق من الحدود
        if amount < 50:
            print(f"   ❌ [SELL] Amount too low: {amount}")
            await update.message.reply_text(
                f"❌ **الكمية قليلة جداً!**\n\n"
                f"📍 **الحد الأدنى:** 50 كوين\n"
                f"أنت أدخلت: {amount} كوين\n\n"
                f"يرجى إدخال كمية أكبر:",
                parse_mode="Markdown",
            )
            return SELL_AMOUNT

        if amount > 20000:
            print(f"   ❌ [SELL] Amount too high: {amount}")
            await update.message.reply_text(
                f"❌ **الكمية كبيرة جداً!**\n\n"
                f"📍 **الحد الأقصى:** 20,000 كوين\n"
                f"أنت أدخلت: {amount:,} كوين\n\n"
                f"لبيع كميات أكبر، يرجى التواصل مع الدعم.",
                parse_mode="Markdown",
            )
            return SELL_AMOUNT

        # حساب السعر
        platform = context.user_data.get("sell_platform", "playstation")
        transfer_type = context.user_data.get("sell_type", "normal")

        price = SellCoinsConversation.calculate_price(amount, transfer_type)

        print(f"✅ [SELL] Valid amount: {amount}, calculated price: {price}")

        # رسالة التأكيد
        platform_name = {
            "playstation": "🎮 PlayStation",
            "xbox": "🎮 Xbox",
            "pc": "🖥️ PC",
        }.get(platform, platform)

        transfer_name = "⚡ فوري" if transfer_type == "instant" else "📅 عادي"

        # جلب سعر المليون كمرجع
        million_price = CoinSellPricing.get_price(platform, 1000000, transfer_type)
        if million_price is None:
            default_prices = {
                "normal": {"playstation": 5600, "xbox": 5600, "pc": 6100},
                "instant": {"playstation": 5300, "xbox": 5300, "pc": 5800},
            }
            million_price = default_prices.get(transfer_type, {}).get(platform, 5600)

        await update.message.reply_text(
            f"🎉 **تم تأكيد طلب البيع بنجاح!**\n\n"
            f"📊 **تفاصيل الطلب:**\n"
            f"🎮 المنصة: {platform_name}\n"
            f"💰 الكمية: {amount:,} كوين\n"
            f"💵 السعر: {price} جنيه\n"
            f"⭐ (سعر المليون: {million_price:,} جنيه)\n"
            f"⏰ نوع التحويل: {transfer_name}\n\n"
            f"📞 **الخطوات التالية:**\n"
            f"1️⃣ سيتم التواصل معك خلال دقائق\n"
            f"2️⃣ تسليم الكوينز للممثل\n"
            f"3️⃣ استلام المبلغ حسب نوع التحويل\n\n"
            f"✅ **تم حفظ طلبك في النظام**\n"
            f"🆔 **رقم الطلب:** #{user_id}{amount}\n\n"
            f"💬 **للاستفسار:** /sell\n"
            f"🏠 **القائمة الرئيسية:** /start",
            parse_mode="Markdown",
        )

        log_user_action(
            user_id,
            f"Completed sell order: {amount} coins, {transfer_type}, {price} EGP",
        )

        # مسح البيانات
        context.user_data.clear()
        print(f"🧹 [SELL] Session cleared for user {user_id}")

        return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════════════
    # FALLBACKS
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء العملية"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        print(f"❌ [SELL] User {user_id} cancelled sell service")

        await update.message.reply_text(
            "❌ تم إلغاء عملية البيع\n\n🔹 /sell للبدء من جديد"
        )

        context.user_data.clear()
        log_user_action(user_id, "Cancelled coin selling")

        return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def calculate_price(amount: int, transfer_type: str = "normal") -> int:
        """حساب السعر حسب الكمية ونوع التحويل"""
        base_price_per_1000 = 5  # 5 جنيه لكل 1000 كوين

        # حساب السعر الأساسي
        base_price = (amount / 1000) * base_price_per_1000

        # إضافة رسوم حسب نوع التحويل
        if transfer_type == "instant":
            base_price *= 1.2  # زيادة 20% للتحويل الفوري

        return int(base_price)

    # ═══════════════════════════════════════════════════════════════════════
    # CONVERSATION HANDLER - 🔥 WITH block=True INSIDE 🔥
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def get_conversation_handler():
        """إنشاء ConversationHandler للخدمة - مع block=True بالداخل"""
        return ConversationHandler(
            entry_points=[CommandHandler("sell", SellCoinsConversation.start_sell)],
            states={
                SELL_PLATFORM: [
                    CallbackQueryHandler(
                        SellCoinsConversation.choose_platform,
                        pattern="^sell_platform_|^sell_cancel$",
                    )
                ],
                SELL_TYPE: [
                    CallbackQueryHandler(
                        SellCoinsConversation.choose_type,
                        pattern="^sell_type_|^sell_back$",
                    )
                ],
                SELL_AMOUNT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        SellCoinsConversation.enter_amount,
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", SellCoinsConversation.cancel)],
            name="sell_coins_conversation",
            persistent=False,
            block=True,  # 🔥 المكان الصحيح!
        )
