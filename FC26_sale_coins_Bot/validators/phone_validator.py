# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📱 FC26 PHONE VALIDATOR - مدقق أرقام الهاتف              ║
# ║                     Phone Number Validation                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PhoneValidator:
    """Egyptian phone number validation"""

    # Egyptian mobile patterns
    EGYPTIAN_PATTERNS = {
        "vodafone": r"^010[0-9]{8}$",
        "etisalat": r"^011[0-9]{8}$",
        "orange": r"^012[0-9]{8}$",
        "we": r"^015[0-9]{8}$",
        "general": r"^01[0125][0-9]{8}$",
    }

    @classmethod
    def validate_whatsapp(cls, phone: str) -> Dict[str, Any]:
        """
        Validate Egyptian WhatsApp phone number - أرقام فقط

        Args:
            phone (str): Phone number to validate

        Returns:
            Dict[str, Any]: Validation result with formatted data
        """
        try:
            # تحقق من وجود حروف أو رموز قبل التنظيف
            if re.search(r"[^\d\s]", phone):  # أي حاجة غير رقم أو مسافة
                return {
                    "valid": False,
                    "error": "❌ يُسمح بالأرقام فقط! لا تستخدم حروف أو رموز",
                }

            # تحقق من وجود مسافات كتير
            if phone.count(" ") > 3:  # لو المسافات كتير أوي
                return {
                    "valid": False,
                    "error": "❌ مسافات كتيرة! اكتب الرقم بدون مسافات أو بمسافات قليلة",
                }

            # Clean input - remove all non-digits
            cleaned = re.sub(r"[^\d]", "", phone)

            # تحقق من وجود أرقام أصلاً
            if not cleaned:
                return {
                    "valid": False,
                    "error": "❌ لم يتم العثور على أرقام! أدخل رقم واتساب صحيح",
                }

            # Validate Egyptian mobile pattern
            if not re.match(cls.EGYPTIAN_PATTERNS["general"], cleaned):
                return {
                    "valid": False,
                    "error": "❌ رقم غير صحيح. يجب أن يبدأ بـ 010/011/012/015 ويتكون من 11 رقماً",
                }

            # Determine network provider
            provider = cls._get_network_provider(cleaned)

            return {
                "valid": True,
                "cleaned": cleaned,
                "formatted": f"+20{cleaned}",
                "display": cleaned,  # Enhanced UX: Display without country code
                "provider": provider,
                "clickable": f"`{cleaned}`",  # For Telegram click-to-copy
            }

        except Exception as e:
            logger.error(f"Phone validation error: {e}")
            return {"valid": False, "error": "❌ حدث خطأ في التحقق من الرقم"}

    @classmethod
    def _get_network_provider(cls, phone: str) -> str:
        """Get network provider from phone number"""
        if phone.startswith("010"):
            return "vodafone"
        elif phone.startswith("011"):
            return "etisalat"
        elif phone.startswith("012"):
            return "orange"
        elif phone.startswith("015"):
            return "we"
        else:
            return "unknown"

    @classmethod
    def format_for_display(cls, phone: str, include_country_code: bool = False) -> str:
        """Format phone number for display"""
        cleaned = re.sub(r"[^\d]", "", phone)

        if include_country_code:
            return f"+20 {cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"
        else:
            return f"{cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"

    @classmethod
    def is_valid_egyptian_mobile(cls, phone: str) -> bool:
        """Quick check if phone is valid Egyptian mobile"""
        cleaned = re.sub(r"[^\d]", "", phone)
        return bool(re.match(cls.EGYPTIAN_PATTERNS["general"], cleaned))

    @classmethod
    def get_validation_tips(cls) -> str:
        """Get validation tips message"""
        return """💡 <b>قواعد إدخال رقم الواتساب:</b>

✅ <b>المسموح:</b>
   • أرقام فقط: 01012345678
   • مسافات قليلة: 010 123 456 78

❌ <b>غير مسموح:</b>
   • حروف: 010abc45678
   • رموز: 010-123-4567
   • أقواس: (010) 1234567

🔢 <b>الشكل الصحيح:</b>
   • يبدأ بـ: 010, 011, 012, 015
   • العدد: 11 رقم بالضبط

🔹 <b>أمثلة صحيحة:</b>
   • 01012345678
   • 01112345678
   • 01212345678
   • 01512345678

❌ <b>أمثلة خاطئة:</b>
   • +201012345678 (لا تضع كود الدولة)
   • 1012345678 (ناقص صفر في البداية)
   • 010123456 (أقل من 11 رقم)"""
