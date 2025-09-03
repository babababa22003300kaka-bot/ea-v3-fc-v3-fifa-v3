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
            ENTERING_CARD,
            context.user_data['registration']
        )
        
        # الانتقال للخطوة التالية
        formatted_number = format_phone_display(cleaned_number)
        await update.message.reply_text(
            f"✅ تم حفظ رقم الهاتف: {formatted_number}\n" +
            MESSAGES['data_saved']
        )
        
        await update.message.reply_text(
            MESSAGES['enter_card']
        )
        
        return ENTERING_CARD
    
    async def handle_card_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال آخر 4 أرقام من البطاقة"""
        card_input = update.message.text.strip()
        
        # التحقق من أمر التخطي
        if is_skip_command(card_input):
            context.user_data['registration']['card_last_four'] = None
            
            # الانتقال للخطوة التالية
            await update.message.reply_text(
                "⏭️ تم تخطي هذه الخطوة\n\n" + MESSAGES['enter_instapay'],
                reply_markup=get_skip_keyboard()
            )
            return ENTERING_INSTAPAY
        
        # التحقق من الأرقام
        is_valid, cleaned_digits = validate_card_digits(card_input)
        
        if not is_valid:
            await update.message.reply_text(
                f"❌ {cleaned_digits}\n\nحاول مرة أخرى أو اكتب 'تخطي'"
            )
            return ENTERING_CARD
        
        # حفظ الأرقام
        context.user_data['registration']['card_last_four'] = cleaned_digits
        
        # حفظ تلقائي
        self.db.save_temp_registration(
            context.user_data['registration']['telegram_id'],
            'card_entered',
            ENTERING_INSTAPAY,
            context.user_data['registration']
        )
        
        # الانتقال للخطوة التالية
        masked = mask_card_number(cleaned_digits)
        await update.message.reply_text(
            f"✅ تم حفظ البيانات: {masked}\n🔐 بياناتك آمنة ومشفرة\n" +
            MESSAGES['data_saved']
        )
        
        await update.message.reply_text(
            MESSAGES['enter_instapay'],
            reply_markup=get_skip_keyboard()
        )
        
        return ENTERING_INSTAPAY
    
    async def handle_instapay_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة إدخال رابط InstaPay"""
        instapay_input = update.message.text.strip()
        
        # التحقق من أمر التخطي
        if is_skip_command(instapay_input) or update.callback_query:
            context.user_data['registration']['instapay'] = None
            
            # الانتقال للخطوة التالية
            message = "⏭️ تم تخطي رابط InstaPay\n\n" + MESSAGES['enter_emails']
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=get_skip_keyboard()
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=get_skip_keyboard()
                )
            return ENTERING_EMAILS
        
        # استخراج الرابط
        extracted_link = extract_instapay_link(instapay_input)
        
        if extracted_link:
            context.user_data['registration']['instapay'] = extracted_link
            
            # حفظ تلقائي
            self.db.save_temp_registration(
                context.user_data['registration']['telegram_id'],
                'instapay_entered',
                ENTERING_EMAILS,
                context.user_data['registration']
            )
            
            await update.message.reply_text(
                f"✅ تم استخراج وحفظ الرابط:\n{extracted_link}\n" +
                MESSAGES['data_saved']
            )
        else:
            context.user_data['registration']['instapay'] = instapay_input
            await update.message.reply_text(
                "✅ تم حفظ المعلومات"
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
        
        summary = f"""
📊 **ملخص بياناتك:**
━━━━━━━━━━━━━━━━
🎮 المنصة: {platform_name}
📱 واتساب: {format_phone_display(reg_data.get('whatsapp', ''))}
💳 طريقة الدفع: {payment_name}
📞 الهاتف: {format_phone_display(reg_data.get('phone', ''))}
💳 البطاقة: {mask_card_number(reg_data.get('card_last_four', '****'))}
🏦 InstaPay: {reg_data.get('instapay', 'غير محدد')}
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
                    ENTERING_CARD: MESSAGES['enter_card'],
                    ENTERING_INSTAPAY: MESSAGES['enter_instapay'],
                    ENTERING_EMAILS: MESSAGES['enter_emails']
                }
                
                message = step_messages.get(step, "")
                
                # عرض لوحة المفاتيح المناسبة
                if step == CHOOSING_PAYMENT:
                    await query.edit_message_text(message, reply_markup=get_payment_keyboard())
                elif step == CHOOSING_PLATFORM:
                    await query.edit_message_text(message, reply_markup=get_platform_keyboard())
                elif step in [ENTERING_INSTAPAY, ENTERING_EMAILS]:
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
            ENTERING_CARD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_card_input)
            ],
            ENTERING_INSTAPAY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_instapay_input),
                CallbackQueryHandler(handler.handle_instapay_input, pattern="^skip_step$")
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