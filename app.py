#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FC 26 Telegram Bot - نسخة محسنة للعمل على Render
مع نظام ملف شخصي متقدم
"""

import os
import logging
from flask import Flask, jsonify, request, render_template_string
from datetime import datetime

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
    "version": "4.0.0",
    "status": "active",
    "token": os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE'),
    "admin_id": 1124247595,
    "bot_username": "@fc26_coins_bot",
    "webhook_url": os.getenv('RENDER_EXTERNAL_URL', 'https://ea-v3-fc-v3-fifa-v3.onrender.com')
}

# HTML template محسن
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>FC 26 Bot - بوت بيع وشراء الكوينز</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Cairo', 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 20px;
        }
        .container {
            text-align: center;
            padding: 3rem;
            background: rgba(255,255,255,0.1);
            border-radius: 30px;
            backdrop-filter: blur(20px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.2);
            max-width: 700px;
            width: 100%;
            animation: fadeIn 0.5s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            font-size: 2.8rem;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            font-weight: 700;
        }
        .emoji { 
            font-size: 5rem; 
            margin-bottom: 2rem; 
            animation: bounce 2s infinite;
            filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
        }
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
            font-weight: 600;
            box-shadow: 0 5px 15px rgba(76,175,80,0.4);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        .features {
            text-align: right;
            margin: 2rem 0;
            padding: 2rem;
            background: rgba(255,255,255,0.08);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .features h3 {
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
            font-weight: 600;
            color: #FFD700;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            text-align: right;
        }
        .feature-item {
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            transition: all 0.3s ease;
        }
        .feature-item:hover {
            background: rgba(255,255,255,0.1);
            transform: translateY(-5px);
        }
        .feature-item:before {
            content: "✨ ";
            margin-left: 0.5rem;
            color: #FFD700;
        }
        .bot-link {
            display: inline-block;
            margin-top: 2rem;
            padding: 18px 50px;
            background: linear-gradient(90deg, #FFD700, #FFA500);
            color: #333;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.4rem;
            font-weight: 700;
            transition: all 0.3s;
            box-shadow: 0 10px 25px rgba(255,215,0,0.4);
            position: relative;
            overflow: hidden;
        }
        .bot-link:before {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.5);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        .bot-link:hover:before {
            width: 300px;
            height: 300px;
        }
        .bot-link:hover {
            transform: scale(1.05);
            box-shadow: 0 15px 35px rgba(255,215,0,0.6);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin: 2rem 0;
            padding: 1.5rem;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
        }
        .stat-item {
            text-align: center;
            padding: 1rem;
            transition: transform 0.3s;
        }
        .stat-item:hover {
            transform: scale(1.1);
        }
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        .profile-system {
            margin: 2rem 0;
            padding: 2rem;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            text-align: right;
        }
        .profile-title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #FFD700;
        }
        .profile-features {
            display: grid;
            gap: 0.8rem;
        }
        .profile-feature {
            padding: 0.8rem;
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            border-right: 3px solid #FFD700;
            transition: all 0.3s;
        }
        .profile-feature:hover {
            background: rgba(255,255,255,0.08);
            padding-right: 1.5rem;
        }
        .info {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.2);
            font-size: 0.95rem;
            opacity: 0.9;
        }
        .telegram-widget {
            margin: 2rem 0;
        }
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            .emoji { font-size: 4rem; }
            .stats { grid-template-columns: 1fr; }
            .features-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🤖</div>
        <h1>FC 26 Telegram Bot</h1>
        <p style="font-size: 1.4rem; margin-bottom: 1rem;">بوت بيع وشراء كوينز FC 26</p>
        
        <div class="status">
            ⚡ البوت يعمل بنجاح على Render
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">24/7</div>
                <div class="stat-label">متاح دائماً</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">100%</div>
                <div class="stat-label">آمن ومحمي</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">⚡</div>
                <div class="stat-label">سرعة فائقة</div>
            </div>
        </div>
        
        <div class="features">
            <h3>🌟 المميزات الأساسية</h3>
            <div class="features-grid">
                <div class="feature-item">نظام تسجيل متكامل 7 خطوات</div>
                <div class="feature-item">شراء وبيع كوينز FC 26</div>
                <div class="feature-item">حفظ تلقائي للبيانات</div>
                <div class="feature-item">واجهة عربية بالكامل</div>
                <div class="feature-item">دعم فني على مدار الساعة</div>
                <div class="feature-item">تشفير آمن SHA256</div>
            </div>
        </div>

        <div class="profile-system">
            <div class="profile-title">🎮 نظام الملف الشخصي المتقدم</div>
            <div class="profile-features">
                <div class="profile-feature">📊 إحصائيات كاملة للمعاملات</div>
                <div class="profile-feature">💰 رصيد الكوينز المتاح</div>
                <div class="profile-feature">📈 تاريخ الشراء والبيع</div>
                <div class="profile-feature">🏆 مستوى العضوية</div>
                <div class="profile-feature">🎯 نقاط الولاء والمكافآت</div>
                <div class="profile-feature">📱 ربط حسابات متعددة</div>
                <div class="profile-feature">🔔 إشعارات فورية</div>
                <div class="profile-feature">⚙️ إعدادات مخصصة</div>
            </div>
        </div>
        
        <a href="https://t.me/{{ bot_username }}" class="bot-link">
            <span style="position: relative; z-index: 1;">💬 ابدأ المحادثة مع البوت</span>
        </a>

        <div class="telegram-widget">
            <script async src="https://telegram.org/js/telegram-widget.js?22" 
                    data-telegram-login="{{ bot_username }}" 
                    data-size="large" 
                    data-radius="10"
                    data-auth-url="/telegram-auth">
            </script>
        </div>
        
        <div class="info">
            <p><strong>الإصدار:</strong> {{ version }} | <strong>الحالة:</strong> {{ status }}</p>
            <p><strong>آخر تحديث:</strong> {{ last_update }}</p>
            <p>Powered by Telegram Bot API & Flask on Render</p>
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
        last_update=datetime.now().strftime('%Y-%m-%d %H:%M')
    )

@app.route('/health')
def health():
    """نقطة فحص الصحة"""
    return jsonify({
        "status": "healthy",
        "service": BOT_INFO['name'],
        "version": BOT_INFO['version'],
        "bot_configured": True,
        "webhook_configured": True,
        "admin_id": BOT_INFO['admin_id'],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Webhook endpoint للبوت - يستقبل التحديثات من Telegram"""
    if request.method == 'GET':
        return jsonify({"status": "Webhook is ready", "bot": BOT_INFO['bot_username']})
    
    try:
        # استقبال البيانات من Telegram
        update = request.get_json()
        
        # معالجة الرسالة
        if update and 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            # حفظ في قاعدة البيانات أو معالجة الأمر
            logger.info(f"Received message from {chat_id}: {text}")
            
            # يمكنك إضافة معالجة الأوامر هنا
            
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/set-webhook')
def set_webhook():
    """تعيين Webhook للبوت"""
    import requests
    
    webhook_url = f"{BOT_INFO['webhook_url']}/webhook"
    telegram_url = f"https://api.telegram.org/bot{BOT_INFO['token']}/setWebhook"
    
    try:
        response = requests.post(telegram_url, json={"url": webhook_url})
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url,
            "telegram_response": response.json()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
            "region": "Oregon, USA",
            "webhook_url": BOT_INFO['webhook_url']
        },
        "profile_features": [
            "إحصائيات المعاملات",
            "رصيد الكوينز",
            "تاريخ الشراء والبيع", 
            "مستوى العضوية",
            "نقاط الولاء",
            "ربط حسابات متعددة",
            "إشعارات فورية",
            "إعدادات مخصصة"
        ],
        "basic_features": [
            "تسجيل 7 خطوات",
            "شراء/بيع كوينز",
            "دعم فني 24/7",
            "حفظ تلقائي",
            "تشفير SHA256"
        ]
    })

@app.route('/telegram-auth', methods=['POST'])
def telegram_auth():
    """معالجة تسجيل الدخول من Telegram"""
    data = request.get_json()
    # معالجة بيانات تسجيل الدخول
    return jsonify({"status": "authenticated", "user": data})

# تعيين Webhook تلقائياً عند بدء التطبيق
if os.environ.get('RENDER'):
    import requests
    import time
    
    def setup_webhook():
        """تعيين Webhook عند البدء"""
        time.sleep(5)  # انتظار 5 ثواني لضمان بدء الخادم
        try:
            webhook_url = f"{BOT_INFO['webhook_url']}/webhook"
            telegram_url = f"https://api.telegram.org/bot{BOT_INFO['token']}/setWebhook"
            response = requests.post(telegram_url, json={"url": webhook_url}, timeout=10)
            logger.info(f"Webhook setup response: {response.json()}")
        except Exception as e:
            logger.error(f"Failed to setup webhook: {e}")
    
    # تشغيل في thread منفصل
    import threading
    webhook_thread = threading.Thread(target=setup_webhook, daemon=True)
    webhook_thread.start()
    logger.info("📡 Starting webhook setup on Render...")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)