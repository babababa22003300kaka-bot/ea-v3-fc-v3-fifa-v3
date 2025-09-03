#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت لإصلاح زر حذف الحساب وتعديل الملف الشخصي
"""

import re

print("🔧 بدء إصلاح المشاكل...")

# 1. إضافة handlers للحذف في main_bot.py
with open('main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن مكان إضافة callback handlers
callback_section = content.find("# إضافة معالج الأوامر")
if callback_section == -1:
    callback_section = content.find("application.add_handler(CommandHandler")

# إضافة callback handlers للحذف
if 'CallbackQueryHandler(bot.handle_delete_confirmation' not in content:
    # نبحث عن آخر handler
    last_handler = content.rfind("application.add_handler(")
    if last_handler != -1:
        # نجيب نهاية السطر
        end_line = content.find("\n", last_handler)
        
        # نضيف الـ handlers الجديدة
        new_handlers = """
    # معالجات حذف الحساب
    application.add_handler(CallbackQueryHandler(bot.handle_delete_confirmation, pattern="^confirm_delete$"))
    application.add_handler(CallbackQueryHandler(bot.handle_delete_cancellation, pattern="^cancel_delete$"))
"""
        content = content[:end_line+1] + new_handlers + content[end_line+1:]
        print("✅ تم إضافة callback handlers للحذف")

# 2. إضافة الـ methods المفقودة
delete_methods = '''
    async def handle_delete_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة تأكيد حذف الحساب"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        
        # حذف المستخدم من قاعدة البيانات
        try:
            conn = sqlite3.connect('fc26_bot.db')
            cursor = conn.cursor()
            
            # جلب user_id
            cursor.execute('SELECT id FROM users WHERE telegram_id = ?', (telegram_id,))
            user = cursor.fetchone()
            
            if user:
                user_id = user[0]
                
                # حذف من جميع الجداول
                tables = [
                    'transactions', 'offers', 'notifications', 'sessions',
                    'referrals', 'verification_requests', 'temp_registration',
                    'user_levels', 'wallet', 'users'
                ]
                
                for table in tables:
                    if table == 'users':
                        cursor.execute(f'DELETE FROM {table} WHERE telegram_id = ?', (telegram_id,))
                    else:
                        cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
                
                conn.commit()
                
                await query.edit_message_text(
                    "✅ تم حذف حسابك بنجاح.\\n\\n"
                    "نأسف لرؤيتك تغادر 😢\\n"
                    "يمكنك التسجيل مرة أخرى في أي وقت بكتابة /start"
                )
            else:
                await query.edit_message_text("❌ لم يتم العثور على حسابك!")
                
            conn.close()
            
        except Exception as e:
            logger.error(f"خطأ في حذف الحساب: {e}")
            await query.edit_message_text(
                "❌ حدث خطأ أثناء حذف الحساب. الرجاء المحاولة مرة أخرى."
            )
    
    async def handle_delete_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إلغاء حذف الحساب"""
        query = update.callback_query
        await query.answer("تم إلغاء عملية الحذف")
        
        await query.edit_message_text(
            "✅ تم إلغاء عملية حذف الحساب.\\n\\n"
            "سعيدون ببقائك معنا! 😊"
        )
'''

# نضيف الـ methods قبل نهاية الـ class
class_end = content.rfind("def main():")
if class_end != -1:
    # نضع الـ methods قبل main
    content = content[:class_end] + delete_methods + "\n" + content[class_end:]
    print("✅ تم إضافة methods الحذف")

# حفظ main_bot.py
with open('main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ تم تعديل main_bot.py")

# 3. تعديل عرض الملف الشخصي - إزالة المعلومات المالية
with open('main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن profile message
old_profile = '''💰 **المعلومات المالية:**
• الرصيد: {coins} عملة
• القيمة: {value:.2f} جنيه
• نقاط الولاء: {loyalty_points} نقطة

🏆 **المستوى والتقدم:**
• المستوى الحالي: {current_level}
• المستوى التالي: {next_level} ({next_points} نقطة)
• التقدم: {progress_bar} {progress_percent}%

📊 **الإحصائيات:**
• عمليات البيع: {sales_count}
• إجمالي المعاملات: {total_transactions}'''

new_profile = '''📊 **معلومات الحساب:**
• تاريخ التسجيل: {join_date}
• حالة الحساب: {account_status}
• رقم العضوية: #{user_id}'''

# استبدال المعلومات المالية
content = content.replace(old_profile, new_profile)

# تعديل متغيرات format
old_format = '''coins=wallet[2],
            value=wallet[2] * 0.5,
            loyalty_points=level[3],
            current_level=USER_LEVELS[level[2]]['name'],
            next_level=USER_LEVELS.get(level[2] + 1, {}).get('name', 'المستوى الأقصى'),
            next_points=USER_LEVELS.get(level[2] + 1, {}).get('min_points', 0),
            progress_bar=progress_bar,
            progress_percent=progress_percent,
            sales_count=wallet[5],
            total_transactions=wallet[6]'''

new_format = '''join_date=user[7] if len(user) > 7 else 'غير محدد',
            account_status='✅ نشط' if user[6] == 1 else '❌ غير نشط',
            user_id=user[0]'''

content = re.sub(r'coins=wallet\[2\].*?total_transactions=wallet\[6\]', new_format, content, flags=re.DOTALL)

# حفظ التعديلات
with open('main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ تم تعديل عرض الملف الشخصي")

# 4. تحديث التوكن الجديد في config
with open('bot/config.py', 'r', encoding='utf-8') as f:
    config = f.read()

# استبدال التوكن القديم
old_token = "7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE"
new_token = "7607085569:AAEq91WtoNg68U9e8-mWm8DsOTh2W9MmmTw"

config = config.replace(old_token, new_token)

with open('bot/config.py', 'w', encoding='utf-8') as f:
    f.write(config)

print(f"✅ تم تحديث التوكن")

print("\n🎉 تم إصلاح جميع المشاكل!")
print("📋 الملفات المعدلة:")
print("  1. main_bot.py - إضافة handlers الحذف وتعديل الملف الشخصي")
print("  2. bot/config.py - تحديث التوكن")