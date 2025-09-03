#!/usr/bin/env python3
"""
🧪 اختبار إصلاحات التليجرام
============================
اختبار شامل للتأكد من عمل نظام التليجرام بعد الإصلاحات
"""

import os
import json
import sys

# إضافة المسار الحالي
sys.path.insert(0, '/home/user/webapp')

def test_telegram_manager():
    """اختبار وزارة التليجرام المُصلحة"""
    print("\n" + "="*60)
    print("🧪 اختبار وزارة التليجرام المُصلحة")
    print("="*60)
    
    # استيراد الوحدة المُصلحة
    from telegram_manager_fixed import telegram_manager
    
    # 1. اختبار معلومات البوت
    print("\n📌 اختبار 1: معلومات البوت")
    bot_info = telegram_manager.get_bot_info()
    print(f"   Bot Username: @{bot_info.get('username')}")
    print(f"   Bot Status: {bot_info.get('status', 'unknown')}")
    assert bot_info.get('username') == 'ea_fc_fifa_bot', "❌ اسم البوت غير صحيح"
    print("   ✅ نجح")
    
    # 2. اختبار توليد كود
    print("\n📌 اختبار 2: توليد كود تليجرام")
    result = telegram_manager.create_telegram_code(
        platform="playstation",
        whatsapp_number="01012345678",
        payment_method="vodafone_cash",
        payment_details="01098765432",
        telegram_username=""
    )
    print(f"   Code: {result.get('code')}")
    print(f"   Link: {result.get('telegram_link')}")
    print(f"   Bot Username: {result.get('bot_username')}")
    assert result.get('success') == True, "❌ فشل توليد الكود"
    assert result.get('bot_username') == 'ea_fc_fifa_bot', "❌ اسم البوت غير صحيح"
    assert 'ea_fc_fifa_bot' in result.get('telegram_link', ''), "❌ الرابط غير صحيح"
    print("   ✅ نجح")
    
    # 3. اختبار فحص حالة الكود
    print("\n📌 اختبار 3: فحص حالة الكود")
    code = result.get('code')
    status = telegram_manager.check_telegram_status(code)
    print(f"   Code Exists: {status.get('exists')}")
    print(f"   Code Linked: {status.get('linked')}")
    assert status.get('exists') == True, "❌ الكود غير موجود"
    assert status.get('linked') == False, "❌ الكود مربوط خطأ"
    print("   ✅ نجح")
    
    # 4. اختبار معالجة webhook
    print("\n📌 اختبار 4: معالجة webhook")
    webhook_data = {
        "message": {
            "text": f"/start {code}",
            "chat": {"id": 123456789},
            "from": {
                "username": "testuser",
                "first_name": "Test"
            }
        }
    }
    webhook_result = telegram_manager.process_telegram_webhook(webhook_data)
    print(f"   Processing Success: {webhook_result.get('success')}")
    assert webhook_result.get('success') == True, "❌ فشل معالجة webhook"
    print("   ✅ نجح")
    
    # 5. التحقق من ربط الكود
    print("\n📌 اختبار 5: التحقق من ربط الكود")
    status_after = telegram_manager.check_telegram_status(code)
    print(f"   Code Linked After: {status_after.get('linked')}")
    print(f"   Chat ID: {status_after.get('telegram_chat_id')}")
    assert status_after.get('linked') == True, "❌ الكود لم يتم ربطه"
    print("   ✅ نجح")
    
    print("\n" + "="*60)
    print("✅ جميع اختبارات التليجرام نجحت!")
    print("="*60)
    return True

def test_app_endpoints():
    """اختبار endpoints التطبيق"""
    print("\n" + "="*60)
    print("🧪 اختبار Endpoints التطبيق")
    print("="*60)
    
    # استيراد التطبيق المُصلح
    from app_fixed import app
    
    # إنشاء test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # 1. اختبار الصفحة الرئيسية
    print("\n📌 اختبار 1: الصفحة الرئيسية")
    response = client.get('/')
    print(f"   Status Code: {response.status_code}")
    assert response.status_code == 200, "❌ فشل تحميل الصفحة الرئيسية"
    print("   ✅ نجح")
    
    # 2. اختبار get-bot-username
    print("\n📌 اختبار 2: endpoint get-bot-username")
    response = client.get('/get-bot-username')
    data = json.loads(response.data)
    print(f"   Status Code: {response.status_code}")
    print(f"   Bot Username: {data.get('username')}")
    assert response.status_code == 200, "❌ فشل endpoint"
    assert data.get('username') == 'ea_fc_fifa_bot', "❌ اسم البوت غير صحيح"
    print("   ✅ نجح")
    
    # 3. اختبار generate-telegram-code
    print("\n📌 اختبار 3: endpoint generate-telegram-code")
    response = client.post('/generate-telegram-code',
        json={
            "platform": "pc",
            "whatsapp_number": "01012345678",
            "payment_method": "instapay",
            "payment_details": "https://ipn.eg/S/test/instapay/ABC123"
        }
    )
    data = json.loads(response.data)
    print(f"   Status Code: {response.status_code}")
    print(f"   Success: {data.get('success')}")
    print(f"   Code: {data.get('code')}")
    print(f"   Bot Username: {data.get('bot_username')}")
    assert response.status_code == 200, "❌ فشل توليد الكود"
    assert data.get('success') == True, "❌ فشل في الاستجابة"
    assert data.get('bot_username') == 'ea_fc_fifa_bot', "❌ اسم البوت غير صحيح"
    print("   ✅ نجح")
    
    # 4. اختبار setup-telegram
    print("\n📌 اختبار 4: endpoint setup-telegram")
    response = client.get('/setup-telegram')
    data = json.loads(response.data)
    print(f"   Status Code: {response.status_code}")
    print(f"   Bot Username: {data.get('bot_username')}")
    assert response.status_code == 200, "❌ فشل setup"
    assert data.get('bot_username') == 'ea_fc_fifa_bot', "❌ اسم البوت غير صحيح"
    print("   ✅ نجح")
    
    print("\n" + "="*60)
    print("✅ جميع اختبارات Endpoints نجحت!")
    print("="*60)
    return True

def main():
    """تشغيل جميع الاختبارات"""
    print("\n🚀 بدء اختبارات إصلاح التليجرام")
    
    try:
        # اختبار وزارة التليجرام
        test_telegram_manager()
        
        # اختبار endpoints
        test_app_endpoints()
        
        print("\n" + "🎉"*20)
        print("\n✅✅✅ جميع الاختبارات نجحت! النظام جاهز للعمل ✅✅✅")
        print("\n" + "🎉"*20)
        
        print("\n📋 ملخص الإصلاحات:")
        print("   ✅ اسم البوت يعمل بشكل صحيح: @ea_fc_fifa_bot")
        print("   ✅ توليد الأكواد يعمل حتى بدون توكن")
        print("   ✅ الروابط تتولد بشكل صحيح")
        print("   ✅ معالجة webhook تعمل بشكل صحيح")
        print("   ✅ فحص حالة الربط يعمل بشكل صحيح")
        print("   ✅ جميع endpoints تعمل بشكل صحيح")
        
        print("\n🔥 النظام جاهز للنشر على Render!")
        
    except AssertionError as e:
        print(f"\n❌ فشل الاختبار: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()