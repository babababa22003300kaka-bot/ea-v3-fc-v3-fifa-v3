# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📝 REGISTRATION CONVERSATION                                ║
# ║                  محادثة التسجيل - ConversationHandler                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
محادثة التسجيل الكاملة
- مع Persistence
- مع Message Tagging
- مع Session Buckets
"""

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .handlers import RegistrationHandlers
from .states import REG_INTERRUPTED, REG_PAYMENT, REG_PLATFORM, REG_WHATSAPP


def get_registration_handler():
    """إنشاء ConversationHandler للتسجيل"""

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
                    RegistrationHandlers.handle_platform_callback,
                    pattern="^platform_",
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    RegistrationHandlers.nudge_platform,
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
                    RegistrationHandlers.handle_payment_callback,
                    pattern="^payment_",
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
        persistent=True,  # 🔥 تفعيل Persistence
        per_user=True,
        allow_reentry=True,
        block=True,
    )
