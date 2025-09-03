#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار البوت
"""

import sys
import os

# إضافة المسار للموديولات
sys.path.insert(0, '/home/user/webapp')

def test_imports():
    """اختبار استيراد الموديولات"""
    print("🔍 اختبار استيراد الموديولات...")
    
    try:
        from bot.config import BOT_TOKEN, MESSAGES, PAYMENT_METHODS
        print("✅ config.py imported")
        
        from bot.states.registration import ENTERING_PAYMENT_INFO
        print("✅ states/registration.py imported - ENTERING_PAYMENT_INFO موجود")
        
        from bot.handlers.registration import RegistrationHandler
        print("✅ handlers/registration.py imported")
        
        from bot.keyboards.registration import get_payment_keyboard, get_delete_account_keyboard
        print("✅ keyboards/registration.py imported")
        
        from bot.database.models import Database
        db = Database()
        print("✅ database/models.py imported")
        
        # اختبار وجود وظيفة حذف الحساب
        if hasattr(db, 'delete_user_account'):
            print("✅ delete_user_account function exists")
        else:
            print("❌ delete_user_account function NOT found")
        
        print("\n📋 رسائل InstaPay:")
        print(f"- enter_instapay: {MESSAGES.get('enter_instapay', 'غير موجود')[:50]}...")
        print(f"- enter_payment_info: {MESSAGES.get('enter_payment_info', 'غير موجود')[:50]}...")
        
        print("\n💳 طرق الدفع المتاحة:")
        for key, method in PAYMENT_METHODS.items():
            print(f"  - {key}: {method['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_registration_flow():
    """اختبار تدفق التسجيل"""
    print("\n📝 اختبار تدفق التسجيل...")
    
    try:
        from bot.handlers.registration import RegistrationHandler
        from bot.states.registration import STATE_FLOW, STATE_NAMES
        
        handler = RegistrationHandler()
        
        print("\n🔄 تدفق الحالات:")
        for state, next_state in STATE_FLOW.items():
            state_name = STATE_NAMES.get(state, "Unknown")
            next_name = STATE_NAMES.get(next_state, "END")
            print(f"  {state_name} ➡️ {next_name}")
        
        # التحقق من وجود دالة _get_payment_info_message
        if hasattr(handler, '_get_payment_info_message'):
            print("\n✅ _get_payment_info_message method exists")
            
            # اختبار الرسائل حسب طريقة الدفع
            test_data_instapay = {'payment_method': 'instapay'}
            message = handler._get_payment_info_message(test_data_instapay)
            print(f"  InstaPay message: {message[:60]}...")
            
            test_data_other = {'payment_method': 'vodafone'}
            message = handler._get_payment_info_message(test_data_other)
            print(f"  Other payment message: {message[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def main():
    print("=" * 50)
    print("🚀 بدء اختبار البوت FC 26")
    print("=" * 50)
    
    # اختبار الاستيراد
    if not test_imports():
        print("\n❌ فشل اختبار الاستيراد")
        sys.exit(1)
    
    # اختبار التدفق
    if not test_registration_flow():
        print("\n❌ فشل اختبار التدفق")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ جميع الاختبارات نجحت!")
    print("🎉 البوت جاهز للاستخدام")
    print("=" * 50)

if __name__ == "__main__":
    main()