#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Telegram Bot - الكود الأساسي للبوت
"""

import os
import sqlite3
import hashlib
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

logger = logging.getLogger(__name__)

# حالات المحادثة
(MAIN_MENU, REGISTER_NAME, REGISTER_PHONE, REGISTER_WHATSAPP, 
 REGISTER_CARD, REGISTER_PASSWORD, REGISTER_BIRTH, CONFIRM_DATA,
 BUY_COINS, SELL_COINS) = range(10)

class FC26Bot:
    """بوت FC 26 لبيع وشراء الكوينز"""
    
    def __init__(self):
        """تهيئة البوت"""
        self.TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE')
        self.ADMIN_ID = 1124247595
        self.DB_PATH = 'fc26_bot.db'
        self.setup_database()
        logger.info("تم تهيئة البوت بنجاح")
    
    def setup_database(self):
        """إنشاء قاعدة البيانات"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                whatsapp_number TEXT,
                card_number_hash TEXT,
                password_hash TEXT NOT NULL,
                birth_date TEXT,
                registration_date TEXT DEFAULT CURRENT_TIMESTAMP,
                balance INTEGER DEFAULT 0
            )
        ''')
        
        # جدول التسجيل المؤقت
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_registration (
                telegram_id INTEGER PRIMARY KEY,
                full_name TEXT,
                phone_number TEXT,
                whatsapp_number TEXT,
                card_number TEXT,
                password TEXT,
                birth_date TEXT,
                current_step TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المعاملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                transaction_type TEXT,
                amount INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("تم إنشاء قاعدة البيانات")
    
    def hash_data(self, data: str) -> str:
        """تشفير البيانات الحساسة"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def save_temp_data(self, telegram_id: int, field: str, value: str, step: str):
        """حفظ البيانات المؤقتة"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT telegram_id FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
        exists = cursor.fetchone()
        
        if exists:
            query = f'UPDATE temp_registration SET {field} = ?, current_step = ?, last_updated = CURRENT_TIMESTAMP WHERE telegram_id = ?'
            cursor.execute(query, (value, step, telegram_id))
        else:
            cursor.execute(
                f'INSERT INTO temp_registration (telegram_id, {field}, current_step) VALUES (?, ?, ?)',
                (telegram_id, value, step)
            )
        
        conn.commit()
        conn.close()
        logger.info(f"تم حفظ {field} للمستخدم {telegram_id}")
    
    def get_temp_data(self, telegram_id: int) -> Optional[Dict]:
        """جلب البيانات المؤقتة"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'telegram_id': row[0],
                'full_name': row[1],
                'phone_number': row[2],
                'whatsapp_number': row[3],
                'card_number': row[4],
                'password': row[5],
                'birth_date': row[6],
                'current_step': row[7]
            }
        return None
    
    def clear_temp_data(self, telegram_id: int):
        """مسح البيانات المؤقتة"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
        conn.commit()
        conn.close()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """أمر البدء"""
        user = update.effective_user
        telegram_id = user.id
        
        # التحقق من التسجيل
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, full_name FROM users WHERE telegram_id = ?', (telegram_id,))
        existing_user = cursor.fetchone()
        conn.close()
        
        if existing_user:
            # المستخدم مسجل
            keyboard = [
                [InlineKeyboardButton("💰 شراء كوينز", callback_data="buy")],
                [InlineKeyboardButton("💵 بيع كوينز", callback_data="sell")],
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile")],
                [InlineKeyboardButton("💬 الدعم", callback_data="support")],
                [InlineKeyboardButton("📊 الأسعار", callback_data="prices")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🎮 *أهلاً {existing_user[1]}!*\n\n"
                f"مرحباً بك في بوت FC 26\n"
                f"اختر من القائمة:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return MAIN_MENU
        else:
            # مستخدم جديد
            temp_data = self.get_temp_data(telegram_id)
            
            if temp_data and temp_data['current_step']:
                # يوجد تسجيل غير مكتمل
                keyboard = [
                    [InlineKeyboardButton("✅ متابعة التسجيل", callback_data="resume")],
                    [InlineKeyboardButton("🔄 البدء من جديد", callback_data="restart")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "🔄 *لديك تسجيل غير مكتمل*\n\n"
                    "هل تريد المتابعة من حيث توقفت؟",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                # بدء تسجيل جديد
                keyboard = [[InlineKeyboardButton("📝 بدء التسجيل", callback_data="register")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "🎮 *مرحباً بك في بوت FC 26!*\n\n"
                    "🔥 أفضل مكان لشراء وبيع الكوينز\n"
                    "✨ أسعار منافسة وخدمة سريعة\n\n"
                    "للبدء، يجب عليك التسجيل أولاً:",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            return MAIN_MENU
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """معالج الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        telegram_id = update.effective_user.id
        
        if data == "register":
            await query.edit_message_text(
                "📝 *التسجيل - خطوة 1 من 7*\n\n"
                "اكتب اسمك الثلاثي بالعربي:",
                parse_mode='Markdown'
            )
            return REGISTER_NAME
        
        elif data == "buy":
            keyboard = [
                [InlineKeyboardButton("100K - 50 جنيه", callback_data="buy_100k")],
                [InlineKeyboardButton("500K - 230 جنيه", callback_data="buy_500k")],
                [InlineKeyboardButton("1M - 450 جنيه", callback_data="buy_1m")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "💰 *شراء كوينز FC 26*\n\n"
                "اختر الكمية المطلوبة:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return BUY_COINS
        
        elif data == "sell":
            await query.edit_message_text(
                "💵 *بيع كوينز FC 26*\n\n"
                "اكتب الكمية التي تريد بيعها:\n"
                "مثال: 500000 أو 500k",
                parse_mode='Markdown'
            )
            return SELL_COINS
        
        elif data == "prices":
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📊 *أسعار كوينز FC 26*\n\n"
                "*الشراء:*\n"
                "• 100K = 50 جنيه\n"
                "• 500K = 230 جنيه\n"
                "• 1M = 450 جنيه\n\n"
                "*البيع:*\n"
                "• 100K = 40 جنيه\n"
                "• 500K = 190 جنيه\n"
                "• 1M = 370 جنيه",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return MAIN_MENU
        
        elif data == "support":
            keyboard = [
                [InlineKeyboardButton("📞 واتساب", url="https://wa.me/201234567890")],
                [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "💬 *الدعم الفني*\n\n"
                "ساعات العمل: 10 ص - 2 ص\n"
                "للتواصل المباشر عبر الواتساب",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return MAIN_MENU
        
        elif data == "back":
            return await self.show_main_menu(query, telegram_id)
        
        return MAIN_MENU
    
    async def show_main_menu(self, query, telegram_id):
        """عرض القائمة الرئيسية"""
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT full_name FROM users WHERE telegram_id = ?', (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            keyboard = [
                [InlineKeyboardButton("💰 شراء كوينز", callback_data="buy")],
                [InlineKeyboardButton("💵 بيع كوينز", callback_data="sell")],
                [InlineKeyboardButton("👤 الملف الشخصي", callback_data="profile")],
                [InlineKeyboardButton("💬 الدعم", callback_data="support")],
                [InlineKeyboardButton("📊 الأسعار", callback_data="prices")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🎮 *القائمة الرئيسية*\n\n"
                f"مرحباً {user[0]}!",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("📝 بدء التسجيل", callback_data="register")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "يجب عليك التسجيل أولاً",
                reply_markup=reply_markup
            )
        
        return MAIN_MENU
    
    async def register_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """تسجيل الاسم"""
        name = update.message.text.strip()
        telegram_id = update.effective_user.id
        
        # التحقق من الاسم
        if len(name.split()) < 3:
            await update.message.reply_text(
                "❌ من فضلك اكتب اسمك الثلاثي"
            )
            return REGISTER_NAME
        
        # حفظ الاسم
        self.save_temp_data(telegram_id, 'full_name', name, 'NAME_DONE')
        context.user_data['full_name'] = name
        
        await update.message.reply_text(
            f"✅ تم حفظ الاسم\n\n"
            f"📝 *خطوة 2 من 7*\n"
            f"اكتب رقم الموبايل:",
            parse_mode='Markdown'
        )
        
        return REGISTER_PHONE
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        await update.message.reply_text(
            "🎮 *دليل الاستخدام*\n\n"
            "/start - بدء البوت\n"
            "/help - المساعدة\n"
            "/prices - الأسعار\n"
            "/support - الدعم",
            parse_mode='Markdown'
        )
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر الأسعار"""
        await update.message.reply_text(
            "📊 *الأسعار الحالية*\n\n"
            "الشراء:\n"
            "• 100K = 50 جنيه\n"
            "• 500K = 230 جنيه\n"
            "• 1M = 450 جنيه\n\n"
            "البيع:\n"
            "• 100K = 40 جنيه\n"
            "• 500K = 190 جنيه",
            parse_mode='Markdown'
        )
    
    def run(self):
        """تشغيل البوت"""
        # إنشاء التطبيق
        application = Application.builder().token(self.TOKEN).build()
        
        # معالج المحادثات
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                MAIN_MENU: [CallbackQueryHandler(self.button_handler)],
                REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.register_name)],
                REGISTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.register_name)]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )
        
        # إضافة المعالجات
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler('help', self.help_command))
        application.add_handler(CommandHandler('prices', self.prices_command))
        
        # تشغيل البوت
        logger.info("🤖 البوت شغال دلوقتي...")
        print("✅ FC 26 Bot جاهز!")
        
        # تشغيل البوت بطريقة تدعم threading
        import asyncio
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"خطأ في البوت: {e}")