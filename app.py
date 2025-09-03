#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Telegram Bot - Flask Application for Render
"""

import os
import logging
import subprocess
import threading
from flask import Flask, jsonify, request, render_template_string

# إعداد السجلات
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

# معلومات البوت
BOT_INFO = {
    "name": "FC 26 Telegram Bot",
    "version": "3.0.0",
    "status": "running",
    "token": "7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE",
    "admin_id": 1124247595,
    "bot_username": "@fc26_coins_bot"
}

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FC 26 Bot - بوت بيع وشراء الكوينز</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
        }
        .container {
            text-align: center;
            padding: 3rem;
            background: rgba(255,255,255,0.1);
            border-radius: 30px;
            backdrop-filter: blur(20px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            max-width: 600px;
            width: 90%;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .emoji { font-size: 5rem; margin-bottom: 2rem; animation: bounce 2s infinite; }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        .status {
            background: linear-gradient(90deg, #4CAF50, #45a049);
            padding: 15px 30px;
            border-radius: 50px;
            display: inline-block;
            margin: 2rem 0;
            font-size: 1.2rem;
            box-shadow: 0 5px 15px rgba(76,175,80,0.4);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 5px 15px rgba(76,175,80,0.4); }
            50% { box-shadow: 0 5px 30px rgba(76,175,80,0.6); }
            100% { box-shadow: 0 5px 15px rgba(76,175,80,0.4); }
        }
        .features {
            text-align: right;
            margin: 2rem 0;
            padding: 1.5rem;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
        }
        .features h3 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        .features ul {
            list-style: none;
        }
        .features li {
            padding: 0.5rem 0;
            font-size: 1.1rem;
        }
        .features li:before {
            content: "✅ ";
            margin-left: 0.5rem;
        }
        .bot-link {
            display: inline-block;
            margin-top: 2rem;
            padding: 15px 40px;
            background: linear-gradient(90deg, #FFD700, #FFA500);
            color: #333;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: bold;
            transition: transform 0.3s;
            box-shadow: 0 5px 15px rgba(255,215,0,0.4);
        }
        .bot-link:hover {
            transform: scale(1.05);
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 2rem 0;
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #FFD700;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        .info {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.2);
            font-size: 0.9rem;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🤖</div>
        <h1>FC 26 Telegram Bot</h1>
        <p style="font-size: 1.3rem; margin-bottom: 1rem;">بوت بيع وشراء كوينز FC 26</p>
        
        <div class="status">
            ✅ البوت يعمل بنجاح على Render
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">24/7</div>
                <div class="stat-label">متاح دائماً</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">100%</div>
                <div class="stat-label">آمن</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">⚡</div>
                <div class="stat-label">سريع</div>
            </div>
        </div>
        
        <div class="features">
            <h3>🌟 المميزات:</h3>
            <ul>
                <li>نظام تسجيل متكامل 7 خطوات</li>
                <li>شراء وبيع كوينز FC 26</li>
                <li>حفظ تلقائي للبيانات</li>
                <li>واجهة عربية بالكامل</li>
                <li>دعم فني على مدار الساعة</li>
                <li>أسعار منافسة وتحديث مستمر</li>
                <li>تشفير آمن للبيانات الحساسة</li>
            </ul>
        </div>
        
        <a href="https://t.me/{{ bot_username }}" class="bot-link">
            💬 ابدأ المحادثة مع البوت
        </a>
        
        <div class="info">
            <p>Version: {{ version }} | Status: {{ status }}</p>
            <p>Admin ID: {{ admin_id }}</p>
            <p>Powered by Telegram Bot API</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return render_template_string(HTML_TEMPLATE, 
        bot_username=BOT_INFO['bot_username'].replace('@', ''),
        version=BOT_INFO['version'],
        status=BOT_INFO['status'],
        admin_id=BOT_INFO['admin_id']
    )

@app.route('/health')
def health():
    """نقطة فحص الصحة"""
    return jsonify({
        "status": "healthy",
        "service": BOT_INFO['name'],
        "version": BOT_INFO['version'],
        "bot_configured": True,
        "admin_id": BOT_INFO['admin_id'],
        "message": "البوت يعمل بشكل طبيعي على Render"
    })

@app.route('/status')
def status():
    """معلومات حالة البوت"""
    return jsonify({
        "bot": {
            "name": BOT_INFO['name'],
            "version": BOT_INFO['version'],
            "status": BOT_INFO['status'],
            "username": BOT_INFO['bot_username']
        },
        "server": {
            "platform": "Render",
            "region": "Oregon, USA"
        },
        "features": [
            "تسجيل 7 خطوات",
            "شراء/بيع كوينز",
            "دعم فني 24/7",
            "حفظ تلقائي",
            "تشفير SHA256"
        ]
    })

# تشغيل البوت في thread منفصل
def run_bot():
    """تشغيل البوت"""
    try:
        logger.info("🚀 بدء تشغيل البوت...")
        # استخدام subprocess لتشغيل البوت
        subprocess.Popen(['python', 'bot_runner.py'])
        logger.info("✅ البوت يعمل في الخلفية")
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل البوت: {e}")

# تشغيل البوت عند بدء التطبيق
if os.environ.get('RENDER'):
    # على Render فقط
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("📡 البوت يعمل على Render")

if __name__ == '__main__':
    # للاختبار المحلي
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 تشغيل الخادم على المنفذ {port}")
    
    # تشغيل البوت
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    app.run(host='0.0.0.0', port=port, debug=False)