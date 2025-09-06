#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار حذف كل أزرار الكيبورد
"""

print("=" * 50)
print("🔍 اختبار البوت - بدون أزرار كيبورد نهائي")
print("=" * 50)

# اختبار قراءة الملف
try:
    with open('/home/user/webapp/app_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من حذف ReplyKeyboard
    checks = {
        "حذف ReplyKeyboardMarkup من imports": "ReplyKeyboardMarkup" not in content,
        "حذف ReplyKeyboardRemove": "ReplyKeyboardRemove" not in content,
        "حذف get_main_menu_keyboard": "def get_main_menu_keyboard" not in content,
        "كل الأزرار InlineKeyboard فقط": "InlineKeyboardMarkup" in content and "ReplyKeyboardMarkup" not in content,
        "لا يوجد resize_keyboard": "resize_keyboard" not in content
    }
    
    print("\n📋 فحص الحذف:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    # التحقق من عدم وجود reply_markup مع keyboards عادية
    import re
    reply_markups = re.findall(r'reply_markup=.*', content)
    
    print(f"\n📊 عدد reply_markup المتبقية: {len(reply_markups)}")
    
    # عرض الـ reply_markups المتبقية
    if reply_markups:
        print("\n📌 الـ reply_markups المتبقية (يجب أن تكون InlineKeyboard فقط):")
        for i, markup in enumerate(reply_markups[:5], 1):  # أول 5 فقط
            if "InlineKeyboard" in markup or "get_" in markup:
                print(f"  {i}. ✅ {markup[:60]}...")
            else:
                print(f"  {i}. ❌ {markup[:60]}...")
    
    # التحقق النهائي
    print("\n" + "=" * 50)
    if all(checks.values()):
        print("✅ تم حذف كل أزرار الكيبورد بنجاح!")
        print("🎉 البوت الآن يعمل بالأوامر والأزرار التفاعلية فقط!")
    else:
        print("⚠️ لا زال هناك بعض keyboards تحتاج حذف")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ خطأ: {e}")

print("\n📝 للرفع على GitHub:")
print("1. git add app_complete.py")
print("2. git commit -m '🗑️ حذف كل أزرار الكيبورد'")
print("3. git push origin main")