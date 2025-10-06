# ╔══════════════════════════════════════════════════════════════════════════╗
# ║           🛡️ GLOBAL RECOVERY ROUTER - موجه الاسترداد العام              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""الموجه العالمي لاسترداد المستخدمين الضائعين"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters

from database.operations import UserOperations
from utils.message_tagger import MessageTagger


class GlobalRecoveryRouter:
    """موجه الاسترداد العام"""

    @staticmethod
    async def handle_lost_message(update, context):
        """
        معالج الرسائل الضائعة - مع فحص الوسم

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


def get_recovery_handler():
    """
    🎯 الحصول على معالج الاسترداد العام

    Returns:
        MessageHandler: معالج الرسائل للاسترداد
    """

    return MessageHandler(
        filters.TEXT & ~filters.COMMAND, GlobalRecoveryRouter.handle_lost_message
    )
