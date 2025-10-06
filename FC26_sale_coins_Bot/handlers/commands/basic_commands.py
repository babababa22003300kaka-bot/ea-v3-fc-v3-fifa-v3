# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📋 BASIC COMMANDS - الأوامر البسيطة                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""الأوامر البسيطة: help, profile, delete"""

from telegram.ext import CommandHandler

from database.operations import UserOperations
from messages.welcome_messages import WelcomeMessages
from messages.error_messages import ErrorMessages
from messages.summary_messages import SummaryMessages
from handlers.profile_delete_handler import ProfileDeleteHandler
from utils.logger import log_user_action


class BasicCommands:
    """الأوامر البسيطة للبوت"""

    @staticmethod
    async def handle_help(update, context):
        """أمر /help"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Help")

        await update.message.reply_text(
            WelcomeMessages.get_help_message(), parse_mode="HTML"
        )

    @staticmethod
    async def handle_profile(update, context):
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

    @staticmethod
    async def handle_delete(update, context):
        """أمر /delete"""
        user_id = update.effective_user.id
        log_user_action(user_id, "Delete request")

        user_data = UserOperations.get_user_data(user_id)

        if not user_data:
            await update.message.reply_text(
                "❌ <b>لا يوجد ملف شخصي!</b>\n\n🚀 /start للتسجيل", parse_mode="HTML"
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


def get_command_handlers() -> list:
    """
    🎯 الحصول على قائمة معالجات الأوامر

    Returns:
        list: قائمة الـ handlers
    """

    handlers = [
        CommandHandler("help", BasicCommands.handle_help),
        CommandHandler("profile", BasicCommands.handle_profile),
        CommandHandler("delete", BasicCommands.handle_delete),
    ]

    # إضافة handlers الحذف
    handlers.extend(ProfileDeleteHandler.get_handlers())

    return handlers
