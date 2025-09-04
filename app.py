#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask App for FC 26 Bot deployment on Render - Fixed Version
"""

import os
import logging
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء Flask app
app = Flask(__name__)

# متغير للبوت
bot_app = None
bot_thread = None
is_local = os.getenv("RENDER") is None

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return jsonify({
        'status': 'running',
        'bot': 'FC 26 Trading Bot',
        'version': '2.0',
        'features': [
            'تسجيل تفاعلي من 3 خطوات',
            'حفظ تلقائي لكل خطوة',
            'دعم منصات الألعاب المختلفة',
            'طرق دفع متعددة',
            'إدارة الملف الشخصي',
            'واجهة عربية مصرية'
        ],
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/stats': 'Bot statistics'
        }
    })

@app.route('/health')
def health():
    """فحص الصحة"""
    return jsonify({
        'status': 'healthy',
        'bot_active': bot_app is not None,
        'service': 'FC 26 Bot'
    })

@app.route('/stats')
def stats():
    """إحصائيات البوت"""
    try:
        from bot.database.models import Database
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # إحصائيات المستخدمين
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE registration_status = 'complete'")
        registered_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM temp_registration")
        pending_registrations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        total_transactions = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'users': {
                'total': total_users,
                'registered': registered_users,
                'pending': pending_registrations
            },
            'transactions': total_transactions,
            'bot_status': 'active' if bot_app else 'starting'
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'error': 'Database not ready',
            'bot_status': 'starting'
        })

def run_bot_in_thread():
    """تشغيل البوت في thread منفصل"""
    global bot_app
    
    try:
        # إنشاء event loop جديد للـ thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # استيراد البوت
        from main_bot import FC26Bot
        
        # إنشاء البوت
        fc26_bot = FC26Bot()
        
        logger.info("🚀 تشغيل البوت في وضع polling...")
        
        # تشغيل البوت مباشرة
        fc26_bot.run()
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    if is_local:
        logger.info("🖥️ Running locally - using polling mode")
        
        # إنشاء البوت وتشغيله في thread منفصل
        bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
        bot_thread.start()
        
        # تشغيل Flask
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.info("☁️ Running on Render - webhook mode")
        # على Render، سيتم تشغيل Flask فقط
        # والبوت سيعمل من خلال webhook