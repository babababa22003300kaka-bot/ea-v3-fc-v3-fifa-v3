#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
لوحات المفاتيح للتسجيل
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from bot.config import GAMING_PLATFORMS, PAYMENT_METHODS

def get_start_keyboard():
    """لوحة البداية"""
    keyboard = [
        [InlineKeyboardButton("🆕 تسجيل جديد", callback_data="register_new")],
        [InlineKeyboardButton("🔑 تسجيل دخول", callback_data="login")],
        [InlineKeyboardButton("📞 الدعم الفني", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_platform_keyboard():
    """لوحة اختيار المنصة"""
    keyboard = []
    for key, platform in GAMING_PLATFORMS.items():
        keyboard.append([
            InlineKeyboardButton(
                platform['name'], 
                callback_data=f"platform_{key}"
            )
        ])
    return InlineKeyboardMarkup(keyboard)

def get_payment_keyboard():
    """لوحة اختيار طريقة الدفع"""
    keyboard = []
    # نقسم طرق الدفع إلى صفوف
    methods = list(PAYMENT_METHODS.items())
    
    # أول 3 طرق في صف واحد
    row1 = []
    for key, method in methods[:3]:
        row1.append(InlineKeyboardButton(
            method['emoji'], 
            callback_data=f"payment_{key}"
        ))
    keyboard.append(row1)
    
    # باقي الطرق كل 2 في صف
    for i in range(3, len(methods), 2):
        row = []
        for j in range(i, min(i+2, len(methods))):
            key, method = methods[j]
            row.append(InlineKeyboardButton(
                method['name'], 
                callback_data=f"payment_{key}"
            ))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def get_skip_keyboard():
    """لوحة التخطي"""
    keyboard = [
        [InlineKeyboardButton("⏭️ تخطي", callback_data="skip_step")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_continue_registration_keyboard():
    """لوحة استكمال التسجيل"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، أكمل من حيث توقفت", callback_data="continue_registration")],
        [InlineKeyboardButton("🔄 ابدأ من جديد", callback_data="restart_registration")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    """لوحة التأكيد"""
    keyboard = [
        [InlineKeyboardButton("✅ تأكيد وإنهاء التسجيل", callback_data="confirm_registration")],
        [InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_registration")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_emails_keyboard():
    """لوحة الإيميلات"""
    keyboard = [
        [InlineKeyboardButton("➕ إضافة إيميل آخر", callback_data="add_email")],
        [InlineKeyboardButton("✅ انتهى", callback_data="finish_emails")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard():
    """لوحة القائمة الرئيسية بعد التسجيل"""
    keyboard = [
        ["💰 شراء عملات", "💸 بيع عملات"],
        ["👤 الملف الشخصي", "💳 المحفظة"],
        ["📊 المعاملات", "🎁 العروض"],
        ["⚙️ الإعدادات", "📞 الدعم"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)