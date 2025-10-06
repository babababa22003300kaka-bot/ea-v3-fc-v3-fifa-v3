# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    📊 SESSION MONITOR SYSTEM                             ║
# ║                  نظام مراقبة صحة الجلسات                                ║
# ║            فحص دوري لملف الجلسات والتنبيه بالمشاكل                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
📊 نظام مراقبة صحة الجلسات

الهدف:
-------
فحص دوري لملف الجلسات لاكتشاف المشاكل مبكراً.

الميزات:
--------
✅ فحص وجود الملف
✅ فحص حجم الملف (تحذير إذا تجاوز 50 MB)
✅ تقدير عدد الجلسات النشطة
✅ تحذيرات في الـ logs
✅ فحص كل 6 ساعات
"""

import pickle
from pathlib import Path


async def session_health_check(context):
    """
    فحص صحة ملف الجلسات

    يقوم بـ:
    1. التحقق من وجود الملف
    2. فحص حجم الملف
    3. تقدير عدد الجلسات النشطة
    4. طباعة تقرير في الـ logs

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    print(f"\n{'='*80}")
    print(f"📊 [SESSION-MONITOR] Health check started...")
    print(f"{'='*80}")

    session_file = Path("data/sessions.pkl")

    # فحص 1: وجود الملف
    if not session_file.exists():
        print(f"   ⚠️ [SESSION-MONITOR] Session file not found!")
        print(f"   📝 This is normal for first run")
        print(f"{'='*80}\n")
        return

    # فحص 2: حجم الملف
    try:
        size_bytes = session_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        print(f"   📁 [SESSION-MONITOR] File size: {size_mb:.2f} MB")

        if size_mb > 50:
            print(f"   ⚠️ [SESSION-MONITOR] WARNING: Large session file!")
            print(f"   💡 Consider clearing old sessions or optimizing")
        elif size_mb > 100:
            print(f"   🚨 [SESSION-MONITOR] CRITICAL: Very large session file!")
            print(f"   🔧 Immediate action required")
    except Exception as e:
        print(f"   ❌ [SESSION-MONITOR] Error checking file size: {e}")

    # فحص 3: محتوى الملف
    try:
        with open(session_file, "rb") as f:
            data = pickle.load(f)

        # تقدير عدد الجلسات
        if isinstance(data, dict):
            user_count = len(data.get("user_data", {}))
            chat_count = len(data.get("chat_data", {}))
            bot_data_exists = "bot_data" in data

            print(f"   👥 [SESSION-MONITOR] Active users: {user_count}")
            print(f"   💬 [SESSION-MONITOR] Active chats: {chat_count}")
            print(
                f"   🤖 [SESSION-MONITOR] Bot data: {'Yes' if bot_data_exists else 'No'}"
            )

            # تحذير إذا كان العدد كبير جداً
            if user_count > 10000:
                print(f"   ⚠️ [SESSION-MONITOR] Very high user count!")
        else:
            print(f"   ⚠️ [SESSION-MONITOR] Unexpected data format")

    except Exception as e:
        print(f"   ❌ [SESSION-MONITOR] Error reading session data: {e}")
        print(f"   💡 File might be corrupted or locked")

    print(f"{'='*80}")
    print(f"✅ [SESSION-MONITOR] Health check completed")
    print(f"{'='*80}\n")


def register_monitoring(app):
    """
    تسجيل وظيفة المراقبة في الجدول الزمني

    يقوم بتسجيل فحص صحة كل 6 ساعات

    Args:
        app: telegram.ext.Application
    """
    print("\n📊 [SESSION-MONITOR] Registering monitoring jobs...")

    # فحص صحة كل 6 ساعات
    app.job_queue.run_repeating(
        session_health_check,
        interval=21600,  # 6 ساعات بالثواني
        first=60,  # أول فحص بعد دقيقة من البدء
        name="session_monitoring",
    )
    print("   ✅ Health check scheduled: Every 6 hours")
    print("   ✅ First check: 1 minute after start")

    print("📊 [SESSION-MONITOR] Monitoring jobs registered successfully\n")


# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS (إضافية)
# ═══════════════════════════════════════════════════════════════════════════


def get_session_stats() -> dict:
    """
    الحصول على إحصائيات الجلسات

    Returns:
        dict: إحصائيات مفصلة
    """
    session_file = Path("data/sessions.pkl")

    if not session_file.exists():
        return {
            "exists": False,
            "size_mb": 0,
            "user_count": 0,
            "chat_count": 0,
        }

    stats = {
        "exists": True,
        "size_mb": round(session_file.stat().st_size / (1024 * 1024), 2),
    }

    try:
        with open(session_file, "rb") as f:
            data = pickle.load(f)

        if isinstance(data, dict):
            stats["user_count"] = len(data.get("user_data", {}))
            stats["chat_count"] = len(data.get("chat_data", {}))
            stats["has_bot_data"] = "bot_data" in data
        else:
            stats["user_count"] = 0
            stats["chat_count"] = 0
            stats["has_bot_data"] = False

    except:
        stats["user_count"] = 0
        stats["chat_count"] = 0
        stats["error"] = True

    return stats


def print_session_report():
    """
    طباعة تقرير مفصل عن الجلسات (للاستخدام اليدوي)
    """
    stats = get_session_stats()

    print("\n" + "=" * 80)
    print("📊 SESSION REPORT")
    print("=" * 80)

    if not stats["exists"]:
        print("❌ No session file found")
    else:
        print(f"✅ File exists: data/sessions.pkl")
        print(f"📁 Size: {stats['size_mb']} MB")
        print(f"👥 Users: {stats.get('user_count', 'N/A')}")
        print(f"💬 Chats: {stats.get('chat_count', 'N/A')}")
        print(f"🤖 Bot Data: {'Yes' if stats.get('has_bot_data') else 'No'}")

        if stats.get("error"):
            print("⚠️ Warning: Could not read session data")

    print("=" * 80 + "\n")
