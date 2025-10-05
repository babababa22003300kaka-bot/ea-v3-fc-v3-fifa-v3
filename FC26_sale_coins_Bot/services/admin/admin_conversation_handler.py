# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              👑 ADMIN - CONVERSATION HANDLER                             ║
# ║                   خدمة الأدمن - ConversationHandler                     ║
# ║                  🔥 WITH MESSAGE TAGGING SYSTEM 🔥                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
خدمة الأدمن باستخدام ConversationHandler
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

from database.admin_operations import AdminOperations
from utils.message_tagger import MessageTagger  # 🔥 النظام الجديد

from .price_management import PriceManagement

# ═══════════════════════════════════════════════════════════════════════════
# STATES
# ═══════════════════════════════════════════════════════════════════════════

ADMIN_MAIN, ADMIN_PRICES, ADMIN_PLATFORM, ADMIN_PRICE_INPUT = range(4)


class AdminConversation:
    """معالج الأدمن - ConversationHandler مع نظام الوسم"""

    ADMIN_ID = 1124247595  # ضع معرف الأدمن هنا

    # ═══════════════════════════════════════════════════════════════════════
    # ENTRY POINT
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء لوحة الأدمن - /admin"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"

        print(f"\n👑 [ADMIN] Admin command from user {user_id} (@{username})")

        # التحقق من الصلاحية
        if user_id != AdminConversation.ADMIN_ID:
            print(f"❌ [ADMIN] Unauthorized access by {user_id}")
            await update.message.reply_text("❌ غير مصرح لك بالوصول لهذه الخدمة!")
            return ConversationHandler.END

        AdminOperations.log_admin_action(user_id, "ADMIN_LOGIN", "Accessed via /admin")
        print(f"✅ [ADMIN] Admin {user_id} logged in")

        # عرض اللوحة الرئيسية
        keyboard = [
            [InlineKeyboardButton("💰 إدارة الأسعار", callback_data="admin_prices")],
            [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
            [InlineKeyboardButton("❌ خروج", callback_data="admin_exit")],
        ]

        await update.message.reply_text(
            f"👑 <b>لوحة الأدمن</b>\n\n" f"مرحباً @{username}\n\n" f"اختر الخدمة:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

        return ADMIN_MAIN

    # ═══════════════════════════════════════════════════════════════════════
    # STATE HANDLERS
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة القائمة الرئيسية"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        if query.data == "admin_exit":
            await query.edit_message_text("👋 تم الخروج من لوحة الأدمن")
            return ConversationHandler.END

        if query.data == "admin_prices":
            print(f"💰 [ADMIN] {user_id} accessing price management")
            AdminOperations.log_admin_action(user_id, "ACCESSED_PRICE_MANAGEMENT")

            # عرض إدارة الأسعار
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

            await query.edit_message_text(
                "💰 <b>إدارة الأسعار</b>\n\n🎮 اختر المنصة:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )

            return ADMIN_PLATFORM

        if query.data == "admin_stats":
            await query.edit_message_text(
                "📊 <b>الإحصائيات</b>\n\nقريباً...",
                parse_mode="HTML",
            )
            return ConversationHandler.END

        return ADMIN_MAIN

    @staticmethod
    async def handle_platform_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة اختيار المنصة"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        if query.data == "admin_back_main":
            # رجوع للقائمة الرئيسية
            keyboard = [
                [
                    InlineKeyboardButton(
                        "💰 إدارة الأسعار", callback_data="admin_prices"
                    )
                ],
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
                [InlineKeyboardButton("❌ خروج", callback_data="admin_exit")],
            ]

            await query.edit_message_text(
                "👑 <b>لوحة الأدمن</b>\n\nاختر الخدمة:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )

            return ADMIN_MAIN

        user_id = query.from_user.id
        platform = query.data.replace("admin_platform_", "")

        print(f"🎮 [ADMIN] {user_id} selected platform: {platform}")

        # عرض أنواع التحويل
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

        await query.edit_message_text(
            f"💰 <b>أسعار {platform_name}</b>\n\nاختر نوع التحويل:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML",
        )

        return ADMIN_PLATFORM

    @staticmethod
    async def handle_transfer_type_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """معالجة اختيار نوع التحويل"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        if query.data == "admin_back_platforms":
            # رجوع لاختيار المنصة
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

            await query.edit_message_text(
                "💰 <b>إدارة الأسعار</b>\n\n🎮 اختر المنصة:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )

            return ADMIN_PLATFORM

        user_id = query.from_user.id

        # استخراج البيانات
        parts = query.data.split("_")  # admin_edit_playstation_normal
        if len(parts) >= 4:
            platform = parts[2]
            transfer_type = parts[3]

            print(f"⚡ [ADMIN] {user_id} editing {platform} {transfer_type}")

            # جلب السعر الحالي
            current_price = PriceManagement.get_current_price(platform, transfer_type)

            if current_price is None:
                await query.edit_message_text(
                    "❌ خطأ في جلب السعر الحالي",
                    parse_mode="HTML",
                )
                return ConversationHandler.END

            # حفظ البيانات في context
            context.user_data["admin_platform"] = platform
            context.user_data["admin_type"] = transfer_type
            context.user_data["admin_current_price"] = current_price

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

            await query.edit_message_text(
                f"💰 <b>تعديل سعر {platform_name} - {transfer_name}</b>\n\n"
                f"💵 السعر الحالي: {current_price:,} ج.م\n\n"
                f"📝 أدخل السعر الجديد:\n"
                f"• الحد الأدنى: 1,000 ج.م\n"
                f"• الحد الأقصى: 50,000 ج.م\n\n"
                f"❌ للإلغاء: /cancel",
                parse_mode="HTML",
            )

            return ADMIN_PRICE_INPUT

        return ADMIN_PLATFORM

    @staticmethod
    async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال السعر"""
        # 🏷️ وسم الرسالة - الأهم!
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        price_text = update.message.text.strip()

        print(f"💰 [ADMIN] Price input from {user_id}: {price_text}")

        # التحقق من الصيغة
        if not price_text.isdigit():
            print(f"   ❌ [ADMIN] Invalid format")
            await update.message.reply_text("❌ صيغة غير صحيحة! أدخل أرقاماً فقط")
            return ADMIN_PRICE_INPUT

        new_price = int(price_text)

        # التحقق من الحدود
        if new_price < 1000:
            print(f"   ❌ [ADMIN] Price too low: {new_price}")
            await update.message.reply_text(
                f"❌ السعر قليل جداً! الحد الأدنى: 1,000 ج.م"
            )
            return ADMIN_PRICE_INPUT

        if new_price > 50000:
            print(f"   ❌ [ADMIN] Price too high: {new_price}")
            await update.message.reply_text(
                f"❌ السعر عالي جداً! الحد الأقصى: 50,000 ج.م"
            )
            return ADMIN_PRICE_INPUT

        # جلب البيانات
        platform = context.user_data.get("admin_platform")
        transfer_type = context.user_data.get("admin_type")
        old_price = context.user_data.get("admin_current_price")

        print(
            f"🔄 [ADMIN] Updating {platform} {transfer_type}: {old_price} → {new_price}"
        )

        # تحديث السعر
        success = await PriceManagement.update_price(
            platform, transfer_type, new_price, user_id
        )

        if not success:
            await update.message.reply_text("❌ حدث خطأ في تحديث السعر")
            return ConversationHandler.END

        platform_name = {
            "playstation": "PlayStation",
            "xbox": "Xbox",
            "pc": "PC",
        }.get(platform, platform)

        transfer_name = "فوري" if transfer_type == "instant" else "عادي"

        await update.message.reply_text(
            f"✅ <b>تم تحديث السعر بنجاح!</b>\n\n"
            f"🎮 المنصة: {platform_name}\n"
            f"⚡ النوع: {transfer_name}\n"
            f"💰 السعر القديم: {old_price:,} ج.م\n"
            f"💵 السعر الجديد: {new_price:,} ج.م\n\n"
            f"🔹 /admin للرجوع للوحة التحكم",
            parse_mode="HTML",
        )

        # مسح البيانات
        context.user_data.clear()
        print(f"✅ [ADMIN] Price updated successfully")

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
        print(f"❌ [ADMIN] {user_id} cancelled operation")

        await update.message.reply_text(
            "❌ تم إلغاء العملية\n\n🔹 /admin للرجوع للوحة التحكم"
        )

        context.user_data.clear()
        AdminOperations.log_admin_action(user_id, "CANCELLED_OPERATION")

        return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════════════
    # CONVERSATION HANDLER - 🔥 WITH block=True INSIDE 🔥
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def get_conversation_handler():
        """إنشاء ConversationHandler للخدمة - مع block=True بالداخل"""
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
            persistent=False,
            block=True,  # 🔥 المكان الصحيح!
        )
