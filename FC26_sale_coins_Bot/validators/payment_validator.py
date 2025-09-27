# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💳 FC26 PAYMENT VALIDATOR - مدقق بيانات الدفع             ║
# ║                     Payment Details Validation                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PaymentValidator:
    """Payment methods validation"""

    @classmethod
    def validate_payment_details(
        cls, payment_method: str, details: str
    ) -> Dict[str, Any]:
        """
        Validate payment details based on payment method

        Args:
            payment_method (str): Payment method type
            details (str): Payment details to validate

        Returns:
            Dict[str, Any]: Validation result with formatted data
        """
        try:
            # للمحافظ المحمولة وتيلدا - تحقق من الحروف والرموز أولاً
            if payment_method in [
                "vodafone_cash",
                "etisalat_cash",
                "orange_cash",
                "we_cash",
                "bank_wallet",
                "telda",
            ]:
                # تحقق من وجود حروف أو رموز غير مسموحة
                if re.search(r"[^\d\s\-]", details):  # أي حاجة غير رقم أو مسافة أو شرطة
                    return {
                        "valid": False,
                        "error": "❌ يُسمح بالأرقام فقط! لا تستخدم حروف أو رموز",
                    }

                # تحقق من وجود مسافات أو شرطات كتير
                special_chars_count = details.count(" ") + details.count("-")
                if special_chars_count > 5:
                    return {
                        "valid": False,
                        "error": "❌ مسافات أو شرطات كتيرة! اكتب الرقم بشكل بسيط",
                    }

            # Clean input for mobile wallets and Telda
            cleaned = (
                re.sub(r"[^\d]", "", details)
                if payment_method != "instapay"
                else details.strip()
            )

            # Route to specific validator
            if payment_method in [
                "vodafone_cash",
                "etisalat_cash",
                "orange_cash",
                "we_cash",
                "bank_wallet",
            ]:
                return cls._validate_mobile_wallet(cleaned, payment_method)
            elif payment_method == "telda":
                return cls._validate_telda_card(cleaned)
            elif payment_method == "instapay":
                return cls._validate_instapay(details)
            else:
                return {"valid": False, "error": "❌ طريقة دفع غير معروفة"}

        except Exception as e:
            logger.error(f"Payment validation error: {e}")
            return {"valid": False, "error": "❌ حدث خطأ في التحقق من بيانات الدفع"}

    @classmethod
    def _validate_mobile_wallet(
        cls, cleaned: str, payment_method: str
    ) -> Dict[str, Any]:
        """Validate mobile wallet phone number"""

        # تحقق من وجود أرقام أصلاً
        if not cleaned:
            return {
                "valid": False,
                "error": "❌ لم يتم العثور على أرقام! أدخل رقم صحيح",
            }

        if not re.match(r"^01[0125][0-9]{8}$", cleaned):
            return {
                "valid": False,
                "error": "❌ رقم غير صحيح. يجب أن يبدأ بـ 010/011/012/015 ويتكون من 11 رقماً",
            }

        # Check if number matches payment method (optional validation)
        provider_map = {
            "vodafone_cash": "010",
            "etisalat_cash": "011",
            "orange_cash": "012",
            "we_cash": "015",
        }

        expected_prefix = provider_map.get(payment_method)
        if expected_prefix and not cleaned.startswith(expected_prefix):
            warning = f"⚠️ تحذير: الرقم لا يطابق شبكة {payment_method.replace('_cash', '').title()}"
        else:
            warning = None

        return {
            "valid": True,
            "cleaned": cleaned,
            "formatted": f"+20{cleaned}",
            "display": cleaned,
            "clickable": cleaned,
            "warning": warning,
        }

    @classmethod
    def _validate_telda_card(cls, cleaned: str) -> Dict[str, Any]:
        """Validate Telda card number"""

        # تحقق من وجود أرقام أصلاً
        if not cleaned:
            return {
                "valid": False,
                "error": "❌ لم يتم العثور على أرقام! أدخل رقم كارت صحيح",
            }

        if len(cleaned) != 16 or not cleaned.isdigit():
            return {
                "valid": False,
                "error": "❌ رقم كارت تيلدا غير صحيح. يجب أن يتكون من 16 رقماً بالضبط",
            }

        # Format card number for display (بدون تشفير)
        formatted = f"{cleaned[:4]}-{cleaned[4:8]}-{cleaned[8:12]}-{cleaned[12:16]}"

        return {
            "valid": True,
            "cleaned": cleaned,
            "formatted": formatted,
            "display": cleaned,
            "formatted_display": formatted,
            "clickable": cleaned,
        }

    @classmethod
    def _validate_instapay(cls, details: str) -> Dict[str, Any]:
        """Validate InstaPay URL and extract clean URL from any text"""
        details = details.strip()

        # Extract clean InstaPay URL from text using advanced regex patterns
        url_patterns = [
            # Pattern 1: Full URLs with https/http
            r"https?://[^\s]*(?:instapay\.com\.eg|ipn\.eg)[^\s]*",
            # Pattern 2: URLs without protocol
            r"(?:instapay\.com\.eg|ipn\.eg)[^\s]*",
            # Pattern 3: Find URLs within Arabic/English text
            r"(?:https?://)?(?:www\.)?(?:instapay\.com\.eg|ipn\.eg)[^\s\u0600-\u06FF]*",
            # Pattern 4: Extract from any position in text
            r"(?:https?://)?[^\s]*(?:instapay\.com\.eg|ipn\.eg)[^\s]*",
        ]

        clean_url = None

        # Try each pattern to extract URL
        for pattern in url_patterns:
            matches = re.findall(pattern, details, re.IGNORECASE)
            if matches:
                # Get the first match and clean it
                potential_url = matches[0].strip()

                # Clean URL from any trailing characters
                potential_url = re.sub(r"[^\w\-\.\/\:\?=&%]+$", "", potential_url)

                # Verify it contains the domain
                if any(
                    domain in potential_url.lower()
                    for domain in ["instapay.com.eg", "ipn.eg"]
                ):
                    clean_url = potential_url
                    break

        # If no URL found, check if text contains domain
        if not clean_url:
            if any(
                domain in details.lower() for domain in ["instapay.com.eg", "ipn.eg"]
            ):
                return {
                    "valid": False,
                    "error": "❌ تم العثور على نطاق إنستاباي ولكن لا يمكن استخراج رابط صحيح. أرسل الرابط كاملاً",
                }
            else:
                return {
                    "valid": False,
                    "error": "❌ لم يتم العثور على رابط إنستاباي. يجب أن يحتوي على instapay.com.eg أو ipn.eg",
                }

        # Add https if missing
        if not clean_url.startswith(("http://", "https://")):
            clean_url = "https://" + clean_url

        # Final validation
        if not any(
            domain in clean_url.lower() for domain in ["instapay.com.eg", "ipn.eg"]
        ):
            return {
                "valid": False,
                "error": "❌ رابط إنستاباي غير صحيح. يجب أن يحتوي على instapay.com.eg أو ipn.eg",
            }

        # Additional URL cleanup - remove any duplicate protocols
        clean_url = re.sub(r"https?://(https?://)+", "https://", clean_url)

        return {
            "valid": True,
            "cleaned": clean_url,
            "formatted": clean_url,
            "display": clean_url,
            "clickable": clean_url,
        }

    @classmethod
    def validate_whatsapp(cls, phone: str) -> Dict[str, Any]:
        """Validate WhatsApp phone number - 11 digits only starting with 010/011/012/015"""
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

            # Check exact length
            if len(cleaned) != 11:
                return {
                    "valid": False,
                    "error": "❌ رقم غير صحيح. يجب أن يتكون من 11 رقماً بالضبط",
                }

            # Check if starts with valid Egyptian prefixes
            if not re.match(r"^01[0125][0-9]{8}$", cleaned):
                return {
                    "valid": False,
                    "error": "❌ رقم غير صحيح. يجب أن يبدأ بـ 010/011/012/015 ويتكون من 11 رقماً",
                }

            return {
                "valid": True,
                "cleaned": cleaned,
                "formatted": f"+20{cleaned}",
                "display": cleaned,
                "clickable": cleaned,
            }

        except Exception as e:
            logger.error(f"WhatsApp validation error: {e}")
            return {"valid": False, "error": "❌ حدث خطأ في التحقق من رقم الواتساب"}

    @classmethod
    def get_payment_instructions(cls, payment_method: str) -> str:
        """Get specific instructions for payment method"""
        instructions = {
            "vodafone_cash": "أدخل رقم فودافون كاش (11 رقماً يبدأ بـ 010) - أرقام فقط!",
            "etisalat_cash": "أدخل رقم اتصالات كاش (11 رقماً يبدأ بـ 011) - أرقام فقط!",
            "orange_cash": "أدخل رقم أورانج كاش (11 رقماً يبدأ بـ 012) - أرقام فقط!",
            "we_cash": "أدخل رقم وي كاش (11 رقماً يبدأ بـ 015) - أرقام فقط!",
            "bank_wallet": "أدخل رقم المحفظة البنكية (11 رقماً لأي شبكة مصرية) - أرقام فقط!",
            "telda": "أدخل رقم كارت تيلدا (16 رقماً بدون مسافات) - أرقام فقط!",
            "instapay": "أدخل رابط إنستاباي الكامل\n**مثال:** https://instapay.com.eg/abc123",
        }

        return instructions.get(payment_method, "أدخل تفاصيل الدفع")

    @classmethod
    def get_payment_examples(cls, payment_method: str) -> str:
        """Get examples for payment method"""
        examples = {
            "vodafone_cash": "**مثال:** 01012345678 (أرقام فقط)",
            "etisalat_cash": "**مثال:** 01112345678 (أرقام فقط)",
            "orange_cash": "**مثال:** 01212345678 (أرقام فقط)",
            "we_cash": "**مثال:** 01512345678 (أرقام فقط)",
            "bank_wallet": "**مثال:** 01012345678 (أي شبكة - أرقام فقط)",
            "telda": "**مثال:** 1234567890123456 (16 رقم - أرقام فقط)",
            "instapay": "**مثال:** https://instapay.com.eg/abc123",
        }

        return examples.get(payment_method, "")
