# ╔══════════════════════════════════════════════════════════════════════════╗
# ║        🎯 REGISTRATION CONVERSATION - محادثة التسجيل                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""إعداد ConversationHandler للتسجيل"""

from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .states import REG_PLATFORM, REG_WHATSAPP, REG_PAYMENT, REG_INTERRUPTED
from .handlers import RegistrationHandlers


def get_registration_handler() -> ConversationHandler:
    """
    🎯 إنشاء ConversationHandler للتسجيل

    Features:
    - Smart interruption handling
    - Anti-silence nudge handlers
    - Message tagging for zero duplicates
    - Flexible reentry (allow_reentry=True)
    - Per-user isolation (per_user=True)

    Returns:
        ConversationHandler: معالج محادثة التسجيل جاهز
    """

    return ConversationHandler(
        entry_points=[
            CommandHandler("start", RegistrationHandlers.start_registration),
            CallbackQueryHandler(
                RegistrationHandlers.handle_interrupted_choice,
                pattern="^reg_(continue|restart)$",
            ),
        ],
        states={
            REG_PLATFORM: [
                CallbackQueryHandler(
                    RegistrationHandlers.handle_platform_callback, pattern="^platform_"
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, RegistrationHandlers.nudge_platform
                ),
            ],
            REG_WHATSAPP: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    RegistrationHandlers.handle_whatsapp,
                ),
            ],
            REG_PAYMENT: [
                CallbackQueryHandler(
                    RegistrationHandlers.handle_payment_callback, pattern="^payment_"
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    RegistrationHandlers.handle_payment_details,
                ),
            ],
            REG_INTERRUPTED: [
                CallbackQueryHandler(
                    RegistrationHandlers.handle_interrupted_choice,
                    pattern="^reg_(continue|restart)$",
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    RegistrationHandlers.nudge_interrupted,
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", RegistrationHandlers.cancel_registration)],
        name="registration",
        persistent=False,
        per_user=True,
        allow_reentry=True,
        block=True,
    )
