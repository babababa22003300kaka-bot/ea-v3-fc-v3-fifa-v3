# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📱 FC26 PHONE VALIDATOR - مدقق أرقام الهاتف              ║
# ║                     Phone Number Validation                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PhoneValidator:
    """Egyptian phone number validation"""
    
    # Egyptian mobile patterns
    EGYPTIAN_PATTERNS = {
        'vodafone': r'^010[0-9]{8}$',
        'etisalat': r'^011[0-9]{8}$', 
        'orange': r'^012[0-9]{8}$',
        'we': r'^015[0-9]{8}$',
        'general': r'^01[0125][0-9]{8}$'
    }
    
    @classmethod
    def validate_whatsapp(cls, phone: str) -> Dict[str, Any]:
        """
        Validate Egyptian WhatsApp phone number
        
        Args:
            phone (str): Phone number to validate
            
        Returns:
            Dict[str, Any]: Validation result with formatted data
        """
        try:
            # Clean input - remove all non-digits
            cleaned = re.sub(r'[^\d]', '', phone)
            
            # Validate Egyptian mobile pattern
            if not re.match(cls.EGYPTIAN_PATTERNS['general'], cleaned):
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
                "clickable": f"`{cleaned}`"  # For Telegram click-to-copy
            }
            
        except Exception as e:
            logger.error(f"Phone validation error: {e}")
            return {
                "valid": False,
                "error": "❌ حدث خطأ في التحقق من الرقم"
            }
    
    @classmethod
    def _get_network_provider(cls, phone: str) -> str:
        """Get network provider from phone number"""
        if phone.startswith('010'):
            return 'vodafone'
        elif phone.startswith('011'):
            return 'etisalat'
        elif phone.startswith('012'):
            return 'orange'
        elif phone.startswith('015'):
            return 'we'
        else:
            return 'unknown'
    
    @classmethod
    def format_for_display(cls, phone: str, include_country_code: bool = False) -> str:
        """Format phone number for display"""
        cleaned = re.sub(r'[^\d]', '', phone)
        
        if include_country_code:
            return f"+20 {cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"
        else:
            return f"{cleaned[:3]} {cleaned[3:6]} {cleaned[6:]}"
    
    @classmethod
    def is_valid_egyptian_mobile(cls, phone: str) -> bool:
        """Quick check if phone is valid Egyptian mobile"""
        cleaned = re.sub(r'[^\d]', '', phone)
        return bool(re.match(cls.EGYPTIAN_PATTERNS['general'], cleaned))
    
    @classmethod
    def get_validation_tips(cls) -> str:
        """Get validation tips message"""
        return """💡 **نصائح لإدخال رقم الواتساب:**

🔹 **يجب أن يبدأ الرقم بـ:**
   • 010 (فودافون)
   • 011 (اتصالات)  
   • 012 (أورانج)
   • 015 (وي)

🔹 **يجب أن يتكون من 11 رقماً بالضبط**

🔹 **أمثلة صحيحة:**
   • 01012345678
   • 01112345678
   • 01212345678
   • 01512345678

❌ **أمثلة خاطئة:**
   • +201012345678 (لا تضع كود الدولة)
   • 1012345678 (ناقص صفر في البداية)
   • 010123456 (أقل من 11 رقم)"""