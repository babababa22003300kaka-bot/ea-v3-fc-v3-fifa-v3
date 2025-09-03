"""
✅ التحقق من صحة المدخلات
"""

import re

class InputValidator:
    """التحقق من صحة المدخلات"""
    
    def validate_whatsapp(self, number):
        """التحقق من رقم الواتساب"""
        # إزالة المسافات والرموز
        cleaned = re.sub(r'[\s\-\(\)\+]', '', number)
        
        # التأكد من أنه أرقام فقط
        if not cleaned.isdigit():
            return False, None, "الرقم يجب أن يحتوي على أرقام فقط"
        
        # إضافة كود الدولة إذا لم يكن موجود
        if cleaned.startswith('0'):
            cleaned = '2' + cleaned  # مصر
        
        if not cleaned.startswith('2'):
            cleaned = '2' + cleaned
        
        # إضافة +
        cleaned = '+' + cleaned
        
        # التحقق من الطول
        if len(cleaned) < 10 or len(cleaned) > 15:
            return False, None, "رقم الواتساب غير صحيح"
        
        return True, cleaned, None
    
    def validate_egyptian_phone(self, phone):
        """التحقق من رقم مصري"""
        # إزالة المسافات
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # التحقق من الطول
        if len(cleaned) != 11:
            return False, f"الرقم يجب أن يكون 11 رقم (أنت أدخلت {len(cleaned)})"
        
        # التحقق من البداية
        valid_prefixes = ['010', '011', '012', '015']
        if not any(cleaned.startswith(p) for p in valid_prefixes):
            return False, f"الرقم يجب أن يبدأ بـ: {', '.join(valid_prefixes)}"
        
        # التأكد من أنه أرقام فقط
        if not cleaned.isdigit():
            return False, "الرقم يجب أن يحتوي على أرقام فقط"
        
        return True, None