# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    🗂️ SESSION BUCKET SYSTEM                             ║
# ║                  نظام عزل بيانات الجلسات                               ║
# ║            منع تداخل البيانات بين الخدمات المختلفة                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
🗂️ نظام مساحات العمل المعزولة (Session Buckets)

الهدف:
-------
منع تداخل بيانات الخدمات المختلفة داخل context.user_data.
بدلاً من حذف كل البيانات عند إنهاء محادثة، نحذف فقط بيانات المحادثة المحددة.

الاستخدام:
----------
بدلاً من:
    context.user_data['platform'] = 'pc'
    context.user_data.clear()

استخدم:
    bucket(context, 'reg')['platform'] = 'pc'
    clear_bucket(context, 'reg')

الفوائد:
--------
✅ عزل كامل بين الخدمات (reg, sell, admin)
✅ إنهاء محادثة لا يؤثر على محادثة أخرى
✅ أمان أعلى للبيانات
✅ متوافق مع Persistence
"""


def bucket(context, name: str) -> dict:
    """
    الحصول على مساحة عمل معزولة داخل context.user_data

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
        name: اسم المساحة (مثل 'reg', 'sell', 'admin')

    Returns:
        dict: قاموس خاص بهذه المساحة فقط

    Example:
        # في handlers التسجيل:
        bucket(context, 'reg')['platform'] = 'playstation'

        # في handlers البيع:
        bucket(context, 'sell')['amount'] = 5000

        # لا يتداخلان!
    """
    # إنشاء المساحة الرئيسية إذا لم تكن موجودة
    if '_buckets' not in context.user_data:
        context.user_data['_buckets'] = {}

    # إنشاء المساحة الفرعية إذا لم تكن موجودة
    if name not in context.user_data['_buckets']:
        context.user_data['_buckets'][name] = {}

    return context.user_data['_buckets'][name]


def clear_bucket(context, name: str) -> None:
    """
    مسح مساحة عمل محددة فقط (بدون التأثير على المساحات الأخرى)

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
        name: اسم المساحة المراد مسحها

    Example:
        # مسح بيانات التسجيل فقط
        clear_bucket(context, 'reg')

        # بيانات البيع تبقى كما هي!
        bucket(context, 'sell').get('amount')  # ✅ موجودة
    """
    if '_buckets' in context.user_data:
        if name in context.user_data['_buckets']:
            context.user_data['_buckets'][name].clear()
            print(f"   🧹 [BUCKET] Cleared bucket: {name}")


def get_all_buckets(context) -> dict:
    """
    الحصول على جميع المساحات (للفحص والتطوير)

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE

    Returns:
        dict: جميع المساحات الموجودة
    """
    return context.user_data.get('_buckets', {})


def has_bucket(context, name: str) -> bool:
    """
    التحقق من وجود مساحة عمل

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
        name: اسم المساحة

    Returns:
        bool: True إذا كانت المساحة موجودة وغير فارغة
    """
    if '_buckets' not in context.user_data:
        return False
    return name in context.user_data['_buckets'] and bool(context.user_data['_buckets'][name])


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 TESTING (للتطوير فقط)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Testing Session Bucket System...\n")

    # محاكاة context
    class MockContext:
        def __init__(self):
            self.user_data = {}

    context = MockContext()

    # اختبار 1: إنشاء مساحات منفصلة
    print("Test 1: Creating separate buckets...")
    bucket(context, 'reg')['platform'] = 'playstation'
    bucket(context, 'sell')['amount'] = 5000

    assert bucket(context, 'reg')['platform'] == 'playstation'
    assert bucket(context, 'sell')['amount'] == 5000
    print("✅ Passed\n")

    # اختبار 2: عزل البيانات
    print("Test 2: Data isolation...")
    clear_bucket(context, 'reg')

    assert 'platform' not in bucket(context, 'reg')
    assert bucket(context, 'sell')['amount'] == 5000  # لم تتأثر!
    print("✅ Passed\n")

    # اختبار 3: has_bucket
    print("Test 3: has_bucket check...")
    assert has_bucket(context, 'sell') == True
    assert has_bucket(context, 'reg') == False
    print("✅ Passed\n")

    print("🎉 All tests passed!")
    print("\n📝 Session Bucket System is ready for production!")
