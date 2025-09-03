#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask App for FC 26 Bot deployment on Render
"""

import os
import logging
import asyncio
import threading
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application

# استيراد البوت
from main_bot import FC26Bot
from bot.config import BOT_TOKEN, ADMIN_ID

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

def run_bot_in_thread():
    """تشغيل البوت في thread منفصل"""
    global bot_app
    
    try:
        # إنشاء event loop جديد للـ thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # إنشاء البوت
        fc26_bot = FC26Bot()
        
        # إنشاء التطبيق
        bot_app = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة المعالجات
        from bot.handlers.registration import get_registration_conversation
        
        bot_app.add_handler(get_registration_conversation())
        
        # معالجات الأوامر الأساسية
        from telegram.ext import CommandHandler
        bot_app.add_handler(CommandHandler("start", fc26_bot.start))
        bot_app.add_handler(CommandHandler("help", fc26_bot.help_command))
        bot_app.add_handler(CommandHandler("profile", fc26_bot.profile_command))
        bot_app.add_handler(CommandHandler("wallet", fc26_bot.wallet_command))
        bot_app.add_handler(CommandHandler("prices", fc26_bot.prices_command))
        bot_app.add_handler(CommandHandler("admin", fc26_bot.admin_command))
        
        logger.info("🚀 تشغيل البوت في وضع polling...")
        
        # تشغيل البوت
        loop.run_until_complete(bot_app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        ))
        
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return jsonify({
        'status': 'running',
        'bot': 'FC 26 Trading Bot',
        'version': '2.0',
        'features': [
            '7-step interactive registration',
            'Auto-save on every step',
            'Gaming platforms support',
            'Multiple payment methods',
            'Profile management',
            'Wallet system',
            'Egyptian Arabic interface'
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

@app.route('/webhook', methods=['POST'])
async def webhook():
    """استقبال تحديثات Telegram webhook"""
    if not bot_app:
        return jsonify({'error': 'Bot not initialized'}), 503
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data'}), 400
        
        # تحويل إلى Update object
        update = Update.de_json(data, bot_app.bot)
        
        # معالجة التحديث
        await bot_app.process_update(update)
        
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

def setup_webhook():
    """إعداد webhook إذا كنا على Render"""
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    
    if render_url:
        logger.info(f"🌐 Render URL detected: {render_url}")
        
        try:
            import httpx
            webhook_url = f"{render_url}/webhook"
            
            # إعداد webhook
            response = httpx.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                json={
                    'url': webhook_url,
                    'drop_pending_updates': True,
                    'allowed_updates': Update.ALL_TYPES
                }
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Webhook set successfully: {webhook_url}")
            else:
                logger.error(f"❌ Failed to set webhook: {response.text}")
                
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
    else:
        logger.info("🖥️ Running locally - using polling mode")
        # بدء البوت في thread منفصل
        bot_thread = threading.Thread(target=run_bot_in_thread, daemon=True)
        bot_thread.start()

# إعداد البوت عند بدء التشغيل
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    setup_webhook()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)