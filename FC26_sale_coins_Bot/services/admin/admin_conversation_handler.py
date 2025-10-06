# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              👑 ADMIN - CONVERSATION HANDLER                             ║
# ║                   خدمة الأدمن - مع bucket و persistence                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
خدمة الأدمن باستخدام ConversationHandler
- مع نظام وسم الرسائل (MessageTagger)
- مع نظام عزل البيانات (Session Buckets)
- مع Persistence
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

from database.admin_operations import AdminOperations
from utils.message_tagger import MessageTagger
from utils.session_bucket import bucket, clear_bucket

# 🔥 نظام الرسائل النشطة - Active Message System
from utils.active_message_helper import send_or_edit, clear_active_message

from .price_management import PriceManagement

# ═══════════════════════════════════════════════════════════════════════════
# STATES
# ═══════════════════════════════════════════════════════════════════════════

ADMIN_MAIN, ADMIN_PRICES, ADMIN_PLATFORM, ADMIN_PRICE_INPUT = range(4)


class AdminConversation:
    """معالج الأدمن - مع bucket"""

    ADMIN_ID = 1124247595

    @staticmethod
    async def start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء لوحة الأدمن - /admin"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"

        print(f"\n👑 [ADMIN] Admin command from user {user_id} (@{username})")

        if user_id != AdminConversation.ADMIN_ID:
            print(f"❌ [ADMIN] Unauthorized access by {user_id}")
            await send_or_edit(context, update.effective_chat.id, "❌ غير مصرح لك بالوصول لهذه الخدمة!")
            return ConversationHandler.END

        AdminOperations.log_admin_action(user_id, "ADMIN_LOGIN", "Accessed via /admin")
        print(f"✅ [ADMIN] Admin {user_id} logged in")

        keyboard = [
            [InlineKeyboardButton("💰 إدارة الأسعار", callback_data="admin_prices")],
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
            [InlineKeyboardButton("❌ خروج", callback_data="admin_exit")],
        ]

        await send_or_edit(context, update.effective_chat.id, f"👑 <b>لوحة الأدمن</b>\n\n" f"مرحباً @{username}\n\n" f"اختر الخدمة:", InlineKeyboardMarkup(keyboard))

        return ADMIN_MAIN

    @staticmethod
    async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة القائمة الرئيسية"""
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        if query.data == "admin_exit":
            await send_or_edit(context, update.effective_chat.id, "👋 تم الخروج من لوحة الأدمن")
            return ConversationHandler.END

        if query.data == "admin_prices":
            print(f"💰 [ADMIN] {user_id} accessing price management")
            AdminOperations.log_admin_action(user_id, "ACCESSED_PRICE_MANAGEMENT")

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎮 PlayStation", callback_data="admin_platform_playstation"
                    )
                ],
                [InlineKeyboardButton("🎮 Xbox", callback_data="admin_platform_xbox")],
                [InlineKeyboardButton("🖥️ PC", callback_data="admin_platform_pc")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back_main")],
            ]

            await send_or_edit(context, update.effective_chat.id, "💰 <b>إدارة الأسعار</b>\n\n🎮 اختر المنصة:", InlineKeyboardMarkup(keyboard))

            return ADMIN_PLATFORM

        if query.data == "admin_stats":
            await send_or_edit(context, update.effective_chat.id, "📊 <b>الإحصائيات</b>\n\nقريباً...")
            return ConversationHandler.END

        return ADMIN_MAIN

    @staticmethod
    async def handle_platform_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة اختيار المنصة"""
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        if query.data == "admin_back_main":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "💰 إدارة الأسعار", callback_data="admin_prices"
                    )
                ],
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
                [InlineKeyboardButton("❌ خروج", callback_data="admin_exit")],
            ]

            await send_or_edit(context, update.effective_chat.id, "👑 <b>لوحة الأدمن</b>\n\nاختر الخدمة:", InlineKeyboardMarkup(keyboard))

            return ADMIN_MAIN

        user_id = query.from_user.id
        platform = query.data.replace("admin_platform_", "")

        print(f"🎮 [ADMIN] {user_id} selected platform: {platform}")

        normal_price = PriceManagement.get_current_price(platform, "normal")
        instant_price = PriceManagement.get_current_price(platform, "instant")

        platform_name = {
            "playstation": "🎮 PlayStation",
            "xbox": "🎮 Xbox",
            "pc": "🖥️ PC",
        }.get(platform, platform)

        keyboard = [
            [
                InlineKeyboardButton(
                    f"📅 عادي - {normal_price:,} ج.م" if normal_price else "📅 عادي",
                    callback_data=f"admin_edit_{platform}_normal",
                )
            ],
            [
                InlineKeyboardButton(
                    f"⚡ فوري - {instant_price:,} ج.م" if instant_price else "⚡ فوري",
                    callback_data=f"admin_edit_{platform}_instant",
                )
            ],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back_platforms")],
        ]

        await send_or_edit(context, update.effective_chat.id, f"💰 <b>أسعار {platform_name}</b>\n\nاختر نوع التحويل:", InlineKeyboardMarkup(keyboard))

        return ADMIN_PLATFORM

    @staticmethod
    async def handle_transfer_type_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة اختيار نوع التحويل"""
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        if query.data == "admin_back_platforms":
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎮 PlayStation", callback_data="admin_platform_playstation"
                    )
                ],
                [InlineKeyboardButton("🎮 Xbox", callback_data="admin_platform_xbox")],
                [InlineKeyboardButton("🖥️ PC", callback_data="admin_platform_pc")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="admin_back_main")],
            ]

            await send_or_edit(context, update.effective_chat.id, "💰 <b>إدارة الأسعار</b>\n\n🎮 اختر المنصة:", InlineKeyboardMarkup(keyboard))

            return ADMIN_PLATFORM

        user_id = query.from_user.id

        parts = query.data.split("_")
        if len(parts) >= 4:
            platform = parts[2]
            transfer_type = parts[3]

            print(f"⚡ [ADMIN] {user_id} editing {platform} {transfer_type}")

            current_price = PriceManagement.get_current_price(platform, transfer_type)

            if current_price is None:
                await send_or_edit(context, update.effective_chat.id, "❌ خطأ في جلب السعر الحالي")
                return ConversationHandler.END

            # 🔥 استخدام bucket بدلاً من context.user_data
            admin_bucket = bucket(context, "admin")
            admin_bucket["platform"] = platform
            admin_bucket["type"] = transfer_type
            admin_bucket["current_price"] = current_price

            AdminOperations.log_admin_action(
                user_id,
                "STARTED_PRICE_EDIT",
                f"{platform} {transfer_type} - Current: {current_price}",
            )

            platform_name = {
                "playstation": "PlayStation",
                "xbox": "Xbox",
                "pc": "PC",
            }.get(platform, platform)

            transfer_name = "فوري" if transfer_type == "instant" else "عادي"

            await send_or_edit(context, update.effective_chat.id, f"💰 <b>تعديل سعر {platform_name} - {transfer_name}</b>\n\n"
                f"💵 السعر الحالي: {current_price:,} ج.م\n\n"
                f"📝 أدخل السعر الجديد:\n"
                f"• الحد الأدنى: 1,000 ج.م\n"
                f"• الحد الأقصى: 50,000 ج.م\n\n"
                f"❌ للإلغاء: /cancel")

            return ADMIN_PRICE_INPUT

        return ADMIN_PLATFORM

    @staticmethod
    async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال السعر"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        price_text = update.message.text.strip()

        print(f"💰 [ADMIN] Price input from {user_id}: {price_text}")

        if not price_text.isdigit():
            print(f"   ❌ [ADMIN] Invalid format")
            await send_or_edit(context, update.effective_chat.id, "❌ صيغة غير صحيحة! أدخل أرقاماً فقط")
            return ADMIN_PRICE_INPUT

        new_price = int(price_text)

        if new_price < 1000:
            print(f"   ❌ [ADMIN] Price too low: {new_price}")
            await send_or_edit(context, update.effective_chat.id, 
                f"❌ السعر قليل جداً! الحد الأدنى: 1,000 ج.م"
            )
            return ADMIN_PRICE_INPUT

        if new_price > 50000:
            print(f"   ❌ [ADMIN] Price too high: {new_price}")
            await send_or_edit(context, update.effective_chat.id, 
                f"❌ السعر عالي جداً! الحد الأقصى: 50,000 ج.م"
            )
            return ADMIN_PRICE_INPUT

        # 🔥 استخدام bucket
        admin_bucket = bucket(context, "admin")
        platform = admin_bucket.get("platform")
        transfer_type = admin_bucket.get("type")
        old_price = admin_bucket.get("current_price")

        print(
            f"🔄 [ADMIN] Updating {platform} {transfer_type}: {old_price} → {new_price}"
        )

        success = await PriceManagement.update_price(
            platform, transfer_type, new_price, user_id
        )

        if not success:
            await send_or_edit(context, update.effective_chat.id, "❌ حدث خطأ في تحديث السعر")
            return ConversationHandler.END

        platform_name = {
            "playstation": "PlayStation",
            "xbox": "Xbox",
            "pc": "PC",
        }.get(platform, platform)

        transfer_name = "فوري" if transfer_type == "instant" else "عادي"

        await send_or_edit(context, update.effective_chat.id, f"✅ <b>تم تحديث السعر بنجاح!</b>\n\n"
            f"🎮 المنصة: {platform_name}\n"
            f"⚡ النوع: {transfer_name}\n"
            f"💰 السعر القديم: {old_price:,} ج.م\n"
            f"💵 السعر الجديد: {new_price:,} ج.م\n\n"
            f"🔹 /admin للرجوع للوحة التحكم")

        # 🔥 مسح bucket فقط
        clear_bucket(context, "admin")
        print(f"✅ [ADMIN] Price updated successfully")

        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء العملية"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        print(f"❌ [ADMIN] {user_id} cancelled operation")

        await send_or_edit(context, update.effective_chat.id, 
            "❌ تم إلغاء العملية\n\n🔹 /admin للرجوع للوحة التحكم"
        )

        # 🔥 مسح bucket فقط
        clear_bucket(context, "admin")
        AdminOperations.log_admin_action(user_id, "CANCELLED_OPERATION")

        return ConversationHandler.END

    @staticmethod
    def get_conversation_handler():
        """إنشاء ConversationHandler للخدمة"""
        return ConversationHandler(
            entry_points=[CommandHandler("admin", AdminConversation.start_admin)],
            states={
                ADMIN_MAIN: [
                    CallbackQueryHandler(
                        AdminConversation.handle_main_menu,
                        pattern="^admin_prices$|^admin_stats$|^admin_exit$",
                    )
                ],
                ADMIN_PLATFORM: [
                    CallbackQueryHandler(
                        AdminConversation.handle_platform_selection,
                        pattern="^admin_platform_|^admin_back_main$",
                    ),
                    CallbackQueryHandler(
                        AdminConversation.handle_transfer_type_selection,
                        pattern="^admin_edit_|^admin_back_platforms$",
                    ),
                ],
                ADMIN_PRICE_INPUT: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        AdminConversation.handle_price_input,
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", AdminConversation.cancel)],
            name="admin_conversation",
            persistent=True,  # 🔥 تفعيل Persistence
            block=True,
        )
