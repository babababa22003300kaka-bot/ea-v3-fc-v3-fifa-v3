#!/usr/bin/env python3
# -- coding: utf-8 --
"""
🔥 FC 26 Trading Bot - النسخة الكاملة المتكاملة مع نظام الأدمن
البوت الكامل في ملف واحد مع نظام الرسائل الذكي ولوحة تحكم الأدمن
مشروع لبيع كوينز FC 26

================================================================================
⚠️⚠️⚠️ تحذير هام جداً للمساعد الذكي - اقرأ هذا أولاً قبل أي تعديل ⚠️⚠️⚠️
================================================================================

## 🛑 خطوات إجبارية للمساعد الذكي:
1️⃣ اقرأ كامل قسم "المناطق المحظورة المطلقة" أدناه
2️⃣ اقرأ قسم "المميزات المكتملة 100%" 
3️⃣ تأكد من فهم "خريطة السطور الفعلية"
4️⃣ استخدم فقط "المناطق الآمنة" للإضافات الجديدة
5️⃣ بعد التعديل، حدث قسم "آخر التعديلات" أدناه
6️⃣ انتظر تأكيد المطور قبل نقل الميزة لقائمة "المكتملة"

## ❌ المناطق المحظورة المطلقة (RED ZONES):

### 🚫 Zone 1: نظام إدارة الرسائل الذكي
📍 السطور: 151-304 (class SmartMessageManager)
🎯 الوظيفة: رسالة واحدة نشطة فقط + حماية Race Conditions
⛔ الممنوع: إنشاء طرق بديلة لإرسال الرسائل بأزرار
✅ الإجباري: استخدم smartmessagemanager لكل رسالة تفاعلية

### 🚫 Zone 2: نظام الحماية المتقدم للواتساب
📍 السطور: 305-380 (class WhatsAppSecuritySystem)
🎯 الوظيفة: حماية من محاولات متكررة + تحليل مفصل للمدخلات
⛔ الممنوع: تغيير منطق التحقق أو الحماية
✅ المسموح: قراءة البيانات فقط

### 🚫 Zone 3: نظام التشفير المتقدم
📍 السطور: 381-420 (class EncryptionSystem)
🎯 الوظيفة: تشفير البيانات الحساسة (أرقام الدفع)
⛔ الممنوع: تغيير المفاتيح أو آلية التشفير
✅ المسموح: استخدام encrypt/decrypt فقط

### 🚫 Zone 4: نظام التحقق من طرق الدفع
📍 السطور: 421-650 (class PaymentValidationSystem)
🎯 الوظيفة: تحقق متقدم من 7 طرق دفع + حماية من التكرار
⛔ الممنوع: تغيير قواعد التحقق أو منطق الحماية
✅ المسموح: قراءة النتائج فقط

### 🚫 Zone 5: آلية استكمال التسجيل "أهلاً بعودتك"
📍 السطور: 1020-1080 (دالة start في SmartRegistrationHandler)
🎯 الوظيفة: استكمال التسجيل من نقطة التوقف + حفظ التقدم
⛔ الممنوع: تغيير منطق tempregistration أو آلية الاستكمال
✅ المسموح: تعديل النصوص والأزرار فقط

### 🚫 Zone 6: جداول قاعدة البيانات الأساسية
📍 السطور: 670-750 (initdatabase في Database class)
🎯 الوظيفة: 5 جداول أساسية للتسجيل والمحفظة والمعاملات
⛔ الممنوع: تعديل/حذف الجداول الموجودة أو علاقاتها
✅ المسموح: إضافة جداول جديدة فقط

## ✅ المميزات المكتملة 100% (تمت واختُبرت بنجاح):
• ✅ نظام التسجيل 4 مراحل (منصة→واتساب→دفع→تفاصيل دفع)
• ✅ حماية متقدمة للواتساب (حظر مؤقت + تحليل مفصل)
• ✅ 7 طرق دفع مع تحقق متقدم (محافظ + تيلدا + إنستاباي)
• ✅ تشفير البيانات الحساسة
• ✅ نظام الرسائل الذكي (رسالة واحدة نشطة)
• ✅ لوحة تحكم الأدمن الكاملة (عرض/بحث/حذف/بث)
• ✅ نظام صفحات لعرض المستخدمين (10 لكل صفحة)
• ✅ حفظ التقدم المؤقت + استكمال التسجيل
• ✅ صلاحيات الأدمن المحمية
• ✅ تعديلات أزرار الأدمن (حذف حسابي + إزالة الحذف من المستخدمين)
• ✅ تعليقات توضيحية للمناطق المحظورة في بداية الملف
• ✅ تحسين رسالة الخطأ للمستخدمين العاديين
• ✅ نظام تعديل الملف الشخصي الكامل:
  - ✅ تعديل المنصة (تفاعلي بالكامل مع قائمة اختيار)
  - ✅ تعديل الواتساب (إدخال مباشر مع التحقق الذكي)
  - ✅ تعديل طريقة الدفع (اختيار تفاعلي مع تفاصيل)
  - ✅ حفظ شبكة الواتساب في قاعدة البيانات
  - ✅ إصلاح مشكلة HTTP 400 في عرض الملف الشخصي
• ✅ رسائل مساعدة للمستخدمين عند محاولة استخدام أوامر الأدمن

## 🔄 الميزات قيد الاختبار (منتظر تأكيد المطور):
• ⏳ لوجز مفصلة لتشخيص مشاكل الأجهزة المتعددة

## 📝 آخر التعديلات:
• تاريخ: 2025-09-09
• التحديث الأخير: إصلاح خطأ Markdown parsing (Can't parse entities)
• المساعد الذكي سيحدث هذا القسم تلقائياً بعد كل تعديل
• آخر تعديل معتمد: رسائل مساعدة + نظام تعديل الملف

## ⏰ آخر تعديل للمساعد (ينتظر التأكيد):
- التاريخ والوقت: 2025-09-09 
- الميزات المضافة:
  • حل جذري نهائي - إزالة كل الـ Markdown formatting من الكود
  • إلغاء parse_mode='Markdown' من جميع الرسائل
  • تنظيف كامل لكل الرسائل من أي formatting
- الموقع: 
  • السطور 358, 430, 438, 496, 3511: إزالة parse_mode
  • كل الملف: إزالة جميع ** و * و ` من الرسائل
  • تنظيف شامل لكل النصوص
- التعديل المضاف: حل جذري بإزالة Markdown نهائياً
- الملفات المعدلة: app_complete.py
- حالة الاختبار: منتظر تأكيد المطور
- ملاحظات: الحل النهائي - لا يوجد أي Markdown في الكود 

## 🎯 خريطة السطور الحقيقية:
السطور 1-80: الإعدادات والاستيراد
السطور 81-150: البيانات الثابتة (GAMINGPLATFORMS, PAYMENTMETHODS, MESSAGES)
السطور 151-304: SmartMessageManager ⚠️ (لا تلمس)
السطور 305-380: WhatsAppSecuritySystem ⚠️ (لا تلمس)
السطور 381-420: EncryptionSystem ⚠️ (لا تلمس)
السطور 421-650: PaymentValidationSystem ⚠️ (لا تلمس)
السطور 651-850: Database class ⚠️ (لا تلمس الأساسيات)
السطور 851-950: Keyboards class 🟢 (آمن للتعديل)
السطور 951-1400: SmartRegistrationHandler ⚠️ (لا تلمس الأساسيات)
السطور 1401-1800: FC26SmartBot + لوحة الأدمن 🟢 (آمن للإضافة)
السطور 1801+: التشغيل والإعداد

## 🟢 المناطق الآمنة للإضافة (GREEN ZONES):
✅ إضافة أزرار جديدة في Keyboards class (السطور 851-950)
✅ إضافة رسائل جديدة في MESSAGES dictionary (السطور 81-150)
✅ إضافة دوال جديدة في FC26SmartBot class (السطور 1401+)
✅ إضافة معالجات أوامر جديدة
✅ إضافة callback handlers جديدة
✅ إضافة جداول قاعدة بيانات جديدة (بدون مس الموجود)

## 🤖 تعليمات التحديث الذاتي للمساعد:
بعد كل تعديل، يجب على المساعد الذكي:

1️⃣ تحديث قسم "آخر تعديل للمساعد":
``
- التاريخ والوقت: [YYYY-MM-DD HH:MM]
- التعديل المضاف: [وصف مختصر للتعديل]
- الملفات المعدلة: appcomplete.py
- حالة الاختبار: ⏳ منتظر اختبار المطور
- ملاحظات: [أي ملاحظات مهمة]
`

2️⃣ إضافة الميزة الجديدة لقسم "قيد الاختبار":
- ضع علامة 🔄 بجانب الميزة الجديدة
- اذكر التفاصيل والموقع في الكود

3️⃣ إضافة Zone جديد إذا لزم الأمر:
- إذا أضفت ميزة معقدة، أضف Zone جديد برقم تسلسلي
- مثال: ### 🚫 Zone 7: نظام أسعار الكوينز

4️⃣ كتابة رسالة للمطور:
`
🎯 تم إضافة ميزة جديدة!

📝 التعديل: [اسم الميزة]
📍 الموقع: [أرقام السطور]
🔧 التفاصيل: [شرح مختصر]

⏰ حالة الاختبار: منتظر تأكيدك
✅ إذا اشتغلت بنجاح، قول "تمام" وسأنقلها للمكتملة
❌ إذا فيها مشكلة، اشرح المطلوب تعديله
`

## 🔧 قواعد التطوير الآمن:
1. ✅ استخدم smartmessagemanager للرسائل التفاعلية الجديدة
2. ✅ أضف دوال جديدة في نهاية FC26SmartBot class
3. ✅ استخدم نفس أسلوب التعليقات العربية
4. ✅ اتبع نمط التسمية الحالي
5. ✅ اختبر مع النظام الموجود بدون كسره
6. ✅ حدث قسم التعليمات تلقائياً بعد كل إضافة

## ❌ أمثلة طلبات مرفوضة:
"غير نظام التحقق من الواتساب"
"عدل طريقة التشفير"  
"أنشئ طريقة جديدة لإرسال الرسائل بأزرار"
"غير منطق حفظ التقدم المؤقت"
"عدل جداول قاعدة البيانات الأساسية"

## ✅ أمثلة طلبات مقبولة:
"أضف زر 'أسعار الكوينز' للقائمة الرئيسية"
"اجعل البوت يستجيب لأمر /prices جديد"
"أضف جدول جديد لحفظ أسعار الكوينز"
"أنشئ نظام إشعارات منفصل"
"أضف ميزة عرض الإحصائيات للأدمن"

================================================================================
⚠️ تنبيه للمساعد الذكي: اقرأ، عدل، حدث التعليمات، ثم انتظر تأكيد المطور ⚠️
================================================================================
"""

 
import os
import logging
import sqlite3
import hashlib
import json
import re
import asyncio
import time
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# ================================ الإعدادات ================================
BOTTOKEN = '7607085569:AAEDNKwt8j8BCjG5gjKLJ8MLjrTRCCrx6k'
ADMINID = 1124247595
DATABASEPATH = 'fc26bot.db'

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================ حالات التسجيل ================================
(
    CHOOSINGPLATFORM,
    ENTERINGWHATSAPP,
    CHOOSINGPAYMENT,
    ENTERINGPAYMENTDETAILS
) = range(4)

# ================================ البيانات الثابتة ================================
GAMINGPLATFORMS = {
    'playstation': {'name': 'PlayStation 🎮', 'emoji': '🎮'},
    'xbox': {'name': 'Xbox ❎', 'emoji': '❎'},
    'pc': {'name': 'PC 💻', 'emoji': '💻'}
}

PAYMENTMETHODS = {
    'vodafonecash': {'name': '⭕️ فودافون كاش', 'emoji': '⭕️'},
    'etisalatcash': {'name': '🟢 اتصالات كاش', 'emoji': '🟢'},
    'orangecash': {'name': '🍊 أورانج كاش', 'emoji': '🍊'},
    'wecash': {'name': '🟣 وي كاش', 'emoji': '🟣'},
    'bankwallet': {'name': '🏦 محفظة بنكية', 'emoji': '🏦'},
    'telda': {'name': '💳 تيلدا', 'emoji': '💳'},
    'instapay': {'name': '🔗 إنستا باي', 'emoji': '🔗'}
}

MESSAGES = {
    'welcome': """🌟 أهلاً وسهلاً في بوت FC 26! 🎮

البوت الأول في مصر لبيع كوينز FC 26 🇪🇬

✨ مميزاتنا:
• أسعار منافسة جداً 💰
• معاملات آمنة 100% 🔒
• دعم فني 24/7 📞
• سرعة في التنفيذ ⚡

اضغط على "تسجيل جديد" للبدء! 👇""",

    'chooseplatform': """🎮 اختر منصة اللعب:""",

    'enterwhatsapp': """📱 أرسل رقم الواتساب:

📝 القواعد:
• 11 رقم بالضبط
• يبدأ بـ: 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ مثال صحيح: 01094591331""",

    'choosepayment': """💳 اختر طريقة الدفع:""",



    'registrationcomplete': """🎉 مبروك! تم إنشاء حسابك بنجاح! 🎊

✅ ملخص بياناتك:
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {whatsapp}
💳 طريقة الدفع: {payment}
━━━━━━━━━━━━━━━━

مرحباً بك في عائلة FC 26! 🚀""",

    'welcomeback': """👋 أهلاً بعودتك!

كنا واقفين عند: {laststep}

هل تريد المتابعة من حيث توقفت؟""",





    'datasaved': """💾 تم حفظ البيانات تلقائياً ✅

يمكنك العودة في أي وقت وسنكمل من نفس النقطة!"""
}

# ================================ نظام إدارة الرسائل الذكي ================================
class SmartMessageManager:
    """مدير الرسائل الذكي - رسالة واحدة نشطة فقط مع حماية من Race Conditions"""

    def __init__(self):
        self.useractivemessages: Dict[int, Dict[str, Any]] = {}
        # إضافة قفل لكل مستخدم لمنع Race Conditions
        self.userlocks: Dict[int, asyncio.Lock] = {}
        # تتبع الأجهزة المتعددة للمستخدم
        self.userdevices: Dict[int, set] = {}

    async def getorcreatelock(self, userid: int) -> asyncio.Lock:
        """الحصول على قفل المستخدم أو إنشاء واحد جديد"""
        if userid not in self.userlocks:
            self.userlocks[userid] = asyncio.Lock()
        return self.userlocks[userid]
    
    async def cleanupuserdata(self, userid: int):
        """تنظيف بيانات المستخدم عند انتهاء المحادثة"""
        # حذف القفل إذا كان موجوداً
        if userid in self.userlocks:
            del self.userlocks[userid]
        
        # حذف الرسائل النشطة إذا كانت موجودة
        if userid in self.useractivemessages:
            del self.useractivemessages[userid]
        
        # حذف بيانات الأجهزة
        if userid in self.userdevices:
            del self.userdevices[userid]
        
        logger.info(f"🧽 تم تنظيف بيانات المستخدم {userid}")

    async def disable_old_message(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, choice_made: str = None):
        """إلغاء تفعيل الرسالة القديمة وتحويلها لسجل تاريخي"""
        # الحصول على القفل للمستخدم
        lock = await self.getorcreatelock(userid)
        
        async with lock:  # استخدام القفل لحماية العملية
            if userid not in self.useractivemessages:
                return

            try:
                oldmessageinfo = self.useractivemessages[userid]

                if oldmessageinfo.get('messageid') and oldmessageinfo.get('chatid'):
                    # إذا كانت الرسالة القديمة فيها أزرار، نحذفها ونضع "تم"
                    if oldmessageinfo.get('haskeyboard', False):
                        try:
                            # تحديث الرسالة بدون أزرار وإضافة "تم"
                            await context.bot.editmessagetext(
                                chatid=oldmessageinfo['chatid'],
                                messageid=oldmessageinfo['messageid'],
                                text=oldmessageinfo.get('text', '') + "\n\n✅ تم",
                                # parsemode removed to avoid parsing errors
                            )
                        except Exception as e:
                            # إذا فشل التحديث، نحاول حذف الرسالة
                            try:
                                await context.bot.deletemessage(
                                    chatid=oldmessageinfo['chatid'],
                                    messageid=oldmessageinfo['messageid']
                                )
                            except:
                                pass

                    del self.useractivemessages[userid]
            except Exception as e:
                logger.debug(f"تعذر تعديل الرسالة القديمة: {e}")

    async def sendnewactivemessage(
        self,
        update: Update,
        context: ContextTypes.DEFAULTTYPE,
        text: str,
        replymarkup: Optional[InlineKeyboardMarkup] = None,
        choicemade: str = None,
        disableprevious: bool = True,
        removekeyboard: bool = True
    ):
        """إرسال رسالة جديدة نشطة مع حماية من Race Conditions"""
        userid = update.effectiveuser.id
        
        # لوج عند دخول المستخدم
        deviceinfo = "Callback" if update.callbackquery else "Message"
        deviceid = update.effectivemessage.messageid if update.effectivemessage else "Unknown"
        logger.info(f"🔵 المستخدم {userid} دخل من جهاز جديد - Device: {deviceinfo} - Device ID: {deviceid}")
        
        # تتبع الأجهزة المتعددة
        if userid not in self.userdevices:
            self.userdevices[userid] = set()
        self.userdevices[userid].add(deviceid)
        
        # إذا كان هناك أكثر من جهاز، نظف الرسائل القديمة
        if len(self.userdevices[userid]) > 1:
            logger.warning(f"⚠️ المستخدم {userid} يستخدم أجهزة متعددة: {len(self.userdevices[userid])} أجهزة")
            # حذف الرسائل القديمة لتجنب التضارب
            if userid in self.useractivemessages:
                oldmessage = self.useractivemessages[userid]
                if oldmessage.get('messageid') != deviceid:
                    logger.info(f"🧽 حذف رسالة قديمة للمستخدم {userid} بسبب استخدام جهاز جديد")
                    del self.useractivemessages[userid]
        
        # الحصول على القفل للمستخدم
        lock = await self.getorcreatelock(userid)

        if disableprevious:
            await self.disable_old_message(user_id, context, choice_made)

        async with lock:  # استخدام القفل لحماية عملية الإرسال والحفظ
            try:
                # التحقق من عدم وجود رسالة مطابقة نشطة بالفعل
                if userid in self.useractivemessages:
                    existingmsg = self.useractivemessages[userid]
                    if existingmsg.get('text') == text:
                        # نفس الرسالة موجودة بالفعل، لا نرسل مرة أخرى
                        logger.debug(f"تجاهل إرسال رسالة مكررة للمستخدم {userid}")
                        # لوج عند تضارب الرسائل
                        activecount = len([k for k in self.useractivemessages if k == userid])
                        logger.warning(f"⚠️ تضارب رسائل للمستخدم {userid} - Active Messages: {activecount}")
                        return None
                
                if update.callbackquery:
                    sentmessage = await update.callbackquery.message.replytext(
                        text=text,
                        replymarkup=replymarkup,
                        # parsemode removed to avoid parsing errors
                    )
                else:
                    # إزالة الكيبورد إذا لم يكن هناك replymarkup
                    finalmarkup = replymarkup if replymarkup else (ReplyKeyboardRemove() if removekeyboard else None)
                    sentmessage = await update.message.replytext(
                        text=text,
                        replymarkup=finalmarkup,
                        # parsemode removed to avoid parsing errors
                    )

                # حفظ معلومات الرسالة الجديدة
                self.useractivemessages[userid] = {
                    'messageid': sentmessage.messageid,
                    'chatid': sentmessage.chatid,
                    'text': text,
                    'haskeyboard': replymarkup is not None,
                    'timestamp': datetime.now()  # إضافة timestamp للتتبع
                }

                return sentmessage

            except Exception as e:
                logger.error(f"خطأ في إرسال رسالة: {e}")
                return None

    async def updatecurrentmessage(
        self,
        update: Update,
        context: ContextTypes.DEFAULTTYPE,
        text: str,
        replymarkup: Optional[InlineKeyboardMarkup] = None
    ):
        """تحديث الرسالة الحالية مع حماية من Race Conditions"""
        if not update.callbackquery:
            return await self.sendnewactivemessage(update, context, text, replymarkup)

        userid = update.effectiveuser.id
        messageid = update.callbackquery.message.messageid
        
        # لوج قبل editMessageText
        logger.info(f"🟠 محاولة تعديل رسالة للمستخدم {userid} - Message ID: {messageid} - New Content Length: {len(text)}")
        
        # الحصول على القفل للمستخدم
        lock = await self.getorcreatelock(userid)
        
        async with lock:  # استخدام القفل لحماية عملية التحديث
            try:
                # التحقق من عدم تكرار نفس الرسالة
                if userid in self.useractivemessages:
                    oldmsg = self.useractivemessages[userid]
                    if oldmsg.get('text') == text and oldmsg.get('messageid') == update.callbackquery.message.messageid:
                        # نفس الرسالة، لا نحدث
                        logger.debug(f"تجاهل تحديث رسالة مطابقة للمستخدم {userid}")
                        return
                    
                    # التحقق من الـ timestamp لمنع التحديثات السريعة جداً
                    if 'timestamp' in oldmsg:
                        timediff = (datetime.now() - oldmsg['timestamp']).totalseconds()
                        if timediff < 0.5:  # أقل من نصف ثانية
                            logger.debug(f"تجاهل تحديث سريع جداً للمستخدم {userid}")
                            return

                await update.callbackquery.editmessagetext(
                    text=text,
                    replymarkup=replymarkup,
                    # parsemode removed to avoid parsing errors
                )
                logger.info(f"✅ تم تعديل الرسالة بنجاح للمستخدم {userid} - Message ID: {messageid}")

                # حفظ معلومات الرسالة المحدثة
                self.useractivemessages[userid] = {
                    'messageid': update.callbackquery.message.messageid,
                    'chatid': update.callbackquery.message.chatid,
                    'text': text,
                    'haskeyboard': replymarkup is not None,
                    'timestamp': datetime.now()  # إضافة timestamp للتتبع
                }

            except Exception as e:
                # إذا كان الخطأ "لم يتغير النص"، نتجاهله
                if "message is not modified" in str(e).lower():
                    logger.debug(f"الرسالة لم تتغير للمستخدم {userid}")
                elif "400" in str(e) or "Bad Request" in str(e):
                    # لوج عند HTTP 400
                    logger.error(f"🔴 خطأ HTTP 400 للمستخدم {userid} - Message ID: {messageid} - Error: {str(e)}")
                    # محاولة إرسال رسالة جديدة بدلاً من التعديل
                    logger.info(f"📨 محاولة إرسال رسالة جديدة بدلاً من التعديل للمستخدم {userid}")
                    await self.sendnewactivemessage(update, context, text, replymarkup)
                else:
                    logger.debug(f"خطأ في تحديث الرسالة للمستخدم {userid}: {e}")

# إنشاء المدير الذكي
smartmessagemanager = SmartMessageManager()

# ================================ نظام الحماية المتقدم للواتساب ================================
class WhatsAppSecuritySystem:
    """نظام حماية متقدم للتحقق من أرقام الواتساب"""
    
    def __init__(self):
        # تتبع المحاولات لكل مستخدم
        self.userattempts: Dict[int, List[datetime]] = defaultdict(list)
        self.failedattempts: Dict[int, int] = defaultdict(int)
        self.blockedusers: Dict[int, datetime] = {}
        self.lastnumbers: Dict[int, str] = {}
        
        # إعدادات الحماية
        self.MAXATTEMPTSPERMINUTE = 5
        self.MAXFAILEDATTEMPTS = 5
        self.BLOCKDURATIONMINUTES = 15
        self.RATELIMITWINDOW = 60  # ثانية
        
        # شبكات الاتصال المصرية
        self.EGYPTIANNETWORKS = {
            '010': {'name': 'فودافون', 'emoji': '⭕️'},
            '011': {'name': 'اتصالات', 'emoji': '🟢'},
            '012': {'name': 'أورانج', 'emoji': '🍊'},
            '015': {'name': 'وي', 'emoji': '🟣'}
        }
    
    def isuserblocked(self, userid: int) -> Tuple[bool, Optional[int]]:
        """التحقق من حظر المستخدم"""
        if userid in self.blockedusers:
            blocktime = self.blockedusers[userid]
            elapsed = (datetime.now() - blocktime).totalseconds() / 60
            
            if elapsed < self.BLOCKDURATIONMINUTES:
                remaining = self.BLOCKDURATIONMINUTES - int(elapsed)
                return True, remaining
            else:
                # انتهت فترة الحظر
                del self.blockedusers[userid]
                self.failedattempts[userid] = 0
        
        return False, None
    
    def checkratelimit(self, userid: int) -> Tuple[bool, Optional[str]]:
        """فحص معدل الطلبات"""
        now = datetime.now()
        
        # تنظيف المحاولات القديمة
        if userid in self.userattempts:
            self.userattempts[userid] = [
                attempt for attempt in self.userattempts[userid]
                if (now - attempt).totalseconds() < self.RATELIMITWINDOW
            ]
        
        # فحص عدد المحاولات
        attemptscount = len(self.userattempts[userid])
        
        if attemptscount >= self.MAXATTEMPTSPERMINUTE:
            return False, f"⚠️ لقد تجاوزت الحد المسموح ({self.MAXATTEMPTSPERMINUTE} محاولات في الدقيقة)\\n\\n⏰ انتظر قليلاً ثم حاول مرة أخرى"
        
        # تسجيل المحاولة الجديدة
        self.userattempts[userid].append(now)
        return True, None
    
    def checkduplicate(self, userid: int, phone: str) -> bool:
        """فحص الأرقام المكررة"""
        if userid in self.lastnumbers:
            if self.lastnumbers[userid] == phone:
                return True
        return False
    
    def analyzeinput(self, text: str) -> Dict[str, Any]:
        """تحليل المدخل بشكل تفصيلي"""
        analysis = {
            'original': text,
            'hasletters': False,
            'hassymbols': False,
            'hasspaces': False,
            'hasarabicnumbers': False,
            'extracteddigits': '',
            'allchars': [],
            'invalidchars': []
        }
        
        # استخراج الأرقام فقط
        digitsonly = re.sub(r'[^\d]', '', text)
        analysis['extracteddigits'] = digitsonly
        
        # تحليل كل حرف
        for char in text:
            analysis['allchars'].append(char)
            
            # فحص الأحرف
            if char.isalpha():
                analysis['hasletters'] = True
                analysis['invalidchars'].append(char)
            
            # فحص الرموز
            elif not char.isdigit() and not char.isspace():
                analysis['hassymbols'] = True
                analysis['invalidchars'].append(char)
            
            # فحص المسافات
            elif char.isspace():
                analysis['hasspaces'] = True
                analysis['invalidchars'].append(char)
            
            # فحص الأرقام العربية
            elif char in '٠١٢٣٤٥٦٧٨٩':
                analysis['hasarabicnumbers'] = True
                analysis['invalidchars'].append(char)
        
        return analysis
    
    def validatewhatsapp(self, text: str, userid: int) -> Dict[str, Any]:
        """التحقق الشامل من رقم الواتساب"""
        result = {
            'isvalid': False,
            'cleanednumber': '',
            'errortype': None,
            'errormessage': '',
            'networkinfo': None,
            'analysis': None
        }
        
        # التحليل التفصيلي للمدخل
        analysis = self.analyzeinput(text)
        result['analysis'] = analysis
        
        # 1. فحص وجود أحرف أو رموز
        if analysis['hasletters'] or analysis['hassymbols'] or analysis['hasspaces'] or analysis['hasarabicnumbers']:
            invalidcharsdisplay = ''.join(set(analysis['invalidchars']))
            result['errortype'] = 'invalidchars'
            result['errormessage'] = f"""❌ رقم الواتساب يجب أن يكون أرقام فقط

📍 المدخل الخاطئ: {text}
🚫 الأحرف/الرموز الغير مسموحة: {invalidcharsdisplay}
📊 الأرقام المستخرجة: {analysis['extracteddigits'] or 'لا توجد أرقام'}

✅ مثال صحيح: 01094591331

💡 تلميح: استخدم الأرقام الإنجليزية فقط (0-9) بدون مسافات أو رموز"""
            return result
        
        cleaned = analysis['extracteddigits']
        
        # 2. فحص الطول
        if len(cleaned) < 11:
            result['errortype'] = 'tooshort'
            result['errormessage'] = f"""❌ طول الرقم غير صحيح

📏 المطلوب: 11 رقم بالضبط
📍 أنت أدخلت: {len(cleaned)} رقم فقط
🔢 الرقم المدخل: {cleaned}

✅ مثال صحيح: 01094591331"""
            return result
        
        elif len(cleaned) > 11:
            result['errortype'] = 'toolong'
            result['errormessage'] = f"""❌ طول الرقم غير صحيح

📏 المطلوب: 11 رقم بالضبط
📍 أنت أدخلت: {len(cleaned)} رقم (أكثر من المطلوب)
🔢 الرقم المدخل: {cleaned}

✅ مثال صحيح: 01094591331"""
            return result
        
        # 3. فحص البداية
        prefix = cleaned[:3]
        if prefix not in self.EGYPTIANNETWORKS:
            result['errortype'] = 'invalidprefix'
            result['errormessage'] = f"""❌ بداية الرقم غير صحيحة

📍 يجب أن يبدأ بـ: 010 / 011 / 012 / 015
🚫 رقمك يبدأ بـ: {prefix}
🔢 الرقم المدخل: {cleaned}

📱 الشبكات المدعومة:
⭕️ 010 - فودافون
🟢 011 - اتصالات  
🍊 012 - أورانج
🟣 015 - وي

✅ مثال صحيح: 01094591331"""
            return result
        
        # النجاح!
        network = self.EGYPTIANNETWORKS[prefix]
        result['isvalid'] = True
        result['cleanednumber'] = cleaned
        result['networkinfo'] = network
        
        # حفظ الرقم لمنع التكرار
        self.lastnumbers[userid] = cleaned
        
        return result
    
    def recordfailure(self, userid: int):
        """تسجيل محاولة فاشلة"""
        self.failedattempts[userid] += 1
        
        if self.failedattempts[userid] >= self.MAXFAILEDATTEMPTS:
            self.blockedusers[userid] = datetime.now()
            return True  # تم الحظر
        
        return False
    
    def resetuserfailures(self, userid: int):
        """إعادة تعيين المحاولات الفاشلة عند النجاح"""
        self.failedattempts[userid] = 0
        if userid in self.blockedusers:
            del self.blockedusers[userid]
    
    def getremainingattempts(self, userid: int) -> int:
        """الحصول على عدد المحاولات المتبقية"""
        return self.MAXFAILEDATTEMPTS - self.failedattempts.get(userid, 0)

# إنشاء نظام الحماية
whatsappsecurity = WhatsAppSecuritySystem()

# ================================ نظام التشفير المتقدم ================================
class EncryptionSystem:
    """نظام تشفير متقدم للبيانات الحساسة"""
    
    def __init__(self):
        # استخدام مفتاح ثابت آمن (في الإنتاج يجب استخدام مفتاح من متغيرات البيئة)
        self.masterkey = b'FC26BOTSECUREENCRYPTIONKEY2025PRODUCTION'
        self.initcipher()
    
    def _init_cipher(self):
        """تهيئة نظام التشفير"""
        # إنشاء KDF للحصول على مفتاح قوي
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'FC26SALT2025',
            iterations=100000,
        )
        key = base64.urlsafeb64encode(kdf.derive(self.masterkey))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """تشفير البيانات"""
        if not data:
            return ""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafeb64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"خطأ في التشفير: {e}")
            return data  # إرجاع البيانات بدون تشفير في حالة الخطأ
    
    def decrypt(self, encrypteddata: str) -> str:
        """فك تشفير البيانات"""
        if not encrypteddata:
            return ""
        try:
            decoded = base64.urlsafeb64decode(encrypteddata.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"خطأ في فك التشفير: {e}")
            return encrypteddata  # إرجاع البيانات كما هي في حالة الخطأ

# إنشاء نظام التشفير
encryptionsystem = EncryptionSystem()

# ================================ نظام التحقق من طرق الدفع ================================
class PaymentValidationSystem:
    """نظام التحقق المتقدم من طرق الدفع"""
    
    def __init__(self):
        # تتبع المحاولات لكل مستخدم
        self.userattempts: Dict[int, List[datetime]] = defaultdict(list)
        self.failedattempts: Dict[int, int] = defaultdict(int)
        self.blockedusers: Dict[int, datetime] = {}
        
        # إعدادات الحماية
        self.MAXATTEMPTSPERMINUTE = 8
        self.MAXFAILEDATTEMPTS = 4
        self.BLOCKDURATIONMINUTES = 10
        self.RATELIMITWINDOW = 60  # ثانية
        
        # قواعد التحقق لكل طريقة دفع
        self.PAYMENTRULES = {
            'vodafonecash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'فودافون كاش',
                'example': '01012345678',
                'network': 'جميع الشبكات'
            },
            'etisalatcash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'اتصالات كاش',
                'example': '01112345678',
                'network': 'جميع الشبكات'
            },
            'orangecash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'أورانج كاش',
                'example': '01212345678',
                'network': 'جميع الشبكات'
            },
            'wecash': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'وي كاش',
                'example': '01512345678',
                'network': 'جميع الشبكات'
            },
            'bankwallet': {
                'type': 'wallet',
                'length': 11,
                'prefix': ['010', '011', '012', '015'],
                'name': 'محفظة بنكية',
                'example': '01012345678',
                'network': 'جميع الشبكات المصرية'
            },
            'telda': {
                'type': 'card',
                'length': 16,
                'name': 'تيلدا',
                'example': '1234567890123456'
            },
            'instapay': {
                'type': 'link',
                'name': 'إنستا باي',
                'keywords': ['instapay', 'ipn.eg'],
                'example': 'https://instapay.com/username'
            }
        }
    
    def isuserblocked(self, userid: int) -> Tuple[bool, Optional[int]]:
        """التحقق من حظر المستخدم"""
        if userid in self.blockedusers:
            blocktime = self.blockedusers[userid]
            elapsed = (datetime.now() - blocktime).totalseconds() / 60
            
            if elapsed < self.BLOCKDURATIONMINUTES:
                remaining = self.BLOCKDURATIONMINUTES - int(elapsed)
                return True, remaining
            else:
                # انتهت فترة الحظر
                del self.blockedusers[userid]
                self.failedattempts[userid] = 0
        
        return False, None
    
    def checkratelimit(self, userid: int) -> Tuple[bool, Optional[str]]:
        """فحص معدل الطلبات"""
        now = datetime.now()
        
        # تنظيف المحاولات القديمة
        if userid in self.userattempts:
            self.userattempts[userid] = [
                attempt for attempt in self.userattempts[userid]
                if (now - attempt).totalseconds() < self.RATELIMITWINDOW
            ]
        
        # فحص عدد المحاولات
        attemptscount = len(self.userattempts[userid])
        
        if attemptscount >= self.MAXATTEMPTSPERMINUTE:
            return False, f"⚠️ لقد تجاوزت الحد المسموح ({self.MAXATTEMPTSPERMINUTE} محاولات في الدقيقة)\\n\\n⏰ انتظر قليلاً ثم حاول مرة أخرى"
        
        # تسجيل المحاولة الجديدة
        self.userattempts[userid].append(now)
        return True, None
    
    def validatewallet(self, text: str, paymentmethod: str) -> Dict[str, Any]:
        """التحقق من رقم المحفظة الإلكترونية"""
        result = {
            'isvalid': False,
            'cleaneddata': '',
            'errormessage': '',
            'network': ''
        }
        
        # تنظيف الرقم من الرموز
        cleaned = re.sub(r'[^\d]', '', text)
        
        rules = self.PAYMENTRULES[paymentmethod]
        
        # فحص وجود أحرف أو رموز
        if re.search(r'[a-zA-Z]', text):
            result['errormessage'] = f"""❌ رقم {rules['name']} غير صحيح

📍 يجب أن يكون:
• أرقام فقط (بدون حروف أو رموز)
• 11 رقم بالضبط
• يبدأ بـ {'/'.join(rules['prefix'])} فقط

✅ مثال صحيح: {rules['example']}"""
            
            if paymentmethod == 'bankwallet':
                result['errormessage'] += "\n\n📍 تنبيه: المحفظة البنكية تقبل جميع الشبكات المصرية (010/011/012/015)"
            
            return result
        
        # فحص الطول
        if len(cleaned) != rules['length']:
            result['errormessage'] = f"""❌ رقم {rules['name']} غير صحيح

📏 الطول المطلوب: {rules['length']} رقم
📍 أنت أدخلت: {len(cleaned)} رقم

✅ مثال صحيح: {rules['example']}"""
            return result
        
        # فحص البداية
        prefix = cleaned[:3]
        if prefix not in rules['prefix']:
            result['errormessage'] = f"""❌ رقم {rules['name']} غير صحيح

📍 يجب أن يبدأ بـ: {'/'.join(rules['prefix'])} فقط
🚫 رقمك يبدأ بـ: {prefix}

✅ مثال صحيح: {rules['example']}"""
            
            if paymentmethod == 'bankwallet':
                result['errormessage'] += "\n\n📍 تنبيه: المحفظة البنكية تقبل جميع الشبكات المصرية (010/011/012/015)"
            
            return result
        
        # النجاح
        result['isvalid'] = True
        result['cleaneddata'] = cleaned
        result['network'] = rules['network']
        
        return result
    
    def validatetelda(self, text: str) -> Dict[str, Any]:
        """التحقق من رقم كارت تيلدا"""
        result = {
            'isvalid': False,
            'cleaneddata': '',
            'errormessage': ''
        }
        
        # السماح بالمسافات والشرطات ثم إزالتها
        cleaned = re.sub(r'[\s\-]', '', text)
        
        # إزالة أي شيء غير الأرقام
        digitsonly = re.sub(r'[^\d]', '', cleaned)
        
        # فحص وجود أحرف
        if re.search(r'[a-zA-Z]', text):
            result['errormessage'] = """❌ رقم كارت تيلدا غير صحيح

📍 يجب أن يكون:
• 16 رقم بالضبط
• أرقام فقط (يُسمح بالمسافات والشرطات)
• بدون حروف أو رموز غريبة

✅ أمثلة صحيحة:
• 1234567890123456
• 1234-5678-9012-3456
• 1234 5678 9012 3456"""
            return result
        
        # فحص الطول
        if len(digitsonly) != 16:
            result['errormessage'] = f"""❌ رقم كارت تيلدا غير صحيح

📏 المطلوب: 16 رقم بالضبط
📍 أنت أدخلت: {len(digitsonly)} رقم

✅ أمثلة صحيحة:
• 1234567890123456
• 1234-5678-9012-3456
• 1234 5678 9012 3456"""
            return result
        
        # النجاح
        result['isvalid'] = True
        result['cleaneddata'] = digitsonly
        
        return result
    
    def validateinstapay(self, text: str) -> Dict[str, Any]:
        """التحقق من رابط إنستاباي واستخراج الرابط الصحيح فقط"""
        result = {
            'isvalid': False,
            'cleaneddata': '',
            'errormessage': ''
        }
        
        # تنظيف النص
        text = text.strip()
        
        # البحث عن روابط InstaPay أو IPN في النص
        import re
        
        # نمط للبحث عن روابط ipn.eg أو instapay
        # يبحث عن روابط كاملة مثل https://ipn.eg/S/username/instapay/ABC123
        urlpatterns = [
            r'https?://ipn\.eg/[^\s]+',  # روابط ipn.eg
            r'https?://instapay\.com/[^\s]+',  # روابط instapay.com
            r'ipn\.eg/[^\s]+',  # روابط ipn.eg بدون https
            r'instapay\.com/[^\s]+',  # روابط instapay.com بدون https
        ]
        
        # البحث عن أول رابط مطابق
        for pattern in urlpatterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                foundurl = match.group(0)
                # إضافة https:// إذا لم يكن موجوداً
                if not foundurl.startswith('http'):
                    foundurl = f"https://{foundurl}"
                result['isvalid'] = True
                result['cleaneddata'] = foundurl
                return result
        
        # إذا لم يتم العثور على رابط، نتحقق من النص بشكل عام
        if any(keyword in text.lower() for keyword in ['instapay', 'ipn.eg', 'ipn']):
            # إذا كان النص يحتوي على كلمات مفتاحية لكن ليس بتنسيق رابط صحيح
            # نحاول تنظيف النص وأخذ أول رابط
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if 'https://' in line or 'http://' in line:
                    # استخراج الرابط من السطر
                    urlmatch = re.search(r'https?://[^\s]+', line)
                    if urlmatch:
                        result['isvalid'] = True
                        result['cleaneddata'] = urlmatch.group(0)
                        return result
        
        # فشل التحقق
        result['errormessage'] = """❌ رابط إنستاباي غير صحيح

📍 يجب إدخال رابط كامل فقط
• لا يُقبل اسم المستخدم بدون رابط
• يجب أن يحتوي على instapay أو ipn.eg

✅ أمثلة صحيحة:
• https://ipn.eg/S/username/instapay/ABC123
• https://instapay.com/username
• ipn.eg/S/ABC123
• instapay.com/username"""
        
        return result
    
    def recordfailure(self, userid: int):
        """تسجيل محاولة فاشلة"""
        self.failedattempts[userid] += 1
        
        if self.failedattempts[userid] >= self.MAXFAILEDATTEMPTS:
            self.blockedusers[userid] = datetime.now()
            return True  # تم الحظر
        
        return False
    
    def resetuserfailures(self, userid: int):
        """إعادة تعيين المحاولات الفاشلة عند النجاح"""
        self.failedattempts[userid] = 0
        if userid in self.blockedusers:
            del self.blockedusers[userid]
    
    def getremainingattempts(self, userid: int) -> int:
        """الحصول على عدد المحاولات المتبقية"""
        return self.MAXFAILEDATTEMPTS - self.failedattempts.get(userid, 0)

# إنشاء نظام التحقق من طرق الدفع
paymentvalidation = PaymentValidationSystem()

# ================================ قاعدة البيانات ================================
class Database:
    """مدير قاعدة البيانات"""

    def __init__(self):
        self.initdatabase()

    def getconnection(self):
        """إنشاء اتصال جديد"""
        conn = sqlite3.connect(DATABASEPATH)
        conn.rowfactory = sqlite3.Row
        return conn

    def initdatabase(self):
        """تهيئة قاعدة البيانات"""
        conn = self.getconnection()
        cursor = conn.cursor()

        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                userid INTEGER PRIMARY KEY AUTOINCREMENT,
                telegramid INTEGER UNIQUE NOT NULL,
                username TEXT,
                fullname TEXT,
                registrationstatus TEXT DEFAULT 'incomplete',
                createdat TIMESTAMP DEFAULT CURRENTTIMESTAMP
            )
        ''')

        # جدول بيانات التسجيل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrationdata (
                userid INTEGER PRIMARY KEY,
                platform TEXT,
                whatsapp TEXT,
                whatsappnetwork TEXT,
                paymentmethod TEXT,
                paymentdetails TEXT,
                paymentdetailstype TEXT,
                paymentnetwork TEXT,
                phone TEXT,
                paymentinfo TEXT,
                FOREIGN KEY (userid) REFERENCES users(userid)
            )
        ''')
        
        # إضافة العمود whatsappnetwork للجداول الموجودة (للتوافق مع قواعد البيانات القديمة)
        try:
            cursor.execute('ALTER TABLE registrationdata ADD COLUMN whatsappnetwork TEXT')
            conn.commit()
            logger.info("تم إضافة عمود whatsappnetwork بنجاح")
        except:
            # العمود موجود بالفعل، لا مشكلة
            pass



        # جدول التسجيل المؤقت
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tempregistration (
                telegramid INTEGER PRIMARY KEY,
                stepname TEXT,
                stepnumber INTEGER,
                data TEXT,
                updatedat TIMESTAMP DEFAULT CURRENTTIMESTAMP
            )
        ''')

        # جدول المحفظة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet (
                userid INTEGER PRIMARY KEY,
                coinbalance REAL DEFAULT 0,
                loyaltypoints INTEGER DEFAULT 0,
                FOREIGN KEY (userid) REFERENCES users(userid)
            )
        ''')

        # جدول المعاملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER,
                type TEXT,
                amount REAL,
                status TEXT,
                createdat TIMESTAMP DEFAULT CURRENTTIMESTAMP,
                FOREIGN KEY (userid) REFERENCES users(userid)
            )
        ''')

        conn.commit()
        conn.close()

    def createuser(self, telegramid: int, username: str, fullname: str) -> int:
        """إنشاء مستخدم جديد"""
        conn = self.getconnection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO users (telegramid, username, fullname)
                VALUES (?, ?, ?)
            ''', (telegramid, username, fullname))

            if cursor.rowcount == 0:
                cursor.execute('SELECT userid FROM users WHERE telegramid = ?', (telegramid,))
                userid = cursor.fetchone()['userid']
            else:
                userid = cursor.lastrowid

                # إنشاء سجلات فارغة
                cursor.execute('INSERT INTO registrationdata (userid) VALUES (?)', (userid,))
                cursor.execute('INSERT INTO wallet (userid) VALUES (?)', (userid,))

            conn.commit()
            conn.close()
            return userid

        except Exception as e:
            conn.close()
            logger.error(f"خطأ في إنشاء المستخدم: {e}")
            return None

    def savetempregistration(self, telegramid: int, stepname: str, stepnumber: int, data: dict):
        """حفظ التسجيل المؤقت"""
        conn = self.getconnection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO tempregistration (telegramid, stepname, stepnumber, data)
            VALUES (?, ?, ?, ?)
        ''', (telegramid, stepname, stepnumber, json.dumps(data)))

        conn.commit()
        conn.close()

    def gettempregistration(self, telegramid: int) -> Optional[dict]:
        """استرجاع التسجيل المؤقت"""
        conn = self.getconnection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT  FROM tempregistration WHERE telegramid = ?
        ''', (telegramid,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'stepname': row['stepname'],
                'stepnumber': row['stepnumber'],
                'data': json.loads(row['data'])
            }
        return None

    def cleartempregistration(self, telegramid: int):
        """حذف التسجيل المؤقت"""
        conn = self.getconnection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tempregistration WHERE telegramid = ?', (telegramid,))
        conn.commit()
        conn.close()

    def completeregistration(self, telegramid: int, data: dict) -> bool:
        """إكمال التسجيل"""
        conn = self.getconnection()
        cursor = conn.cursor()

        try:
            # الحصول على معرف المستخدم
            cursor.execute('SELECT userid FROM users WHERE telegramid = ?', (telegramid,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                return False

            userid = user['userid']

            # محاولة إضافة الحقول الجديدة إذا لم تكن موجودة (مع حماية من الأخطاء)
            try:
                cursor.execute("ALTER TABLE registrationdata ADD COLUMN paymentdetails TEXT")
            except sqlite3.OperationalError:
                pass  # العمود موجود بالفعل
            except Exception as e:
                logger.debug(f"Column paymentdetails may already exist: {e}")
                pass
            
            try:
                cursor.execute("ALTER TABLE registrationdata ADD COLUMN paymentdetailstype TEXT")
            except sqlite3.OperationalError:
                pass  # العمود موجود بالفعل
            except Exception as e:
                logger.debug(f"Column paymentdetailstype may already exist: {e}")
                pass
            
            try:
                cursor.execute("ALTER TABLE registrationdata ADD COLUMN paymentnetwork TEXT")
            except sqlite3.OperationalError:
                pass  # العمود موجود بالفعل
            except Exception as e:
                logger.debug(f"Column paymentnetwork may already exist: {e}")
                pass
            
            # تحديث بيانات التسجيل
            cursor.execute('''
                UPDATE registrationdata
                SET platform = ?, whatsapp = ?, whatsappnetwork = ?, paymentmethod = ?
                WHERE userid = ?
            ''', (
                data.get('platform'),
                data.get('whatsapp'),
                data.get('whatsappnetwork', ''),
                data.get('paymentmethod'),
                userid
            ))
            
            # محاولة تحديث الحقول الجديدة إذا كانت موجودة
            if data.get('paymentdetails'):
                try:
                    cursor.execute('''
                        UPDATE registrationdata
                        SET paymentdetails = ?, paymentdetailstype = ?, paymentnetwork = ?
                        WHERE userid = ?
                    ''', (
                        data.get('paymentdetails'),
                        data.get('paymentdetailstype'),
                        data.get('paymentnetwork'),
                        userid
                    ))
                except:
                    pass



            # تحديث حالة التسجيل
            cursor.execute('''
                UPDATE users SET registrationstatus = 'complete' WHERE userid = ?
            ''', (userid,))

            # إضافة نقاط الترحيب
            cursor.execute('''
                UPDATE wallet SET loyaltypoints = loyaltypoints + 100 WHERE userid = ?
            ''', (userid,))

            conn.commit()
            conn.close()

            # حذف البيانات المؤقتة
            self.cleartempregistration(telegramid)

            return True

        except Exception as e:
            conn.close()
            logger.error(f"خطأ في إكمال التسجيل: {e}")
            return False

    def getuserbytelegramid(self, telegramid: int) -> Optional[dict]:
        """الحصول على المستخدم"""
        conn = self.getconnection()
        cursor = conn.cursor()

        cursor.execute('SELECT  FROM users WHERE telegramid = ?', (telegramid,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    def getuserdata(self, telegramid: int) -> Optional[dict]:
        """الحصول على بيانات المستخدم الكاملة"""
        conn = self.getconnection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u., r.
            FROM users u
            LEFT JOIN registrationdata r ON u.userid = r.userid
            WHERE u.telegramid = ?
        ''', (telegramid,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def getuserprofile(self, telegramid: int) -> Optional[dict]:
        """الحصول على الملف الشخصي"""
        conn = self.getconnection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u., r., w.
            FROM users u
            LEFT JOIN registrationdata r ON u.userid = r.userid
            LEFT JOIN wallet w ON u.userid = w.userid
            WHERE u.telegramid = ?
        ''', (telegramid,))

        row = cursor.fetchone()

        if row:
            profile = dict(row)

            # عدد المعاملات
            cursor.execute('''
                SELECT COUNT() as transactioncount
                FROM transactions WHERE userid = ?
            ''', (profile['userid'],))

            profile['transactioncount'] = cursor.fetchone()['transactioncount']
            profile['levelname'] = self.getlevelname(profile.get('loyaltypoints', 0))

            conn.close()
            return profile

        conn.close()
        return None

    def getlevelname(self, points: int) -> str:
        """تحديد اسم المستوى"""
        if points >= 5000:
            return 'أسطورة 👑'
        elif points >= 1000:
            return 'خبير 💎'
        elif points >= 500:
            return 'محترف ⚡'
        elif points >= 100:
            return 'نشط 🔥'
        else:
            return 'مبتدئ 🌱'

    def updateuserdata(self, telegramid: int, updatedata: dict) -> bool:
        """تحديث بيانات المستخدم"""
        conn = self.getconnection()
        cursor = conn.cursor()
        
        try:
            # الحصول على userid
            cursor.execute('SELECT userid FROM users WHERE telegramid = ?', (telegramid,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False
            
            userid = user['userid']
            
            # تحديث بيانات التسجيل
            if 'platform' in updatedata:
                cursor.execute('''
                    UPDATE registrationdata
                    SET platform = ?
                    WHERE userid = ?
                ''', (updatedata['platform'], userid))
            
            if 'whatsapp' in updatedata:
                cursor.execute('''
                    UPDATE registrationdata
                    SET whatsapp = ?, whatsappnetwork = ?
                    WHERE userid = ?
                ''', (
                    updatedata.get('whatsapp'),
                    updatedata.get('whatsappnetwork', ''),
                    userid
                ))
            
            if 'paymentmethod' in updatedata:
                cursor.execute('''
                    UPDATE registrationdata
                    SET paymentmethod = ?
                    WHERE userid = ?
                ''', (updatedata['paymentmethod'], userid))
            
            if 'paymentdetails' in updatedata:
                cursor.execute('''
                    UPDATE registrationdata
                    SET paymentdetails = ?, paymentdetailstype = ?, paymentnetwork = ?
                    WHERE userid = ?
                ''', (
                    updatedata.get('paymentdetails'),
                    updatedata.get('paymentdetailstype', ''),
                    updatedata.get('paymentnetwork', ''),
                    userid
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            logger.error(f"خطأ في تحديث بيانات المستخدم: {e}")
            return False
    
    def updateuserplatform(self, telegramid: int, platform: str) -> bool:
        """تحديث منصة المستخدم"""
        return self.updateuserdata(telegramid, {'platform': platform})
    
    def deleteuseraccount(self, telegramid: int) -> bool:
        """حذف حساب المستخدم"""
        conn = self.getconnection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT userid FROM users WHERE telegramid = ?', (telegramid,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                return False

            userid = user['userid']

            # حذف من جميع الجداول
            cursor.execute('DELETE FROM transactions WHERE userid = ?', (userid,))
            cursor.execute('DELETE FROM wallet WHERE userid = ?', (userid,))

            cursor.execute('DELETE FROM registrationdata WHERE userid = ?', (userid,))
            cursor.execute('DELETE FROM tempregistration WHERE telegramid = ?', (telegramid,))
            cursor.execute('DELETE FROM users WHERE userid = ?', (userid,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            conn.rollback()
            conn.close()
            logger.error(f"خطأ في حذف الحساب: {e}")
            return False







# ================================ لوحات المفاتيح ================================
class Keyboards:
    """لوحات المفاتيح"""

    @staticmethod
    def getstartkeyboard():
        """لوحة البداية"""
        keyboard = [
            [InlineKeyboardButton("🆕 تسجيل جديد", callbackdata="registernew")],
            [InlineKeyboardButton("📞 الدعم الفني", callbackdata="support")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def getplatformkeyboard():
        """لوحة المنصات"""
        keyboard = []
        for key, platform in GAMINGPLATFORMS.items():
            keyboard.append([
                InlineKeyboardButton(platform['name'], callbackdata=f"platform{key}")
            ])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def getpaymentkeyboard():
        """لوحة طرق الدفع"""
        keyboard = []
        for key, method in PAYMENTMETHODS.items():
            keyboard.append([
                InlineKeyboardButton(method['name'], callbackdata=f"payment{key}")
            ])
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def getcontinuekeyboard():
        """لوحة الاستكمال"""
        keyboard = [
            [InlineKeyboardButton("✅ أكمل من حيث توقفت", callbackdata="continueregistration")],
            [InlineKeyboardButton("🔄 ابدأ من جديد", callbackdata="restartregistration")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def getdeletekeyboard():
        """لوحة حذف الحساب"""
        keyboard = [
            [InlineKeyboardButton("✅ نعم، احذف حسابي", callbackdata="confirmdelete")],
            [InlineKeyboardButton("❌ لا، تراجع", callbackdata="canceldelete")]
        ]
        return InlineKeyboardMarkup(keyboard)

# ================================ معالج التسجيل الذكي ================================
class SmartRegistrationHandler:
    """معالج التسجيل مع النظام الذكي"""

    def __init__(self):
        self.db = Database()

    async def start(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """بداية التسجيل"""
        telegramid = update.effectiveuser.id
        username = update.effectiveuser.username

        # التحقق من وجود تسجيل سابق غير مكتمل
        tempdata = self.db.gettempregistration(telegramid)

        if tempdata:
            # استعادة البيانات المحفوظة
            context.userdata['registration'] = tempdata['data']
            step = tempdata['stepnumber']

            stepnames = {
                ENTERINGWHATSAPP: "إدخال واتساب",
                CHOOSINGPAYMENT: "اختيار طريقة الدفع"
            }
            laststep = stepnames.get(step, "غير معروف")

            message = MESSAGES['welcomeback'].format(laststep=laststep)

            # إضافة أزرار للاختيار بين المتابعة أو البدء من جديد
            keyboard = [
                [InlineKeyboardButton("✅ متابعة من حيث توقفت", callbackdata="continueregistration")],
                [InlineKeyboardButton("🔄 البدء من جديد", callbackdata="restartregistration")]
            ]
            replymarkup = InlineKeyboardMarkup(keyboard)

            # إرسال رسالة مع الأزرار
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                message + "\n\nماذا تريد أن تفعل؟",
                replymarkup=replymarkup
            )

            # لا نرسل رسالة الخطوة مباشرة، بل ننتظر اختيار المستخدم
            return ConversationHandler.END


        # مستخدم جديد
        await smartmessagemanager.sendnewactivemessage(
            update, context, MESSAGES['welcome'],
            replymarkup=Keyboards.getstartkeyboard()
        )

        return ConversationHandler.END

    async def handleregistrationstart(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """بدء التسجيل الجديد مع حماية من الضغط المتكرر"""
        query = update.callbackquery
        
        # الرد على الـ callback query بسرعة
        await query.answer()
        
        telegramid = query.fromuser.id
        username = query.fromuser.username
        fullname = query.fromuser.fullname
        
        # التحقق من عدم وجود تسجيل قيد المعالجة
        if 'registration' in context.userdata and context.userdata['registration'].get('inprogress'):
            logger.debug(f"تجاهل محاولة بدء تسجيل مكرر للمستخدم {telegramid}")
            return

        # وضع علامة أن التسجيل قيد المعالجة
        context.userdata['registration'] = {
            'inprogress': True,
            'telegramid': telegramid
        }

        # مسح أي بيانات تسجيل قديمة
        self.db.cleartempregistration(telegramid)

        userid = self.db.createuser(telegramid, username, fullname)

        # تحديث بيانات التسجيل
        context.userdata['registration'].update({
            'userid': userid,
            'inprogress': False  # إلغاء العلامة بعد اكتمال المعالجة
        })

        await smartmessagemanager.updatecurrentmessage(
            update, context, MESSAGES['chooseplatform'],
            replymarkup=Keyboards.getplatformkeyboard()
        )

        return CHOOSINGPLATFORM

    async def handleplatformchoice(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """اختيار المنصة مع حماية من الضغط المتكرر"""
        query = update.callbackquery
        
        # الرد على الـ callback query بسرعة لمنع ظهور رمز التحميل
        await query.answer()
        
        # التحقق من أن البيانات صحيحة
        if not query.data.startswith("platform"):
            return
        
        platformkey = query.data.replace("platform", "")
        
        # التحقق من صحة المنصة
        if platformkey not in GAMINGPLATFORMS:
            await query.answer("❌ منصة غير صحيحة", showalert=True)
            return
        
        platformname = GAMINGPLATFORMS[platformkey]['name']
        
        # التحقق من وضع التعديل
        isediting = context.userdata.get('editingmode') == 'whatsappfull'
        
        if isediting:
            # في وضع التعديل - نحفظ في editregistration
            if 'editregistration' not in context.userdata:
                context.userdata['editregistration'] = {
                    'telegramid': query.fromuser.id,
                    'isediting': True
                }
            
            context.userdata['editregistration']['platform'] = platformkey
            
            # عرض رسالة إدخال رقم الواتساب الجديد
            await smartmessagemanager.updatecurrentmessage(
                update, context,
                f"✅ تم اختيار: {platformname}\n\n📱 أدخل رقم الواتساب الجديد:\n\n" + MESSAGES['enterwhatsapp']
            )
        else:
            # في وضع التسجيل العادي
            if 'registration' not in context.userdata:
                context.userdata['registration'] = {
                    'telegramid': query.fromuser.id
                }
            
            # التحقق من عدم تكرار نفس الاختيار
            if context.userdata['registration'].get('platform') == platformkey:
                logger.debug(f"تجاهل اختيار منصة مكرر: {platformkey}")
                return

            context.userdata['registration']['platform'] = platformkey

            self.db.savetempregistration(
                context.userdata['registration']['telegramid'],
                'platformchosen', ENTERINGWHATSAPP,
                context.userdata['registration']
            )

            # استخدام updatecurrentmessage لتحديث الرسالة الحالية بدلاً من إرسال جديدة
            await smartmessagemanager.updatecurrentmessage(
                update, context,
                f"✅ تم اختيار: {platformname}\n\n" + MESSAGES['enterwhatsapp']
            )

        return ENTERINGWHATSAPP

    async def handlewhatsappinput(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """إدخال واتساب مع نظام الحماية المتقدم"""
        userid = update.effectiveuser.id
        whatsappinput = update.message.text.strip()
        
        # 1. فحص الحظر
        isblocked, remainingminutes = whatsappsecurity.isuserblocked(userid)
        if isblocked:
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                f"""🚫 أنت محظور مؤقتاً

⏰ المدة المتبقية: {remainingminutes} دقيقة

📝 السبب: تجاوز عدد المحاولات الخاطئة المسموح بها

💡 نصيحة: تأكد من إدخال رقم واتساب صحيح عند المحاولة مرة أخرى""",
                disableprevious=False
            )
            return ENTERINGWHATSAPP
        
        # 2. فحص معدل الطلبات
        rateok, ratemessage = whatsappsecurity.checkratelimit(userid)
        if not rateok:
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                ratemessage,
                disableprevious=False
            )
            return ENTERINGWHATSAPP
        
        # 3. فحص التكرار
        if whatsappsecurity.checkduplicate(userid, whatsappinput):
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                f"""⚠️ لقد أدخلت هذا الرقم بالفعل

🔢 الرقم: {whatsappinput}

💡 نصيحة: إذا كان الرقم صحيحاً، انتظر رسالة التأكيد
إذا كنت تريد تغييره، أدخل رقماً مختلفاً""",
                disableprevious=False
            )
            return ENTERINGWHATSAPP
        
        # 4. التحقق الشامل من الرقم
        validation = whatsappsecurity.validatewhatsapp(whatsappinput, userid)
        
        if not validation['isvalid']:
            # تسجيل المحاولة الفاشلة
            wasblocked = whatsappsecurity.recordfailure(userid)
            remaining = whatsappsecurity.getremainingattempts(userid)
            
            # إضافة معلومات المحاولات المتبقية للرسالة
            errormsg = validation['errormessage']
            
            if wasblocked:
                errormsg += f"""

🚫 تم حظرك مؤقتاً لمدة {whatsappsecurity.BLOCKDURATIONMINUTES} دقيقة
السبب: تجاوز عدد المحاولات الخاطئة"""
            elif remaining > 0:
                errormsg += f"""

⚠️ تحذير: لديك {remaining} محاولات متبقية"""
            
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                errormsg,
                disableprevious=False
            )
            
            # تسجيل المحاولة في السجلات
            logger.warning(f"محاولة فاشلة من المستخدم {userid}: {validation['errortype']} - Input: {whatsappinput}")
            
            return ENTERINGWHATSAPP
        
        # 5. النجاح! إعادة تعيين المحاولات الفاشلة
        whatsappsecurity.resetuserfailures(userid)
        
        # حفظ الرقم المنظف في السياق
        cleanednumber = validation['cleanednumber']
        networkinfo = validation['networkinfo']
        
        # التحقق من وضع التعديل
        isediting = context.userdata.get('editingmode') in ['whatsapponly', 'whatsappfull', 'paymentonly']
        
        if isediting:
            # في وضع التعديل - نحفظ في editregistration
            if 'editregistration' not in context.userdata:
                context.userdata['editregistration'] = {
                    'telegramid': userid,
                    'isediting': True
                }
            
            context.userdata['editregistration']['whatsapp'] = cleanednumber
            context.userdata['editregistration']['whatsappnetwork'] = networkinfo['name']
            
            # في حالة تعديل الواتساب فقط، نحفظ مباشرة
            if context.userdata.get('editingmode') == 'whatsapponly':
                # تحديث قاعدة البيانات
                success = self.db.updateuserdata(userid, {
                    'whatsapp': cleanednumber,
                    'whatsappnetwork': networkinfo['name']
                })
                
                if success:
                    # عرض رسالة النجاح والعودة للملف الشخصي
                    profile = self.db.getuserprofile(userid)
                    
                    profiletext = f"""
✅ تم تحديث رقم الواتساب بنجاح!
━━━━━━━━━━━━━━━━

👤 الملف الشخصي المحدث
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {cleanednumber} ✅
💳 طريقة الدفع: {profile.get('paymentmethod', 'غير محدد')}

━━━━━━━━━━━━━━━━
🔐 بياناتك محمية ومشفرة
"""
                    
                    keyboard = [
                        [InlineKeyboardButton("✏️ تعديل آخر", callbackdata="editprofile")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callbackdata="mainmenu")]
                    ]
                    replymarkup = InlineKeyboardMarkup(keyboard)
                    
                    await smartmessagemanager.sendnewactivemessage(
                        update, context, profiletext,
                        replymarkup=replymarkup
                    )
                    
                    # مسح وضع التعديل
                    context.userdata.pop('editingmode', None)
                    context.userdata.pop('editregistration', None)
                    
                    return ConversationHandler.END
                else:
                    await smartmessagemanager.sendnewactivemessage(
                        update, context,
                        "❌ حدث خطأ في حفظ البيانات. حاول مرة أخرى.",
                        disableprevious=False
                    )
                    return ConversationHandler.END
        else:
            # في وضع التسجيل العادي
            if 'registration' not in context.userdata:
                context.userdata['registration'] = {
                    'telegramid': userid
                }
            
            context.userdata['registration']['whatsapp'] = cleanednumber
            context.userdata['registration']['whatsappnetwork'] = networkinfo['name']
            
            # حفظ في قاعدة البيانات المؤقتة
            try:
                self.db.savetempregistration(
                    context.userdata['registration']['telegramid'],
                    'whatsappentered',
                    CHOOSINGPAYMENT,
                    context.userdata['registration']
                )
            except Exception as e:
                logger.error(f"Error saving temp registration: {e}")
        
        # رسالة النجاح المفصلة
        successmessage = f"""✅ تم حفظ رقم الواتساب بنجاح!

📱 الرقم: {cleanednumber}
🌐 الشبكة: {networkinfo['emoji']} {networkinfo['name']}
💾 تم الحفظ التلقائي ✅

━━━━━━━━━━━━━━━━
⏭️ الخطوة التالية: اختر طريقة الدفع المفضلة"""
        
        # إرسال رسالة النجاح مع خيارات الدفع
        await smartmessagemanager.sendnewactivemessage(
            update, context,
            successmessage + "\n\n" + MESSAGES['choosepayment'],
            replymarkup=Keyboards.getpaymentkeyboard(),
            choicemade=f"واتساب: {cleanednumber}"
        )
        
        # تسجيل النجاح
        logger.info(f"تم حفظ رقم واتساب للمستخدم {userid}: {cleanednumber} - شبكة: {networkinfo['name']}")
        
        return CHOOSINGPAYMENT

    async def handlepaymentchoice(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """اختيار طريقة الدفع مع حماية من الضغط المتكرر"""
        query = update.callbackquery
        
        # الرد على الـ callback query بسرعة
        await query.answer()
        
        # التحقق من أن البيانات صحيحة
        if not query.data.startswith("payment"):
            return
        
        paymentkey = query.data.replace("payment", "")
        
        # التحقق من صحة طريقة الدفع
        if paymentkey not in PAYMENTMETHODS:
            await query.answer("❌ طريقة دفع غير صحيحة", showalert=True)
            return
        
        paymentname = PAYMENTMETHODS[paymentkey]['name']
        
        # التحقق من وضع التعديل
        isediting = context.userdata.get('editingmode') in ['whatsappfull', 'paymentonly']
        
        if isediting:
            # في وضع التعديل - نحفظ في editregistration
            if 'editregistration' not in context.userdata:
                await query.answer("❌ يجب البدء من جديد", showalert=True)
                return ConversationHandler.END
            
            # التحقق من عدم تكرار نفس الاختيار
            if context.userdata['editregistration'].get('paymentmethod') == paymentkey:
                logger.debug(f"تجاهل اختيار طريقة دفع مكررة: {paymentkey}")
                return
            
            context.userdata['editregistration']['paymentmethod'] = paymentkey
        else:
            # في وضع التسجيل العادي
            if 'registration' not in context.userdata:
                await query.answer("❌ يجب البدء من جديد", showalert=True)
                return ConversationHandler.END
            
            # التحقق من عدم تكرار نفس الاختيار
            if context.userdata['registration'].get('paymentmethod') == paymentkey:
                logger.debug(f"تجاهل اختيار طريقة دفع مكررة: {paymentkey}")
                return

            context.userdata['registration']['paymentmethod'] = paymentkey
            
            # حفظ في قاعدة البيانات المؤقتة
            self.db.savetempregistration(
                context.userdata['registration']['telegramid'],
                'paymentmethodchosen',
                ENTERINGPAYMENTDETAILS,
                context.userdata['registration']
            )
        
        # عرض التعليمات حسب نوع طريقة الدفع
        instructions = self.getpaymentinstructions(paymentkey)
        
        await smartmessagemanager.updatecurrentmessage(
            update, context,
            instructions
        )
        
        return ENTERINGPAYMENTDETAILS
    
    def getpaymentinstructions(self, paymentkey: str) -> str:
        """الحصول على التعليمات المناسبة لكل طريقة دفع"""
        
        if paymentkey == 'vodafonecash':
            return """⭕️ فودافون كاش

📱 أدخل رقم:

📝 القواعد:
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ مثال صحيح: 01012345678"""
        
        elif paymentkey == 'etisalatcash':
            return """🟢 اتصالات كاش

📱 أدخل رقم:

📝 القواعد:
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ مثال صحيح: 01112345678"""
        
        elif paymentkey == 'orangecash':
            return """🍊 أورانج كاش

📱 أدخل رقم:

📝 القواعد:
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ مثال صحيح: 01212345678"""
        
        elif paymentkey == 'wecash':
            return """🟣 وي كاش

📱 أدخل رقم:

📝 القواعد:
• 11 رقم بالضبط
• يبدأ بـ 010 / 011 / 012 / 015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ مثال صحيح: 01512345678"""
        
        elif paymentkey == 'bankwallet':
            return """🏦 محفظة بنكية

📱 أدخل رقم المحفظة البنكية:

📝 القواعد:
• 11 رقم بالضبط
• يقبل جميع الشبكات: 010/011/012/015
• أرقام إنجليزية فقط (0-9)
• بدون مسافات أو رموز

✅ أمثلة صحيحة:
• 01012345678 - فودافون ⭕
• 01112345678 - اتصالات 🟢
• 01212345678 - أورانج 🍊
• 01512345678 - وي 🟣

📌 ملاحظة مهمة: المحفظة البنكية تقبل جميع الشبكات المصرية
✅ يمكنك استخدام أي رقم من الشبكات الأربعة"""
        
        elif paymentkey == 'telda':
            return """💳 تيلدا

💳 أدخل رقم كارت تيلدا:

📝 القواعد:
• 16 رقم بالضبط
• أرقام فقط
• يُسمح بالمسافات والشرطات (سيتم إزالتها تلقائياً)

✅ أمثلة صحيحة:
• 1234567890123456
• 1234-5678-9012-3456
• 1234 5678 9012 3456"""
        
        elif paymentkey == 'instapay':
            return """🔗 إنستا باي

🔗 أدخل رابط إنستاباي كامل:

📝 القواعد:
• يجب إدخال رابط كامل فقط
• لا يُقبل اسم المستخدم بدون رابط
• يجب أن يحتوي على instapay أو ipn.eg

✅ أمثلة صحيحة:
• https://ipn.eg/S/username/instapay/ABC123
• https://instapay.com/username
• ipn.eg/S/ABC123
• instapay.com/username"""
        
        return "طريقة دفع غير معروفة"
    
    async def handlepaymentdetailsinput(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """معالج إدخال بيانات طريقة الدفع مع التشفير"""
        userid = update.effectiveuser.id
        paymentinput = update.message.text.strip()
        
        # التحقق من وضع التعديل
        isediting = context.userdata.get('editingmode') in ['whatsappfull', 'paymentonly']
        
        if isediting:
            # في وضع التعديل
            if 'editregistration' not in context.userdata or 'paymentmethod' not in context.userdata['editregistration']:
                await smartmessagemanager.sendnewactivemessage(
                    update, context,
                    "❌ حدث خطأ. يرجى البدء من جديد بكتابة /start",
                    disableprevious=False
                )
                return ConversationHandler.END
            
            paymentmethod = context.userdata['editregistration']['paymentmethod']
        else:
            # في وضع التسجيل العادي
            if 'registration' not in context.userdata or 'paymentmethod' not in context.userdata['registration']:
                await smartmessagemanager.sendnewactivemessage(
                    update, context,
                    "❌ حدث خطأ. يرجى البدء من جديد بكتابة /start",
                    disableprevious=False
                )
                return ConversationHandler.END
            
            paymentmethod = context.userdata['registration']['paymentmethod']
        
        # 1. فحص الحظر
        isblocked, remainingminutes = paymentvalidation.isuserblocked(userid)
        if isblocked:
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                f"""🚫 أنت محظور مؤقتاً

⏰ المدة المتبقية: {remainingminutes} دقيقة

📝 السبب: تجاوز عدد المحاولات الخاطئة المسموح بها

💡 نصيحة: تأكد من إدخال البيانات الصحيحة عند المحاولة مرة أخرى""",
                disableprevious=False
            )
            return ENTERINGPAYMENTDETAILS
        
        # 2. فحص معدل الطلبات
        rateok, ratemessage = paymentvalidation.checkratelimit(userid)
        if not rateok:
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                ratemessage,
                disableprevious=False
            )
            return ENTERINGPAYMENTDETAILS
        
        # 3. التحقق حسب نوع طريقة الدفع
        validationresult = None
        paymenttype = None
        
        if paymentmethod in ['vodafonecash', 'etisalatcash', 'orangecash', 'wecash', 'bankwallet']:
            validationresult = paymentvalidation.validatewallet(paymentinput, paymentmethod)
            paymenttype = 'wallet'
        elif paymentmethod == 'telda':
            validationresult = paymentvalidation.validatetelda(paymentinput)
            paymenttype = 'card'
        elif paymentmethod == 'instapay':
            validationresult = paymentvalidation.validateinstapay(paymentinput)
            paymenttype = 'link'
        
        # 4. معالجة النتيجة
        if not validationresult['isvalid']:
            # تسجيل المحاولة الفاشلة
            wasblocked = paymentvalidation.recordfailure(userid)
            remaining = paymentvalidation.getremainingattempts(userid)
            
            # إضافة معلومات المحاولات المتبقية للرسالة
            errormsg = validationresult['errormessage']
            
            if wasblocked:
                errormsg += f"""

🚫 تم حظرك مؤقتاً لمدة {paymentvalidation.BLOCKDURATIONMINUTES} دقيقة
السبب: تجاوز عدد المحاولات الخاطئة"""
            elif remaining > 0:
                errormsg += f"""

⚠️ تحذير: لديك {remaining} محاولات متبقية"""
            
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                errormsg,
                disableprevious=False
            )
            
            # تسجيل المحاولة في السجلات (بدون البيانات الحساسة)
            logger.warning(f"محاولة فاشلة من المستخدم {userid} لطريقة دفع: {paymentmethod}")
            
            return ENTERINGPAYMENTDETAILS
        
        # 5. النجاح! إعادة تعيين المحاولات الفاشلة
        paymentvalidation.resetuserfailures(userid)
        
        # 6. تشفير البيانات الحساسة
        encrypteddata = encryptionsystem.encrypt(validationresult['cleaneddata'])
        
        if isediting:
            # في وضع التعديل - نحفظ في editregistration
            context.userdata['editregistration']['paymentdetails'] = encrypteddata
            context.userdata['editregistration']['paymentdetailstype'] = paymenttype
            
            if paymenttype == 'wallet':
                context.userdata['editregistration']['paymentnetwork'] = validationresult.get('network', '')
        else:
            # في وضع التسجيل العادي
            context.userdata['registration']['paymentdetails'] = encrypteddata
            context.userdata['registration']['paymentdetailstype'] = paymenttype
            
            if paymenttype == 'wallet':
                context.userdata['registration']['paymentnetwork'] = validationresult.get('network', '')
            
            # حفظ في قاعدة البيانات المؤقتة
            try:
                self.db.savetempregistration(
                    context.userdata['registration']['telegramid'],
                    'paymentdetailsentered',
                    ConversationHandler.END,
                    context.userdata['registration']
                )
            except Exception as e:
                logger.error(f"Error saving temp registration: {e}")
        
        # 9. إعداد رسالة النجاح
        paymentname = PAYMENTMETHODS[paymentmethod]['name']
        
        if paymenttype == 'wallet':
            successmessage = f"""✅ تم حفظ {paymentname}!

📱 الرقم: {validationresult['cleaneddata']}

━━━━━━━━━━━━━━━━"""
        elif paymenttype == 'card':
            # عرض رقم الكارت كامل للعميل بدون إخفاء
            successmessage = f"""✅ تم حفظ كارت تيلدا!

💳 رقم الكارت: {validationresult['cleaneddata']}

━━━━━━━━━━━━━━━━"""
        elif paymenttype == 'link':
            successmessage = f"""✅ تم حفظ رابط إنستاباي!

🔗 الرابط: {validationresult['cleaneddata']}

━━━━━━━━━━━━━━━━"""
        
        # 10. إرسال رسالة النجاح ثم الانتقال للتأكيد النهائي
        await smartmessagemanager.sendnewactivemessage(
            update, context,
            successmessage,
            choicemade=f"{paymentname}: تم الحفظ"
        )
        
        # تسجيل النجاح (بدون البيانات الحساسة)
        logger.info(f"تم حفظ بيانات دفع للمستخدم {userid}: نوع {paymentmethod}")
        
        # الانتقال للتأكيد النهائي
        return await self.showconfirmation(update, context)



    async def showconfirmation(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """عرض التأكيد والحفظ التلقائي مع فك تشفير البيانات"""
        # التحقق من وضع التعديل
        isediting = context.userdata.get('editingmode') in ['whatsappfull', 'paymentonly']
        
        if isediting:
            # في وضع التعديل - نحدث البيانات في قاعدة البيانات
            regdata = context.userdata['editregistration']
            telegramid = regdata['telegramid']
            
            # تحديث البيانات في قاعدة البيانات
            updatedata = {}
            
            if 'platform' in regdata:
                updatedata['platform'] = regdata['platform']
            
            if 'whatsapp' in regdata:
                updatedata['whatsapp'] = regdata['whatsapp']
                if 'whatsappnetwork' in regdata:
                    updatedata['whatsappnetwork'] = regdata['whatsappnetwork']
            
            if 'paymentmethod' in regdata:
                updatedata['paymentmethod'] = regdata['paymentmethod']
            
            if 'paymentdetails' in regdata:
                updatedata['paymentdetails'] = regdata['paymentdetails']
                updatedata['paymentdetailstype'] = regdata.get('paymentdetailstype', '')
                if 'paymentnetwork' in regdata:
                    updatedata['paymentnetwork'] = regdata['paymentnetwork']
            
            # تحديث البيانات في قاعدة البيانات
            success = self.db.updateuserdata(telegramid, updatedata)
            
            # مسح وضع التعديل
            context.userdata.pop('editingmode', None)
            context.userdata.pop('editregistration', None)
        else:
            # في وضع التسجيل العادي
            regdata = context.userdata['registration']
            telegramid = regdata['telegramid']
            success = self.db.completeregistration(telegramid, regdata)
        
        # الحصول على اسم المستخدم
        if update.callbackquery:
            username = update.callbackquery.fromuser.username
        else:
            username = update.effectiveuser.username
        
        # إضافة @ للمستخدم إذا كان موجود
        usernamedisplay = f"@{username}" if username else "غير محدد"

        if success:
            # الحصول على البيانات المحدثة من قاعدة البيانات
            updateduserdata = self.db.getuserdata(telegramid)
            
            if updateduserdata:
                platform = GAMINGPLATFORMS.get(updateduserdata.get('platform'), {}).get('name', 'غير محدد')
                paymentmethod = updateduserdata.get('paymentmethod', '')
                paymentname = PAYMENTMETHODS.get(paymentmethod, {}).get('name', 'غير محدد')
                whatsapp = updateduserdata.get('whatsapp', 'غير محدد')
            else:
                platform = GAMINGPLATFORMS.get(regdata.get('platform'), {}).get('name', 'غير محدد')
                paymentmethod = regdata.get('paymentmethod', '')
                paymentname = PAYMENTMETHODS.get(paymentmethod, {}).get('name', 'غير محدد')
                whatsapp = regdata.get('whatsapp', 'غير محدد')
            
            # فك تشفير بيانات الدفع إذا كانت موجودة
            paymentdetailsdisplay = ""
            if 'paymentdetails' in regdata:
                try:
                    decrypteddata = encryptionsystem.decrypt(regdata['paymentdetails'])
                    paymenttype = regdata.get('paymentdetailstype', '')
                    
                    if paymenttype == 'wallet':
                        paymentdetailsdisplay = f"""
💰 بيانات الدفع:
• الرقم: {decrypteddata}"""
                    elif paymenttype == 'card':
                        # عرض رقم الكارت كامل للعميل بدون إخفاء
                        paymentdetailsdisplay = f"""
💰 بيانات الدفع:
• رقم الكارت: {decrypteddata}"""
                    elif paymenttype == 'link':
                        paymentdetailsdisplay = f"""
💰 بيانات الدفع:
• الرابط: {decrypteddata}"""
                except:
                    paymentdetailsdisplay = ""
            
            # رسالة النجاح - مختلفة حسب وضع التعديل
            if isediting:
                successmessage = f"""
✅ تم تحديث بياناتك بنجاح!

📊 ملخص البيانات المحدثة:
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {whatsapp}
💳 طريقة الدفع: {paymentname}{paymentdetailsdisplay}
━━━━━━━━━━━━━━━━

👤 اسم المستخدم: {usernamedisplay}
🆔 معرف التليجرام: {telegramid}

✨ تم تحديث ملفك الشخصي بنجاح!
"""
            else:
                successmessage = f"""
✅ تم حفظ بياناتك بنجاح!

📊 ملخص البيانات المحفوظة:
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform}
📱 واتساب: {whatsapp}
💳 طريقة الدفع: {paymentname}{paymentdetailsdisplay}
━━━━━━━━━━━━━━━━

👤 اسم المستخدم: {usernamedisplay}
🆔 معرف التليجرام: {telegramid}

🎉 مرحباً بك في عائلة FC 26! 🚀
"""

            # استخدام updatecurrentmessage إذا كان من callback
            if update.callbackquery:
                await smartmessagemanager.updatecurrentmessage(
                    update, context, successmessage
                )
            else:
                await smartmessagemanager.sendnewactivemessage(
                    update, context, successmessage
                )
            
            # مسح البيانات المؤقتة
            context.userdata.clear()
            
            # تنظيف بيانات المستخدم في SmartMessageManager
            await smartmessagemanager.cleanupuserdata(telegramid)
            
            return ConversationHandler.END
        else:
            # في حالة الفشل
            errormessage = "❌ حدث خطأ في حفظ البيانات. الرجاء المحاولة مرة أخرى."
            
            if update.callbackquery:
                await smartmessagemanager.updatecurrentmessage(
                    update, context, errormessage
                )
            else:
                await smartmessagemanager.sendnewactivemessage(
                    update, context, errormessage
                )
            
            return ConversationHandler.END



    async def handlecontinueregistration(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """استكمال التسجيل"""
        query = update.callbackquery
        await query.answer()

        telegramid = query.fromuser.id

        if query.data == "continueregistration":
            tempdata = self.db.gettempregistration(telegramid)

            if tempdata:
                context.userdata['registration'] = tempdata['data']
                step = tempdata['stepnumber']

                stepmessages = {
                    ENTERINGWHATSAPP: MESSAGES['enterwhatsapp'],
                    CHOOSINGPAYMENT: MESSAGES['choosepayment']
                }

                message = stepmessages.get(step, "")

                # عرض الرسالة المناسبة حسب الخطوة
                if step == CHOOSINGPAYMENT:
                    await smartmessagemanager.updatecurrentmessage(
                        update, context, message,
                        replymarkup=Keyboards.getpaymentkeyboard()
                    )
                elif step == CHOOSINGPLATFORM:
                    await smartmessagemanager.updatecurrentmessage(
                        update, context, message,
                        replymarkup=Keyboards.getplatformkeyboard()
                    )
                elif step == ENTERINGWHATSAPP:
                    # للواتساب نرسل الرسالة بدون لوحة مفاتيح
                    await smartmessagemanager.updatecurrentmessage(
                        update, context, message
                    )

                else:
                    await smartmessagemanager.updatecurrentmessage(
                        update, context, message
                    )

                return step

        elif query.data == "restartregistration":
            self.db.cleartempregistration(telegramid)

            await smartmessagemanager.updatecurrentmessage(
                update, context, MESSAGES['chooseplatform'],
                replymarkup=Keyboards.getplatformkeyboard()
            )

            context.userdata['registration'] = {'telegramid': telegramid}

            return CHOOSINGPLATFORM



    async def cancel(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """إلغاء التسجيل"""
        context.userdata.clear()

        await smartmessagemanager.sendnewactivemessage(
            update, context,
            "تم إلغاء عملية التسجيل. يمكنك البدء من جديد بكتابة /start"
        )

        return ConversationHandler.END

# ================================ البوت الرئيسي ================================
class FC26SmartBot:
    """البوت الذكي الكامل"""

    def __init__(self):
        self.db = Database()
        self.registrationhandler = SmartRegistrationHandler()

    async def start(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """أمر البداية مع النظام الذكي الموحد"""
        telegramid = update.effectiveuser.id
        
        # إذا كان هناك callbackquery، نتجاهل الطلب (منع التكرار)
        if update.callbackquery:
            return

        user = self.db.getuserbytelegramid(telegramid)

        if user and user.get('registrationstatus') == 'complete':
            # مستخدم مسجل - عرض القائمة الرئيسية مع النظام الذكي
            
            # التحقق من صلاحيات الأدمن
            isadmin = telegramid == ADMINID
            
            if isadmin:
                welcomemessage = f"""
👋 مرحباً بالأدمن!

🎮 بوت FC 26 - لوحة التحكم

⚡ لديك صلاحيات كاملة
"""
            else:
                welcomemessage = f"""
👋 أهلاً بعودتك!

🎮 بوت FC 26 - أفضل مكان لبيع كوينز

كيف يمكنني مساعدتك اليوم؟
"""
            
            # أزرار تفاعلية حسب الصلاحيات
            keyboard = [
                [InlineKeyboardButton("💸 بيع كوينز", callbackdata="sellcoins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callbackdata="profile")],
                [InlineKeyboardButton("📞 الدعم", callbackdata="support")]
            ]
            
            # إضافة أزرار الأدمن فقط للأدمن
            if isadmin:
                keyboard.append([InlineKeyboardButton("🔐 لوحة الأدمن", callbackdata="adminpanel")])
                keyboard.append([InlineKeyboardButton("🗑️ حذف حسابي", callbackdata="deleteaccount")])
                keyboard.append([InlineKeyboardButton("🗑️ حذف حساب مستخدم", callbackdata="admindeleteuser")])
            # المستخدمين العاديين لا يرون زر حذف الحساب
            
            replymarkup = InlineKeyboardMarkup(keyboard)

            # استخدام النظام الذكي دائماً
            await smartmessagemanager.sendnewactivemessage(
                update, context, welcomemessage,
                replymarkup=replymarkup,
                disableprevious=True  # تعطيل الرسالة السابقة
            )
        else:
            # مستخدم جديد - استخدام النظام الذكي للتسجيل
            await self.registrationhandler.start(update, context)

    async def profilecommand(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """عرض الملف الشخصي مع النظام الذكي"""
        telegramid = update.effectiveuser.id
        profile = self.db.getuserprofile(telegramid)

        if not profile:
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
            )
            return

        # الحصول على معلومات الشبكة إذا كان الرقم موجود
        whatsappdisplay = profile.get('whatsapp', 'غير محدد')
        networkdisplay = ""
        
        if whatsappdisplay != 'غير محدد' and len(whatsappdisplay) >= 3:
            prefix = whatsappdisplay[:3]
            if prefix in whatsappsecurity.EGYPTIANNETWORKS:
                network = whatsappsecurity.EGYPTIANNETWORKS[prefix]
                networkdisplay = f" ({network['emoji']} {network['name']})"
        
        profiletext = f"""
👤 الملف الشخصي
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {whatsappdisplay}{networkdisplay}
💳 طريقة الدفع: {profile.get('paymentmethod', 'غير محدد')}

━━━━━━━━━━━━━━━━
🔐 بياناتك محمية
"""

        # أزرار العودة
        keyboard = [
            [InlineKeyboardButton("✏️ تعديل الملف الشخصي", callbackdata="editprofile")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callbackdata="mainmenu")]
        ]
        replymarkup = InlineKeyboardMarkup(keyboard)

        await smartmessagemanager.sendnewactivemessage(
            update, context, profiletext,
            replymarkup=replymarkup
        )

    async def helpcommand(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """عرض المساعدة"""
        telegramid = update.effectiveuser.id
        isadmin = telegramid == ADMINID
        
        if isadmin:
            helptext = """
🆘 المساعدة والأوامر - أدمن
━━━━━━━━━━━━━━━━

📢 الأوامر المتاحة:

/start - البداية والقائمة الرئيسية
/profile - عرض ملفك الشخصي
/delete - حذف حسابك (أدمن فقط)
/help - هذه الرسالة

🔐 صلاحيات الأدمن:
• لوحة تحكم خاصة
• عرض جميع المستخدمين
• حذف المستخدمين
• البث الجماعي

🔗 للدعم والمساعدة:
@FC26Support
"""
        else:
            helptext = """
🆘 المساعدة والأوامر
━━━━━━━━━━━━━━━━

📢 الأوامر المتاحة:

/start - البداية والقائمة الرئيسية
/profile - عرض ملفك الشخصي
/help - هذه الرسالة

🔗 للدعم والمساعدة:
@FC26Support
"""
        # أزرار مفيدة
        keyboard = [
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callbackdata="mainmenu")],
            [InlineKeyboardButton("👤 ملفي الشخصي", callbackdata="profile")],
            [InlineKeyboardButton("📞 الدعم الفني", callbackdata="support")]
        ]
        replymarkup = InlineKeyboardMarkup(keyboard)

        await smartmessagemanager.sendnewactivemessage(
            update, context, helptext,
            replymarkup=replymarkup
        )

    async def deleteaccountcommand(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """حذف الحساب - للأدمن فقط"""
        telegramid = update.effectiveuser.id
        
        # التحقق من أن المستخدم هو الأدمن
        if telegramid != ADMINID:
            # عرض رسالة مساعدة للمستخدمين العاديين
            await update.message.replytext(
                "👋 استخدم الأوامر التالية:\n\n"
                "/start - البداية\n"
                "/profile - الملف الشخصي\n"
                "/help - المساعدة",
                replymarkup=ReplyKeyboardRemove()
            )
            return
        
        warning = """
⚠️ تحذير مهم!
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك الشخصي كأدمن؟

سيتم حذف:
• جميع بياناتك 🗑️
• صلاحيات الأدمن ستبقى

لا يمكن التراجع! ⛔
"""
        await smartmessagemanager.sendnewactivemessage(
            update, context, warning,
            replymarkup=Keyboards.getdeletekeyboard()
        )

    async def handledeleteconfirmation(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """تأكيد حذف الحساب مع النظام الذكي"""
        query = update.callbackquery
        await query.answer()

        if query.data == "confirmdelete":
            telegramid = query.fromuser.id

            success = self.db.deleteuseraccount(telegramid)

            if success:
                await smartmessagemanager.updatecurrentmessage(
                    update, context,
                    "✅ تم حذف حسابك بنجاح.\n\nيمكنك التسجيل مرة أخرى بكتابة /start"
                )
            else:
                await smartmessagemanager.updatecurrentmessage(
                    update, context,
                    "❌ حدث خطأ. حاول لاحقاً."
                )

        elif query.data == "canceldelete":
            telegramid = query.fromuser.id
            isadmin = telegramid == ADMINID
            
            # العودة للقائمة الرئيسية
            if isadmin:
                welcomemessage = f"""
✅ تم الإلغاء.

🎮 بوت FC 26 - لوحة التحكم

⚡ لديك صلاحيات كاملة
"""
            else:
                welcomemessage = f"""
✅ تم الإلغاء. سعداء لبقائك معنا! 😊

🎮 بوت FC 26 - أفضل مكان  لبيع كوينز

كيف يمكنني مساعدتك اليوم؟
"""

            keyboard = [
                [InlineKeyboardButton("💸 بيع كوينز", callbackdata="sellcoins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callbackdata="profile")],
                [InlineKeyboardButton("📞 الدعم", callbackdata="support")]
            ]
            
            if isadmin:
                keyboard.append([InlineKeyboardButton("🔐 لوحة الأدمن", callbackdata="adminpanel")])
                keyboard.append([InlineKeyboardButton("🗑️ حذف حسابي", callbackdata="deleteaccount")])
                keyboard.append([InlineKeyboardButton("🗑️ حذف حساب مستخدم", callbackdata="admindeleteuser")])
            # المستخدمين العاديين لا يرون زر حذف الحساب
            
            replymarkup = InlineKeyboardMarkup(keyboard)

            await smartmessagemanager.updatecurrentmessage(
                update, context, welcomemessage,
                replymarkup=replymarkup
            )

    async def handlemenubuttons(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """معالجة أزرار القائمة التفاعلية مع النظام الذكي"""
        query = update.callbackquery
        await query.answer()
        
        # لوج عند الضغط على الأزرار
        userid = query.fromuser.id
        messageid = query.message.messageid
        logger.info(f"🟡 المستخدم {userid} ضغط على زر: {query.data} - Message ID: {messageid}")

        if query.data == "profile":
            # استخدام النظام الذكي لعرض الملف الشخصي
            telegramid = query.fromuser.id
            profile = self.db.getuserprofile(telegramid)

            if not profile:
                await smartmessagemanager.updatecurrentmessage(
                    update, context,
                    "❌ يجب عليك التسجيل أولاً!\n\nاكتب /start للبدء"
                )
                return

            # الحصول على معلومات الشبكة إذا كان الرقم موجود
            whatsappdisplay = profile.get('whatsapp', 'غير محدد')
            networkdisplay = ""
            
            if whatsappdisplay != 'غير محدد' and len(whatsappdisplay) >= 3:
                prefix = whatsappdisplay[:3]
                if prefix in whatsappsecurity.EGYPTIANNETWORKS:
                    network = whatsappsecurity.EGYPTIANNETWORKS[prefix]
                    networkdisplay = f" ({network['emoji']} {network['name']})"
            
            profiletext = f"""
👤 الملف الشخصي
━━━━━━━━━━━━━━━━

🎮 المنصة: {profile.get('platform', 'غير محدد')}
📱 واتساب: {whatsappdisplay}{networkdisplay}
💳 طريقة الدفع: {profile.get('paymentmethod', 'غير محدد')}

━━━━━━━━━━━━━━━━
🔐 بياناتك محمية
"""

            # أزرار العودة
            keyboard = [
                [InlineKeyboardButton("✏️ تعديل الملف الشخصي", callbackdata="editprofile")],
                [InlineKeyboardButton("🏠 القائمة الرئيسية", callbackdata="mainmenu")]
            ]
            replymarkup = InlineKeyboardMarkup(keyboard)

            # تجنب خطأ HTTP 400 - نتأكد إن الرسالة مختلفة
            try:
                await smartmessagemanager.updatecurrentmessage(
                    update, context, profiletext,
                    replymarkup=replymarkup
                )
            except Exception as e:
                # لو حصل خطأ، نرسل رسالة جديدة
                logger.debug(f"Error updating message: {e}")
                await smartmessagemanager.sendnewactivemessage(
                    update, context, profiletext,
                    replymarkup=replymarkup,
                    disableprevious=True
                )

        elif query.data == "deleteaccount":
            # التحقق من أن المستخدم هو الأدمن
            telegramid = query.fromuser.id
            if telegramid != ADMINID:
                await query.answer("⛔ هذه الميزة للأدمن فقط!", showalert=True)
                return
            
            warning = """
⚠️ تحذير مهم!
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك الشخصي كأدمن؟

سيتم حذف:
• جميع بياناتك 🗑️
• صلاحيات الأدمن ستبقى

لا يمكن التراجع! ⛔
"""

            await smartmessagemanager.updatecurrentmessage(
                update, context, warning,
                replymarkup=Keyboards.getdeletekeyboard()
            )

        elif query.data == "sellcoins":
            await smartmessagemanager.updatecurrentmessage(
                update, context, "🚧 قريباً... خدمة بيع كوينز",
                choicemade="بيع كوينز"
            )

        elif query.data == "support":
            await smartmessagemanager.updatecurrentmessage(
                update, context, "📞 للدعم: @FC26Support",
                choicemade="الدعم الفني"
            )

        elif query.data == "mainmenu":
            telegramid = query.fromuser.id
            isadmin = telegramid == ADMINID
            
            # العودة للقائمة الرئيسية باستخدام النظام الذكي
            if isadmin:
                welcomemessage = f"""
👋 مرحباً بالأدمن!

🎮 بوت FC 26 - لوحة التحكم

⚡ لديك صلاحيات كاملة
"""
            else:
                welcomemessage = f"""
👋 أهلاً بعودتك!

🎮 بوت FC 26 - أفضل مكان  لبيع كوينز

كيف يمكنني مساعدتك اليوم؟
"""

            keyboard = [
                [InlineKeyboardButton("💸 بيع كوينز", callbackdata="sellcoins")],
                [InlineKeyboardButton("👤 الملف الشخصي", callbackdata="profile")],
                [InlineKeyboardButton("📞 الدعم", callbackdata="support")]
            ]
            
            if isadmin:
                keyboard.append([InlineKeyboardButton("🔐 لوحة الأدمن", callbackdata="adminpanel")])
                keyboard.append([InlineKeyboardButton("🗑️ حذف حسابي", callbackdata="deleteaccount")])
                keyboard.append([InlineKeyboardButton("🗑️ حذف حساب مستخدم", callbackdata="admindeleteuser")])
            # المستخدمين العاديين لا يرون زر حذف الحساب
            
            replymarkup = InlineKeyboardMarkup(keyboard)

            await smartmessagemanager.updatecurrentmessage(
                update, context, welcomemessage,
                replymarkup=replymarkup
            )
    
    async def handleeditprofile(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """معالج تعديل الملف الشخصي"""
        query = update.callbackquery
        await query.answer()
        
        # لوج عند الضغط على أزرار التعديل
        userid = query.fromuser.id
        messageid = query.message.messageid
        logger.info(f"🟡 المستخدم {userid} ضغط على زر: {query.data} - Message ID: {messageid}")
        
        if query.data == "editprofile":
            # عرض خيارات التعديل
            message = """
✏️ تعديل الملف الشخصي
━━━━━━━━━━━━━━━━

اختر ما تريد تعديله:
"""
            keyboard = [
                [InlineKeyboardButton("🎮 تعديل المنصة", callbackdata="editplatform")],
                [InlineKeyboardButton("📱 تعديل رقم الواتساب", callbackdata="editwhatsapp")],
                [InlineKeyboardButton("💳 تعديل طريقة الدفع", callbackdata="editpayment")],
                [InlineKeyboardButton("🔙 رجوع", callbackdata="profile")]
            ]
            replymarkup = InlineKeyboardMarkup(keyboard)
            
            await smartmessagemanager.updatecurrentmessage(
                update, context, message,
                replymarkup=replymarkup
            )
        
        elif query.data == "editplatform":
            # عرض خيارات المنصات للتعديل
            message = "🎮 اختر المنصة الجديدة:"
            keyboard = []
            
            for key, platform in GAMINGPLATFORMS.items():
                keyboard.append([
                    InlineKeyboardButton(
                        f"{platform['emoji']} {platform['name']}",
                        callbackdata=f"updateplatform{key}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("🔙 رجوع", callbackdata="editprofile")])
            replymarkup = InlineKeyboardMarkup(keyboard)
            
            await smartmessagemanager.updatecurrentmessage(
                update, context, message,
                replymarkup=replymarkup
            )
        
        elif query.data == "editwhatsapp":
            # بدء عملية تعديل الواتساب بشكل مباشر
            telegramid = query.fromuser.id
            
            # الحصول على بيانات المستخدم الحالية
            userdata = self.db.getuserdata(telegramid)
            if not userdata:
                await query.answer("❌ لم يتم العثور على بياناتك", showalert=True)
                return
            
            # حفظ البيانات الحالية للاستخدام في التعديل
            context.userdata['editingmode'] = 'whatsapponly'
            context.userdata['editregistration'] = {
                'telegramid': telegramid,
                'platform': userdata.get('platform'),  # نحتفظ بالمنصة الحالية
                'paymentmethod': userdata.get('paymentmethod'),  # نحتفظ بطريقة الدفع الحالية
                'isediting': True,
                'edittype': 'whatsapponly'
            }
            
            # طلب رقم الواتساب الجديد مباشرة
            message = """
📱 تعديل رقم الواتساب
━━━━━━━━━━━━━━━━

أرسل رقم الواتساب الجديد:

📌 مثال: 01012345678

⚠️ يجب أن يبدأ بـ:
• 010 (فودافون)
• 011 (اتصالات)
• 012 (أورانج)
• 015 (وي)
"""
            
            await smartmessagemanager.updatecurrentmessage(
                update, context, message,
                replymarkup=None  # لا نحتاج أزرار هنا
            )
            
            # ننتظر إدخال الرقم
            return ENTERINGWHATSAPP
        
        elif query.data == "editpayment":
            # بدء عملية تعديل طريقة الدفع بشكل تفاعلي
            telegramid = query.fromuser.id
            
            # الحصول على بيانات المستخدم الحالية
            userdata = self.db.getuserdata(telegramid)
            if not userdata:
                await query.answer("❌ لم يتم العثور على بياناتك", showalert=True)
                return
            
            # بدء عملية تعديل طريقة الدفع فقط
            context.userdata['editingmode'] = 'paymentonly'
            context.userdata['editregistration'] = {
                'telegramid': telegramid,
                'platform': userdata.get('platform'),
                'whatsapp': userdata.get('whatsapp'),  # نحتفظ بالواتساب الحالي
                'isediting': True,
                'edittype': 'paymentonly'
            }
            
            # الانتقال مباشرة لاختيار طريقة الدفع
            message = """
💳 تعديل طريقة الدفع
━━━━━━━━━━━━━━━━

اختر طريقة الدفع الجديدة:
"""
            replymarkup = Keyboards.getpaymentkeyboard()
            
            await smartmessagemanager.updatecurrentmessage(
                update, context, message,
                replymarkup=replymarkup
            )
            
            return CHOOSINGPAYMENT
        
        elif query.data.startswith("updateplatform"):
            # معالج تحديث المنصة
            platformkey = query.data.replace("updateplatform", "")
            telegramid = query.fromuser.id
            
            if platformkey in GAMINGPLATFORMS:
                # تحديث المنصة في قاعدة البيانات
                success = self.db.updateuserplatform(telegramid, platformkey)
                
                if success:
                    # عرض الملف الشخصي المحدث مباشرة
                    profile = self.db.getuserprofile(telegramid)
                    
                    whatsappdisplay = profile.get('whatsapp', 'غير محدد')
                    networkdisplay = ""
                    
                    if whatsappdisplay != 'غير محدد' and len(whatsappdisplay) >= 3:
                        prefix = whatsappdisplay[:3]
                        if prefix in whatsappsecurity.EGYPTIANNETWORKS:
                            network = whatsappsecurity.EGYPTIANNETWORKS[prefix]
                            networkdisplay = f" ({network['emoji']} {network['name']})"
                    
                    profiletext = f"""
✅ تم التحديث بنجاح!
━━━━━━━━━━━━━━━━

👤 الملف الشخصي المحدث
━━━━━━━━━━━━━━━━

🎮 المنصة: {GAMINGPLATFORMS[platformkey]['name']} ✅
📱 واتساب: {whatsappdisplay}{networkdisplay}
💳 طريقة الدفع: {profile.get('paymentmethod', 'غير محدد')}

━━━━━━━━━━━━━━━━
🔐 بياناتك محمية ومشفرة
"""
                    
                    keyboard = [
                        [InlineKeyboardButton("✏️ تعديل آخر", callbackdata="editprofile")],
                        [InlineKeyboardButton("🏠 القائمة الرئيسية", callbackdata="mainmenu")]
                    ]
                    replymarkup = InlineKeyboardMarkup(keyboard)
                    
                    await smartmessagemanager.updatecurrentmessage(
                        update, context, profiletext,
                        replymarkup=replymarkup
                    )
                else:
                    await query.answer("❌ فشل تحديث المنصة", showalert=True)
            else:
                await query.answer("❌ منصة غير صالحة", showalert=True)

    async def adminpanel(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """لوحة تحكم الأدمن"""
        query = update.callbackquery
        await query.answer()
        
        telegramid = query.fromuser.id
        
        # التحقق من صلاحيات الأدمن
        if telegramid != ADMINID:
            await query.answer("⛔ ليس لديك صلاحية!", showalert=True)
            return
        
        # جلب إحصائيات البوت
        conn = self.db.getconnection()
        cursor = conn.cursor()
        
        # عدد المستخدمين
        cursor.execute("SELECT COUNT() FROM users")
        totalusers = cursor.fetchone()[0]
        
        # عدد المستخدمين المسجلين بالكامل
        cursor.execute("SELECT COUNT() FROM users WHERE registrationstatus = 'complete'")
        registeredusers = cursor.fetchone()[0]
        
        # آخر المستخدمين المسجلين
        cursor.execute("""
            SELECT telegramid, username, fullname, createdat 
            FROM users 
            WHERE registrationstatus = 'complete'
            ORDER BY createdat DESC 
            LIMIT 5
        """)
        recentusers = cursor.fetchall()
        
        conn.close()
        
        # بناء رسالة الإحصائيات
        admintext = f"""
🔐 لوحة تحكم الأدمن
━━━━━━━━━━━━━━━━

📊 إحصائيات البوت:
• إجمالي المستخدمين: {totalusers}
• مستخدمين مسجلين: {registeredusers}
• غير مكتملين: {totalusers - registeredusers}

🕔 آخر التسجيلات:
"""
        
        for user in recentusers:
            username = f"@{user['username']}" if user['username'] else "غير محدد"
            admintext += f"• {username} (ID: {user['telegramid']})\n"
        
        if not recentusers:
            admintext += "• لا يوجد تسجيلات جديدة\n"
        
        # أزرار لوحة الأدمن
        keyboard = [
            [InlineKeyboardButton("👥 عرض جميع المستخدمين", callbackdata="adminviewusers")],
            [InlineKeyboardButton("🔍 بحث عن مستخدم", callbackdata="adminsearchuser")],
            [InlineKeyboardButton("📢 إرسال رسالة للجميع", callbackdata="adminbroadcast")],
            [InlineKeyboardButton("🗑️ حذف مستخدم", callbackdata="admindeleteuser")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callbackdata="mainmenu")]
        ]
        replymarkup = InlineKeyboardMarkup(keyboard)
        
        await smartmessagemanager.updatecurrentmessage(
            update, context, admintext,
            replymarkup=replymarkup
        )
    
    async def handletextmessages(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """معالجة الرسائل النصية - نعيد توجيههم للأوامر"""
        # إزالة أي كيبورد موجود
        await update.message.replytext(
            "👋 استخدم الأوامر التالية:\n\n"
            "/start - البداية\n"
            "/profile - الملف الشخصي\n"
            "/help - المساعدة",
            replymarkup=ReplyKeyboardRemove()
        )
    
    async def adminviewusers(self, update: Update, context: ContextTypes.DEFAULTTYPE, page: int = 1):
        """عرض جميع المستخدمين للأدمن بنظام الصفحات"""
        query = update.callbackquery
        
        # استخراج رقم الصفحة من callbackdata إن وجد
        if query and query.data.startswith("adminuserspage"):
            page = int(query.data.replace("adminuserspage", ""))
        
        if query:
            await query.answer()
            telegramid = query.fromuser.id
        else:
            telegramid = update.effectiveuser.id
        
        # التحقق من صلاحيات الأدمن
        if telegramid != ADMINID:
            if query:
                await query.answer("⛔ ليس لديك صلاحية!", showalert=True)
            return
        
        conn = self.db.getconnection()
        cursor = conn.cursor()
        
        # الحصول على إجمالي عدد المستخدمين
        cursor.execute("SELECT COUNT() FROM users")
        totalusers = cursor.fetchone()[0]
        
        # حساب عدد الصفحات
        usersperpage = 10
        totalpages = (totalusers + usersperpage - 1) // usersperpage
        
        # التأكد من أن رقم الصفحة صحيح
        if page < 1:
            page = 1
        elif page > totalpages:
            page = totalpages
        
        # حساب offset للصفحة الحالية
        offset = (page - 1) * users_per_page
        
        # جلب المستخدمين للصفحة الحالية
        cursor.execute("""
            SELECT u.telegramid, u.username, u.fullname, u.registrationstatus,
                   r.platform, r.whatsapp, r.paymentmethod
            FROM users u
            LEFT JOIN registrationdata r ON u.userid = r.userid
            ORDER BY u.createdat DESC
            LIMIT ? OFFSET ?
        """, (usersperpage, offset))
        users = cursor.fetchall()
        
        conn.close()
        
        # بناء نص الرسالة
        userstext = f"""
👥 قائمة المستخدمين
📄 الصفحة {page} من {totalpages}
👤 إجمالي المستخدمين: {totalusers}
━━━━━━━━━━━━━━━━

"""
        
        if not users:
            userstext += "لا يوجد مستخدمين في هذه الصفحة."
        else:
            for i, user in enumerate(users, start=offset+1):
                username = f"@{user['username']}" if user['username'] else "غير محدد"
                status = "✅" if user['registrationstatus'] == 'complete' else "⏳"
                userstext += f"{i}. {status} {username}\n"
                userstext += f"   ID: {user['telegramid']}\n"
                if user['platform']:
                    userstext += f"   🎮 {user['platform']}\n"
                if user['whatsapp']:
                    userstext += f"   📱 {user['whatsapp']}\n"
                userstext += "\n"
        
        # بناء أزرار التنقل
        keyboard = []
        
        # صف أزرار التنقل بين الصفحات
        navigationrow = []
        
        # زر الصفحة الأولى
        if page > 1:
            navigationrow.append(InlineKeyboardButton("⏪ الأولى", callbackdata="adminuserspage1"))
        
        # زر الصفحة السابقة
        if page > 1:
            navigationrow.append(InlineKeyboardButton("◀️ السابقة", callbackdata=f"adminuserspage{page-1}"))
        
        # زر عرض رقم الصفحة الحالي (غير قابل للضغط)
        navigationrow.append(InlineKeyboardButton(f"📄 {page}/{totalpages}", callbackdata="ignore"))
        
        # زر الصفحة التالية
        if page < totalpages:
            navigationrow.append(InlineKeyboardButton("▶️ التالية", callbackdata=f"adminuserspage{page+1}"))
        
        # زر الصفحة الأخيرة
        if page < totalpages:
            navigationrow.append(InlineKeyboardButton("⏩ الأخيرة", callbackdata=f"adminuserspage{totalpages}"))
        
        if navigationrow:
            keyboard.append(navigationrow)
        
        # زر الرجوع للوحة الأدمن
        keyboard.append([InlineKeyboardButton("🔙 رجوع للوحة الأدمن", callbackdata="adminpanel")])
        
        replymarkup = InlineKeyboardMarkup(keyboard)
        
        # إرسال أو تحديث الرسالة
        if query:
            await smartmessagemanager.updatecurrentmessage(
                update, context, userstext,
                replymarkup=replymarkup
            )
        else:
            await smartmessagemanager.sendnewactivemessage(
                update, context, userstext,
                replymarkup=replymarkup
            )
    
    async def admindeleteuser(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """حذف مستخدم - للأدمن فقط"""
        query = update.callbackquery
        await query.answer()
        
        telegramid = query.fromuser.id
        
        # التحقق من صلاحيات الأدمن
        if telegramid != ADMINID:
            await query.answer("⛔ ليس لديك صلاحية!", showalert=True)
            return
        
        # وضع البوت في وضع انتظار إدخال ID المستخدم
        context.userdata['adminaction'] = 'deleteuser'
        
        await smartmessagemanager.updatecurrentmessage(
            update, context,
            "🗑️ حذف مستخدم\n\n"
            "أدخل معرف التليجرام (ID) للمستخدم المراد حذفه:\n\n"
            "مثال: 123456789\n\n"
            "⚠️ تحذير: سيتم حذف جميع بيانات المستخدم نهائياً!"
        )
    
    async def adminconfirmdelete(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """تأكيد حذف المستخدم"""
        query = update.callbackquery
        await query.answer()
        
        telegramid = query.fromuser.id
        
        # التحقق من صلاحيات الأدمن
        if telegramid != ADMINID:
            await query.answer("⛔ ليس لديك صلاحية!", showalert=True)
            return
        
        # استخراج ID المستخدم من callbackdata
        usertodelete = int(query.data.replace("adminconfirmdelete", ""))
        
        # حذف المستخدم
        success = self.db.deleteuseraccount(usertodelete)
        
        if success:
            await smartmessagemanager.updatecurrentmessage(
                update, context,
                f"✅ تم حذف المستخدم بنجاح!\n\n"
                f"ID: {usertodelete}\n\n"
                f"تم حذف جميع البيانات المرتبطة بهذا المستخدم."
            )
        else:
            await smartmessagemanager.updatecurrentmessage(
                update, context,
                "❌ فشل حذف المستخدم\n\n"
                "قد يكون المستخدم غير موجود أو حدث خطأ."
            )
        
        # مسح حالة الأدمن
        context.userdata.pop('adminaction', None)
    
    async def adminbroadcast(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """إرسال رسالة للجميع - للأدمن فقط"""
        query = update.callbackquery
        await query.answer()
        
        telegramid = query.fromuser.id
        
        # التحقق من صلاحيات الأدمن
        if telegramid != ADMINID:
            await query.answer("⛔ ليس لديك صلاحية!", showalert=True)
            return
        
        # وضع البوت في وضع انتظار الرسالة
        context.userdata['adminaction'] = 'broadcast'
        
        await smartmessagemanager.updatecurrentmessage(
            update, context,
            "📢 إرسال رسالة للجميع\n\n"
            "اكتب الرسالة التي تريد إرسالها لجميع المستخدمين:\n\n"
            "📝 ملاحظة: سيتم إرسال الرسالة لجميع المستخدمين المسجلين.\n"
            "⚠️ استخدم هذه الميزة بحذر!"
        )
    
    async def adminsearchuser(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """البحث عن مستخدم - للأدمن فقط"""
        query = update.callbackquery
        await query.answer()
        
        telegramid = query.fromuser.id
        
        # التحقق من صلاحيات الأدمن
        if telegramid != ADMINID:
            await query.answer("⛔ ليس لديك صلاحية!", showalert=True)
            return
        
        # وضع البوت في وضع انتظار البحث
        context.userdata['adminaction'] = 'searchuser'
        
        await smartmessagemanager.updatecurrentmessage(
            update, context,
            "🔍 البحث عن مستخدم\n\n"
            "أدخل واحد من التالي للبحث:\n\n"
            "• معرف التليجرام (ID)\n"
            "• اسم المستخدم (@username)\n\n"
            "مثال: 123456789 أو @username"
        )
    
    async def handleadmintextinput(self, update: Update, context: ContextTypes.DEFAULTTYPE):
        """معالج إدخال النص من الأدمن"""
        telegramid = update.effectiveuser.id
        
        # التحقق من أن المرسل هو الأدمن
        if telegramid != ADMINID:
            # إذا لم يكن أدمن، نعامله كمستخدم عادي
            await self.handletextmessages(update, context)
            return
        
        # التحقق من وجود إجراء أدمن نشط
        adminaction = context.userdata.get('adminaction')
        
        if not adminaction:
            # لا يوجد إجراء نشط، نعامله كرسالة عادية
            await self.handletextmessages(update, context)
            return
        
        text = update.message.text.strip()
        
        if adminaction == 'deleteuser':
            # محاولة حذف المستخدم
            try:
                useridtodelete = int(text)
                
                # التحقق من أن الأدمن لا يحذف نفسه
                if useridtodelete == ADMINID:
                    await smartmessagemanager.sendnewactivemessage(
                        update, context,
                        "❌ لا يمكنك حذف حسابك الخاص!\n\n"
                        "أنت الأدمن الرئيسي للبوت."
                    )
                    context.userdata.pop('adminaction', None)
                    return
                
                # التحقق من وجود المستخدم
                user = self.db.getuserbytelegramid(useridtodelete)
                
                if user:
                    # عرض تأكيد الحذف
                    username = f"@{user['username']}" if user['username'] else "غير محدد"
                    
                    keyboard = [
                        [InlineKeyboardButton("✅ تأكيد الحذف", callbackdata=f"adminconfirmdelete{useridtodelete}")],
                        [InlineKeyboardButton("❌ إلغاء", callbackdata="adminpanel")]
                    ]
                    replymarkup = InlineKeyboardMarkup(keyboard)
                    
                    await smartmessagemanager.sendnewactivemessage(
                        update, context,
                        f"⚠️ تأكيد حذف المستخدم\n\n"
                        f"👤 الاسم: {user['fullname']}\n"
                        f"🆔 المعرف: {useridtodelete}\n"
                        f"📝 اسم المستخدم: {username}\n\n"
                        f"هل أنت متأكد من حذف هذا المستخدم؟",
                        replymarkup=replymarkup
                    )
                else:
                    await smartmessagemanager.sendnewactivemessage(
                        update, context,
                        f"❌ المستخدم غير موجود\n\n"
                        f"لا يوجد مستخدم بالمعرف: {useridtodelete}"
                    )
                
            except ValueError:
                await smartmessagemanager.sendnewactivemessage(
                    update, context,
                    "❌ معرف غير صحيح\n\n"
                    "يجب إدخال رقم صحيح فقط."
                )
            
            context.userdata.pop('adminaction', None)
        
        elif adminaction == 'broadcast':
            # إرسال الرسالة لجميع المستخدمين
            conn = self.db.getconnection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT telegramid FROM users WHERE registrationstatus = 'complete'")
            users = cursor.fetchall()
            
            conn.close()
            
            successcount = 0
            failcount = 0
            
            broadcastmsg = f"📢 رسالة من الإدارة\n\n{text}"
            
            for user in users:
                try:
                    await context.bot.sendmessage(
                        chatid=user['telegramid'],
                        text=broadcastmsg,
                        # parsemode removed to avoid parsing errors
                    )
                    successcount += 1
                    await asyncio.sleep(0.1)  # تأخير بسيط لتجنب حدود التليجرام
                except Exception as e:
                    failcount += 1
                    logger.error(f"فشل إرسال رسالة للمستخدم {user['telegramid']}: {e}")
            
            await smartmessagemanager.sendnewactivemessage(
                update, context,
                f"✅ تمت عملية البث\n\n"
                f"📊 الإحصائيات:\n"
                f"• نجح الإرسال: {successcount}\n"
                f"• فشل الإرسال: {failcount}\n"
                f"• الإجمالي: {len(users)}"
            )
            
            context.userdata.pop('adminaction', None)
        
        elif adminaction == 'searchuser':
            # البحث عن مستخدم
            conn = self.db.getconnection()
            cursor = conn.cursor()
            
            # البحث بالمعرف أو اسم المستخدم
            if text.startswith('@'):
                # البحث باسم المستخدم
                username = text[1:]  # إزالة @
                cursor.execute("""
                    SELECT u., r.platform, r.whatsapp, r.paymentmethod
                    FROM users u
                    LEFT JOIN registrationdata r ON u.userid = r.userid
                    WHERE u.username = ?
                """, (username,))
            else:
                # البحث بالمعرف
                try:
                    searchid = int(text)
                    cursor.execute("""
                        SELECT u., r.platform, r.whatsapp, r.paymentmethod
                        FROM users u
                        LEFT JOIN registrationdata r ON u.userid = r.userid
                        WHERE u.telegramid = ?
                    """, (searchid,))
                except ValueError:
                    await smartmessagemanager.sendnewactivemessage(
                        update, context,
                        "❌ بحث غير صحيح\n\n"
                        "يجب إدخال معرف رقمي أو اسم مستخدم يبدأ بـ @"
                    )
                    context.userdata.pop('adminaction', None)
                    conn.close()
                    return
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                usernamedisplay = f"@{user['username']}" if user['username'] else "غير محدد"
                status = "✅ مكتمل" if user['registrationstatus'] == 'complete' else "⏳ غير مكتمل"
                
                userinfo = f"""
🔍 نتيجة البحث
━━━━━━━━━━━━━━━━

👤 معلومات المستخدم:
• الاسم: {user['fullname']}
• المعرف: {user['telegramid']}
• اسم المستخدم: {usernamedisplay}
• الحالة: {status}
• تاريخ التسجيل: {user['createdat']}
"""
                
                if user['platform']:
                    userinfo += f"\n🎮 المنصة: {user['platform']}"
                if user['whatsapp']:
                    userinfo += f"\n📱 واتساب: {user['whatsapp']}"
                if user['paymentmethod']:
                    userinfo += f"\n💳 طريقة الدفع: {user['paymentmethod']}"
                
                keyboard = [
                    [InlineKeyboardButton("🗑️ حذف هذا المستخدم", callbackdata=f"adminconfirmdelete{user['telegramid']}")],
                    [InlineKeyboardButton("🔙 رجوع", callbackdata="adminpanel")]
                ]
                replymarkup = InlineKeyboardMarkup(keyboard)
                
                await smartmessagemanager.sendnewactivemessage(
                    update, context, userinfo,
                    replymarkup=replymarkup
                )
            else:
                await smartmessagemanager.sendnewactivemessage(
                    update, context,
                    f"❌ لم يتم العثور على المستخدم\n\n"
                    f"لا يوجد مستخدم بـ: {text}"
                )
            
            context.userdata.pop('adminaction', None)

    def getregistrationconversation(self):
        """معالج المحادثة للتسجيل"""
        return ConversationHandler(
            entrypoints=[
                CallbackQueryHandler(
                    self.registrationhandler.handleregistrationstart,
                    pattern="^registernew$"
                ),
                CallbackQueryHandler(
                    self.registrationhandler.handlecontinueregistration,
                    pattern="^(continueregistration|restartregistration)$"
                )
            ],
            states={
                CHOOSINGPLATFORM: [
                    CallbackQueryHandler(
                        self.registrationhandler.handleplatformchoice,
                        pattern="^platform"
                    )
                ],
                ENTERINGWHATSAPP: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registrationhandler.handlewhatsappinput
                    )
                ],
                CHOOSINGPAYMENT: [
                    CallbackQueryHandler(
                        self.registrationhandler.handlepaymentchoice,
                        pattern="^payment"
                    )
                ],
                ENTERINGPAYMENTDETAILS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registrationhandler.handlepaymentdetailsinput
                    )
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.registrationhandler.cancel),
                CommandHandler('start', self.registrationhandler.start)
            ],
            allowreentry=True
        )
    
    def geteditconversation(self):
        """معالج المحادثة للتعديل"""
        return ConversationHandler(
            entrypoints=[
                CallbackQueryHandler(
                    self.handleeditprofile,
                    pattern="^(editwhatsapp|editpayment)$"
                )
            ],
            states={
                CHOOSINGPLATFORM: [
                    CallbackQueryHandler(
                        self.registrationhandler.handleplatformchoice,
                        pattern="^platform"
                    )
                ],
                ENTERINGWHATSAPP: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registrationhandler.handlewhatsappinput
                    )
                ],
                CHOOSINGPAYMENT: [
                    CallbackQueryHandler(
                        self.registrationhandler.handlepaymentchoice,
                        pattern="^payment"
                    )
                ],
                ENTERINGPAYMENTDETAILS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        self.registrationhandler.handlepaymentdetailsinput
                    )
                ]
            },
            fallbacks=[
                CommandHandler('cancel', self.registrationhandler.cancel),
                CommandHandler('profile', self.profilecommand)
            ],
            allowreentry=True
        )

    def run(self):
        """تشغيل البوت"""
        app = Application.builder().token(BOTTOKEN).build()

        # معالج التسجيل (يجب أن يكون أولاً ليأخذ الأولوية)
        app.addhandler(self.getregistrationconversation())
        
        # معالج التعديل (للتعديل التفاعلي)
        app.addhandler(self.geteditconversation())

        # الأوامر
        app.addhandler(CommandHandler("start", self.start))
        app.addhandler(CommandHandler("profile", self.profilecommand))
        app.addhandler(CommandHandler("help", self.helpcommand))
        # أمر حذف الحساب للأدمن فقط
        app.addhandler(CommandHandler("delete", self.deleteaccountcommand))

        # الأزرار
        app.addhandler(CallbackQueryHandler(
            self.handledeleteconfirmation,
            pattern="^(confirmdelete|canceldelete)$"
        ))

        # أزرار القائمة الرئيسية (محدثة بدون الأزرار المحذوفة)
        app.addhandler(CallbackQueryHandler(
            self.handlemenubuttons,
            pattern="^(profile|deleteaccount|sellcoins|support|mainmenu)$"
        ))
        
        # أزرار تعديل الملف الشخصي
        app.addhandler(CallbackQueryHandler(
            self.handleeditprofile,
            pattern="^(editprofile|editplatform|editwhatsapp|editpayment|updateplatform.|updatepayment.)$"
        ))
        
        # أزرار لوحة الأدمن
        app.addhandler(CallbackQueryHandler(
            self.adminpanel,
            pattern="^adminpanel$"
        ))
        
        app.addhandler(CallbackQueryHandler(
            self.adminviewusers,
            pattern="^adminviewusers$"
        ))
        
        # معالج الصفحات لعرض المستخدمين
        app.addhandler(CallbackQueryHandler(
            self.adminviewusers,
            pattern=r"^adminuserspage\d+$"
        ))
        
        app.addhandler(CallbackQueryHandler(
            self.admindeleteuser,
            pattern="^admindeleteuser$"
        ))
        
        app.addhandler(CallbackQueryHandler(
            self.adminconfirmdelete,
            pattern=r"^adminconfirmdelete\d+$"
        ))
        
        app.addhandler(CallbackQueryHandler(
            self.adminbroadcast,
            pattern="^adminbroadcast$"
        ))
        
        app.addhandler(CallbackQueryHandler(
            self.adminsearchuser,
            pattern="^adminsearchuser$"
        ))
        
        # معالج رسائل البحث والبث للأدمن
        app.addhandler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handleadmintextinput
        ))



        # التشغيل
        logger.info("🚀 بدء تشغيل FC 26 Smart Bot...")
        logger.info("✨ النظام الذكي للرسائل مفعّل")
        logger.info("📱 البوت جاهز: https://t.me/FC26TradingBot")

        app.runpolling(allowedupdates=Update.ALLTYPES)

# ================================ نقطة البداية ================================
if __name__ == "__main__":
    bot = FC26SmartBot()
    bot.run()
