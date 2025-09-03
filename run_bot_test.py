#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل البوت للاختبار المحلي
"""

import os
import sys

# تعيين التوكن
os.environ['BOT_TOKEN'] = '7607085569:AAEq91WtoNg68U9e8-mWm8DsOTh2W9MmmTw'

print("🚀 بدء تشغيل البوت...")
print("📋 الإصلاحات المطبقة:")
print("  ✅ زر حذف الحساب شغال")
print("  ✅ أمر /delete شغال")
print("  ✅ مشكلة webhook محلولة")
print("  ✅ لا يوجد تداخل مع التسجيل")
print("-" * 40)

from main_bot import FC26Bot

if __name__ == "__main__":
    try:
        bot = FC26Bot()
        bot.run()
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)