# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎮 FC26 GAMING BOT - MAIN                                   ║
# ║              بوت FC26 - الملف الرئيسي (منسق فقط) 🔥                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import asyncio
import platform as sys_platform

from core.bot_app import FC26BotApp
from database.models import DatabaseModels
from handlers.commands.basic_commands import get_command_handlers
from handlers.recovery.global_router import get_recovery_handler
from handlers.registration.conversation import get_registration_handler
from services.admin.admin_conversation_handler import AdminConversation
from services.sell_coins.sell_conversation_handler import SellCoinsConversation
from utils.backup_job import register_backup_job
from utils.logger import fc26_logger
from utils.session_monitor import register_monitoring


def setup_handlers(app):
    """
    🎯 تسجيل جميع الـ handlers
    """

    print("\n" + "=" * 80)
    print("🎯 [SYSTEM] REGISTERING HANDLERS")
    print("=" * 80)

    # 1️⃣ REGISTRATION
    print("\n🧠 [REGISTRATION] Registering...")
    app.add_handler(get_registration_handler())
    print("   ✅ Done")

    # 2️⃣ SELL SERVICE
    print("\n🔧 [SELL] Registering...")
    try:
        app.add_handler(SellCoinsConversation.get_conversation_handler())
        print("   ✅ Done")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 3️⃣ ADMIN SERVICE
    print("\n🔧 [ADMIN] Registering...")
    try:
        app.add_handler(AdminConversation.get_conversation_handler())
        print("   ✅ Done")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # 4️⃣ SIMPLE COMMANDS
    print("\n🔧 [COMMANDS] Registering...")
    for handler in get_command_handlers():
        app.add_handler(handler)
    print("   ✅ Done")

    # 5️⃣ GLOBAL RECOVERY
    print("\n🛡️ [RECOVERY] Registering...")
    app.add_handler(get_recovery_handler(), group=99)
    print("   ✅ Done")

    print("\n" + "=" * 80)
    print("✅ [SYSTEM] ALL HANDLERS REGISTERED")
    print("=" * 80 + "\n")


def main():
    """🚀 نقطة البداية الرئيسية"""

    # Windows compatibility
    if sys_platform.system() == "Windows":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except:
            pass

    # تهيئة قاعدة البيانات
    fc26_logger.get_logger().info("💾 Initializing database...")
    if not DatabaseModels.create_all_tables():
        print("❌ Database initialization failed!")
        return

    # إنشاء تطبيق البوت (مع Persistence)
    bot_app = FC26BotApp()
    app = bot_app.create_application()

    # تسجيل الـ handlers
    setup_handlers(app)

    # 🔥 تسجيل وظائف الصيانة (النسخ الاحتياطي والمراقبة)
    register_backup_job(app)
    register_monitoring(app)

    # طباعة البانر
    fc26_logger.log_bot_start()
    print(
        """
╔══════════════════════════════════════════════════════════════════════════╗
║       🎮 FC26 GAMING BOT - COMPLETE SYSTEM 🎮                            ║
║         بوت FC26 - النظام الكامل مع Persistence 🔥                      ║
║                                                                          ║
║  🔥 FEATURES:                                                           ║
║  ✅ Modular architecture - هيكل معياري                                 ║
║  ✅ Session persistence - جلسات دائمة                                  ║
║  ✅ Session buckets - عزل البيانات                                    ║
║  ✅ Auto backup - نسخ احتياطي تلقائي                                   ║
║  ✅ Health monitoring - مراقبة الصحة                                   ║
║  ✅ Message tagging - نظام الوسم                                       ║
║  ✅ Zero duplicates - بدون تكرار                                       ║
║  ✅ Production ready - جاهز للإنتاج                                    ║
╚══════════════════════════════════════════════════════════════════════════╝
    """
    )

    # تشغيل البوت
    try:
        app.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("🔴 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        fc26_logger.log_bot_stop()


if __name__ == "__main__":
    main()
