#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
معالج التسجيل التفاعلي
"""

import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.config import MESSAGES, GAMING_PLATFORMS, PAYMENT_METHODS
from bot.database.models import Database
from bot.states.registration import *
from bot.keyboards.registration import *
from bot.utils.validators import *

logger = logging.getLogger(__name__)

class RegistrationHandler:
    """معالج عملية التسجيل الكاملة"""
    
    def __init__(self):
        self.db = Database()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بداية المحادثة"""
        telegram_id = update.effective_user.id
        username = update.effective_user.username
        full_name = update.effective_user.full_name
        
        # التحقق من وجود تسجيل سابق غير مكتمل
        temp_data = self.db.get_temp_registration(telegram_id)
        
        if temp_data:
            # المستخدم لديه تسجيل غير مكتمل
            last_step = get_state_name(temp_data['step_number'])
            message = MESSAGES['welcome_back'].format(last_step=last_step)
            
            await update.message.reply_text(
                message,
                reply_markup=get_continue_registration_keyboard()
            )
            return ConversationHandler.END
        
        # مستخدم جديد
        await update.message.reply_text(
            MESSAGES['welcome'],
            reply_markup=get_start_keyboard()
        )
        
        return ConversationHandler.END
    
    async def handle_registration_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدء عملية التسجيل"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        username = query.from_user.username
        full_name = query.from_user.full_name
        
        # إنشاء مستخدم جديد أو الحصول على الموجود
        user_id = self.db.create_user(telegram_id, username, full_name)
        
        # تهيئة بيانات التسجيل
        context.user_data['registration'] = {
            'user_id': user_id,
            'telegram_id': telegram_id,
            'step': 1
        }
        
        # عرض اختيار المنصة
        await query.edit_message_text(
            MESSAGES['choose_platform'],
            reply_markup=get_platform_keyboard()
        )
        
        return CHOOSING_PLATFORM
    
    async def handle_platform_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار المنصة"""
        query = update.callback_query
        await query.answer()
        
        # استخراج اختيار المنصة
        platform_key = query.data.replace("platform_", "")
        platform_name = GAMING_PLATFORMS[platform_key]['name']
        
        # حفظ الاختيار
        context.user_data['registration']['platform'] = platform_key
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'platform_chosen',
            ENTERING_WHATSAPP,
            context.user_data['registration']
        )
        
        # الانتقال للخطوة التالية
        await query.edit_message_text(
            f"✅ تم اختيار: {platform_name}\n\n" + MESSAGES['enter_whatsapp']
        )
        
        return ENTERING_WHATSAPP
    
    async def handle_whatsapp_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال رقم واتساب"""
        whatsapp = update.message.text.strip()
        
        # التحقق من الرقم
        is_valid, cleaned_number = validate_whatsapp(whatsapp)
        
        if not is_valid:
            await update.message.reply_text(
                MESSAGES['error_invalid_phone']
            )
            return ENTERING_WHATSAPP
        
        # حفظ الرقم
        context.user_data['registration']['whatsapp'] = cleaned_number
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'whatsapp_entered',
            CHOOSING_PAYMENT,
            context.user_data['registration']
        )
        
        # إشعار بالحفظ
        formatted_number = format_phone_display(cleaned_number)
        await update.message.reply_text(
            f"✅ تم حفظ رقم الواتساب: {formatted_number}\n" +
            MESSAGES['data_saved']
        )
        
        # الانتقال للخطوة التالية
        await update.message.reply_text(
            MESSAGES['choose_payment'],
            reply_markup=get_payment_keyboard()
        )
        
        return CHOOSING_PAYMENT
    
    async def handle_payment_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة اختيار طريقة الدفع"""
        query = update.callback_query
        await query.answer()
        
        # استخراج طريقة الدفع
        payment_key = query.data.replace("payment_", "")
        payment_name = PAYMENT_METHODS[payment_key]['name']
        
        # حفظ الاختيار
        context.user_data['registration']['payment_method'] = payment_key
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'payment_chosen',
            ENTERING_PHONE,
            context.user_data['registration']
        )
        
        # الانتقال للخطوة التالية
        await query.edit_message_text(
            f"✅ تم اختيار: {payment_name}\n\n" + MESSAGES['enter_phone']
        )
        
        return ENTERING_PHONE
    
    async def handle_phone_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال رقم الهاتف"""
        phone = update.message.text.strip()
        
        # التحقق من الرقم
        is_valid, cleaned_number = validate_egyptian_phone(phone)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ {cleaned_number}\n\n" + MESSAGES['error_invalid_phone']
            )
            return ENTERING_PHONE
        
        # حفظ الرقم
        context.user_data['registration']['phone'] = cleaned_number
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'phone_entered',
            ENTERING_PAYMENT_INFO,
            context.user_data['registration']
        )
        
        # الانتقال للخطوة التالية
        formatted_number = format_phone_display(cleaned_number)
        await update.message.reply_text(
            f"✅ تم حفظ رقم الهاتف: {formatted_number}\n" +
            MESSAGES['data_saved']
        )
        
        # التحقق من طريقة الدفع المختارة لعرض الرسالة المناسبة
        payment_method = context.user_data['registration'].get('payment_method', '')
        if payment_method == 'instapay':
            message = "🏦 أرسل رابط InstaPay الخاص بك:\n\nيمكنك نسخ الرسالة كاملة من InstaPay أو كتابة 'تخطي' للمتابعة"
        else:
            message = "💳 أرسل معلومات الدفع الخاصة بك:\n\n" + MESSAGES.get('skip_option', 'يمكنك كتابة "تخطي" لتجاوز هذه الخطوة')
        
        await update.message.reply_text(
            message,
            reply_markup=get_skip_keyboard()
        )
        
        return ENTERING_PAYMENT_INFO
    
    async def handle_payment_info_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال معلومات الدفع حسب الطريقة المختارة"""
        
        # التعامل مع الضغط على زر التخطي
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "skip_step":
                context.user_data['registration']['payment_info'] = None
                
                # الانتقال للخطوة التالية
                await query.edit_message_text(
                    "⏭️ تم تخطي معلومات الدفع\n\n" + MESSAGES['enter_emails'],
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
                "⏭️ تم تخطي معلومات الدفع\n\n" + MESSAGES['enter_emails'],
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
                    f"✅ تم استخراج وحفظ رابط InstaPay:\n{extracted_link}\n" +
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
                    f"✅ تم حفظ رقم المحفظة: {formatted_number}\n" +
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
                "✅ تم حفظ معلومات الدفع\n" + MESSAGES['data_saved']
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
    
    async def handle_email_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال البريد الإلكتروني"""
        
        # تهيئة قائمة الإيميلات إذا لم تكن موجودة
        if 'emails' not in context.user_data['registration']:
            context.user_data['registration']['emails'] = []
        
        # التحقق من الضغط على زر
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            if query.data == "skip_step" or query.data == "finish_emails":
                # الانتقال لمرحلة التأكيد
                return await self.show_confirmation(update, context)
            
            elif query.data == "add_email":
                await query.edit_message_text(
                    "📧 أرسل البريد الإلكتروني الإضافي:"
                )
                return ENTERING_EMAILS
        
        # معالجة النص المدخل
        email_input = update.message.text.strip()
        
        # التحقق من أمر الإنهاء
        if is_finish_command(email_input) or is_skip_command(email_input):
            return await self.show_confirmation(update, context)
        
        # التحقق من البريد الإلكتروني
        is_valid, cleaned_email = validate_email(email_input)
        
        if not is_valid:
            await update.message.reply_text(
                MESSAGES['error_invalid_email']
            )
            return ENTERING_EMAILS
        
        # إضافة البريد إلى القائمة
        context.user_data['registration']['emails'].append(cleaned_email)
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'emails_entered',
            ENTERING_EMAILS,
            context.user_data['registration']
        )
        
        # عرض الإيميلات المضافة
        emails_list = '\n'.join([f"• {e}" for e in context.user_data['registration']['emails']])
        await update.message.reply_text(
            f"✅ تم إضافة: {cleaned_email}\n\n" +
            f"📧 الإيميلات المسجلة:\n{emails_list}",
            reply_markup=get_emails_keyboard()
        )
        
        return ENTERING_EMAILS
    
    async def show_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض ملخص البيانات للتأكيد"""
        reg_data = context.user_data['registration']
        
        # إعداد ملخص البيانات
        platform_name = GAMING_PLATFORMS.get(reg_data.get('platform'), {}).get('name', 'غير محدد')
        payment_name = PAYMENT_METHODS.get(reg_data.get('payment_method'), {}).get('name', 'غير محدد')
        emails = ', '.join(reg_data.get('emails', [])) or 'لا يوجد'
        
        # تنسيق معلومات الدفع
        payment_info = reg_data.get('payment_info', 'غير محدد')
        if payment_info and payment_info != 'غير محدد':
            payment_method = reg_data.get('payment_method', '')
            if payment_method in ['vodafone', 'etisalat', 'orange'] and len(payment_info) == 11:
                payment_info = format_phone_display(payment_info)
        
        summary = f"""
📊 **ملخص بياناتك:**
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform_name}
📱 واتساب: {format_phone_display(reg_data.get('whatsapp', ''))}
💳 طريقة الدفع: {payment_name}
📞 الهاتف: {format_phone_display(reg_data.get('phone', ''))}
💰 معلومات الدفع: {payment_info}
📧 الإيميلات: {emails}
━━━━━━━━━━━━━━━━
        """
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            reg_data['telegram_id'],
            'confirming',
            CONFIRMING_DATA,
            reg_data
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                summary,
                reply_markup=get_confirm_keyboard(),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                summary,
                reply_markup=get_confirm_keyboard(),
                parse_mode='Markdown'
            )
        
        return CONFIRMING_DATA
    
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة تأكيد التسجيل"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_registration":
            # إكمال التسجيل
            reg_data = context.user_data['registration']
            
            # حفظ البيانات النهائية
            success = self.db.complete_registration(
                reg_data['telegram_id'],
                reg_data
            )
            
            if success:
                # رسالة النجاح
                completion_message = MESSAGES['registration_complete'].format(
                    platform=GAMING_PLATFORMS[reg_data['platform']]['name'],
                    whatsapp=format_phone_display(reg_data['whatsapp']),
                    payment=PAYMENT_METHODS[reg_data['payment_method']]['name'],
                    phone=format_phone_display(reg_data['phone']),
                    emails=', '.join(reg_data.get('emails', [])) or 'لا يوجد'
                )
                
                await query.edit_message_text(
                    completion_message,
                    parse_mode='Markdown'
                )
                
                # عرض القائمة الرئيسية
                await query.message.reply_text(
                    "يمكنك الآن استخدام جميع خدمات البوت! 🚀",
                    reply_markup=get_main_menu_keyboard()
                )
                
                # تنظيف بيانات المحادثة
                context.user_data.clear()
                
                return ConversationHandler.END
            else:
                await query.edit_message_text(
                    "❌ حدث خطأ في حفظ البيانات. الرجاء المحاولة مرة أخرى."
                )
                return CONFIRMING_DATA
        
        elif query.data == "edit_registration":
            # العودة للبداية للتعديل
            await query.edit_message_text(
                "📝 سنبدأ من جديد لتعديل بياناتك...",
                reply_markup=get_platform_keyboard()
            )
            return CHOOSING_PLATFORM
    
    async def handle_continue_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """استكمال التسجيل من نقطة التوقف"""
        query = update.callback_query
        await query.answer()
        
        telegram_id = query.from_user.id
        
        if query.data == "continue_registration":
            # استرجاع البيانات المحفوظة
            temp_data = self.db.get_temp_registration(telegram_id)
            
            if temp_data:
                # استعادة البيانات
                context.user_data['registration'] = temp_data['data']
                step = temp_data['step_number']
                
                # الانتقال للخطوة المناسبة
                step_messages = {
                    ENTERING_WHATSAPP: MESSAGES['enter_whatsapp'],
                    CHOOSING_PAYMENT: MESSAGES['choose_payment'],
                    ENTERING_PHONE: MESSAGES['enter_phone'],
                    ENTERING_PAYMENT_INFO: self._get_payment_info_message(context.user_data['registration'].get('payment_method', '')),
                    ENTERING_EMAILS: MESSAGES['enter_emails']
                }
                
                message = step_messages.get(step, "")
                
                # عرض لوحة المفاتيح المناسبة
                if step == CHOOSING_PAYMENT:
                    await query.edit_message_text(message, reply_markup=get_payment_keyboard())
                elif step == CHOOSING_PLATFORM:
                    await query.edit_message_text(message, reply_markup=get_platform_keyboard())
                elif step in [ENTERING_PAYMENT_INFO, ENTERING_EMAILS]:
                    await query.edit_message_text(message, reply_markup=get_skip_keyboard())
                else:
                    await query.edit_message_text(message)
                
                return step
        
        elif query.data == "restart_registration":
            # حذف البيانات المحفوظة والبدء من جديد
            self.db.clear_temp_registration(telegram_id)
            
            await query.edit_message_text(
                MESSAGES['choose_platform'],
                reply_markup=get_platform_keyboard()
            )
            
            # تهيئة بيانات جديدة
            context.user_data['registration'] = {
                'telegram_id': telegram_id,
                'step': 1
            }
            
            return CHOOSING_PLATFORM
    
    def _get_payment_info_message(self, payment_method: str) -> str:
        """الحصول على رسالة معلومات الدفع حسب الطريقة المختارة"""
        if payment_method == 'instapay':
            return "🏦 أرسل رابط InstaPay الخاص بك:\n\nيمكنك نسخ الرسالة كاملة من InstaPay أو كتابة 'تخطي' للمتابعة"
        elif payment_method in ['vodafone', 'etisalat', 'orange']:
            method_name = PAYMENT_METHODS.get(payment_method, {}).get('name', 'المحفظة')
            return f"📱 أرسل رقم {method_name}:\n\nأرسل الرقم المسجل في المحفظة الإلكترونية أو اكتب 'تخطي'"
        elif payment_method == 'visa':
            return "💳 أرسل آخر 4 أرقام من البطاقة (للتحقق فقط):\n\nمثال: 1234\nأو اكتب 'تخطي' للمتابعة"
        elif payment_method == 'paypal':
            return "💰 أرسل بريدك الإلكتروني المسجل في PayPal:\n\nأو اكتب 'تخطي' للمتابعة"
        else:
            return "💸 أرسل معلومات الدفع الخاصة بك:\n\nأو اكتب 'تخطي' للمتابعة"
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إلغاء عملية التسجيل"""
        await update.message.reply_text(
            "تم إلغاء عملية التسجيل. يمكنك البدء من جديد في أي وقت بكتابة /start",
            reply_markup=get_main_menu_keyboard()
        )
        
        # تنظيف البيانات
        context.user_data.clear()
        
        return ConversationHandler.END

def get_registration_conversation():
    """إنشاء معالج المحادثة للتسجيل"""
    handler = RegistrationHandler()
    
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handler.handle_registration_start, pattern="^register_new$"),
            CallbackQueryHandler(handler.handle_continue_registration, pattern="^(continue_registration|restart_registration)$")
        ],
        states={
            CHOOSING_PLATFORM: [
                CallbackQueryHandler(handler.handle_platform_choice, pattern="^platform_")
            ],
            ENTERING_WHATSAPP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_whatsapp_input)
            ],
            CHOOSING_PAYMENT: [
                CallbackQueryHandler(handler.handle_payment_choice, pattern="^payment_")
            ],
            ENTERING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_phone_input)
            ],
            ENTERING_PAYMENT_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_payment_info_input),
                CallbackQueryHandler(handler.handle_payment_info_input, pattern="^skip_step$")
            ],
            ENTERING_EMAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_email_input),
                CallbackQueryHandler(handler.handle_email_input, pattern="^(skip_step|add_email|finish_emails)$")
            ],
            CONFIRMING_DATA: [
                CallbackQueryHandler(handler.handle_confirmation, pattern="^(confirm_registration|edit_registration)$")
            ]
        },
        fallbacks=[
            CommandHandler('cancel', handler.cancel)
        ],
        allow_reentry=True
    )