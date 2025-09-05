#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار معالج رقم الواتساب
"""

import re

def test_whatsapp_validation():
    """اختبار التحقق من رقم الواتساب"""
    
    test_numbers = [
        "01080919791",  # الرقم من الصورة
        "01012345678",
        "01512345678",
        "01112345678",
        "01212345678",
        "02012345678",  # خطأ - بادئ بـ 020
        "0108091979",   # خطأ - 10 أرقام فقط
        "010809197911", # خطأ - 12 رقم
        "+201080919791", # مع كود الدولة
        "0 108 091 9791", # مع مسافات
    ]
    
    print("=" * 50)
    print("🔍 اختبار التحقق من أرقام الواتساب")
    print("=" * 50)
    
    for number in test_numbers:
        # تنظيف الرقم
        cleaned = re.sub(r'[^\d]', '', number)
        
        # التحقق
        if len(cleaned) == 11 and cleaned[:3] in ['010', '011', '012', '015']:
            result = f"✅ صحيح: {cleaned}"
        else:
            result = f"❌ خطأ: طول={len(cleaned)}, البداية={cleaned[:3] if len(cleaned) >= 3 else 'N/A'}"
        
        print(f"الرقم: {number:20} -> {result}")
    
    print("\n" + "=" * 50)
    print("✅ الاختبار اكتمل")
    print("=" * 50)

if __name__ == "__main__":
    test_whatsapp_validation()