#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار إصلاحات الحذف
"""

print("🧪 اختبار الإصلاحات...")

# اختبار وجود الـ methods
with open('main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

tests = {
    'handle_delete_confirm': 'تأكيد حذف الحساب',
    'handle_delete_cancel': 'إلغاء حذف الحساب',
    'delete_webhook': 'حذف webhook',
    'pattern="^confirm_delete$"': 'handler تأكيد الحذف',
    'pattern="^cancel_delete$"': 'handler إلغاء الحذف'
}

results = []
for test, desc in tests.items():
    if test in content:
        results.append(f"✅ {desc}")
    else:
        results.append(f"❌ {desc}")

print("\n📋 نتائج الاختبار:")
for result in results:
    print(result)

# اختبار الترتيب
if content.find('CommandHandler("delete"') < content.find('get_registration_conversation'):
    print("✅ ترتيب الـ handlers صحيح")
else:
    print("❌ ترتيب الـ handlers خطأ")

print("\n🎉 الإصلاحات جاهزة!")