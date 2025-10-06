# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    🧠 FC26 BOT APPLICATION                               ║
# ║                      تطبيق البوت الأساسي                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from telegram.ext import Application
from config import BOT_TOKEN
from utils.logger import fc26_logger


class FC26BotApp:
    """تطبيق البوت الأساسي"""

    def __init__(self):
        self.logger = fc26_logger.get_logger()

    def create_application(self) -> Application:
        """
        إنشاء تطبيق Telegram Bot

        Returns:
            Application: تطبيق البوت جاهز للاستخدام
        """
        self.logger.info("🤖 Creating bot application...")

        app = Application.builder().token(BOT_TOKEN).build()

        self.logger.info("✅ Bot application created successfully")

        return app
