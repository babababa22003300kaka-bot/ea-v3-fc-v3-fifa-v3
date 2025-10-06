# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📝 REGISTRATION HANDLERS                                    ║
# ║                  معالجات التسجيل - مع نظام الوسم والعزل                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
معالجات خدمة التسجيل
- مع نظام وسم الرسائل (MessageTagger)
- مع نظام عزل البيانات (Session Buckets)
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from database.operations import StatisticsOperations, UserOperations
from keyboards.payment_keyboard import PaymentKeyboard
from keyboards.platform_keyboard import PlatformKeyboard
from messages.confirmation_msgs import ConfirmationMessages
from messages.error_messages import ErrorMessages
from messages.welcome_messages import WelcomeMessages
from utils.locks import is_rate_limited
from utils.logger import log_user_action
from utils.message_tagger import MessageTagger
from utils.session_bucket import bucket, clear_bucket
from validators.payment_validator import PaymentValidator
from validators.phone_validator import PhoneValidator

# 🔥 نظام الرسائل النشطة - Active Message System
from utils.active_message_helper import send_or_edit, clear_active_message


class RegistrationHandlers:
    """معالجات التسجيل مع نظام الوسم والعزل"""

    @staticmethod
    async def start_registration(update, context):
        """الموجه الذكي - Smart Router"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"

        print(f"\n{'='*80}")
        print(f"🧠 [SMART-ROUTER] /start from user {user_id} (@{username})")
        print(f"{'='*80}")

        if is_rate_limited(user_id):
            print(f"🚫 [SMART-ROUTER] Rate limited")
            await send_or_edit(
                context,
                update.effective_chat.id,
                ErrorMessages.get_rate_limit_error(
            ))
            return ConversationHandler.END

        log_user_action(user_id, "Started bot", f"@{username}")

        print(f"🔍 [SMART-ROUTER] Checking for interrupted registration...")

        reg_bucket = bucket(context, "reg")
        has_memory_data = bool(reg_bucket.get("platform")) or bool(
            reg_bucket.get("interrupted_platform")
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
            await RegistrationHandlers._show_main_menu(update, user_data)
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
            interrupted_data = reg_bucket

        if is_interrupted:
            print(f"🤔 [SMART-ROUTER] Asking user for decision...")

            reg_bucket["interrupted_platform"] = interrupted_data.get(
                "platform", "غير محدد"
            )
            reg_bucket["interrupted_whatsapp"] = interrupted_data.get("whatsapp")
            reg_bucket["interrupted_payment"] = interrupted_data.get("payment_method")
            reg_bucket["interrupted_step"] = current_step

            platform = reg_bucket["interrupted_platform"]
            whatsapp = reg_bucket["interrupted_whatsapp"] or "لم يُدخل بعد"

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

            await send_or_edit(
                context,
                update.effective_chat.id,
                question_text,
                InlineKeyboardMarkup(keyboard),
                user_message_id=update.message.message_id,
            )

            print(f"➡️ [SMART-ROUTER] → REG_INTERRUPTED state")
            print(f"{'='*80}\n")
            from .states import REG_INTERRUPTED

            return REG_INTERRUPTED

        print(f"🆕 [SMART-ROUTER] Fresh start")
        clear_bucket(context, "reg")

        keyboard = PlatformKeyboard.create_platform_selection_keyboard()
        await send_or_edit(
                context,
                update.effective_chat.id,
                WelcomeMessages.get_start_message(),
                keyboard
            )

        print(f"➡️ [SMART-ROUTER] → REG_PLATFORM state")
        print(f"{'='*80}\n")
        from .states import REG_PLATFORM

        return REG_PLATFORM

    @staticmethod
    async def handle_interrupted_choice(update, context):
        """معالج قرار المستخدم"""
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        choice = query.data

        print(f"\n{'='*80}")
        print(f"🎯 [INTERRUPTED-CHOICE] User {user_id}: {choice}")
        print(f"{'='*80}")

        reg_bucket = bucket(context, "reg")

        if choice == "reg_restart":
            print(f"🔄 [INTERRUPTED-CHOICE] RESTART chosen")

            clear_bucket(context, "reg")

            keyboard = PlatformKeyboard.create_platform_selection_keyboard()
            await send_or_edit(
                context,
                update.effective_chat.id,
                "🔄 <b>حسناً، لنبدأ من جديد!</b>\n\n"
                + WelcomeMessages.get_start_message(),
                keyboard
            )

            print(f"➡️ [INTERRUPTED-CHOICE] → REG_PLATFORM")
            print(f"{'='*80}\n")
            from .states import REG_PLATFORM

            return REG_PLATFORM

        elif choice == "reg_continue":
            print(f"✅ [INTERRUPTED-CHOICE] CONTINUE chosen")

            interrupted_step = reg_bucket.get("interrupted_step")
            platform = reg_bucket.get("interrupted_platform")
            whatsapp = reg_bucket.get("interrupted_whatsapp")

            print(f"   📍 Step: {interrupted_step}")
            print(f"   📝 Data: platform={platform}, whatsapp={whatsapp}")

            if not platform:
                print(f"   ⚠️ [EDGE-CASE] Data lost - auto restart")

                await send_or_edit(
                context,
                update.effective_chat.id,
                "😔 <b>عذراً، حدث خطأ في استرجاع بياناتك.</b>\n\n🔄 لنبدأ من جديد..."
            )

                clear_bucket(context, "reg")

                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                await send_or_edit(
                context,
                update.effective_chat.id,
                WelcomeMessages.get_start_message(),
                keyboard
            )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_PLATFORM (data loss)")
                print(f"{'='*80}\n")
                from .states import REG_PLATFORM

                return REG_PLATFORM

            if interrupted_step == "entering_whatsapp" or not whatsapp:
                print(f"   ➡️ Continuing at: WHATSAPP")

                platform_name = PlatformKeyboard.get_platform_name(platform)
                await send_or_edit(
                context,
                update.effective_chat.id,
                f"✅ <b>رائع! لنكمل من حيث توقفنا</b>\n\n"
                    f"🎮 المنصة: {platform_name}\n\n"
                    f"📱 أدخل رقم الواتساب:\n"
                    f"📝 مثال: 01012345678"
            )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_WHATSAPP")
                print(f"{'='*80}\n")
                from .states import REG_WHATSAPP

                return REG_WHATSAPP

            elif interrupted_step in ["choosing_payment", "entering_payment_details"]:
                print(f"   ➡️ Continuing at: PAYMENT")

                keyboard = PaymentKeyboard.create_payment_selection_keyboard()
                await send_or_edit(
                context,
                update.effective_chat.id,
                f"✅ <b>رائع! لنكمل من حيث توقفنا</b>\n\n"
                    f"📱 الواتساب: {whatsapp}\n\n"
                    f"💳 اختر طريقة الدفع:",
                keyboard
            )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_PAYMENT")
                print(f"{'='*80}\n")
                from .states import REG_PAYMENT

                return REG_PAYMENT

            else:
                print(f"   ⚠️ [EDGE-CASE] Unexpected step - auto restart")

                clear_bucket(context, "reg")

                keyboard = PlatformKeyboard.create_platform_selection_keyboard()
                await send_or_edit(
                context,
                update.effective_chat.id,
                "🔄 <b>لنبدأ من جديد للتأكد من صحة البيانات</b>",
                keyboard
            )

                print(f"➡️ [INTERRUPTED-CHOICE] → REG_PLATFORM (unexpected)")
                print(f"{'='*80}\n")
                from .states import REG_PLATFORM

                return REG_PLATFORM

    @staticmethod
    async def nudge_platform(update, context):
        """معالج التنبيه - حالة اختيار المنصة"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        text = update.message.text

        print(f"\n{'='*80}")
        print(f"🔔 [NUDGE-PLATFORM] User {user_id} typed: '{text}'")
        print(f"{'='*80}")

        keyboard = PlatformKeyboard.create_platform_selection_keyboard()

        await send_or_edit(
                context,
                update.effective_chat.id,
                "🎮 <b>من فضلك اختر منصتك من الأزرار أدناه</b>\n\n"
            "⬇️ اضغط على أحد الأزرار:",
                keyboard,
                user_message_id=update.message.message_id,
            )

        print(f"   ✅ Nudge sent - staying in REG_PLATFORM")
        print(f"{'='*80}\n")

        from .states import REG_PLATFORM

        return REG_PLATFORM

    @staticmethod
    async def nudge_interrupted(update, context):
        """معالج التنبيه - حالة المقاطعة"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        text = update.message.text

        print(f"\n{'='*80}")
        print(f"🔔 [NUDGE-INTERRUPTED] User {user_id} typed: '{text}'")
        print(f"{'='*80}")

        reg_bucket = bucket(context, "reg")
        platform = reg_bucket.get("interrupted_platform", "غير محدد")
        whatsapp = reg_bucket.get("interrupted_whatsapp", "لم يُدخل بعد")

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

        await send_or_edit(
                context,
                update.effective_chat.id,
                question_text,
                InlineKeyboardMarkup(keyboard),
                user_message_id=update.message.message_id,
            )

        print(f"   ✅ Nudge sent - staying in REG_INTERRUPTED")
        print(f"{'='*80}\n")

        from .states import REG_INTERRUPTED

        return REG_INTERRUPTED

    @staticmethod
    async def handle_platform_callback(update, context):
        """معالج اختيار المنصة"""
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        platform = query.data.replace("platform_", "")

        print(f"\n{'='*80}")
        print(f"🎮 [PLATFORM] User {user_id}: {platform}")
        print(f"{'='*80}")

        bucket(context, "reg")["platform"] = platform

        UserOperations.save_user_step(
            user_id, "entering_whatsapp", {"platform": platform}
        )

        platform_name = PlatformKeyboard.get_platform_name(platform)
        await send_or_edit(
                context,
                update.effective_chat.id,
                
            WelcomeMessages.get_platform_selected_message(platform_name
            ),
            parse_mode="HTML",
        )

        log_user_action(user_id, f"Selected platform: {platform}")

        print(f"➡️ [PLATFORM] → REG_WHATSAPP")
        print(f"{'='*80}\n")
        from .states import REG_WHATSAPP

        return REG_WHATSAPP

    @staticmethod
    async def handle_whatsapp(update, context):
        """معالج إدخال الواتساب"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        phone = update.message.text.strip()

        print(f"\n{'='*80}")
        print(f"📱 [WHATSAPP] User {user_id} entered number")
        print(f"{'='*80}")

        validation = PhoneValidator.validate_whatsapp(phone)

        if not validation["valid"]:
            print(f"   ❌ Validation failed: {validation['error']}")
            await send_or_edit(
                context,
                update.effective_chat.id,
                
                ErrorMessages.get_phone_validation_error(validation["error"]
            ),
                parse_mode="HTML",
                user_message_id=update.message.message_id,
            )
            print(f"   ⏸️ Staying in REG_WHATSAPP")
            print(f"{'='*80}\n")
            from .states import REG_WHATSAPP

            return REG_WHATSAPP

        print(f"   ✅ Validation OK")

        bucket(context, "reg")["whatsapp"] = validation["cleaned"]

        platform = bucket(context, "reg").get(
            "platform"
        ) or UserOperations.get_user_data(user_id).get("platform")
        UserOperations.save_user_step(
            user_id,
            "choosing_payment",
            {"platform": platform, "whatsapp": validation["cleaned"]},
        )

        keyboard = PaymentKeyboard.create_payment_selection_keyboard()
        await send_or_edit(
                context,
                update.effective_chat.id,
                WelcomeMessages.get_whatsapp_confirmed_message(validation["display"]),
                keyboard,
                user_message_id=update.message.message_id,
            )

        log_user_action(user_id, f"WhatsApp: {validation['display']}")

        print(f"➡️ [WHATSAPP] → REG_PAYMENT")
        print(f"{'='*80}\n")
        from .states import REG_PAYMENT

        return REG_PAYMENT

    @staticmethod
    async def handle_payment_callback(update, context):
        """معالج اختيار طريقة الدفع"""
        MessageTagger.mark_as_handled(context)

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        payment_key = query.data.replace("payment_", "")
        payment_name = PaymentKeyboard.get_payment_display_name(payment_key)

        print(f"\n{'='*80}")
        print(f"💳 [PAYMENT-CB] User {user_id}: {payment_name}")
        print(f"{'='*80}")

        bucket(context, "reg")["payment_method"] = payment_key

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
        await send_or_edit(
                context,
                update.effective_chat.id,
                
            WelcomeMessages.get_payment_method_selected_message(
                payment_name, instruction
            
            ),
            parse_mode="HTML",
        )

        log_user_action(user_id, f"Payment: {payment_key}")

        print(f"   ⏸️ Staying in REG_PAYMENT (waiting for details)")
        print(f"{'='*80}\n")
        from .states import REG_PAYMENT

        return REG_PAYMENT

    @staticmethod
    async def handle_payment_details(update, context):
        """معالج إدخال تفاصيل الدفع"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id
        details = update.message.text.strip()

        print(f"\n{'='*80}")
        print(f"💰 [PAYMENT-TXT] User {user_id} entered details")
        print(f"{'='*80}")

        payment_method = bucket(context, "reg").get("payment_method")
        if not payment_method:
            print(f"   ⚠️ [PROTECTION] No payment method selected yet!")

            keyboard = PaymentKeyboard.create_payment_selection_keyboard()
            await send_or_edit(
                context,
                update.effective_chat.id,
                "⚠️ <b>يجب اختيار طريقة الدفع أولاً!</b>\n\n"
                "💳 اختر طريقة الدفع من الأزرار:",
                keyboard,
                user_message_id=update.message.message_id,
            )

            print(f"   ⏸️ Staying in REG_PAYMENT")
            print(f"{'='*80}\n")
            from .states import REG_PAYMENT

            return REG_PAYMENT

        user_data = UserOperations.get_user_data(user_id)
        validation = PaymentValidator.validate_payment_details(
            user_data["payment_method"], details
        )

        if not validation["valid"]:
            print(f"   ❌ Validation failed: {validation['error']}")
            await send_or_edit(
                context,
                update.effective_chat.id,
                
                ErrorMessages.get_payment_validation_error(
                    user_data["payment_method"], validation["error"]
                
            ),
                parse_mode="HTML",
                user_message_id=update.message.message_id,
            )
            print(f"   ⏸️ Staying in REG_PAYMENT")
            print(f"{'='*80}\n")
            from .states import REG_PAYMENT

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

        clear_bucket(context, "reg")

        payment_name = PaymentKeyboard.get_payment_display_name(
            user_data["payment_method"]
        )

        confirmation = ConfirmationMessages.create_payment_confirmation(
            user_data["payment_method"], validation, payment_name
        )
        await send_or_edit(
                context,
                update.effective_chat.id,
                confirmation,
                user_message_id=update.message.message_id,
            )

        user_info = {
            "id": user_id,
            "username": update.effective_user.username or "غير متوفر",
        }

        final_summary = ConfirmationMessages.create_final_summary(
            user_data, payment_name, validation, user_info
        )
        await send_or_edit(
                context,
                update.effective_chat.id,
                final_summary,
                user_message_id=update.message.message_id,
            )

        StatisticsOperations.update_daily_metric("completed_registrations")
        log_user_action(user_id, "Registration completed")

        print(f"🎉 [PAYMENT-TXT] Registration completed!")
        print(f"➡️ [PAYMENT-TXT] Ending conversation")
        print(f"{'='*80}\n")
        
        # 🔥 مسح الرسالة النشطة عند انتهاء المحادثة
        clear_active_message(context)
        return ConversationHandler.END

    @staticmethod
    async def cancel_registration(update, context):
        """إلغاء التسجيل"""
        MessageTagger.mark_as_handled(context)

        user_id = update.effective_user.id

        print(f"\n{'='*80}")
        print(f"❌ [CANCEL] User {user_id}")
        print(f"{'='*80}\n")

        clear_bucket(context, "reg")

        await send_or_edit(
                context,
                update.effective_chat.id,
                
            "❌ تم إلغاء التسجيل\n\n🔹 /start للبدء من جديد"
        
            )
        return ConversationHandler.END

    @staticmethod
    async def _show_main_menu(update, user_data):
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

        await send_or_edit(
                context,
                update.effective_chat.id,
                main_menu_text
            )
        log_user_action(user_id, "Main menu", f"Platform: {platform}")
