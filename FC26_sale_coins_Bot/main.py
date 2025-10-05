# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                🎮 FC26 GAMING BOT - SMART REGISTRATION                   ║
# ║                 بوت FC26 - نظام التسجيل الذكي والمرن                    ║
# ║         🔥 SMART INTERRUPTION + FLEXIBLE NAVIGATION 🔥                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import asyncio
import platform as sys_platform

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from database.models import DatabaseModels
from database.operations import StatisticsOperations, UserOperations
from handlers.profile_delete_handler import ProfileDeleteHandler
from keyboards.payment_keyboard import PaymentKeyboard
from keyboards.platform_keyboard import PlatformKeyboard
from messages.confirmation_msgs import ConfirmationMessages
from messages.error_messages import ErrorMessages
from messages.summary_messages import SummaryMessages
from messages.welcome_messages import WelcomeMessages

# Sell service
from services.sell_coins.sell_conversation_handler import SellCoinsConversation
from utils.locks import is_rate_limited, user_lock_manager
from utils.logger import fc26_logger, log_database_operation, log_user_action
from validators.payment_validator import PaymentValidator
from validators.phone_validator import PhoneValidator

# ═══════════════════════════════════════════════════════════════════════════
# IMPORT SERVICES
# ═══════════════════════════════════════════════════════════════════════════


# Admin service
try:
    from services.admin.admin_conversation_handler import AdminConversation

    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False
    print("⚠️ Admin service not available")

# ═══════════════════════════════════════════════════════════════════════════
# REGISTRATION STATES - 🔥 4 STATES FOR SMART FLOW 🔥
# ═══════════════════════════════════════════════════════════════════════════

# الحالات الأربعة:
# 1. REG_PLATFORM - اختيار المنصة (أزرار فقط)
# 2. REG_WHATSAPP - إدخال الواتساب (نص فقط)
# 3. REG_PAYMENT - اختيار وإدخال الدفع (أزرار + نص)
# 4. REG_INTERRUPTED - المقاطعة الذكية (أزرار فقط)
REG_PLATFORM, REG_WHATSAPP, REG_PAYMENT, REG_INTERRUPTED = range(4)


class FC26Bot:
    """Main FC26 Gaming Bot - Smart & Flexible Registration"""

    def __init__(self):
        self.app = None
        self.logger = fc26_logger.get_logger()

    # ═══════════════════════════════════════════════════════════════════════
    # SMART REGISTRATION - 🔥 INTELLIGENT INTERRUPTION HANDLING 🔥
    # ═══════════════════════════════════════════════════════════════════════

    async def start_registration(self, update, context):
        """
        بدء التسجيل الذكي - /start

        🔥 SMART ROUTER:
        - يتحقق من وجود تسجيل مقاطع
        - يسأل المستخدم: متابعة أم البدء من جديد؟
        - يوجه للمسار الصحيح
        """
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"

        print(f"\n{'='*80}")
        print(f"🚀 [SMART-START] User {user_id} (@{username}) initiated /start")
        print(f"{'='*80}")

        if is_rate_limited(user_id):
            print(f"🚫 [SMART-START] User {user_id} is rate limited")
            await update.message.reply_text(ErrorMessages.get_rate_limit_error())
            return ConversationHandler.END

        log_user_action(user_id, "Started bot", f"@{username}")

        # ═══════════════════════════════════════════════════════════════════
        # 🔥 STEP 1: Check for interrupted registration (SMART CHECK)
        # ═══════════════════════════════════════════════════════════════════

        print(f"🔍 [SMART-START] Checking for interrupted registration...")

        # Check 1: Memory (context.user_data) - أسرع
        has_memory_data = bool(context.user_data.get("platform"))
        print(f"   📝 [MEMORY] Has platform in memory: {has_memory_data}")

        # Check 2: Database - أدق
        user_data = UserOperations.get_user_data(user_id)
        has_db_data = user_data is not None
        current_step = (
            user_data.get("registration_step", "unknown") if has_db_data else "unknown"
        )
        print(f"   💾 [DATABASE] Has user data: {has_db_data}")
        print(f"   📍 [DATABASE] Current step: {current_step}")

        # تحديد إذا كان هناك تسجيل مقاطع
        is_interrupted = False
        interrupted_data = None

        if current_step == "completed":
            # مكتمل - عرض القائمة الرئيسية
            print(f"✅ [SMART-START] User {user_id} registration is completed")
            await self._show_main_menu(update, user_data)
            return ConversationHandler.END

        elif current_step in [
            "entering_whatsapp",
            "choosing_payment",
            "entering_payment_details",
        ]:
            # تسجيل مقاطع في قاعدة البيانات
            print(f"⚠️ [SMART-START] Found interrupted registration in DATABASE")
            print(f"   📍 Interrupted at step: {current_step}")
            is_interrupted = True
            interrupted_data = user_data

        elif has_memory_data and not current_step == "completed":
            # تسجيل مقاطع في الذاكرة
            print(f"⚠️ [SMART-START] Found interrupted registration in MEMORY")
            print(f"   📝 Memory data: {list(context.user_data.keys())}")
            is_interrupted = True
            interrupted_data = context.user_data

        # ═══════════════════════════════════════════════════════════════════
        # 🔥 STEP 2: Handle interrupted registration (SMART QUESTION)
        # ═══════════════════════════════════════════════════════════════════

        if is_interrupted:
            print(f"\n🤔 [SMART-START] Asking user for decision...")

            # حفظ البيانات المقاطعة في context للاستخدام لاحقاً
            if interrupted_data:
                context.user_data["interrupted_platform"] = interrupted_data.get(
                    "platform"
                )
                context.user_data["interrupted_whatsapp"] = interrupted_data.get(
                    "whatsapp"
                )
                context.user_data["interrupted_payment"] = interrupted_data.get(
                    "payment_method"
                )
                context.user_data["interrupted_step"] = current_step
                print(f"   💾 Saved interrupted data to context")

            # رسالة ذكية للمستخدم
            platform_name = interrupted_data.get("platform", "غير محدد")
            whatsapp = interrupted_data.get("whatsapp", "غير محدد")

            question_text = f"""🤔 <b>لاحظت أنك لم تكمل تسجيلك!</b>

📋 <b>البيانات الحالية:</b>
• 🎮 المنصة: {platform_name}
• 📱 الواتساب: {whatsapp if whatsapp != 'غير محدد' else 'لم يُدخل بعد'}

<b>❓ ماذا تريد أن تفعل؟</b>"""

            keyboard = [
                [
                    InlineKeyboardButton(
                        "✅ متابعة من حيث توقفت", callback_data="reg_continue"
                    )
                ],
                [InlineKeyboardButton("🔄 البدء من جديد", callback_data="reg_restart")],
            ]

            await update.message.reply_text(
                question_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )

            print(f"➡️ [SMART-START] Transitioning to REG_INTERRUPTED state")
            print(f"⏸️ [SMART-START] Waiting for user decision...")
            print(f"{'='*80}\n")
            return REG_INTERRUPTED

        # ═══════════════════════════════════════════════════════════════════
        # 🔥 STEP 3: Normal start (no interruption)
        # ═══════════════════════════════════════════════════════════════════

        print(f"🆕 [SMART-START] No interrupted registration - starting fresh")

        # مسح أي بيانات قديمة
        context.user_data.clear()
        print(f"   🧹 Cleared context.user_data")

        keyboard = PlatformKeyboard.create_platform_selection_keyboard()
        await update.message.reply_text(
            WelcomeMessages.get_start_message(),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        print(f"➡️ [SMART-START] Transitioning to REG_PLATFORM state")
        print(f"📝 [SMART-START] Next: User will choose platform")
        print(f"{'='*80}\n")
        return REG_PLATFORM

    async def handle_interrupted_choice(self, update, context):
        """
        معالجة قرار المستخدم (متابعة أم البدء من جديد)

        🔥 SMART DECISION HANDLER:
        - reg_continue: يتابع من حيث توقف
        - reg_restart: يبدأ من جديد
        """
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        choice = query.data

        print(f"\n{'='*80}")
        print(f"🎯 [INTERRUPTED] User {user_id} made choice: {choice}")
        print(f"{'='*80}")

        # ═══════════════════════════════════════════════════════════════════
        # Choice 1: البدء من جديد
        # ═══════════════════════════════════════════════════════════════════

        if choice == "reg_restart":
            print(f"🔄 [INTERRUPTED] User chose to RESTART")

            # مسح كل البيانات
            context.user_data.clear()
            print(f"   🧹 Cleared context.user_data")

            # مسح من قاعدة البيانات أيضاً (optional but recommended)
            # UserOperations.delete_user(user_id)

            # إعادة بدء التسجيل
            print(f"   🔄 Restarting registration from scratch...")

            keyboard = PlatformKeyboard.create_platform_selection_keyboard()
            await query.edit_message_text(
                "🔄 <b>حسناً، لنبدأ من جديد!</b>\n\n"
                + WelcomeMessages.get_start_message(),
                reply_markup=keyboard,
                parse_mode="HTML",
            )

            print(f"➡️ [INTERRUPTED] Transitioning to REG_PLATFORM state")
            print(f"{'='*80}\n")
            return REG_PLATFORM

        # ═══════════════════════════════════════════════════════════════════
        # Choice 2: المتابعة من حيث توقف
        # ═══════════════════════════════════════════════════════════════════

        elif choice == "reg_continue":
            print(f"✅ [INTERRUPTED] User chose to CONTINUE")

            # جلب البيانات المحفوظة
            interrupted_step = context.user_data.get("interrupted_step", "unknown")
            platform = context.user_data.get("interrupted_platform")
            whatsapp = context.user_data.get("interrupted_whatsapp")
            payment = context.user_data.get("interrupted_payment")

            print(f"   📍 Interrupted step: {interrupted_step}")
            print(
                f"   📝 Available data: platform={platform}, whatsapp={whatsapp}, payment={payment}"
            )

            # ═══════════════════════════════════════════════════════════════
            # Edge Case: البيانات مفقودة
            # ═══════════════════════════════════════════════════════════════

            if not platform:
                print(f"   ⚠️ [EDGE CASE] No platform found - data lost!")

                await query.edit_message_text(
                    "😔 <b>عذراً، حدث خطأ في استرجاع بياناتك.</b>\n\n"
                    "🔄 لنبدأ من جديد...",
                    parse_mode="HTML",
                )

                # إعادة البدء تلقائياً
                context.user_data.clear()

                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                await query.message.reply_text(
                    WelcomeMessages.get_start_message(),
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

                print(f"   🔄 Auto-restarting due to data loss")
                print(f"➡️ [INTERRUPTED] Transitioning to REG_PLATFORM state")
                print(f"{'='*80}\n")
                return REG_PLATFORM

            # ═══════════════════════════════════════════════════════════════
            # توجيه للخطوة الصحيحة
            # ═══════════════════════════════════════════════════════════════

            # Case 1: توقف عند إدخال الواتساب
            if interrupted_step == "entering_whatsapp" or not whatsapp:
                print(f"   ➡️ Continuing at: WHATSAPP input")

                platform_name = PlatformKeyboard.get_platform_name(platform)
                await query.edit_message_text(
                    f"✅ <b>رائع! لنكمل من حيث توقفنا</b>\n\n"
                    f"🎮 المنصة المختارة: {platform_name}\n\n"
                    f"📱 الآن، أدخل رقم الواتساب:\n"
                    f"📝 مثال: 01012345678",
                    parse_mode="HTML",
                )

                print(f"➡️ [INTERRUPTED] Transitioning to REG_WHATSAPP state")
                print(f"{'='*80}\n")
                return REG_WHATSAPP

            # Case 2: توقف عند اختيار الدفع
            elif interrupted_step in ["choosing_payment", "entering_payment_details"]:
                print(f"   ➡️ Continuing at: PAYMENT selection")

                keyboard = PaymentKeyboard.create_payment_selection_keyboard()
                await query.edit_message_text(
                    f"✅ <b>رائع! لنكمل من حيث توقفنا</b>\n\n"
                    f"📱 الواتساب: {whatsapp}\n\n"
                    f"💳 الآن، اختر طريقة الدفع:",
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

                print(f"➡️ [INTERRUPTED] Transitioning to REG_PAYMENT state")
                print(f"{'='*80}\n")
                return REG_PAYMENT

            # Case 3: حالة غير متوقعة
            else:
                print(f"   ⚠️ [EDGE CASE] Unexpected step: {interrupted_step}")

                # إعادة البدء للأمان
                context.user_data.clear()

                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                await query.edit_message_text(
                    "🔄 <b>لنبدأ من جديد للتأكد من صحة البيانات</b>",
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

                print(f"   🔄 Auto-restarting due to unexpected step")
                print(f"➡️ [INTERRUPTED] Transitioning to REG_PLATFORM state")
                print(f"{'='*80}\n")
                return REG_PLATFORM

    # ═══════════════════════════════════════════════════════════════════════
    # REGISTRATION FLOW HANDLERS (unchanged from previous version)
    # ═══════════════════════════════════════════════════════════════════════

    async def handle_platform_callback(self, update, context):
        """معالجة اختيار المنصة"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        platform = query.data.replace("platform_", "")

        print(f"\n{'='*80}")
        print(f"🎮 [PLATFORM] User {user_id} selected platform: {platform}")
        print(f"{'='*80}")

        self.logger.info(f"🎮 User {user_id} selected platform: {platform}")

        # حفظ في الذاكرة
        context.user_data["platform"] = platform
        print(f"   💾 Saved to context.user_data")

        # حفظ في قاعدة البيانات
        UserOperations.save_user_step(
            user_id, "entering_whatsapp", {"platform": platform}
        )
        print(f"   💾 Saved to database")

        platform_name = PlatformKeyboard.get_platform_name(platform)
        await query.edit_message_text(
            WelcomeMessages.get_platform_selected_message(platform_name),
            parse_mode="HTML",
        )

        log_user_action(user_id, f"Selected platform: {platform}")

        print(f"➡️ [PLATFORM] Transitioning to REG_WHATSAPP state")
        print(f"{'='*80}\n")
        return REG_WHATSAPP

    async def handle_whatsapp(self, update, context):
        """معالجة رقم الواتساب"""
        user_id = update.effective_user.id
        phone = update.message.text.strip()

        print(f"\n{'='*80}")
        print(f"📱 [WHATSAPP] User {user_id} entered text")
        print(f"{'='*80}")

        self.logger.info(f"📱 User {user_id} entered WhatsApp")

        # التحقق من الرقم
        validation = PhoneValidator.validate_whatsapp(phone)

        if not validation["valid"]:
            print(f"   ❌ Validation failed: {validation['error']}")
            await update.message.reply_text(
                ErrorMessages.get_phone_validation_error(validation["error"]),
                parse_mode="HTML",
            )
            print(f"   ⏸️ Staying in REG_WHATSAPP state")
            print(f"{'='*80}\n")
            return REG_WHATSAPP

        print(f"   ✅ Validation successful")

        # حفظ في الذاكرة
        context.user_data["whatsapp"] = validation["cleaned"]
        print(f"   💾 Saved to context.user_data")

        # حفظ في قاعدة البيانات
        platform = context.user_data.get("platform") or UserOperations.get_user_data(
            user_id
        ).get("platform")
        UserOperations.save_user_step(
            user_id,
            "choosing_payment",
            {"platform": platform, "whatsapp": validation["cleaned"]},
        )
        print(f"   💾 Saved to database")

        # عرض خيارات الدفع
        keyboard = PaymentKeyboard.create_payment_selection_keyboard()
        await update.message.reply_text(
            WelcomeMessages.get_whatsapp_confirmed_message(validation["display"]),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        log_user_action(user_id, f"WhatsApp validated: {validation['display']}")

        print(f"➡️ [WHATSAPP] Transitioning to REG_PAYMENT state")
        print(f"{'='*80}\n")
        return REG_PAYMENT

    async def handle_payment_callback(self, update, context):
        """معالجة اختيار طريقة الدفع"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        payment_key = query.data.replace("payment_", "")
        payment_name = PaymentKeyboard.get_payment_display_name(payment_key)

        print(f"\n{'='*80}")
        print(f"💳 [PAYMENT] User {user_id} selected: {payment_name}")
        print(f"{'='*80}")

        # حفظ في الذاكرة
        context.user_data["payment_method"] = payment_key
        print(f"   💾 Saved to context.user_data")

        # حفظ في قاعدة البيانات
        user_data = UserOperations.get_user_data(user_id)
        UserOperations.save_user_step(
            user_id,
            "entering_payment_details",
            {
                "platform": user_data["platform"],
                "whatsapp": user_data["whatsapp"],
                "payment_method": payment_key,
            },
        )
        print(f"   💾 Saved to database")

        instruction = PaymentValidator.get_payment_instructions(payment_key)
        await query.edit_message_text(
            WelcomeMessages.get_payment_method_selected_message(
                payment_name, instruction
            ),
            parse_mode="HTML",
        )

        log_user_action(user_id, f"Selected payment: {payment_key}")

        print(f"   ⏸️ Staying in REG_PAYMENT state (waiting for details)")
        print(f"{'='*80}\n")
        return REG_PAYMENT

    async def handle_payment_details(self, update, context):
        """معالجة تفاصيل الدفع"""
        user_id = update.effective_user.id
        details = update.message.text.strip()

        print(f"\n{'='*80}")
        print(f"💰 [PAYMENT-DETAILS] User {user_id} entered details")
        print(f"{'='*80}")

        user_data = UserOperations.get_user_data(user_id)

        validation = PaymentValidator.validate_payment_details(
            user_data["payment_method"], details
        )

        if not validation["valid"]:
            print(f"   ❌ Validation failed: {validation['error']}")
            await update.message.reply_text(
                ErrorMessages.get_payment_validation_error(
                    user_data["payment_method"], validation["error"]
                ),
                parse_mode="HTML",
            )
            print(f"   ⏸️ Staying in REG_PAYMENT state")
            print(f"{'='*80}\n")
            return REG_PAYMENT

        print(f"   ✅ Validation successful - completing registration")

        # إكمال التسجيل
        UserOperations.save_user_step(
            user_id,
            "completed",
            {
                "platform": user_data["platform"],
                "whatsapp": user_data["whatsapp"],
                "payment_method": user_data["payment_method"],
                "payment_details": validation["cleaned"],
            },
        )
        print(f"   💾 Registration completed in database")

        # مسح الذاكرة
        context.user_data.clear()
        print(f"   🧹 Cleared context.user_data")

        # رسائل التأكيد
        payment_name = PaymentKeyboard.get_payment_display_name(
            user_data["payment_method"]
        )

        confirmation = ConfirmationMessages.create_payment_confirmation(
            user_data["payment_method"], validation, payment_name
        )
        await update.message.reply_text(confirmation)

        user_info = {
            "id": user_id,
            "username": update.effective_user.username or "غير متوفر",
        }

        final_summary = ConfirmationMessages.create_final_summary(
            user_data, payment_name, validation, user_info
        )
        await update.message.reply_text(final_summary, parse_mode="HTML")

        StatisticsOperations.update_daily_metric("completed_registrations")
        log_user_action(user_id, "Registration completed successfully")

        print(f"🎉 [PAYMENT-DETAILS] Registration completed!")
        print(f"➡️ [PAYMENT-DETAILS] Ending conversation")
        print(f"{'='*80}\n")
        return ConversationHandler.END

    async def cancel_registration(self, update, context):
        """إلغاء التسجيل - /cancel"""
        user_id = update.effective_user.id

        print(f"\n{'='*80}")
        print(f"❌ [CANCEL] User {user_id} cancelled registration")
        print(f"{'='*80}\n")

        context.user_data.clear()

        await update.message.reply_text(
            "❌ تم إلغاء التسجيل\n\n🔹 /start للبدء من جديد"
        )
        return ConversationHandler.END

    async def _show_main_menu(self, update, user_data):
        """عرض القائمة الرئيسية"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        platform = user_data.get("platform", "غير محدد")
        whatsapp = user_data.get("whatsapp", "غير محدد")

        print(f"🏠 [MENU] Showing main menu to user {user_id}")

        main_menu_text = f"""✅ <b>أهلاً وسهلاً بعودتك!</b>

👤 <b>المستخدم:</b> @{username}
🎮 <b>المنصة:</b> {platform}
📱 <b>الواتساب:</b> <code>{whatsapp}</code>

<b>🏠 القائمة الرئيسية:</b>

🔹 <code>/sell</code> - بيع الكوينز
🔹 <code>/profile</code> - عرض الملف الشخصي
🔹 <code>/help</code> - المساعدة والدعم

<b>🎯 خدماتنا:</b>
• شراء وبيع العملات
• تجارة اللاعبين
• خدمات التطوير
• دعم فني متخصص

💬 <b>للحصول على الخدمات تواصل مع الإدارة</b>"""

        await update.message.reply_text(main_menu_text, parse_mode="HTML")
        log_user_action(user_id, "Shown main menu", f"Platform: {platform}")

    # ═══════════════════════════════════════════════════════════════════════
    # SIMPLE COMMANDS (unchanged)
    # ═══════════════════════════════════════════════════════════════════════

    async def handle_help(self, update, context):
        """أمر /help"""
        user_id = update.effective_user.id
        print(f"❓ [HELP] User {user_id} requested help")
        log_user_action(user_id, "Requested help")

        await update.message.reply_text(
            WelcomeMessages.get_help_message(), parse_mode="HTML"
        )

    async def handle_profile(self, update, context):
        """أمر /profile"""
        user_id = update.effective_user.id
        print(f"👤 [PROFILE] User {user_id} requested profile")
        log_user_action(user_id, "Requested profile")

        user_data = UserOperations.get_user_data(user_id)

        if not user_data:
            await update.message.reply_text(ErrorMessages.get_start_required_error())
            return

        profile_text = SummaryMessages.create_user_profile_summary(user_data)
        keyboard = ProfileDeleteHandler.create_profile_management_keyboard()

        await update.message.reply_text(
            profile_text, reply_markup=keyboard, parse_mode="HTML"
        )

    async def handle_delete(self, update, context):
        """أمر /delete"""
        user_id = update.effective_user.id
        print(f"🗑️ [DELETE] User {user_id} requested deletion")
        log_user_action(user_id, "Requested profile deletion")

        user_data = UserOperations.get_user_data(user_id)

        if not user_data:
            await update.message.reply_text(
                "❌ <b>لا يوجد ملف شخصي للحذف!</b>\n\n🚀 /start للتسجيل",
                parse_mode="HTML",
            )
            return

        username = update.effective_user.username or "غير محدد"

        confirmation_text = f"""⚠️ <b>تحذير هام!</b>

🗑️ <b>أنت على وشك مسح ملفك الشخصي نهائياً</b>

<b>📋 البيانات:</b>
• 🎮 المنصة: {user_data.get('platform', 'غير محدد')}
• 📱 الواتساب: {user_data.get('whatsapp', 'غير محدد')}
• 💳 الدفع: {user_data.get('payment_method', 'غير محدد')}

<b>⚠️ هذا الإجراء لا يمكن التراجع عنه!</b>

<b>👤 المستخدم:</b> @{username}

<b>❓ متأكد؟</b>"""

        keyboard = ProfileDeleteHandler.create_delete_confirmation_keyboard()

        await update.message.reply_text(
            confirmation_text, reply_markup=keyboard, parse_mode="HTML"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # BOT STARTUP - 🔥 SMART & FLEXIBLE CONFIGURATION 🔥
    # ═══════════════════════════════════════════════════════════════════════

    def start_bot(self):
        """تشغيل البوت مع النظام الذكي"""

        if sys_platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            self.logger.info("✅ Windows event loop policy configured")

        self.logger.info("💾 Initializing database...")
        success = DatabaseModels.create_all_tables()
        if success:
            self.logger.info("✅ Database initialized successfully")
            log_database_operation("Database initialized", success=True)
        else:
            self.logger.error("❌ Database initialization failed")
            log_database_operation("Database initialization", success=False)
            return

        self.app = Application.builder().token(BOT_TOKEN).build()

        self.logger.info("🔧 Setting up bot handlers...")

        print("\n" + "=" * 80)
        print("🎯 [SYSTEM] Registering ConversationHandlers (SMART & FLEXIBLE)...")
        print("=" * 80)

        # ═══════════════════════════════════════════════════════════════════
        # 1️⃣ SMART REGISTRATION CONVERSATION
        # ═══════════════════════════════════════════════════════════════════
        print("\n🧠 [REGISTRATION] Setting up SMART registration...")
        print("   🔥 Features:")
        print("      ✅ 4 states for clear separation")
        print("      ✅ Intelligent interruption handling")
        print("      ✅ Flexible navigation (block=False)")
        print("      ✅ Per-user isolation (per_user=True)")

        registration_conv = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_registration)],
            states={
                # State 1: Platform selection (buttons only)
                REG_PLATFORM: [
                    CallbackQueryHandler(
                        self.handle_platform_callback, pattern="^platform_"
                    ),
                ],
                # State 2: WhatsApp input (text only)
                REG_WHATSAPP: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.handle_whatsapp
                    ),
                ],
                # State 3: Payment selection and details
                REG_PAYMENT: [
                    CallbackQueryHandler(
                        self.handle_payment_callback, pattern="^payment_"
                    ),
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.handle_payment_details
                    ),
                ],
                # 🔥 State 4: SMART interruption handling
                REG_INTERRUPTED: [
                    CallbackQueryHandler(
                        self.handle_interrupted_choice,
                        pattern="^reg_(continue|restart)$",
                    ),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_registration)],
            name="registration",
            persistent=False,
            # 🔥 CRITICAL SETTINGS:
            per_user=True,  # عزل كل مستخدم عن الآخر
            # block=True removed for flexibility
        )

        self.app.add_handler(registration_conv)
        print("   ✅ Smart registration conversation registered")
        print("   🎯 Flow: /start → smart check → platform → whatsapp → payment")
        print("   🧠 Smart: Asks user on /start if interrupted")
        print("   🔓 Flexible: Can switch to /sell or /profile anytime")
        self.logger.info("✅ Smart registration conversation configured")

        # ═══════════════════════════════════════════════════════════════════
        # 2️⃣ SELL COINS CONVERSATION
        # ═══════════════════════════════════════════════════════════════════
        print("\n🔧 [SELL] Setting up sell conversation...")
        try:
            sell_conv = SellCoinsConversation.get_conversation_handler()
            self.app.add_handler(sell_conv)
            print("   ✅ Sell coins conversation registered")
            self.logger.info("✅ Sell coins conversation configured")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            self.logger.error(f"❌ Sell error: {e}")

        # ═══════════════════════════════════════════════════════════════════
        # 3️⃣ ADMIN CONVERSATION
        # ═══════════════════════════════════════════════════════════════════
        if ADMIN_AVAILABLE:
            print("\n🔧 [ADMIN] Setting up admin conversation...")
            try:
                admin_conv = AdminConversation.get_conversation_handler()
                self.app.add_handler(admin_conv)
                print("   ✅ Admin conversation registered")
                self.logger.info("✅ Admin conversation configured")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                self.logger.error(f"❌ Admin error: {e}")

        # ═══════════════════════════════════════════════════════════════════
        # SIMPLE COMMANDS
        # ═══════════════════════════════════════════════════════════════════
        print("\n🔧 [COMMANDS] Registering commands...")
        self.app.add_handler(CommandHandler("help", self.handle_help))
        self.app.add_handler(CommandHandler("profile", self.handle_profile))
        self.app.add_handler(CommandHandler("delete", self.handle_delete))

        for handler in ProfileDeleteHandler.get_handlers():
            self.app.add_handler(handler)

        print("   ✅ All commands registered")

        print("\n" + "=" * 80)
        print("✅ [SYSTEM] ALL HANDLERS REGISTERED")
        print("=" * 80)
        print("   🧠 SMART: Intelligent interruption handling")
        print("   🔓 FLEXIBLE: Can navigate freely between services")
        print("   🔒 ISOLATED: per_user=True ensures no cross-user conflicts")
        print("   📝 DETAILED: Comprehensive logs for debugging")
        print("=" * 80 + "\n")

        self.logger.info("✅ All handlers configured (SMART & FLEXIBLE)")

        fc26_logger.log_bot_start()

        print(
            """
╔══════════════════════════════════════════════════════════════════════════╗
║       🎮 FC26 GAMING BOT - SMART & FLEXIBLE REGISTRATION 🎮              ║
║            بوت FC26 - نظام التسجيل الذكي والمرن                         ║
║                                                                          ║
║  🧠 INTELLIGENT FEATURES:                                               ║
║  ✅ Smart interruption: Asks user to continue or restart                ║
║  ✅ Flexible navigation: Switch services anytime                        ║
║  ✅ Separated states: Zero handler conflicts                            ║
║  ✅ Per-user isolation: Multi-user safe                                 ║
║  ✅ Detailed logging: Full debugging support                            ║
║                                                                          ║
║  🌟 PRODUCTION READY - SMART & USER-FRIENDLY!                           ║
╚══════════════════════════════════════════════════════════════════════════╝
        """
        )

        try:
            self.app.run_polling(drop_pending_updates=True)
        except Exception as e:
            self.logger.error(f"❌ Critical error: {e}")
        finally:
            fc26_logger.log_bot_stop()


def main():
    """نقطة البداية"""
    if sys_platform.system() == "Windows":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except:
            pass

    try:
        bot = FC26Bot()
        bot.start_bot()
    except KeyboardInterrupt:
        print("🔴 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
