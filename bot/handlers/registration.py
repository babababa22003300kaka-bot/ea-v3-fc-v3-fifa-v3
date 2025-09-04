#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""معالج التسجيل البسيط"""

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

def get_registration_conversation():
    """إرجاع معالج التسجيل"""
    # معالج بسيط مؤقت
    return ConversationHandler(
        entry_points=[CommandHandler("register", lambda u, c: -1)],
        states={},
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )
