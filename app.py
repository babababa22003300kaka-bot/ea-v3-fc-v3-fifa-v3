#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Telegram Bot - بوت بيع وشراء الكوينز
تطبيق Flask مع Telegram Bot للنشر على Render
"""

import os
import logging
import threading
from flask import Flask, jsonify
from telegram_bot import FC26Bot

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

# متغير للتحقق من حالة البوت
bot_status = {"running": False, "started_at": None}

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return """
    <html dir="rtl">
    <head>
        <title>FC 26 Bot</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3rem; margin-bottom: 1rem; }
            p { font-size: 1.2rem; }
            .status { 
                background: #4CAF50; 
                padding: 10px 20px; 
                border-radius: 50px;
                display: inline-block;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 FC 26 Telegram Bot</h1>
            <p>بوت بيع وشراء كوينز FC 26</p>
            <div class="status">✅ البوت يعمل بنجاح</div>
            <p style="margin-top: 2rem;">
                للتواصل مع البوت: <a href="https://t.me/fc26_coins_bot" style="color: #FFD700;">@fc26_coins_bot</a>
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """نقطة نهاية للتحقق من الصحة"""
    return jsonify({
        "status": "healthy",
        "service": "FC 26 Telegram Bot",
        "bot_running": bot_status["running"],
        "started_at": bot_status["started_at"]
    })

@app.route('/status')
def status():
    """عرض حالة البوت"""
    return jsonify({
        "bot_status": "running" if bot_status["running"] else "stopped",
        "uptime": bot_status["started_at"],
        "version": "1.0.0",
        "features": [
            "نظام تسجيل 7 خطوات",
            "شراء وبيع الكوينز",
            "الدعم الفني",
            "حفظ تلقائي"
        ]
    })

def run_telegram_bot():
    """تشغيل البوت في thread منفصل"""
    try:
        from datetime import datetime
        logger.info("بدء تشغيل البوت...")
        bot_status["running"] = True
        bot_status["started_at"] = datetime.now().isoformat()
        
        # إنشاء وتشغيل البوت
        bot = FC26Bot()
        bot.run()
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        bot_status["running"] = False

# تشغيل البوت عند بدء التطبيق
if __name__ != '__main__':
    # عند التشغيل مع gunicorn
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    logger.info("تم بدء البوت في thread منفصل")

if __name__ == '__main__':
    # عند التشغيل المباشر
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # تشغيل Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)