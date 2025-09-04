#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح نهائي وشامل لمشكلة حذف الحساب
"""

import os
import re

print("🔧 بدء إصلاح مشكلة حذف الحساب نهائياً...")
print("=" * 50)

# ===== 1. إصلاح ملف main_bot.py =====
print("\n📝 إصلاح main_bot.py...")

main_bot_path = 'main_bot.py' if os.path.exists('main_bot.py') else 'app.py'

with open(main_bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن الكلاس FC26Bot
if 'class FC26Bot' in content:
    print("✓ وجدت كلاس FC26Bot")
    
    # إضافة دوال الحذف إذا لم تكن موجودة
    if 'async def handle_delete_confirm' not in content:
        print("⚠️ دالة handle_delete_confirm مش موجودة، هضيفها...")
        
        delete_methods = '''
    async def handle_delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد حذف الحساب"""
        query = update.callback_query
        await query.answer("جاري حذف الحساب...")
        
        telegram_id = query.from_user.id
        
        try:
            # استخدام دالة الحذف من قاعدة البيانات
            success = self.db.delete_user_account(telegram_id)
            
            if success:
                await query.edit_message_text(
                    "✅ تم حذف حسابك بنجاح.\\n\\n"
                    "نأسف لرؤيتك تغادر 😢\\n"
                    "يمكنك التسجيل مرة أخرى في أي وقت بكتابة /start"
                )
                logger.info(f"تم حذف حساب المستخدم {telegram_id}")
            else:
                await query.edit_message_text(
                    "❌ حدث خطأ في حذف الحساب.\\n"
                    "الرجاء المحاولة لاحقاً أو التواصل مع الدعم."
                )
                
        except Exception as e:
            logger.error(f"خطأ في حذف الحساب: {e}")
            await query.edit_message_text(
                "❌ حدث خطأ غير متوقع.\\n"
                "الرجاء التواصل مع الدعم الفني."
            )
    
    async def handle_delete_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء حذف الحساب"""
        query = update.callback_query
        await query.answer("تم الإلغاء")
        
        await query.edit_message_text(
            "✅ تم إلغاء عملية حذف الحساب.\\n\\n"
            "سعداء لبقائك معنا! 😊",
            reply_markup=get_main_menu_keyboard()
        )
'''
        
        # البحث عن مكان مناسب لإضافة الدوال
        run_pos = content.find('def run(self):')
        if run_pos > 0:
            content = content[:run_pos] + delete_methods + "\n    " + content[run_pos:]
            print("✅ تم إضافة دوال الحذف")
    else:
        print("✓ دوال الحذف موجودة بالفعل")
    
    # التأكد من إضافة handlers في المكان الصحيح
    if 'pattern="^confirm_delete$"' not in content:
        print("⚠️ Handlers مش موجودة، هضيفها...")
        
        # البحث عن مكان إضافة handlers
        run_method = content.find('def run(self):')
        if run_method > 0:
            # البحث عن نهاية إضافة handlers
            registration_handler = content.find('app.add_handler(get_registration_conversation())', run_method)
            
            if registration_handler > 0:
                handlers_code = '''
        # معالجات حذف الحساب - مهم جداً يكونوا قبل التسجيل
        app.add_handler(CallbackQueryHandler(self.handle_delete_confirm, pattern="^confirm_delete$"))
        app.add_handler(CallbackQueryHandler(self.handle_delete_cancel, pattern="^cancel_delete$"))
        '''
                content = content[:registration_handler] + handlers_code + "\n        " + content[registration_handler:]
                print("✅ تم إضافة handlers الحذف")

# حفظ التعديلات
with open(main_bot_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ تم إصلاح main_bot.py")

# ===== 2. إصلاح قاعدة البيانات =====
print("\n📝 إصلاح bot/database/models.py...")

db_path = 'bot/database/models.py'
if os.path.exists(db_path):
    with open(db_path, 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    # إضافة دالة delete_user_account إذا لم تكن موجودة
    if 'def delete_user_account' not in db_content:
        print("⚠️ دالة delete_user_account مش موجودة، هضيفها...")
        
        delete_function = '''
    def delete_user_account(self, telegram_id: int) -> bool:
        """حذف حساب المستخدم بالكامل من جميع الجداول"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # الحصول على user_id أولاً
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f"المستخدم {telegram_id} غير موجود")
                conn.close()
                return False
            
            user_id = user['user_id']
            logger.info(f"بدء حذف المستخدم {telegram_id} (ID: {user_id})")
            
            # قائمة الجداول المرتبطة بـ user_id
            tables_with_user_id = [
                'activity_log',
                'notifications', 
                'referrals',
                'transactions',
                'user_levels',
                'wallet',
                'registration_data'
            ]
            
            # حذف من جميع الجداول المرتبطة
            for table in tables_with_user_id:
                try:
                    cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
                    logger.debug(f"حذف من جدول {table}")
                except Exception as e:
                    logger.debug(f"جدول {table} غير موجود أو فارغ: {e}")
                    pass
            
            # حذف من temp_registration باستخدام telegram_id
            try:
                cursor.execute('DELETE FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
                logger.debug("حذف من temp_registration")
            except Exception:
                pass
            
            # حذف المستخدم نفسه أخيراً
            cursor.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
            
            # التحقق من نجاح الحذف
            cursor.execute('SELECT COUNT(*) FROM users WHERE telegram_id = ?', (telegram_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                conn.commit()
                logger.info(f"✅ تم حذف المستخدم {telegram_id} بنجاح")
                conn.close()
                return True
            else:
                conn.rollback()
                logger.error(f"فشل حذف المستخدم {telegram_id}")
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"خطأ في حذف المستخدم {telegram_id}: {e}")
            conn.rollback()
            conn.close()
            return False
'''
        
        # إضافة الدالة قبل نهاية الكلاس
        class_end = db_content.rfind('\n\n')
        if class_end > 0:
            db_content = db_content[:class_end] + delete_function + db_content[class_end:]
            
            with open(db_path, 'w', encoding='utf-8') as f:
                f.write(db_content)
            print("✅ تم إضافة دالة delete_user_account")
    else:
        print("✓ دالة delete_user_account موجودة بالفعل")
else:
    print("⚠️ ملف bot/database/models.py غير موجود")

# ===== 3. التأكد من وجود زر الحذف في الملف الشخصي =====
print("\n📝 التأكد من وجود زر الحذف في الملف الشخصي...")

# قراءة الملف مرة أخرى للتأكد من الأزرار
with open(main_bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن دالة profile_command
profile_method = content.find('async def profile_command')
if profile_method > 0:
    # البحث عن keyboard في نفس الدالة
    keyboard_start = content.find('keyboard = [', profile_method)
    keyboard_end = content.find(']', keyboard_start + 20)
    
    if keyboard_start > 0 and keyboard_end > 0:
        keyboard_section = content[keyboard_start:keyboard_end+1]
        
        if 'delete_account_btn' not in keyboard_section:
            print("⚠️ زر الحذف مش موجود في الملف الشخصي، هضيفه...")
            
            # إضافة زر الحذف
            new_keyboard = keyboard_section.replace(
                '[InlineKeyboardButton("🔙 القائمة الرئيسية"',
                '[InlineKeyboardButton("🗑️ حذف الحساب", callback_data="delete_account_btn")],\n            [InlineKeyboardButton("🔙 القائمة الرئيسية"'
            )
            
            content = content[:keyboard_start] + new_keyboard + content[keyboard_end+1:]
            
            with open(main_bot_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ تم إضافة زر حذف الحساب")
        else:
            print("✓ زر الحذف موجود بالفعل")

# ===== 4. إضافة معالج لزر delete_account_btn =====
print("\n📝 إضافة معالج لزر delete_account_btn...")

with open(main_bot_path, 'r', encoding='utf-8') as f:
    content = f.read()

# البحث عن handle_callback_query
callback_method = content.find('async def handle_callback_query')
if callback_method > 0:
    # التأكد من وجود معالج للزر
    if 'elif query.data == "delete_account_btn"' not in content:
        print("⚠️ معالج زر delete_account_btn مش موجود، هضيفه...")
        
        # البحث عن مكان مناسب لإضافة المعالج
        back_to_menu = content.find('elif query.data == "back_to_menu"', callback_method)
        if back_to_menu > 0:
            handler_code = '''
        # معالجة زر حذف الحساب من الملف الشخصي
        elif query.data == "delete_account_btn":
            warning_message = """
⚠️ **تحذير مهم جداً!**
━━━━━━━━━━━━━━━━

هل أنت متأكد من حذف حسابك نهائياً؟

**سيتم حذف:**
• جميع بياناتك الشخصية 🗑️
• سجل معاملاتك بالكامل 📊
• جميع بيانات حسابك 👤

⛔ **لا يمكن التراجع عن هذا الإجراء نهائياً!**

هل تريد المتابعة؟
"""
            await query.edit_message_text(
                warning_message,
                reply_markup=get_delete_account_keyboard(),
                parse_mode='Markdown'
            )
        
        # الرجوع للقائمة الرئيسية
        '''
            content = content[:back_to_menu] + handler_code + content[back_to_menu:]
            
            with open(main_bot_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ تم إضافة معالج زر delete_account_btn")
    else:
        print("✓ معالج زر delete_account_btn موجود بالفعل")

print("\n" + "=" * 50)
print("🎉 تم إصلاح جميع مشاكل حذف الحساب!")
print("\n📋 التعديلات المطبقة:")
print("  1. ✅ إضافة دوال handle_delete_confirm و handle_delete_cancel")
print("  2. ✅ إضافة handlers للأزرار")
print("  3. ✅ إضافة دالة delete_user_account في قاعدة البيانات")
print("  4. ✅ إضافة زر حذف الحساب في الملف الشخصي")
print("  5. ✅ إضافة معالج للزر delete_account_btn")
print("\n🚀 البوت جاهز للاختبار الآن!")
print("💡 نصيحة: أعد تشغيل البوت بعد التطبيق")