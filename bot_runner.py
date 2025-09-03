#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشغيل البوت بشكل مستقل
"""

import os
import sys
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# معلومات البوت
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE')
ADMIN_ID = 1124247595

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء"""
    await update.message.reply_text(
        "🎮 *مرحباً بك في بوت FC 26!*\n\n"
        "🔥 بوت بيع وشراء كوينز FC 26\n"
        "✨ أفضل الأسعار في السوق\n\n"
        "الأوامر المتاحة:\n"
        "/start - البداية\n"
        "/help - المساعدة\n"
        "/prices - الأسعار\n"
        "/support - الدعم",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المساعدة"""
    await update.message.reply_text(
        "📚 *دليل الاستخدام*\n\n"
        "• /start - بدء البوت\n"
        "• /help - عرض المساعدة\n"
        "• /prices - عرض الأسعار\n"
        "• /support - التواصل مع الدعم\n\n"
        "للشراء أو البيع، استخدم الأزرار في القائمة الرئيسية",
        parse_mode='Markdown'
    )

async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الأسعار"""
    await update.message.reply_text(
        "📊 *أسعار كوينز FC 26*\n\n"
        "*الشراء:*\n"
        "• 100K = 50 جنيه\n"
        "• 500K = 230 جنيه\n"
        "• 1M = 450 جنيه\n"
        "• 2M = 850 جنيه\n\n"
        "*البيع:*\n"
        "• 100K = 40 جنيه\n"
        "• 500K = 190 جنيه\n"
        "• 1M = 370 جنيه\n\n"
        "💳 الدفع: فودافون كاش - انستاباي",
        parse_mode='Markdown'
    )

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الدعم الفني"""
    await update.message.reply_text(
        "💬 *الدعم الفني*\n\n"
        "📞 واتساب: 01234567890\n"
        "⏰ ساعات العمل: 10 صباحاً - 2 بعد منتصف الليل\n\n"
        "أو أرسل رسالتك هنا وسنرد عليك في أقرب وقت",
        parse_mode='Markdown'
    )

def main():
    """تشغيل البوت"""
    # إنشاء التطبيق
    application = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("prices", prices_command))
    application.add_handler(CommandHandler("support", support_command))
    
    # تشغيل البوت
    logger.info("🤖 البوت شغال دلوقتي...")
    print(f"✅ FC 26 Bot is running!")
    print(f"📱 Admin ID: {ADMIN_ID}")
    
    # تشغيل البوت
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()