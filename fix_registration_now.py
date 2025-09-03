#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت سريع لتصليح مشاكل التسجيل
"""

import re

# قراءة ملف registration.py
with open('bot/handlers/registration.py', 'r', encoding='utf-8') as f:
    content = f.read()

# استبدال كل ENTERING_CARD بـ ENTERING_PAYMENT_INFO
content = content.replace('ENTERING_CARD', 'ENTERING_PAYMENT_INFO')

# إضافة الـ method المفقود بعد handle_phone_input
handle_phone_input_end = content.find('return ENTERING_PAYMENT_INFO\n    \n    async def handle_card_input')

if handle_phone_input_end != -1:
    # حذف handle_card_input القديم وإضافة handle_payment_info_input الجديد
    start_of_card = content.find('async def handle_card_input')
    end_of_card = content.find('async def handle_instapay_input')
    
    if start_of_card != -1 and end_of_card != -1:
        # قص الجزء القديم
        before_card = content[:start_of_card]
        after_card = content[end_of_card:]
        
        # إضافة الـ method الجديد
        new_method = '''async def handle_payment_info_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال معلومات الدفع حسب الطريقة المختارة"""
        
        # التعامل مع الضغط على زر التخطي
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "skip_step":
                context.user_data['registration']['payment_info'] = None
                
                # الانتقال للخطوة التالية
                await query.edit_message_text(
                    "⏭️ تم تخطي معلومات الدفع\\n\\n" + MESSAGES['enter_emails'],
                    reply_markup=get_skip_keyboard()
                )
                return ENTERING_EMAILS
        
        # معالجة النص المدخل
        payment_info = update.message.text.strip()
        
        # التحقق من أمر التخطي
        if is_skip_command(payment_info):
            context.user_data['registration']['payment_info'] = None
            
            # الانتقال للخطوة التالية
            await update.message.reply_text(
                "⏭️ تم تخطي معلومات الدفع\\n\\n" + MESSAGES['enter_emails'],
                reply_markup=get_skip_keyboard()
            )
            return ENTERING_EMAILS
        
        payment_method = context.user_data['registration'].get('payment_method', '')
        
        # معالجة حسب طريقة الدفع
        if payment_method == 'instapay':
            # محاولة استخراج رابط InstaPay
            extracted_link = extract_instapay_link(payment_info)
            if extracted_link:
                context.user_data['registration']['payment_info'] = extracted_link
                await update.message.reply_text(
                    f"✅ تم استخراج وحفظ رابط InstaPay:\\n{extracted_link}\\n" +
                    MESSAGES['data_saved']
                )
            else:
                # حفظ المعلومات كما هي
                context.user_data['registration']['payment_info'] = payment_info
                await update.message.reply_text(
                    "✅ تم حفظ معلومات InstaPay"
                )
        elif payment_method in ['vodafone', 'etisalat', 'orange']:
            # للمحافظ الإلكترونية - التحقق من رقم الهاتف
            is_valid, cleaned_number = validate_egyptian_phone(payment_info)
            if is_valid:
                context.user_data['registration']['payment_info'] = cleaned_number
                formatted_number = format_phone_display(cleaned_number)
                await update.message.reply_text(
                    f"✅ تم حفظ رقم المحفظة: {formatted_number}\\n" +
                    MESSAGES['data_saved']
                )
            else:
                # حفظ كما هو إذا لم يكن رقم صالح
                context.user_data['registration']['payment_info'] = payment_info
                await update.message.reply_text(
                    "✅ تم حفظ معلومات الدفع"
                )
        else:
            # لأي طريقة دفع أخرى
            context.user_data['registration']['payment_info'] = payment_info
            await update.message.reply_text(
                "✅ تم حفظ معلومات الدفع\\n" + MESSAGES['data_saved']
            )
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'payment_info_entered',
            ENTERING_EMAILS,
            context.user_data['registration']
        )
        
        # الانتقال للخطوة التالية
        await update.message.reply_text(
            MESSAGES['enter_emails'],
            reply_markup=get_skip_keyboard()
        )
        
        return ENTERING_EMAILS
    
    '''
        
        content = before_card + new_method + after_card

# حذف handle_instapay_input لأنه مش محتاجينه
start_instapay = content.find('async def handle_instapay_input')
end_instapay = content.find('async def handle_email_input')
if start_instapay != -1 and end_instapay != -1:
    content = content[:start_instapay] + content[end_instapay:]

# إضافة helper method قبل cancel
cancel_pos = content.find('async def cancel(')
if cancel_pos != -1:
    helper_method = '''def _get_payment_info_message(self, payment_method: str) -> str:
        """الحصول على رسالة معلومات الدفع حسب الطريقة المختارة"""
        if payment_method == 'instapay':
            return "🏦 أرسل رابط InstaPay الخاص بك:\\n\\nيمكنك نسخ الرسالة كاملة من InstaPay أو كتابة 'تخطي' للمتابعة"
        elif payment_method in ['vodafone', 'etisalat', 'orange']:
            method_name = PAYMENT_METHODS.get(payment_method, {}).get('name', 'المحفظة')
            return f"📱 أرسل رقم {method_name}:\\n\\nأرسل الرقم المسجل في المحفظة الإلكترونية أو اكتب 'تخطي'"
        elif payment_method == 'visa':
            return "💳 أرسل آخر 4 أرقام من البطاقة (للتحقق فقط):\\n\\nمثال: 1234\\nأو اكتب 'تخطي' للمتابعة"
        elif payment_method == 'paypal':
            return "💰 أرسل بريدك الإلكتروني المسجل في PayPal:\\n\\nأو اكتب 'تخطي' للمتابعة"
        else:
            return "💸 أرسل معلومات الدفع الخاصة بك:\\n\\nأو اكتب 'تخطي' للمتابعة"
    
    '''
    content = content[:cancel_pos] + helper_method + content[cancel_pos:]

# تحديث رسالة بعد إدخال الهاتف
phone_msg_pattern = r'await update\.message\.reply_text\(\s*MESSAGES\[\'enter_card\'\]\s*\)'
phone_msg_replacement = '''# التحقق من طريقة الدفع المختارة لعرض الرسالة المناسبة
        payment_method = context.user_data['registration'].get('payment_method', '')
        if payment_method == 'instapay':
            message = "🏦 أرسل رابط InstaPay الخاص بك:\\n\\nيمكنك نسخ الرسالة كاملة من InstaPay أو كتابة 'تخطي' للمتابعة"
        else:
            message = "💳 أرسل معلومات الدفع الخاصة بك:\\n\\n" + MESSAGES.get('skip_option', 'يمكنك كتابة "تخطي" لتجاوز هذه الخطوة')
        
        await update.message.reply_text(
            message,
            reply_markup=get_skip_keyboard()
        )'''

content = re.sub(phone_msg_pattern, phone_msg_replacement, content)

# حفظ الملف المعدل
with open('bot/handlers/registration.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ تم تصليح ملف registration.py")

# تعديل config.py
with open('bot/config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()

# تحديث أرقام الخطوات
config_content = config_content.replace('الخطوة 1️⃣ من 7️⃣', 'الخطوة 1️⃣ من 6️⃣')
config_content = config_content.replace('الخطوة 2️⃣ من 7️⃣', 'الخطوة 2️⃣ من 6️⃣')
config_content = config_content.replace('الخطوة 3️⃣ من 7️⃣', 'الخطوة 3️⃣ من 6️⃣')
config_content = config_content.replace('الخطوة 4️⃣ من 7️⃣', 'الخطوة 4️⃣ من 6️⃣')
config_content = config_content.replace('الخطوة 5️⃣ من 7️⃣', 'الخطوة 5️⃣ من 6️⃣')
config_content = config_content.replace('الخطوة 6️⃣ من 7️⃣', 'الخطوة 5️⃣ من 6️⃣')
config_content = config_content.replace('الخطوة 7️⃣ من 7️⃣', 'الخطوة 6️⃣ من 6️⃣')

with open('bot/config.py', 'w', encoding='utf-8') as f:
    f.write(config_content)

print("✅ تم تصليح ملف config.py")
print("🎉 كل التعديلات تمت بنجاح!")