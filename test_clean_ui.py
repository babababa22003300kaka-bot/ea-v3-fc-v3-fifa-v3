#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار التعديلات الجديدة
"""

print("=" * 50)
print("🔍 اختبار البوت - واجهة نظيفة")
print("=" * 50)

# اختبار قراءة الملف
try:
    with open('/home/user/webapp/app_complete.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من التعديلات
    checks = {
        "إزالة معلومات إضافية من الملف الشخصي": "رصيد العملات:" not in content or content.count("رصيد العملات:") == 0,
        "تغيير القائمة لأزرار تفاعلية": "InlineKeyboardMarkup(keyboard)" in content and "get_main_menu_keyboard" in content,
        "معالج الأزرار الجديد": "handle_menu_buttons" in content,
        "رسالة ترحيب نظيفة": "بوت FC 26 - أفضل مكان لتداول العملات" in content,
        "معالج النصوص المحدث": "استخدم الأوامر التالية" in content
    }
    
    print("\n📋 فحص التعديلات:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
    
    # البحث عن السطور المحذوفة
    deleted_lines = [
        "💰 رصيد العملات:",
        "⭐ نقاط الولاء:",
        "🏆 المستوى:",
        "📊 المعاملات:"
    ]
    
    print("\n🗑️ السطور المحذوفة من الملف الشخصي:")
    profile_section = content[content.find("profile_text = f"):content.find("profile_text = f") + 500] if "profile_text = f" in content else ""
    
    for line in deleted_lines:
        if line in profile_section:
            print(f"  ❌ {line} - لازال موجود!")
        else:
            print(f"  ✅ {line} - تم حذفه")
    
    # التحقق من الأزرار التفاعلية
    print("\n🎮 الأزرار التفاعلية:")
    buttons = ["buy_coins", "sell_coins", "profile", "wallet", "transactions", "offers", "settings", "support", "delete_account"]
    for button in buttons:
        if f'callback_data="{button}"' in content:
            print(f"  ✅ {button}")
        else:
            print(f"  ❌ {button}")
    
    print("\n" + "=" * 50)
    if all(checks.values()):
        print("✅ جميع التعديلات تمت بنجاح!")
        print("🎉 البوت جاهز بواجهة نظيفة!")
    else:
        print("⚠️ بعض التعديلات تحتاج مراجعة")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ خطأ: {e}")

print("\n📝 للرفع على GitHub:")
print("1. git add app_complete.py")
print("2. git commit -m '🎨 واجهة نظيفة'")
print("3. git push origin main")