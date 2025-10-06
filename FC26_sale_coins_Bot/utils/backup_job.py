# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    💾 BACKUP JOB SYSTEM                                  ║
# ║                  نظام النسخ الاحتياطي التلقائي                          ║
# ║            حماية بيانات الجلسات من الفقدان                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
💾 نظام النسخ الاحتياطي اليومي

الهدف:
-------
إنشاء نسخ احتياطية دورية من ملف الجلسات كطبقة أمان إضافية.

الميزات:
--------
✅ نسخ احتياطي يومي في وقت محدد (3 صباحاً)
✅ نسخ احتياطي عند بدء التشغيل (بعد ساعة)
✅ حذف تلقائي للنسخ القديمة (أكثر من 7 أيام)
✅ تنظيم في مجلد data/backups/
"""

import shutil
from datetime import datetime, timedelta, time
from pathlib import Path


async def daily_backup_job(context):
    """
    وظيفة النسخ الاحتياطي اليومي

    تقوم بـ:
    1. نسخ ملف الجلسات الرئيسي
    2. حفظه في مجلد backups/ باسم يحتوي على التاريخ
    3. حذف النسخ الأقدم من 7 أيام

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
    """
    print(f"\n{'='*80}")
    print(f"💾 [BACKUP-JOB] Starting daily backup...")
    print(f"{'='*80}")

    # التحقق من وجود الملف الأصلي
    source = Path("data/sessions.pkl")
    if not source.exists():
        print(f"   ⚠️ [BACKUP-JOB] Source file not found: {source}")
        print(f"{'='*80}\n")
        return

    # إنشاء مجلد النسخ الاحتياطي
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ [BACKUP-JOB] Backup directory ready: {backup_dir}")

    # إنشاء اسم الملف بالتاريخ
    today = datetime.now().strftime("%Y%m%d")
    backup_path = backup_dir / f"sessions_{today}.pkl"

    try:
        # نسخ الملف
        shutil.copy2(source, backup_path)
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        print(
            f"   ✅ [BACKUP-JOB] Backup created: {backup_path.name} ({size_mb:.2f} MB)"
        )
    except Exception as e:
        print(f"   ❌ [BACKUP-JOB] Failed to create backup: {e}")
        print(f"{'='*80}\n")
        return

    # حذف النسخ القديمة
    print(f"   🧹 [BACKUP-JOB] Cleaning old backups...")
    cutoff = datetime.now() - timedelta(days=7)
    deleted_count = 0

    for backup_file in backup_dir.glob("sessions_*.pkl"):
        try:
            # استخراج التاريخ من اسم الملف
            date_str = backup_file.stem.split("_")[1]
            file_date = datetime.strptime(date_str, "%Y%m%d")

            # حذف إذا كان أقدم من 7 أيام
            if file_date < cutoff:
                backup_file.unlink()
                deleted_count += 1
                print(f"      🗑️ Deleted old backup: {backup_file.name}")
        except Exception as e:
            print(f"      ⚠️ Error processing {backup_file.name}: {e}")

    if deleted_count == 0:
        print(f"      ✅ No old backups to delete")
    else:
        print(f"      ✅ Deleted {deleted_count} old backup(s)")

    print(f"{'='*80}")
    print(f"✅ [BACKUP-JOB] Daily backup completed successfully")
    print(f"{'='*80}\n")


def register_backup_job(app):
    """
    تسجيل وظائف النسخ الاحتياطي في الجدول الزمني

    يقوم بتسجيل:
    1. نسخ احتياطي يومي في الساعة 3 صباحاً
    2. نسخ احتياطي عند بدء التشغيل (بعد ساعة)

    Args:
        app: telegram.ext.Application
    """
    print("\n💾 [BACKUP-SYSTEM] Registering backup jobs...")

    # نسخ احتياطي يومي في 3 صباحاً
    app.job_queue.run_daily(
        daily_backup_job,
        time=time(hour=3, minute=0),
        name="daily_backup",
    )
    print("   ✅ Daily backup scheduled: 03:00 AM")

    # نسخ احتياطي بعد ساعة من البدء (احترازي)
    app.job_queue.run_once(
        daily_backup_job,
        when=3600,  # 1 ساعة بالثواني
        name="startup_backup",
    )
    print("   ✅ Startup backup scheduled: 1 hour after start")

    print("💾 [BACKUP-SYSTEM] Backup jobs registered successfully\n")


# ═══════════════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS (إضافية)
# ═══════════════════════════════════════════════════════════════════════════


def list_backups() -> list:
    """
    عرض قائمة بجميع النسخ الاحتياطية الموجودة

    Returns:
        list: قائمة بأسماء الملفات وأحجامها
    """
    backup_dir = Path("data/backups")
    if not backup_dir.exists():
        return []

    backups = []
    for backup_file in sorted(backup_dir.glob("sessions_*.pkl"), reverse=True):
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        backups.append(
            {
                "name": backup_file.name,
                "date": backup_file.stem.split("_")[1],
                "size_mb": round(size_mb, 2),
            }
        )

    return backups


def restore_from_backup(backup_name: str) -> bool:
    """
    استعادة من نسخة احتياطية

    Args:
        backup_name: اسم ملف النسخة الاحتياطية

    Returns:
        bool: True إذا نجحت العملية

    ⚠️ تحذير: هذه الدالة خطيرة! تُستخدم فقط في حالات الطوارئ
    """
    backup_file = Path("data/backups") / backup_name
    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_name}")
        return False

    session_file = Path("data/sessions.pkl")

    try:
        # إنشاء نسخة احتياطية من الملف الحالي أولاً
        if session_file.exists():
            emergency_backup = Path("data/sessions_emergency_backup.pkl")
            shutil.copy2(session_file, emergency_backup)
            print(f"   💾 Emergency backup created: {emergency_backup.name}")

        # استعادة من النسخة الاحتياطية
        shutil.copy2(backup_file, session_file)
        print(f"   ✅ Restored from: {backup_name}")
        return True

    except Exception as e:
        print(f"   ❌ Restore failed: {e}")
        return False
