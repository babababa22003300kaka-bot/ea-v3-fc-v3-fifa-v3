#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أدوات التحقق من صحة البيانات
"""

import re
from typing import Tuple, Optional

def validate_egyptian_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    التحقق من رقم الهاتف المصري
    """
    # إزالة المسافات والشرطات
    phone = phone.replace(" ", "").replace("-", "").replace("+20", "").replace("+2", "")
    
    # التحقق من الطول
    if len(phone) != 11:
        return False, "الرقم يجب أن يكون 11 رقم"
    
    # التحقق من البداية
    if not phone.startswith(('010', '011', '012', '015')):
        return False, "الرقم يجب أن يبدأ بـ 010, 011, 012, أو 015"
    
    # التحقق من أنه أرقام فقط
    if not phone.isdigit():
        return False, "الرقم يجب أن يحتوي على أرقام فقط"
    
    return True, phone

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    التحقق من صحة البريد الإلكتروني
    """
    email = email.strip().lower()
    
    # نمط بسيط للتحقق من الإيميل
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(pattern, email):
        return True, email
    else:
        return False, "البريد الإلكتروني غير صحيح"

def validate_card_digits(digits: str) -> Tuple[bool, Optional[str]]:
    """
    التحقق من آخر 4 أرقام من البطاقة
    """
    digits = digits.strip()
    
    if len(digits) != 4:
        return False, "يجب إدخال 4 أرقام فقط"
    
    if not digits.isdigit():
        return False, "يجب أن تكون أرقام فقط"
    
    return True, digits

def extract_instapay_link(text: str) -> Optional[str]:
    """
    استخراج رابط InstaPay من النص
    """
    # البحث عن روابط InstaPay المختلفة
    patterns = [
        r'https?://[^\s]+instapay[^\s]+',
        r'instapay\.com[^\s]+',
        r'link\.instapay[^\s]+',
        r'ipn\.eg/[^\s]+',
        r'instapay://[^\s]+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    # إذا كان النص يحتوي على @ قد يكون معرف InstaPay
    if '@' in text and len(text) < 50:
        return text.strip()
    
    return None

def validate_whatsapp(number: str) -> Tuple[bool, Optional[str]]:
    """
    التحقق من رقم واتساب
    """
    # نفس التحقق من رقم الهاتف العادي
    is_valid, cleaned = validate_egyptian_phone(number)
    
    if is_valid:
        # يمكن إضافة تحققات إضافية خاصة بواتساب
        return True, cleaned
    
    return is_valid, None

def clean_text_input(text: str) -> str:
    """
    تنظيف النص المدخل
    """
    # إزالة المسافات الزائدة
    text = ' '.join(text.split())
    
    # إزالة الرموز الخطرة
    dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()

def is_skip_command(text: str) -> bool:
    """
    التحقق من أمر التخطي
    """
    skip_words = ['تخطي', 'skip', 'تجاوز', 'next', 'التالي', 'لا', 'no']
    return text.strip().lower() in skip_words

def is_finish_command(text: str) -> bool:
    """
    التحقق من أمر الإنهاء
    """
    finish_words = ['انتهى', 'finish', 'done', 'تم', 'خلاص', 'كفاية', 'end']
    return text.strip().lower() in finish_words

def format_phone_display(phone: str) -> str:
    """
    تنسيق رقم الهاتف للعرض
    """
    if len(phone) == 11:
        return f"{phone[:4]} {phone[4:7]} {phone[7:]}"
    return phone

def mask_card_number(last_four: str) -> str:
    """
    إخفاء رقم البطاقة
    """
    return f"**** **** **** {last_four}"

def validate_platform_choice(choice: str) -> bool:
    """
    التحقق من اختيار المنصة
    """
    valid_platforms = ['playstation', 'xbox', 'pc']
    return choice.lower() in valid_platforms

def validate_payment_method(method: str) -> bool:
    """
    التحقق من طريقة الدفع
    """
    valid_methods = ['vodafone', 'instapay', 'visa', 'paypal', 'etisalat', 'orange', 'other']
    return method.lower() in valid_methods