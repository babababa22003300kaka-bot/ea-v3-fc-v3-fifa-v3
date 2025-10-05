# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                🎮 FC26 GAMING BOT - MESSAGE TAGGING SYSTEM               ║
# ║         بوت FC26 - نظام وسم الرسائل (بدون ردود مزدوجة نهائياً)         ║
# ║    🔥 MESSAGE TAGGING + SMART + ANTI-SILENCE + GLOBAL RECOVERY 🔥        ║
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
from services.sell_coins.sell_conversation_handler import SellCoinsConversation
from utils.locks import is_rate_limited, user_lock_manager
from utils.logger import fc26_logger, log_database_operation, log_user_action
from utils.message_tagger import MessageTagger  # 🔥 نظام الوسم الموحد
from validators.payment_validator import PaymentValidator
from validators.phone_validator import PhoneValidator

# ═══════════════════════════════════════════════════════════════════════════
# IMPORT SERVICES
# ═══════════════════════════════════════════════════════════════════════════

try:
    from services.admin.admin_conversation_handler import AdminConversation

    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False
    print("⚠️ Admin service not available")

# ═══════════════════════════════════════════════════════════════════════════
# REGISTRATION STATES
# ═══════════════════════════════════════════════════════════════════════════

REG_PLATFORM, REG_WHATSAPP, REG_PAYMENT, REG_INTERRUPTED = range(4)


class FC26Bot:
    """FC26 Gaming Bot - Message Tagging System for Zero Duplicates"""

    def __init__(self):
        self.app = None
        self.logger = fc26_logger.get_logger()

    # ═══════════════════════════════════════════════════════════════════════
    # REGISTRATION HANDLERS - 🔥 WITH MESSAGE TAGGING 🔥
    # ═══════════════════════════════════════════════════════════════════════

    async def start_registration(self, update, context):
        """الموجه الذكي - Smart Router"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"

        print(f"\n{'='*80}")
        print(f"🧠 [SMART-ROUTER] /start from user {user_id} (@{username})")
        print(f"{'='*80}")

        if is_rate_limited(user_id):
            print(f"🚫 [SMART-ROUTER] Rate limited")
            await update.message.reply_text(ErrorMessages.get_rate_limit_error())
            return ConversationHandler.END

        log_user_action(user_id, "Started bot", f"@{username}")

        print(f"🔍 [SMART-ROUTER] Checking for interrupted registration...")

        has_memory_data = bool(context.user_data.get("platform")) or bool(
            context.user_data.get("interrupted_platform")
        )
        print(f"   📝 Memory check: {has_memory_data}")

        user_data = UserOperations.get_user_data(user_id)
        current_step = (
            user_data.get("registration_step", "unknown") if user_data else "unknown"
        )
        print(f"   💾 Database step: {current_step}")

        is_interrupted = False
        interrupted_data = None

        if current_step == "completed":
            print(f"✅ [SMART-ROUTER] User completed - showing menu")
            await self._show_main_menu(update, user_data)
            return ConversationHandler.END

        elif current_step in [
            "entering_whatsapp",
            "choosing_payment",
            "entering_payment_details",
        ]:
            print(f"⚠️ [SMART-ROUTER] Interrupted in DATABASE at: {current_step}")
            is_interrupted = True
            interrupted_data = user_data

        elif has_memory_data:
            print(f"⚠️ [SMART-ROUTER] Interrupted in MEMORY")
            is_interrupted = True
            interrupted_data = context.user_data

        if is_interrupted:
            print(f"🤔 [SMART-ROUTER] Asking user for decision...")

            context.user_data["interrupted_platform"] = interrupted_data.get(
                "platform", "غير محدد"
            )
            context.user_data["interrupted_whatsapp"] = interrupted_data.get("whatsapp")
            context.user_data["interrupted_payment"] = interrupted_data.get(
                "payment_method"
            )
            context.user_data["interrupted_step"] = current_step

            platform = context.user_data["interrupted_platform"]
            whatsapp = context.user_data["interrupted_whatsapp"] or "لم يُدخل بعد"

            question_text = f"""🤔 <b>لاحظت أنك لم تكمل تسجيلك!</b>

📋 <b>البيانات الحالية:</b>
• 🎮 المنصة: {platform}
• 📱 الواتساب: {whatsapp}

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

            print(f"➡️ [SMART-ROUTER] → REG_INTERRUPTED state")
            print(f"{'='*80}\n")
            return REG_INTERRUPTED

        print(f"🆕 [SMART-ROUTER] Fresh start")
        context.user_data.clear()

        keyboard = PlatformKeyboard.create_platform_selection_keyboard()
        await update.message.reply_text(
            WelcomeMessages.get_start_message(),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        print(f"➡️ [SMART-ROUTER] → REG_PLATFORM state")
        print(f"{'='*80}\n")
        return REG_PLATFORM

    async def handle_interrupted_choice(self, update, context):
        """معالج قرار المستخدم"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        choice = query.data

        print(f"\n{'='*80}")
        print(f"🎯 [INTERRUPTED-CHOICE] User {user_id}: {choice}")
        print(f"{'='*80}")

        if choice == "reg_restart":
            print(f"🔄 [INTERRUPTED-CHOICE] RESTART chosen")

            context.user_data.clear()

            keyboard = PlatformKeyboard.create_platform_selection_keyboard()
            await query.edit_message_text(
                "🔄 <b>حسناً، لنبدأ من جديد!</b>\n\n"
                + WelcomeMessages.get_start_message(),
                reply_markup=keyboard,
                parse_mode="HTML",
            )

            print(f"➡️ [INTERRUPTED-CHOICE] → REG_PLATFORM")
            print(f"{'='*80}\n")
            return REG_PLATFORM

        elif choice == "reg_continue":
            print(f"✅ [INTERRUPTED-CHOICE] CONTINUE chosen")

            interrupted_step = context.user_data.get("interrupted_step")
            platform = context.user_data.get("interrupted_platform")
            whatsapp = context.user_data.get("interrupted_whatsapp")

            print(f"   📍 Step: {interrupted_step}")
            print(f"   📝 Data: platform={platform}, whatsapp={whatsapp}")

            if not platform:
                print(f"   ⚠️ [EDGE-CASE] Data lost - auto restart")

                await query.edit_message_text(
                    "😔 <b>عذراً، حدث خطأ في استرجاع بياناتك.</b>\n\n🔄 لنبدأ من جديد...",
                    parse_mode="HTML",
                )

                context.user_data.clear()

                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                await query.message.reply_text(
                    WelcomeMessages.get_start_message(),
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_PLATFORM (data loss)")
                print(f"{'='*80}\n")
                return REG_PLATFORM

            if interrupted_step == "entering_whatsapp" or not whatsapp:
                print(f"   ➡️ Continuing at: WHATSAPP")

                platform_name = PlatformKeyboard.get_platform_name(platform)
                await query.edit_message_text(
                    f"✅ <b>رائع! لنكمل من حيث توقفنا</b>\n\n"
                    f"🎮 المنصة: {platform_name}\n\n"
                    f"📱 أدخل رقم الواتساب:\n"
                    f"📝 مثال: 01012345678",
                    parse_mode="HTML",
                )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_WHATSAPP")
                print(f"{'='*80}\n")
                return REG_WHATSAPP

            elif interrupted_step in ["choosing_payment", "entering_payment_details"]:
                print(f"   ➡️ Continuing at: PAYMENT")

                keyboard = PaymentKeyboard.create_payment_selection_keyboard()
                await query.edit_message_text(
                    f"✅ <b>رائع! لنكمل من حيث توقفنا</b>\n\n"
                    f"📱 الواتساب: {whatsapp}\n\n"
                    f"💳 اختر طريقة الدفع:",
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_PAYMENT")
                print(f"{'='*80}\n")
                return REG_PAYMENT

            else:
                print(f"   ⚠️ [EDGE-CASE] Unexpected step - auto restart")

                context.user_data.clear()

                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                await query.edit_message_text(
                    "🔄 <b>لنبدأ من جديد للتأكد من صحة البيانات</b>",
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_PLATFORM (unexpected)")
                print(f"{'='*80}\n")
                return REG_PLATFORM

    async def nudge_platform(self, update, context):
        """معالج التنبيه - حالة اختيار المنصة"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        text = update.message.text

        print(f"\n{'='*80}")
        print(f"🔔 [NUDGE-PLATFORM] User {user_id} typed: '{text}'")
        print(f"{'='*80}")

        keyboard = PlatformKeyboard.create_platform_selection_keyboard()

        await update.message.reply_text(
            "🎮 <b>من فضلك اختر منصتك من الأزرار أدناه</b>\n\n"
            "⬇️ اضغط على أحد الأزرار:",
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        print(f"   ✅ Nudge sent - staying in REG_PLATFORM")
        print(f"{'='*80}\n")

        return REG_PLATFORM

    async def nudge_interrupted(self, update, context):
        """معالج التنبيه - حالة المقاطعة"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        text = update.message.text

        print(f"\n{'='*80}")
        print(f"🔔 [NUDGE-INTERRUPTED] User {user_id} typed: '{text}'")
        print(f"{'='*80}")

        platform = context.user_data.get("interrupted_platform", "غير محدد")
        whatsapp = context.user_data.get("interrupted_whatsapp", "لم يُدخل بعد")

        question_text = f"""🤔 <b>من فضلك اختر من الأزرار أدناه:</b>

📋 <b>بياناتك الحالية:</b>
• 🎮 المنصة: {platform}
• 📱 الواتساب: {whatsapp}

<b>❓ تريد المتابعة أم البدء من جديد؟</b>
⬇️ اضغط على أحد الأزرار:"""

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

        print(f"   ✅ Nudge sent - staying in REG_INTERRUPTED")
        print(f"{'='*80}\n")

        return REG_INTERRUPTED

    async def handle_platform_callback(self, update, context):
        """معالج اختيار المنصة"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        platform = query.data.replace("platform_", "")

        print(f"\n{'='*80}")
        print(f"🎮 [PLATFORM] User {user_id}: {platform}")
        print(f"{'='*80}")

        context.user_data["platform"] = platform

        UserOperations.save_user_step(
            user_id, "entering_whatsapp", {"platform": platform}
        )

        platform_name = PlatformKeyboard.get_platform_name(platform)
        await query.edit_message_text(
            WelcomeMessages.get_platform_selected_message(platform_name),
            parse_mode="HTML",
        )

        log_user_action(user_id, f"Selected platform: {platform}")

        print(f"➡️ [PLATFORM] → REG_WHATSAPP")
        print(f"{'='*80}\n")
        return REG_WHATSAPP

    async def handle_whatsapp(self, update, context):
        """معالج إدخال الواتساب"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        phone = update.message.text.strip()

        print(f"\n{'='*80}")
        print(f"📱 [WHATSAPP] User {user_id} entered number")
        print(f"{'='*80}")

        validation = PhoneValidator.validate_whatsapp(phone)

        if not validation["valid"]:
            print(f"   ❌ Validation failed: {validation['error']}")
            await update.message.reply_text(
                ErrorMessages.get_phone_validation_error(validation["error"]),
                parse_mode="HTML",
            )
            print(f"   ⏸️ Staying in REG_WHATSAPP")
            print(f"{'='*80}\n")
            return REG_WHATSAPP

        print(f"   ✅ Validation OK")

        context.user_data["whatsapp"] = validation["cleaned"]

        platform = context.user_data.get("platform") or UserOperations.get_user_data(
            user_id
        ).get("platform")
        UserOperations.save_user_step(
            user_id,
            "choosing_payment",
            {"platform": platform, "whatsapp": validation["cleaned"]},
        )

        keyboard = PaymentKeyboard.create_payment_selection_keyboard()
        await update.message.reply_text(
            WelcomeMessages.get_whatsapp_confirmed_message(validation["display"]),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

        log_user_action(user_id, f"WhatsApp: {validation['display']}")

        print(f"➡️ [WHATSAPP] → REG_PAYMENT")
        print(f"{'='*80}\n")
        return REG_PAYMENT

    async def handle_payment_callback(self, update, context):
        """معالج اختيار طريقة الدفع"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        payment_key = query.data.replace("payment_", "")
        payment_name = PaymentKeyboard.get_payment_display_name(payment_key)

        print(f"\n{'='*80}")
        print(f"💳 [PAYMENT-CB] User {user_id}: {payment_name}")
        print(f"{'='*80}")

        context.user_data["payment_method"] = payment_key

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

        instruction = PaymentValidator.get_payment_instructions(payment_key)
        await query.edit_message_text(
            WelcomeMessages.get_payment_method_selected_message(
                payment_name, instruction
            ),
            parse_mode="HTML",
        )

        log_user_action(user_id, f"Payment: {payment_key}")

        print(f"   ⏸️ Staying in REG_PAYMENT (waiting for details)")
        print(f"{'='*80}\n")
        return REG_PAYMENT

    async def handle_payment_details(self, update, context):
        """معالج إدخال تفاصيل الدفع"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        details = update.message.text.strip()

        print(f"\n{'='*80}")
        print(f"💰 [PAYMENT-TXT] User {user_id} entered details")
        print(f"{'='*80}")

        payment_method = context.user_data.get("payment_method")
        if not payment_method:
            print(f"   ⚠️ [PROTECTION] No payment method selected yet!")

            keyboard = PaymentKeyboard.create_payment_selection_keyboard()
            await update.message.reply_text(
                "⚠️ <b>يجب اختيار طريقة الدفع أولاً!</b>\n\n"
                "💳 اختر طريقة الدفع من الأزرار:",
                reply_markup=keyboard,
                parse_mode="HTML",
            )

            print(f"   ⏸️ Staying in REG_PAYMENT")
            print(f"{'='*80}\n")
            return REG_PAYMENT

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
            print(f"   ⏸️ Staying in REG_PAYMENT")
            print(f"{'='*80}\n")
            return REG_PAYMENT

        print(f"   ✅ Validation OK - completing registration")

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

        context.user_data.clear()

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
        log_user_action(user_id, "Registration completed")

        print(f"🎉 [PAYMENT-TXT] Registration completed!")
        print(f"➡️ [PAYMENT-TXT] Ending conversation")
        print(f"{'='*80}\n")
        return ConversationHandler.END

    async def cancel_registration(self, update, context):
        """إلغاء التسجيل"""
        # 🏷️ وسم الرسالة
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id

        print(f"\n{'='*80}")
        print(f"❌ [CANCEL] User {user_id}")
        print(f"{'='*80}\n")

        context.user_data.clear()

        await update.message.reply_text(
            "❌ تم إلغاء التسجيل\n\n🔹 /start للبدء من جديد"
        )
        return ConversationHandler.END

    # ═══════════════════════════════════════════════════════════════════════
    # 🔥 GLOBAL RECOVERY ROUTER - WITH TAG CHECK 🔥
    # ═══════════════════════════════════════════════════════════════════════

    async def global_recovery_router(self, update, context):
        """
        الموجه العالمي للاسترداد - مع فحص الوسم

        🛡️ يتحقق أولاً من وجود وسم "_update_handled"
        إذا وُجد، يعني أن ConversationHandler عالج الرسالة بالفعل
        """
        user_id = update.effective_user.id

        print(f"\n{'='*80}")
        print(f"🛡️ [GLOBAL-RECOVERY] Triggered by user {user_id}")
        print(f"{'='*80}")

        # ═══════════════════════════════════════════════════════════════════
        # 🔥 STEP 1: CHECK FOR HANDLED TAG (CRITICAL!)
        # ═══════════════════════════════════════════════════════════════════

        if MessageTagger.check_and_clear(context):
            # الرسالة تمت معالجتها بالفعل - تجاهلها
            print(f"   🏷️ Message already handled by ConversationHandler")
            print(f"{'='*80}\n")
            return  # ✅ توقف هنا - لا تفعل أي شيء

        # إذا وصلنا هنا، معناه الرسالة لم تُعالج من ConversationHandler
        print(f"   ✅ [TAG-CHECK] No tag found - message not handled yet")
        print(f"   🔍 [TAG-CHECK] Proceeding with recovery checks...")

        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: NORMAL RECOVERY LOGIC
        # ═══════════════════════════════════════════════════════════════════

        text = update.message.text

        if text.startswith("/"):
            print(f"   ⏭️ Skipping: Is a command")
            print(f"{'='*80}\n")
            return

        if context.user_data:
            print(f"   ⏭️ Skipping: Active conversation exists")
            print(f"   📝 Context data: {list(context.user_data.keys())}")
            print(f"{'='*80}\n")
            return

        print(f"   🔍 No active conversation - checking database...")

        user_data = UserOperations.get_user_data(user_id)

        if not user_data:
            print(f"   🆕 New user detected")

            await update.message.reply_text(
                "👋 <b>مرحباً!</b>\n\n"
                "يبدو أنك جديد هنا.\n\n"
                "🚀 اكتب <code>/start</code> لبدء التسجيل\n"
                "❓ اكتب <code>/help</code> للمساعدة",
                parse_mode="HTML",
            )

            print(f"   ✅ New user message sent")
            print(f"{'='*80}\n")
            return

        current_step = user_data.get("registration_step", "unknown")

        if current_step == "completed":
            print(f"   ✅ Completed registration detected")

            await update.message.reply_text(
                "✅ <b>أنت مسجل بالفعل!</b>\n\n"
                "📋 <b>الأوامر المتاحة:</b>\n"
                "🔹 <code>/profile</code> - ملفك الشخصي\n"
                "🔹 <code>/sell</code> - بيع الكوينز\n"
                "🔹 <code>/help</code> - المساعدة\n"
                "🔹 <code>/start</code> - القائمة الرئيسية",
                parse_mode="HTML",
            )

            print(f"   ✅ Completed user message sent")
            print(f"{'='*80}\n")
            return

        else:
            print(f"   ⚠️ Interrupted registration detected: {current_step}")

            context.user_data["interrupted_platform"] = user_data.get(
                "platform", "غير محدد"
            )
            context.user_data["interrupted_whatsapp"] = user_data.get("whatsapp")
            context.user_data["interrupted_payment"] = user_data.get("payment_method")
            context.user_data["interrupted_step"] = current_step

            platform = context.user_data["interrupted_platform"]
            whatsapp = context.user_data["interrupted_whatsapp"] or "لم يُدخل بعد"

            question_text = f"""🔄 <b>لاحظت أن تسجيلك لم يكتمل!</b>

📋 <b>بياناتك:</b>
• 🎮 المنصة: {platform}
• 📱 الواتساب: {whatsapp}

<b>❓ تحب تكمل ولا تبدأ من جديد؟</b>"""

            keyboard = [
                [InlineKeyboardButton("✅ متابعة", callback_data="reg_continue")],
                [InlineKeyboardButton("🔄 بدء من جديد", callback_data="reg_restart")],
            ]

            await update.message.reply_text(
                question_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML",
            )

            print(f"   ✅ Recovery question sent")
            print(f"{'='*80}\n")
            return

    # ═══════════════════════════════════════════════════════════════════════
    # HELPER FUNCTIONS
    # ═══════════════════════════════════════════════════════════════════════

    async def _show_main_menu(self, update, user_data):
        """عرض القائمة الرئيسية"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        platform = user_data.get("platform", "غير محدد")
        whatsapp = user_data.get("whatsapp", "غير محدد")

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
        log_user_action(user_id, "Main menu", f"Platform: {platform}")

    async def handle_help(self, update, context):
        """أمر /help"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Help")

        await update.message.reply_text(
            WelcomeMessages.get_help_message(), parse_mode="HTML"
        )

    async def handle_profile(self, update, context):
        """أمر /profile"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Profile")

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
        log_user_action(user_id, "Delete request")

        user_data = UserOperations.get_user_data(user_id)

        if not user_data:
            await update.message.reply_text(
                "❌ <b>لا يوجد ملف شخصي!</b>\n\n🚀 /start للتسجيل",
                parse_mode="HTML",
            )
            return

        username = update.effective_user.username or "غير محدد"

        confirmation_text = f"""⚠️ <b>تحذير!</b>

🗑️ <b>مسح نهائي للملف الشخصي</b>

<b>📋 البيانات:</b>
• 🎮 {user_data.get('platform', 'غير محدد')}
• 📱 {user_data.get('whatsapp', 'غير محدد')}

<b>👤 المستخدم:</b> @{username}

<b>❓ متأكد؟</b>"""

        keyboard = ProfileDeleteHandler.create_delete_confirmation_keyboard()

        await update.message.reply_text(
            confirmation_text, reply_markup=keyboard, parse_mode="HTML"
        )

    # ═══════════════════════════════════════════════════════════════════════
    # BOT STARTUP - 🔥 WITH MESSAGE TAGGING SYSTEM 🔥
    # ═══════════════════════════════════════════════════════════════════════

    def start_bot(self):
        """تشغيل البوت مع نظام الوسم"""

        if sys_platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        self.logger.info("💾 Initializing database...")
        success = DatabaseModels.create_all_tables()
        if not success:
            self.logger.error("❌ Database init failed")
            return

        self.app = Application.builder().token(BOT_TOKEN).build()

        print("\n" + "=" * 80)
        print("🎯 [SYSTEM] MESSAGE TAGGING SYSTEM SETUP")
        print("=" * 80)

        # ═══════════════════════════════════════════════════════════════════
        # 1️⃣ REGISTRATION CONVERSATION
        # ═══════════════════════════════════════════════════════════════════

        print("\n🧠 [REGISTRATION] Setting up registration conversation...")
        print("   Features:")
        print("      ✅ Smart interruption handling")
        print("      ✅ Anti-silence nudge handlers")
        print("      ✅ Message tagging for zero duplicates")
        print("      ✅ Flexible reentry (allow_reentry=True)")
        print("      ✅ Per-user isolation (per_user=True)")
        print("      🔥 MESSAGE TAGGING SYSTEM ACTIVE")

        registration_conv = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.start_registration),
                CallbackQueryHandler(
                    self.handle_interrupted_choice, pattern="^reg_(continue|restart)$"
                ),
            ],
            states={
                REG_PLATFORM: [
                    CallbackQueryHandler(
                        self.handle_platform_callback, pattern="^platform_"
                    ),
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.nudge_platform
                    ),
                ],
                REG_WHATSAPP: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.handle_whatsapp
                    ),
                ],
                REG_PAYMENT: [
                    CallbackQueryHandler(
                        self.handle_payment_callback, pattern="^payment_"
                    ),
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.handle_payment_details
                    ),
                ],
                REG_INTERRUPTED: [
                    CallbackQueryHandler(
                        self.handle_interrupted_choice,
                        pattern="^reg_(continue|restart)$",
                    ),
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, self.nudge_interrupted
                    ),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_registration)],
            name="registration",
            persistent=False,
            per_user=True,
            allow_reentry=True,
            block=True,
        )

        self.app.add_handler(registration_conv)
        print("   ✅ Registration conversation registered")
        print("   🏷️ All handlers tagged to prevent double responses")

        # ═══════════════════════════════════════════════════════════════════
        # 2️⃣ SELL CONVERSATION
        # ═══════════════════════════════════════════════════════════════════

        print("\n🔧 [SELL] Setting up sell conversation...")
        try:
            sell_conv = SellCoinsConversation.get_conversation_handler()
            self.app.add_handler(sell_conv)
            print("   ✅ Sell conversation registered")
        except Exception as e:
            print(f"   ❌ Failed: {e}")

        # ═══════════════════════════════════════════════════════════════════
        # 3️⃣ ADMIN CONVERSATION
        # ═══════════════════════════════════════════════════════════════════

        if ADMIN_AVAILABLE:
            print("\n🔧 [ADMIN] Setting up admin conversation...")
            try:
                admin_conv = AdminConversation.get_conversation_handler()
                self.app.add_handler(admin_conv)
                print("   ✅ Admin conversation registered")
            except Exception as e:
                print(f"   ❌ Failed: {e}")

        # ═══════════════════════════════════════════════════════════════════
        # 4️⃣ SIMPLE COMMANDS
        # ═══════════════════════════════════════════════════════════════════

        print("\n🔧 [COMMANDS] Registering simple commands...")
        self.app.add_handler(CommandHandler("help", self.handle_help))
        self.app.add_handler(CommandHandler("profile", self.handle_profile))
        self.app.add_handler(CommandHandler("delete", self.handle_delete))

        for handler in ProfileDeleteHandler.get_handlers():
            self.app.add_handler(handler)

        print("   ✅ All commands registered")

        # ═══════════════════════════════════════════════════════════════════
        # 🔥 5️⃣ GLOBAL RECOVERY ROUTER - WITH TAG CHECK 🔥
        # ═══════════════════════════════════════════════════════════════════

        print("\n🛡️ [GLOBAL-RECOVERY] Setting up safety net with tag check...")
        print("   Priority: group=99 (LOWEST - last resort)")
        print("   Feature: Checks for '_update_handled' tag FIRST")
        print("   Purpose: Prevent double responses + catch lost users")

        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.global_recovery_router
            ),
            group=99,
        )

        print("   ✅ Global recovery router registered (with tag check)")

        # ═══════════════════════════════════════════════════════════════════
        # SUMMARY
        # ═══════════════════════════════════════════════════════════════════

        print("\n" + "=" * 80)
        print("✅ [SYSTEM] MESSAGE TAGGING SYSTEM CONFIGURED")
        print("=" * 80)
        print("   Layer 1: Registration (with message tagging)")
        print("   Layer 2: Sell (with message tagging)")
        print("   Layer 3: Admin (with message tagging)")
        print("   Layer 4: Commands (default)")
        print("   Layer 5: Global Recovery (tag-aware)")
        print("=" * 80)
        print("   🏷️ TAGGING: All handlers mark messages")
        print("   🛡️ PROTECTION: Global router checks tags first")
        print("   ✅ RESULT: ZERO double responses guaranteed")
        print("   🔓 FLEXIBILITY: All smart features preserved")
        print("=" * 80 + "\n")

        fc26_logger.log_bot_start()

        print(
            """
╔══════════════════════════════════════════════════════════════════════════╗
║       🎮 FC26 GAMING BOT - MESSAGE TAGGING SYSTEM 🎮                     ║
║         بوت FC26 - نظام وسم الرسائل (حل نهائي) 🔥                       ║
║                                                                          ║
║  🔥 ULTIMATE FEATURES:                                                  ║
║  🏷️ Message tagging system for zero duplicates                         ║
║  ✅ Tag check in global router prevents double responses                ║
║  ✅ All smart features preserved (interruption, nudge, recovery)        ║
║  ✅ Clean memory management (tag cleanup after check)                   ║
║  ✅ Production-ready and fully tested                                   ║
║  🔓 Full flexibility maintained (allow_reentry=True)                    ║
║  🔒 User isolation (per_user=True)                                      ║
║  📝 Comprehensive logging                                               ║
║                                                                          ║
║  🌟 NEVER SILENT - NEVER DUPLICATES - PRODUCTION READY!                 ║
╚══════════════════════════════════════════════════════════════════════════╝
        """
        )

        try:
            self.app.run_polling(drop_pending_updates=True)
        except Exception as e:
            self.logger.error(f"❌ Critical: {e}")
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
        print("🔴 Bot stopped")
    except Exception as e:
        print(f"❌ Fatal: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
