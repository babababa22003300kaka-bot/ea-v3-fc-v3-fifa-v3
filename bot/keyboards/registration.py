#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""لوحات المفاتيح"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_start_keyboard():
    """لوحة البداية"""
    keyboard = [[InlineKeyboardButton("📝 تسجيل جديد", callback_data="start_registration")]]
    return InlineKeyboardMarkup(keyboard)

def get_main_menu_keyboard():
    """القائمة الرئيسية"""
    keyboard = [
        [InlineKeyboardButton("👤 الملف الشخصي", callback_data="show_profile")],
        [InlineKeyboardButton("💸 بيع عملات", callback_data="sell_coins")],
        [InlineKeyboardButton("📊 المعاملات", callback_data="transactions")],
        [InlineKeyboardButton("❓ المساعدة", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delete_account_keyboard():
    """لوحة تأكيد حذف الحساب"""
    keyboard = [
        [
            InlineKeyboardButton("⚠️ نعم، احذف نهائياً", callback_data="delete_confirm_final"),
            InlineKeyboardButton("❌ إلغاء", callback_data="delete_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
