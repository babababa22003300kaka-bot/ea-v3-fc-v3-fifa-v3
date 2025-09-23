# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💳 FC26 PAYMENT VALIDATOR - مدقق بيانات الدفع             ║
# ║                     Payment Details Validation                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PaymentValidator:
    """Payment methods validation"""
    
    @classmethod
    def validate_payment_details(cls, payment_method: str, details: str) -> Dict[str, Any]:
        """
        Validate payment details based on payment method
        
        Args:
            payment_method (str): Payment method type
            details (str): Payment details to validate
            
        Returns:
            Dict[str, Any]: Validation result with formatted data
        """
        try:
            # Clean input for mobile wallets and Telda
            cleaned = re.sub(r'[^\d]', '', details) if payment_method != 'instapay' else details.strip()
            
            # Route to specific validator
            if payment_method in ['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash', 'bank_wallet']:
                return cls._validate_mobile_wallet(cleaned, payment_method)
            elif payment_method == 'telda':
                return cls._validate_telda_card(cleaned)
            elif payment_method == 'instapay':
                return cls._validate_instapay(details)
            else:
                return {"valid": False, "error": "❌ طريقة دفع غير معروفة"}
                
        except Exception as e:
            logger.error(f"Payment validation error: {e}")
            return {"valid": False, "error": "❌ حدث خطأ في التحقق من بيانات الدفع"}
    
    @classmethod
    def _validate_mobile_wallet(cls, cleaned: str, payment_method: str) -> Dict[str, Any]:
        """Validate mobile wallet phone number"""
        if not re.match(r'^01[0125][0-9]{8}$', cleaned):
            return {
                "valid": False,
                "error": "❌ رقم غير صحيح. يجب أن يبدأ بـ 010/011/012/015 ويتكون من 11 رقماً",
            }
        
        # Check if number matches payment method (optional validation)
        provider_map = {
            'vodafone_cash': '010',
            'etisalat_cash': '011', 
            'orange_cash': '012',
            'we_cash': '015'
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
            "clickable": f"`{cleaned}`",
            "warning": warning
        }
    
    @classmethod
    def _validate_telda_card(cls, cleaned: str) -> Dict[str, Any]:
        """Validate Telda card number"""
        if len(cleaned) != 16 or not cleaned.isdigit():
            return {
                "valid": False,
                "error": "❌ رقم كارت تيلدا غير صحيح. يجب أن يتكون من 16 رقماً بالضبط",
            }
        
        # Format card number for display
        formatted = f"{cleaned[:4]}-{cleaned[4:8]}-{cleaned[8:12]}-{cleaned[12:16]}"
        
        return {
            "valid": True,
            "cleaned": cleaned,
            "formatted": formatted,
            "display": cleaned,
            "formatted_display": formatted,
            "clickable": f"`{cleaned}`",
            "masked": f"{cleaned[:4]}-****-****-{cleaned[12:16]}"  # For security
        }
    
    @classmethod 
    def _validate_instapay(cls, details: str) -> Dict[str, Any]:
        """Validate InstaPay URL"""
        details = details.strip()
        
        # Check for InstaPay domains
        if not ("instapay.com.eg" in details.lower() or "ipn.eg" in details.lower()):
            return {
                "valid": False,
                "error": "❌ رابط إنستاباي غير صحيح. يجب أن يحتوي على instapay.com.eg أو ipn.eg",
            }
        
        # Validate URL format
        if not details.startswith(('http://', 'https://')):
            details = 'https://' + details
        
        return {
            "valid": True,
            "cleaned": details,
            "formatted": details,
            "display": details,
            "clickable": f"`{details}`"
        }
    
    @classmethod
    def get_payment_instructions(cls, payment_method: str) -> str:
        """Get specific instructions for payment method"""
        instructions = {
            "vodafone_cash": "أدخل رقم فودافون كاش (11 رقماً يبدأ بـ 010)",
            "etisalat_cash": "أدخل رقم اتصالات كاش (11 رقماً يبدأ بـ 011)", 
            "orange_cash": "أدخل رقم أورانج كاش (11 رقماً يبدأ بـ 012)",
            "we_cash": "أدخل رقم وي كاش (11 رقماً يبدأ بـ 015)",
            "bank_wallet": "أدخل رقم المحفظة البنكية (11 رقماً لأي شبكة مصرية)",
            "telda": "أدخل رقم كارت تيلدا (16 رقماً بدون مسافات)",
            "instapay": "أدخل رابط إنستاباي الكامل\n**مثال:** https://instapay.com.eg/abc123"
        }
        
        return instructions.get(payment_method, "أدخل تفاصيل الدفع")
    
    @classmethod
    def get_payment_examples(cls, payment_method: str) -> str:
        """Get examples for payment method"""
        examples = {
            "vodafone_cash": "**مثال:** 01012345678",
            "etisalat_cash": "**مثال:** 01112345678",
            "orange_cash": "**مثال:** 01212345678", 
            "we_cash": "**مثال:** 01512345678",
            "bank_wallet": "**مثال:** 01012345678 (أي شبكة)",
            "telda": "**مثال:** 1234567890123456",
            "instapay": "**مثال:** https://instapay.com.eg/abc123"
        }
        
        return examples.get(payment_method, "")