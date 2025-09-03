#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
لوحات المفاتيح للتسجيل - أزرار تفاعلية فقط
بدون ReplyKeyboard نهائياً
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import GAMING_PLATFORMS, PAYMENT_METHODS

def get_start_keyboard():
    """لوحة البداية - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("🆕 تسجيل جديد", callback_data="register_new")],
        [InlineKeyboardButton("🔑 تسجيل دخول", callback_data="login")],
        [InlineKeyboardButton("📞 الدعم الفني", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_platform_keyboard():
    """لوحة اختيار المنصة - أزرار تفاعلية"""
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
    """لوحة اختيار طريقة الدفع - كل زر في صف منفصل"""
    keyboard = []
    # عرض كل طريقة دفع في صف منفصل (فوق بعض)
    for key, method in PAYMENT_METHODS.items():
        keyboard.append([
            InlineKeyboardButton(
                method['name'], 
                callback_data=f"payment_{key}"
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)

def get_skip_keyboard():
    """لوحة التخطي - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("⏭️ تخطي", callback_data="skip_step")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_continue_registration_keyboard():
    """لوحة استكمال التسجيل - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("✅ نعم، أكمل من حيث توقفت", callback_data="continue_registration")],
        [InlineKeyboardButton("🔄 ابدأ من جديد", callback_data="restart_registration")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirm_keyboard():
    """لوحة التأكيد - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("✅ تأكيد وإنهاء التسجيل", callback_data="confirm_registration")],
        [InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_registration")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_emails_keyboard():
    """لوحة الإيميلات - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("➕ إضافة إيميل آخر", callback_data="add_email")],
        [InlineKeyboardButton("✅ انتهى", callback_data="finish_emails")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard():
    """لوحة القائمة الرئيسية - أزرار تفاعلية فقط"""
    keyboard = [
        [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
        [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile"),
         InlineKeyboardButton("💳 المحفظة", callback_data="wallet")],
        [InlineKeyboardButton("📊 المعاملات", callback_data="transactions"),
         InlineKeyboardButton("💹 الأسعار", callback_data="prices")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings"),
         InlineKeyboardButton("📞 الدعم", callback_data="support")],
        [InlineKeyboardButton("🔴 حذف الحساب", callback_data="delete_account")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delete_account_keyboard():
    """لوحة تأكيد حذف الحساب - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("⚠️ نعم، احذف حسابي نهائياً", callback_data="confirm_delete")],
        [InlineKeyboardButton("❌ لا، تراجع", callback_data="cancel_delete")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_buy_keyboard():
    """لوحة شراء العملات - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("100 عملة", callback_data="buy_100"),
         InlineKeyboardButton("500 عملة", callback_data="buy_500")],
        [InlineKeyboardButton("1000 عملة", callback_data="buy_1000"),
         InlineKeyboardButton("5000 عملة", callback_data="buy_5000")],
        [InlineKeyboardButton("10000 عملة", callback_data="buy_10000")],
        [InlineKeyboardButton("💎 كمية مخصصة", callback_data="buy_custom")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sell_keyboard(balance):
    """لوحة بيع العملات - أزرار تفاعلية"""
    keyboard = []
    
    if balance >= 100:
        keyboard.append([InlineKeyboardButton("100 عملة", callback_data="sell_100")])
    if balance >= 500:
        if keyboard:
            keyboard[-1].append(InlineKeyboardButton("500 عملة", callback_data="sell_500"))
        else:
            keyboard.append([InlineKeyboardButton("500 عملة", callback_data="sell_500")])
    
    if balance >= 1000:
        keyboard.append([InlineKeyboardButton("1000 عملة", callback_data="sell_1000")])
    if balance >= 5000:
        if len(keyboard[-1]) < 2:
            keyboard[-1].append(InlineKeyboardButton("5000 عملة", callback_data="sell_5000"))
        else:
            keyboard.append([InlineKeyboardButton("5000 عملة", callback_data="sell_5000")])
    
    keyboard.append([InlineKeyboardButton(f"💯 بيع الكل ({balance} عملة)", callback_data="sell_all")])
    keyboard.append([InlineKeyboardButton("💎 كمية مخصصة", callback_data="sell_custom")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_profile_keyboard():
    """لوحة الملف الشخصي - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_profile"),
         InlineKeyboardButton("🔐 الأمان", callback_data="security")],
        [InlineKeyboardButton("💳 المحفظة", callback_data="wallet"),
         InlineKeyboardButton("📊 المعاملات", callback_data="transactions")],
        [InlineKeyboardButton("🎁 المكافآت", callback_data="rewards"),
         InlineKeyboardButton("👥 الإحالات", callback_data="referrals")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_wallet_keyboard():
    """لوحة المحفظة - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("💰 شراء عملات", callback_data="buy_coins"),
         InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
        [InlineKeyboardButton("💱 تحويل عملات", callback_data="transfer"),
         InlineKeyboardButton("🎁 استخدام النقاط", callback_data="use_points")],
        [InlineKeyboardButton("📊 كل المعاملات", callback_data="all_transactions")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_keyboard():
    """لوحة الإدارة - أزرار تفاعلية"""
    keyboard = [
        [InlineKeyboardButton("📊 إحصائيات", callback_data="admin_stats"),
         InlineKeyboardButton("👥 المستخدمون", callback_data="admin_users")],
        [InlineKeyboardButton("💳 المعاملات", callback_data="admin_trans"),
         InlineKeyboardButton("📨 رسالة جماعية", callback_data="admin_broadcast")],
        [InlineKeyboardButton("💾 نسخة احتياطية", callback_data="admin_backup"),
         InlineKeyboardButton("📝 السجلات", callback_data="admin_logs")],
        [InlineKeyboardButton("🔙 إغلاق", callback_data="close")]
    ]
    return InlineKeyboardMarkup(keyboard)