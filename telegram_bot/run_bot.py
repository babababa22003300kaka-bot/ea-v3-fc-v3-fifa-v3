#!/usr/bin/env python3
"""
🚀 تشغيل البوت للاختبار
"""

import os
import sys
from pathlib import Path

# إضافة المسارات
sys.path.insert(0, str(Path(__file__).parent))

# توكن تجريبي للاختبار (استبدل بتوكنك الحقيقي)
TEST_TOKEN = "TEST_TOKEN_HERE"  # ضع التوكن الحقيقي هنا

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 بوت FC 26 التليجرام")
    print("=" * 50)
    print()
    print("⚠️ تنبيه: تأكد من وضع التوكن الصحيح في الملف")
    print()
    print("للحصول على توكن:")
    print("1. افتح @BotFather في تليجرام")
    print("2. أرسل /newbot")
    print("3. اتبع التعليمات")
    print("4. انسخ التوكن وضعه في الملف")
    print()
    print("=" * 50)
    
    # تعيين التوكن مؤقتاً
    os.environ['TELEGRAM_BOT_TOKEN'] = TEST_TOKEN
    
    try:
        from bot_main import main
        main()
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        print("\nتأكد من:")
        print("1. وضع التوكن الصحيح")
        print("2. الاتصال بالإنترنت")
        print("3. تثبيت المكتبات المطلوبة")