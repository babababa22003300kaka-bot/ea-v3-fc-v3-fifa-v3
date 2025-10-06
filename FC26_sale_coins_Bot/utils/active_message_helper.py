# ╔══════════════════════════════════════════════════════════════════════════╗
# ║           🔥 ACTIVE MESSAGE SYSTEM - نظام الرسائل النشطة                ║
# ║             منظف المحادثات التلقائي - Conversation Cleaner              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
🔥 نظام الرسائل النشطة - Active Message System

الهدف:
-------
الحفاظ على نظافة المحادثة بتعديل رسالة واحدة بدلاً من إرسال رسائل جديدة.

الآلية:
-------
1. كل مستخدم له رسالة نشطة واحدة فقط (message_id محفوظ في bucket)
2. عند إرسال رسالة جديدة:
   - لو فيه رسالة قديمة → تعديلها
   - لو مفيش → إرسال رسالة جديدة وحفظ الـ ID
3. عند انتهاء المحادثة → مسح الـ ID من الذاكرة

الفوائد:
--------
✅ محادثات نظيفة ومنظمة
✅ تجربة مستخدم احترافية
✅ سهل التكامل (دالة واحدة فقط)
✅ متوافق مع bucket system الموجود
✅ معالجة ذكية للأخطاء (لو الرسالة محذوفة)

الاستخدام:
----------
# بدلاً من:
await update.message.reply_text(text, reply_markup=keyboard, parse_mode="HTML")

# استخدم:
await send_or_edit(context, update.effective_chat.id, text, keyboard)

# في نهاية المحادثة:
clear_active_message(context)
"""

from telegram.error import BadRequest
from utils.session_bucket import bucket, clear_bucket
import logging

logger = logging.getLogger(__name__)


async def send_or_edit(
    context,
    chat_id: int,
    text: str,
    keyboard=None,
    parse_mode: str = "HTML",
):
    """
    🔥 الدالة الرئيسية - إرسال أو تعديل الرسالة النشطة

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
        chat_id: معرف المحادثة
        text: نص الرسالة
        keyboard: InlineKeyboardMarkup (اختياري)
        parse_mode: نوع التنسيق (افتراضي: HTML)

    Returns:
        Message: الرسالة المرسلة/المعدلة

    الآلية:
    ------
    1. البحث عن message_id في active_message bucket
    2. لو موجود → محاولة التعديل
    3. لو التعديل فشل → إرسال رسالة جديدة
    4. لو مش موجود → إرسال رسالة جديدة مباشرة
    5. حفظ message_id الجديد

    Example:
        >>> await send_or_edit(
        ...     context,
        ...     update.effective_chat.id,
        ...     "✅ تم اختيار المنصة",
        ...     keyboard
        ... )
    """
    # الحصول على bucket الرسالة النشطة
    active_message_bucket = bucket(context, "active_message")
    message_id = active_message_bucket.get("message_id")

    print(f"\n🔥 [ACTIVE-MSG] send_or_edit called")
    print(f"   📍 Chat ID: {chat_id}")
    print(f"   📝 Message ID in bucket: {message_id}")

    try:
        if message_id:
            # محاولة تعديل الرسالة الموجودة
            print(f"   ✏️ [ACTIVE-MSG] Attempting to EDIT message {message_id}")

            message = await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
            )

            print(f"   ✅ [ACTIVE-MSG] Message EDITED successfully")
            return message

        else:
            # لا توجد رسالة قديمة - إرسال رسالة جديدة
            print(f"   📤 [ACTIVE-MSG] No old message - SENDING new one")

            message = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
            )

            # حفظ message_id الجديد
            active_message_bucket["message_id"] = message.message_id
            print(f"   ✅ [ACTIVE-MSG] New message SENT - ID: {message.message_id}")
            print(f"   💾 [ACTIVE-MSG] Message ID saved in bucket")
            return message

    except BadRequest as e:
        # فشل التعديل (الرسالة محذوفة أو قديمة جداً)
        print(f"   ⚠️ [ACTIVE-MSG] Edit FAILED (BadRequest): {e}")
        print(f"   🔄 [ACTIVE-MSG] Fallback: SENDING new message")

        try:
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
            )

            # تحديث message_id الجديد
            active_message_bucket["message_id"] = message.message_id
            print(f"   ✅ [ACTIVE-MSG] Fallback message SENT - ID: {message.message_id}")
            print(f"   💾 [ACTIVE-MSG] Message ID updated in bucket")
            return message

        except Exception as fallback_error:
            print(f"   ❌ [ACTIVE-MSG] Fallback FAILED: {fallback_error}")
            logger.error(
                f"Failed to send message after edit failed: {fallback_error}"
            )
            return None

    except Exception as e:
        # خطأ غير متوقع
        print(f"   ❌ [ACTIVE-MSG] Unexpected error: {e}")
        logger.error(f"Unexpected error in send_or_edit: {e}")
        return None


def clear_active_message(context):
    """
    🧹 مسح الرسالة النشطة من الذاكرة

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE

    Usage:
        يُستخدم عند انتهاء المحادثة (ConversationHandler.END)

    Example:
        >>> clear_active_message(context)
        >>> return ConversationHandler.END

    Notes:
        - لا يحذف الرسالة من Telegram (تبقى في المحادثة)
        - فقط يمسح message_id من الذاكرة
        - المحادثة القادمة هتبدأ برسالة جديدة
    """
    print(f"\n🧹 [ACTIVE-MSG] Clearing active message from memory")
    clear_bucket(context, "active_message")
    print(f"   ✅ [ACTIVE-MSG] Active message bucket cleared")


def get_active_message_id(context):
    """
    🔍 الحصول على message_id الحالي (للفحص والتطوير)

    Args:
        context: telegram.ext.ContextTypes.DEFAULT_TYPE

    Returns:
        int or None: message_id إذا كان موجود

    Example:
        >>> message_id = get_active_message_id(context)
        >>> print(f"Current active message: {message_id}")
    """
    return bucket(context, "active_message").get("message_id")


# ═══════════════════════════════════════════════════════════════════════════
# 🧪 TESTING (للتطوير فقط)
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧪 Testing Active Message Helper...\n")

    # محاكاة context
    class MockContext:
        def __init__(self):
            self.user_data = {}

    context = MockContext()

    # اختبار 1: حفظ message_id
    print("Test 1: Saving message_id...")
    bucket(context, "active_message")["message_id"] = 12345
    assert get_active_message_id(context) == 12345
    print("✅ Passed\n")

    # اختبار 2: مسح الرسالة النشطة
    print("Test 2: Clearing active message...")
    clear_active_message(context)
    assert get_active_message_id(context) is None
    print("✅ Passed\n")

    print("🎉 All tests passed!")
    print("\n📝 Active Message Helper is ready for production!")
