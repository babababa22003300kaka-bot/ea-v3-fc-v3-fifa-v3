# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                    🏷️ MESSAGE TAGGING SYSTEM                            ║
# ║                  نظام وسم الرسائل الموحد                                ║
# ║            منع الردود المزدوجة - Zero Duplicate Responses              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
🏷️ نظام وسم الرسائل الموحد
Unified Message Tagging System

الهدف:
-------
منع الردود المزدوجة عن طريق وسم الرسائل التي تمت معالجتها داخل ConversationHandler
حتى لا يتدخل global_recovery_router ويرسل رداً ثانياً.

الاستخدام:
----------
في بداية كل handler:
    MessageTagger.mark_as_handled(context)

في global_recovery_router:
    if MessageTagger.check_and_clear(context):
        return  # الرسالة معالجة مسبقاً - تجاهلها

الميزات:
--------
✅ كود موحد في مكان واحد
✅ سهل الصيانة
✅ تنظيف تلقائي للذاكرة
✅ طباعة تتبع واضحة
"""

from functools import wraps


class MessageTagger:
    """
    نظام وسم الرسائل لمنع الردود المزدوجة

    يستخدم chat_data لتخزين علامة "_update_handled"
    التي تشير إلى أن الرسالة تمت معالجتها من قبل handler معين
    """

    TAG_KEY = "_update_handled"

    @staticmethod
    def mark_as_handled(context) -> None:
        """
        وضع علامة على الرسالة أنها تمت معالجتها

        Args:
            context: telegram.ext.ContextTypes.DEFAULT_TYPE

        Usage:
            @handler
            async def my_handler(update, context):
                MessageTagger.mark_as_handled(context)
                # ... باقي الكود
        """
        context.chat_data[MessageTagger.TAG_KEY] = True
        print(f"   🏷️ [TAGGER] Message marked as handled")

    @staticmethod
    def is_handled(context) -> bool:
        """
        التحقق من وجود علامة المعالجة

        Args:
            context: telegram.ext.ContextTypes.DEFAULT_TYPE

        Returns:
            bool: True إذا تمت معالجة الرسالة مسبقاً

        Usage:
            if MessageTagger.is_handled(context):
                return  # تجاهل الرسالة
        """
        return context.chat_data.get(MessageTagger.TAG_KEY, False)

    @staticmethod
    def clear_tag(context) -> None:
        """
        مسح علامة المعالجة (تنظيف الذاكرة)

        Args:
            context: telegram.ext.ContextTypes.DEFAULT_TYPE

        Usage:
            MessageTagger.clear_tag(context)
        """
        if MessageTagger.TAG_KEY in context.chat_data:
            context.chat_data.pop(MessageTagger.TAG_KEY)
            print(f"   🧹 [TAGGER] Tag cleared")

    @staticmethod
    def check_and_clear(context) -> bool:
        """
        فحص ومسح العلامة في خطوة واحدة (للأداء)

        Args:
            context: telegram.ext.ContextTypes.DEFAULT_TYPE

        Returns:
            bool: True إذا كانت الرسالة معالجة سابقاً

        Usage:
            في global_recovery_router:

            if MessageTagger.check_and_clear(context):
                print("رسالة معالجة - تجاهل")
                return
        """
        is_handled = MessageTagger.is_handled(context)

        if is_handled:
            MessageTagger.clear_tag(context)
            print(f"   🏷️ [TAGGER] Message already handled")
            print(f"   ⏭️ [TAGGER] Skipping to prevent duplicate response")
            print(f"   🧹 [TAGGER] Tag cleared - ready for next message")
            return True

        return False


# ═══════════════════════════════════════════════════════════════════════════
# 🎁 BONUS: AUTO-TAG DECORATOR (اختياري - للمطورين المتقدمين)
# ═══════════════════════════════════════════════════════════════════════════


def auto_tag_handler(func):
    """
    Decorator لوسم الرسائل تلقائياً

    يوفر عليك استدعاء MessageTagger.mark_as_handled() يدوياً

    Usage:
    ------
    @auto_tag_handler
    async def my_handler(update, context):
        # الوسم يحدث تلقائياً!
        user_id = update.effective_user.id
        # ... باقي الكود

    ⚠️ ملاحظة:
    ----------
    استخدام الـ decorator اختياري.
    الطريقة اليدوية (mark_as_handled) أوضح وأسهل للمبتدئين.
    """

    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        # وسم تلقائي قبل تنفيذ الـ handler
        MessageTagger.mark_as_handled(context)

        # تنفيذ الـ handler الأصلي
        return await func(update, context, *args, **kwargs)

    return wrapper


# ═══════════════════════════════════════════════════════════════════════════
# 📊 STATISTICS & DEBUGGING (اختياري)
# ═══════════════════════════════════════════════════════════════════════════


class MessageTaggerStats:
    """
    إحصائيات نظام الوسم (للمراقبة والتطوير)

    يمكن استخدامها لتتبع أداء النظام وكشف المشاكل
    """

    _tags_created = 0
    _tags_checked = 0
    _duplicates_prevented = 0

    @classmethod
    def increment_created(cls):
        """عداد الوسوم المنشأة"""
        cls._tags_created += 1

    @classmethod
    def increment_checked(cls):
        """عداد الفحوصات"""
        cls._tags_checked += 1

    @classmethod
    def increment_prevented(cls):
        """عداد الردود المزدوجة المنعة"""
        cls._duplicates_prevented += 1

    @classmethod
    def get_stats(cls) -> dict:
        """الحصول على الإحصائيات"""
        return {
            "tags_created": cls._tags_created,
            "tags_checked": cls._tags_checked,
            "duplicates_prevented": cls._duplicates_prevented,
            "efficiency": (
                f"{(cls._duplicates_prevented / cls._tags_checked * 100):.2f}%"
                if cls._tags_checked > 0
                else "0%"
            ),
        }

    @classmethod
    def print_stats(cls):
        """طباعة الإحصائيات"""
        stats = cls.get_stats()
        print("\n" + "=" * 80)
        print("📊 [MESSAGE TAGGER STATISTICS]")
        print("=" * 80)
        print(f"   🏷️ Tags Created: {stats['tags_created']}")
        print(f"   🔍 Tags Checked: {stats['tags_checked']}")
        print(f"   🛡️ Duplicates Prevented: {stats['duplicates_prevented']}")
        print(f"   📈 Efficiency: {stats['efficiency']}")
        print("=" * 80 + "\n")


# ═══════════════════════════════════════════════════════════════════════════
# نسخة محسّنة مع إحصائيات (اختياري)
# ═══════════════════════════════════════════════════════════════════════════


class MessageTaggerWithStats(MessageTagger):
    """
    نسخة محسّنة من MessageTagger مع تتبع الإحصائيات

    استخدمها بدلاً من MessageTagger إذا أردت مراقبة الأداء:

    from utils.message_tagger import MessageTaggerWithStats as MessageTagger
    """

    @staticmethod
    def mark_as_handled(context) -> None:
        MessageTagger.mark_as_handled(context)
        MessageTaggerStats.increment_created()

    @staticmethod
    def check_and_clear(context) -> bool:
        MessageTaggerStats.increment_checked()
        result = MessageTagger.check_and_clear(context)
        if result:
            MessageTaggerStats.increment_prevented()
        return result


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 TESTING (للتطوير فقط)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Testing MessageTagger...\n")

    # محاكاة context
    class MockContext:
        def __init__(self):
            self.chat_data = {}

    context = MockContext()

    # اختبار 1: وسم الرسالة
    print("Test 1: Marking message...")
    MessageTagger.mark_as_handled(context)
    assert MessageTagger.is_handled(context) == True
    print("✅ Passed\n")

    # اختبار 2: فحص ومسح
    print("Test 2: Check and clear...")
    result = MessageTagger.check_and_clear(context)
    assert result == True
    assert MessageTagger.is_handled(context) == False
    print("✅ Passed\n")

    # اختبار 3: رسالة غير موسومة
    print("Test 3: Untagged message...")
    context2 = MockContext()
    assert MessageTagger.is_handled(context2) == False
    assert MessageTagger.check_and_clear(context2) == False
    print("✅ Passed\n")

    print("🎉 All tests passed!")
    print("\n📝 MessageTagger is ready for production!")
