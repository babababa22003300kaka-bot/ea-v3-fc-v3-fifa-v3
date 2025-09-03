#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
حالات التسجيل - نظام FSM
"""

from telegram.ext import ConversationHandler

# تعريف حالات التسجيل (6 خطوات بدلاً من 7)
(
    CHOOSING_PLATFORM,
    ENTERING_WHATSAPP,
    CHOOSING_PAYMENT,
    ENTERING_PHONE,
    ENTERING_PAYMENT_INFO,  # حالة موحدة للمعلومات حسب طريقة الدفع
    ENTERING_EMAILS,
    CONFIRMING_DATA
) = range(7)

# أسماء الحالات للعرض
STATE_NAMES = {
    CHOOSING_PLATFORM: "اختيار المنصة",
    ENTERING_WHATSAPP: "إدخال رقم واتساب",
    CHOOSING_PAYMENT: "اختيار طريقة الدفع",
    ENTERING_PHONE: "إدخال رقم الهاتف",
    ENTERING_PAYMENT_INFO: "إدخال معلومات الدفع",
    ENTERING_EMAILS: "إدخال البريد الإلكتروني",
    CONFIRMING_DATA: "تأكيد البيانات"
}

# خريطة الانتقال بين الحالات
STATE_FLOW = {
    CHOOSING_PLATFORM: ENTERING_WHATSAPP,
    ENTERING_WHATSAPP: CHOOSING_PAYMENT,
    CHOOSING_PAYMENT: ENTERING_PHONE,
    ENTERING_PHONE: ENTERING_PAYMENT_INFO,
    ENTERING_PAYMENT_INFO: ENTERING_EMAILS,
    ENTERING_EMAILS: CONFIRMING_DATA,
    CONFIRMING_DATA: ConversationHandler.END
}

def get_next_state(current_state):
    """الحصول على الحالة التالية"""
    return STATE_FLOW.get(current_state, ConversationHandler.END)

def get_state_name(state):
    """الحصول على اسم الحالة"""
    return STATE_NAMES.get(state, "غير معروف")