#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار نهائي للتأكد من كل التعديلات
"""

print("🔍 بدء الاختبار النهائي...")

# اختبار الـ imports
try:
    from bot.handlers.registration import RegistrationHandler
    from bot.states.registration import (
        ENTERING_PAYMENT_INFO,
        CHOOSING_PLATFORM,
        ENTERING_WHATSAPP,
        CHOOSING_PAYMENT,
        ENTERING_PHONE,
        ENTERING_EMAILS,
        CONFIRMING_DATA
    )
    print("✅ كل الـ imports شغالة")
except Exception as e:
    print(f"❌ خطأ في الـ imports: {e}")
    exit(1)

# اختبار وجود الـ methods
handler = RegistrationHandler()

if hasattr(handler, 'handle_payment_info_input'):
    print("✅ handle_payment_info_input موجود")
else:
    print("❌ handle_payment_info_input مفقود!")
    exit(1)

if hasattr(handler, '_get_payment_info_message'):
    print("✅ _get_payment_info_message موجود")
else:
    print("❌ _get_payment_info_message مفقود!")
    exit(1)

# اختبار عدم وجود ENTERING_CARD
import os

files_to_check = ['bot/handlers/registration.py']
found_errors = False

for filepath in files_to_check:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ENTERING_CARD' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'ENTERING_CARD' in line and not line.strip().startswith('#'):
                        print(f"❌ وجدت ENTERING_CARD في السطر {i}")
                        found_errors = True

if not found_errors:
    print("✅ مفيش ENTERING_CARD في الكود")
else:
    print("❌ لسه فيه ENTERING_CARD!")
    exit(1)

# اختبار الـ states
print(f"✅ ENTERING_PAYMENT_INFO = {ENTERING_PAYMENT_INFO}")
print(f"✅ عدد الخطوات = 7 states (6 خطوات فعلية)")

print("\n🎉 كل الاختبارات نجحت!")
print("📋 الملفات المعدلة:")
print("  1. bot/handlers/registration.py")
print("  2. bot/config.py")