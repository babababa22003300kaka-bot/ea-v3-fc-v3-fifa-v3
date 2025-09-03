#!/usr/bin/env python3
# test_fortress.py - اختبار مبسط لـ Fort Knox Phase 2
"""
🏰 اختبار Fort Knox Digital Identity Phase 2
===========================================
تطبيق مبسط لاختبار جميع مكونات Fort Knox
"""

from config_env import FortKnoxConfig
from flask import Flask, render_template, session
import os
import secrets

# إنشاء Flask app بسيط
app = Flask(__name__)
app.secret_key = FortKnoxConfig.SECRET_KEY

@app.route('/')
def index():
    """الصفحة الرئيسية مع Fort Knox Phase 2"""
    # إنشاء CSRF token للجلسة
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)
    
    return render_template('index.html', csrf_token=session['csrf_token'])

@app.route('/fortress-status')
def fortress_status():
    """عرض حالة Fort Knox Phase 2"""
    status = FortKnoxConfig.get_fortress_status()
    ready, checks = FortKnoxConfig.is_production_ready()
    
    return {
        'fortress_status': status,
        'production_ready': ready,
        'security_checks': checks,
        'security_level': FortKnoxConfig.get_security_level(),
        'message': '🏰 Fort Knox Phase 2 - Digital Identity System Ready!'
    }

if __name__ == '__main__':
    print("🏰 بدء تشغيل Fort Knox Phase 2 - نظام الهوية الرقمية")
    print(f"✅ وضع الحصن: {FortKnoxConfig.FORTRESS_MODE}")
    print(f"✅ مستوى الأمان: {FortKnoxConfig.get_security_level()}")
    print(f"✅ الهوية الصامتة: {FortKnoxConfig.SILENT_IDENTITY_ENABLED}")
    
    # تشغيل الخادم
    app.run(
        host=FortKnoxConfig.HOST,
        port=FortKnoxConfig.PORT,
        debug=FortKnoxConfig.DEBUG
    )