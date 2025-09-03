#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إصلاح مشاكل الحذف والـ webhook
"""

import re

print("🔧 بدء إصلاح المشاكل...")

# قراءة main_bot.py
with open('main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. إصلاح مشكلة الـ webhook - إضافة force delete في البداية
webhook_fix = """        # حذف أي webhook قديم
        try:
            await app.bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ تم حذف الـ webhook القديم")
        except Exception as e:
            logger.warning(f"تحذير webhook: {e}")
        """

# البحث عن مكان إضافة الكود
app_build_pos = content.find("app = ApplicationBuilder()")
if app_build_pos != -1:
    # نضيف بعد بناء الـ app
    end_line = content.find("\n", app_build_pos)
    next_line = content.find("\n", end_line + 1)
    content = content[:next_line] + "\n" + webhook_fix + content[next_line:]
    print("✅ تم إضافة حذف webhook تلقائي")

# 2. تعديل ترتيب الـ handlers - نخلي الأوامر قبل التسجيل
handlers_section = content.find("# إضافة معالجات الأوامر")
if handlers_section != -1:
    # نقطع الجزء بتاع الـ handlers
    start = handlers_section
    end = content.find("# تشغيل البوت", start)
    
    handlers_code = content[start:end]
    
    # نعيد ترتيبهم - الأوامر العادية أولاً
    new_order = """        # إضافة معالجات الأوامر
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("profile", self.profile_command))
        app.add_handler(CommandHandler("wallet", self.wallet_command))
        app.add_handler(CommandHandler("delete", self.delete_command))
        app.add_handler(CommandHandler("deleteuser", self.deleteuser_command))
        app.add_handler(CommandHandler("admin", self.admin_command))
        app.add_handler(CommandHandler("broadcast", self.broadcast_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        
        # معالجات حذف الحساب - قبل التسجيل
        app.add_handler(CallbackQueryHandler(self.handle_delete_confirm, pattern="^confirm_delete$"))
        app.add_handler(CallbackQueryHandler(self.handle_delete_cancel, pattern="^cancel_delete$"))
        
        # معالج الأزرار التفاعلية الأخرى
        app.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # إضافة معالج التسجيل - في الآخر
        app.add_handler(get_registration_conversation())
        
"""
    content = content[:start] + new_order + content[end:]
    print("✅ تم إعادة ترتيب الـ handlers")

# 3. إضافة methods منفصلة للحذف
delete_methods = '''
    async def handle_delete_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تأكيد حذف الحساب"""
        query = update.callback_query
        await query.answer("جاري حذف الحساب...")
        
        telegram_id = query.from_user.id
        success = self.db.delete_user_account(telegram_id)
        
        if success:
            await query.edit_message_text(
                "✅ تم حذف حسابك بنجاح.\\n\\n"
                "نأسف لرؤيتك تغادر 😢\\n"
                "يمكنك التسجيل مرة أخرى في أي وقت بكتابة /start"
            )
        else:
            await query.edit_message_text(
                "❌ حدث خطأ في حذف الحساب. الرجاء المحاولة لاحقاً."
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

# نضيف الـ methods قبل run
run_pos = content.find("def run(self):")
if run_pos != -1:
    content = content[:run_pos] + delete_methods + "\n    " + content[run_pos:]
    print("✅ تم إضافة methods الحذف المنفصلة")

# 4. تعديل handle_callback_query ليتجاهل أزرار الحذف
callback_method = content.find("async def handle_callback_query(self, update")
if callback_method != -1:
    # نضيف شرط في البداية
    method_start = content.find("{", callback_method)
    first_line = content.find("\n", method_start)
    
    check_code = """
        # تجاهل أزرار الحذف - لها handlers منفصلة
        if query.data in ["confirm_delete", "cancel_delete"]:
            return
        """
    
    content = content[:first_line] + check_code + content[first_line:]
    print("✅ تم تعديل handle_callback_query")

# حفظ الملف
with open('main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ تم إصلاح جميع المشاكل!")
print("📋 التعديلات:")
print("  1. إضافة حذف webhook تلقائي عند البدء")
print("  2. إعادة ترتيب handlers - الأوامر أولاً")
print("  3. إضافة handlers منفصلة لأزرار الحذف")
print("  4. منع التداخل مع التسجيل")