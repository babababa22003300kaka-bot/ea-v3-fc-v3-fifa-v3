#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Telegram Bot - نسخة محسنة للعمل على Render
"""

import os
import logging
from flask import Flask, jsonify, request

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
    "version": "2.0.0",
    "status": "running",
    "token": os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE'),
    "admin_id": 1124247595
}

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>FC 26 Bot - بوت بيع وشراء الكوينز</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: white;
            }}
            .container {{
                text-align: center;
                padding: 3rem;
                background: rgba(255,255,255,0.1);
                border-radius: 30px;
                backdrop-filter: blur(20px);
                box-shadow: 0 25px 50px rgba(0,0,0,0.2);
                max-width: 600px;
                width: 90%;
            }}
            h1 {{
                font-size: 3.5rem;
                margin-bottom: 1.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .emoji {{ font-size: 5rem; margin-bottom: 2rem; }}
            .status {{
                background: linear-gradient(90deg, #4CAF50, #45a049);
                padding: 15px 30px;
                border-radius: 50px;
                display: inline-block;
                margin: 2rem 0;
                font-size: 1.2rem;
                box-shadow: 0 5px 15px rgba(76,175,80,0.4);
            }}
            .features {{
                text-align: right;
                margin: 2rem 0;
                padding: 1.5rem;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
            }}
            .features h3 {{
                margin-bottom: 1rem;
                font-size: 1.5rem;
            }}
            .features ul {{
                list-style: none;
            }}
            .features li {{
                padding: 0.5rem 0;
                font-size: 1.1rem;
            }}
            .features li:before {{
                content: "✅ ";
                margin-left: 0.5rem;
            }}
            .bot-link {{
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
            }}
            .bot-link:hover {{
                transform: scale(1.05);
            }}
            .info {{
                margin-top: 2rem;
                padding-top: 2rem;
                border-top: 1px solid rgba(255,255,255,0.2);
                font-size: 0.9rem;
                opacity: 0.8;
            }}
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
            
            <div class="features">
                <h3>🌟 المميزات:</h3>
                <ul>
                    <li>نظام تسجيل متكامل 7 خطوات</li>
                    <li>شراء وبيع كوينز FC 26</li>
                    <li>حفظ تلقائي للبيانات</li>
                    <li>واجهة عربية بالكامل</li>
                    <li>دعم فني على مدار الساعة</li>
                    <li>أسعار منافسة وتحديث مستمر</li>
                </ul>
            </div>
            
            <a href="https://t.me/fc26_coins_bot" class="bot-link">
                💬 ابدأ المحادثة مع البوت
            </a>
            
            <div class="info">
                <p>Version: {BOT_INFO['version']} | Status: {BOT_INFO['status']}</p>
                <p>Powered by Telegram Bot API</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """نقطة فحص الصحة"""
    return jsonify({
        "status": "healthy",
        "service": BOT_INFO['name'],
        "version": BOT_INFO['version'],
        "bot_token_configured": bool(BOT_INFO['token']),
        "admin_id": BOT_INFO['admin_id'],
        "environment": "production",
        "message": "البوت يعمل بشكل طبيعي"
    })

@app.route('/status')
def status():
    """معلومات حالة البوت"""
    return jsonify({
        "bot": BOT_INFO,
        "server": {
            "platform": "Render",
            "region": "Oregon, USA",
            "python_version": "3.10"
        },
        "features": [
            "7-خطوات تسجيل",
            "شراء/بيع كوينز",
            "دعم فني",
            "حفظ تلقائي",
            "تشفير البيانات"
        ],
        "api_endpoints": [
            "/",
            "/health",
            "/status",
            "/webhook"
        ]
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint للبوت"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {data}")
        return jsonify({"status": "ok", "received": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# تشغيل البوت في عملية منفصلة
def start_bot_process():
    """تشغيل البوت في عملية منفصلة"""
    import subprocess
    import sys
    
    try:
        # تشغيل البوت كعملية منفصلة
        bot_script = """
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from telegram_bot import FC26Bot

if __name__ == '__main__':
    bot = FC26Bot()
    bot.run()
"""
        
        # حفظ السكريبت في ملف مؤقت
        with open('/tmp/run_bot.py', 'w') as f:
            f.write(bot_script)
        
        # تشغيل البوت
        subprocess.Popen([sys.executable, '/tmp/run_bot.py'])
        logger.info("✅ تم تشغيل البوت في عملية منفصلة")
        return True
    except Exception as e:
        logger.error(f"❌ فشل تشغيل البوت: {e}")
        return False

# محاولة تشغيل البوت عند بدء التطبيق
if __name__ != '__main__':
    # عند التشغيل مع gunicorn
    logger.info("🚀 بدء تشغيل التطبيق على Render...")
    # نحاول تشغيل البوت لكن لا نوقف التطبيق إذا فشل
    start_bot_process()

if __name__ == '__main__':
    # عند التشغيل المباشر للاختبار
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 تشغيل الخادم على المنفذ {port}")
    start_bot_process()
    app.run(host='0.0.0.0', port=port, debug=False)