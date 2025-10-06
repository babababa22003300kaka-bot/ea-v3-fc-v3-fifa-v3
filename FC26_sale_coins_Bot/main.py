# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                🎮 FC26 GAMING BOT - MAIN ORCHESTRATOR                   ║
# ║              بوت FC26 - الملف الرئيسي (المنسق فقط) 🔥                  ║
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
from utils.logger import fc26_logger


def setup_handlers(app):
    """
    🎯 تسجيل جميع الـ handlers

    ✅ لإضافة خدمة جديدة:
       1. Import الخدمة في الأعلى
       2. أضف سطر واحد هنا: app.add_handler(...)
       3. خلاص! 🔥
    """

    print("\n" + "=" * 80)
    print("🎯 [SYSTEM] REGISTERING HANDLERS")
    print("=" * 80)

    # ═══════════════════════════════════════════════════════════════════════
    # 1️⃣ REGISTRATION (أولوية: group=0)
    # ═══════════════════════════════════════════════════════════════════════
    print("\n🧠 [REGISTRATION] Registering...")
    app.add_handler(get_registration_handler())
    print("   ✅ Done")

    # ═══════════════════════════════════════════════════════════════════════
    # 2️⃣ SELL SERVICE (أولوية: group=0)
    # ═══════════════════════════════════════════════════════════════════════
    print("\n🔧 [SELL] Registering...")
    try:
        app.add_handler(SellCoinsConversation.get_conversation_handler())
        print("   ✅ Done")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # 3️⃣ ADMIN SERVICE (أولوية: group=0)
    # ═══════════════════════════════════════════════════════════════════════
    print("\n🔧 [ADMIN] Registering...")
    try:
        app.add_handler(AdminConversation.get_conversation_handler())
        print("   ✅ Done")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # 4️⃣ SIMPLE COMMANDS (أولوية: group=0)
    # ═══════════════════════════════════════════════════════════════════════
    print("\n🔧 [COMMANDS] Registering...")
    for handler in get_command_handlers():
        app.add_handler(handler)
    print("   ✅ Done")

    # ═══════════════════════════════════════════════════════════════════════
    # 5️⃣ GLOBAL RECOVERY (أولوية: group=99 - آخر خط دفاع)
    # ═══════════════════════════════════════════════════════════════════════
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

    # إنشاء تطبيق البوت
    bot_app = FC26BotApp()
    app = bot_app.create_application()

    # تسجيل الـ handlers
    setup_handlers(app)

    # طباعة البانر
    fc26_logger.log_bot_start()
    print(
        """
╔══════════════════════════════════════════════════════════════════════════╗
║       🎮 FC26 GAMING BOT - MODULAR ARCHITECTURE 🎮                       ║
║         بوت FC26 - هيكل معياري احترافي 🔥                               ║
║                                                                          ║
║  🔥 FEATURES:                                                           ║
║  ✅ Modular architecture - هيكل معياري                                 ║
║  ✅ Easy maintenance - سهولة الصيانة                                   ║
║  ✅ Add new service = 1 line! - إضافة خدمة = سطر واحد!                 ║
║  ✅ Zero duplicates - بدون تكرار                                       ║
║  ✅ Message tagging system - نظام الوسم                                ║
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
