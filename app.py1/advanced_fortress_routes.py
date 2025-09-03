"""
🏰 Advanced Fortress Routes V2 - المسارات المحمية المتقدمة
نظام مسارات محمي بالكامل مع Zero Trust Architecture V2
"""

from flask import Blueprint, render_template, request, jsonify, session
from functools import wraps
import logging
import json

# استيراد وزارة الأمان المتقدمة
try:
    from ministries.advanced_security_ministry import (
        advanced_security_ministry,
        require_security,
        ThreatLevel,
        SecurityEventType,
        SecurityException
    )
    ADVANCED_SECURITY_ENABLED = True
except ImportError:
    ADVANCED_SECURITY_ENABLED = False
    advanced_security_ministry = None

# إنشاء Blueprint
advanced_fortress_bp = Blueprint('advanced_fortress', __name__, url_prefix='/fortress/v2')

# إعداد نظام السجلات
logger = logging.getLogger('AdvancedFortressRoutes')


def require_advanced_security(threat_level=ThreatLevel.MEDIUM):
    """Decorator للتحقق من الأمان المتقدم قبل الوصول للمسار"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not ADVANCED_SECURITY_ENABLED:
                return jsonify({'error': 'Advanced security system not available'}), 503
            
            # الحصول على بيانات الطلب
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            # التحقق من حظر IP
            if advanced_security_ministry.is_ip_blocked(ip_address):
                return jsonify({'error': 'Access denied'}), 403
            
            # التحقق من مستوى التهديد
            if advanced_security_ministry.threat_level.value > threat_level.value:
                return jsonify({
                    'error': 'System threat level too high',
                    'current_level': advanced_security_ministry.threat_level.name
                }), 503
            
            # التحقق من الجلسة أو إنشاء واحدة جديدة
            session_token = session.get('advanced_session_token')
            
            if not session_token:
                # محاولة المصادقة التلقائية للزوار الجدد
                import uuid
                user_id = str(uuid.uuid4())
                credentials = {
                    'user_id': user_id,
                    'password': f"{user_id}_password",  # Placeholder
                    'mfa_code': '123456',  # Placeholder
                    'ip_address': ip_address
                }
                
                success, token = advanced_security_ministry.authenticate_user(credentials)
                if success:
                    session['advanced_session_token'] = token
                    session['user_id'] = user_id
                else:
                    return jsonify({'error': 'Authentication failed'}), 401
            else:
                # التحقق من صحة الجلسة
                if not advanced_security_ministry.session_manager.validate_session(session_token):
                    session.pop('advanced_session_token', None)
                    return jsonify({'error': 'Session expired'}), 401
            
            # التحقق من حد المعدل
            if not advanced_security_ministry.check_rate_limit(f"request_{ip_address}"):
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # تطبيق Zero Trust
            request_data = {
                'session_token': session.get('advanced_session_token'),
                'user_id': session.get('user_id'),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'resource': request.endpoint,
                'action': request.method,
                'data': request.get_json() if request.is_json else {}
            }
            
            is_valid, message = advanced_security_ministry.validate_request(request_data)
            if not is_valid:
                return jsonify({'error': f'Zero Trust validation failed: {message}'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@advanced_fortress_bp.route('/')
@require_advanced_security(ThreatLevel.LOW)
def advanced_home():
    """الصفحة الرئيسية المحمية V2"""
    return render_template('fortress/advanced_index.html')


@advanced_fortress_bp.route('/dashboard')
@require_advanced_security(ThreatLevel.LOW)
def security_dashboard():
    """لوحة المعلومات الأمنية المتقدمة"""
    if not ADVANCED_SECURITY_ENABLED:
        return jsonify({'error': 'Advanced security not available'}), 503
    
    dashboard_data = advanced_security_ministry.get_security_dashboard()
    return jsonify(dashboard_data)


@advanced_fortress_bp.route('/authenticate', methods=['POST'])
def authenticate():
    """مصادقة المستخدم المتقدمة"""
    if not ADVANCED_SECURITY_ENABLED:
        return jsonify({
            'success': False,
            'message': 'Advanced security not available'
        }), 503
    
    try:
        data = request.get_json()
        
        credentials = {
            'user_id': data.get('username'),
            'password': data.get('password'),
            'mfa_code': data.get('mfa_code'),
            'ip_address': request.remote_addr
        }
        
        success, result = advanced_security_ministry.authenticate_user(credentials)
        
        if success:
            session['advanced_session_token'] = result
            session['user_id'] = credentials['user_id']
            
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'session_token': result[:20] + '...',  # عرض جزء فقط
                'trust_score': advanced_security_ministry.trust_scores.get(
                    credentials['user_id'], 50
                )
            })
        else:
            return jsonify({
                'success': False,
                'message': result
            }), 401
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({
            'success': False,
            'message': 'Authentication error'
        }), 500


@advanced_fortress_bp.route('/validate', methods=['POST'])
@require_advanced_security(ThreatLevel.MEDIUM)
def validate_data():
    """التحقق من البيانات بالنظام المتقدم"""
    if not ADVANCED_SECURITY_ENABLED:
        return jsonify({
            'success': False,
            'message': 'Advanced security not available'
        }), 503
    
    try:
        data = request.form.to_dict() if request.form else request.get_json()
        
        # فحص التهديدات
        for key, value in data.items():
            if isinstance(value, str):
                if advanced_security_ministry.detect_threat(value):
                    return jsonify({
                        'success': False,
                        'message': f'Security threat detected in {key}',
                        'threat_level': advanced_security_ministry.threat_level.name
                    }), 400
        
        # تشفير البيانات الحساسة
        if 'sensitive_data' in data:
            encrypted = advanced_security_ministry.encrypt_sensitive_data(
                data['sensitive_data']
            )
            data['encrypted_data'] = encrypted
            del data['sensitive_data']
        
        # تحديث نقاط الثقة
        user_id = session.get('user_id')
        if user_id:
            trust_score = advanced_security_ministry.update_trust_score(user_id, 2)
        else:
            trust_score = 50
        
        return jsonify({
            'success': True,
            'message': 'Data validated successfully',
            'trust_score': trust_score,
            'system_status': {
                'threat_level': advanced_security_ministry.threat_level.name,
                'security_version': advanced_security_ministry.version
            }
        })
        
    except SecurityException as e:
        logger.error(f"Security exception: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 403
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'message': 'Validation error'
        }), 500


@advanced_fortress_bp.route('/encrypt', methods=['POST'])
@require_advanced_security(ThreatLevel.LOW)
def encrypt_data():
    """تشفير البيانات"""
    if not ADVANCED_SECURITY_ENABLED:
        return jsonify({'error': 'Advanced security not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'No content to encrypt'
            }), 400
        
        encrypted = advanced_security_ministry.encrypt_sensitive_data(data['content'])
        
        return jsonify({
            'success': True,
            'encrypted': encrypted,
            'algorithm': 'AES-256-GCM'
        })
        
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return jsonify({
            'success': False,
            'message': 'Encryption failed'
        }), 500


@advanced_fortress_bp.route('/decrypt', methods=['POST'])
@require_advanced_security(ThreatLevel.MEDIUM)
def decrypt_data():
    """فك تشفير البيانات"""
    if not ADVANCED_SECURITY_ENABLED:
        return jsonify({'error': 'Advanced security not available'}), 503
    
    try:
        data = request.get_json()
        
        if not data or 'encrypted' not in data:
            return jsonify({
                'success': False,
                'message': 'No encrypted data provided'
            }), 400
        
        decrypted = advanced_security_ministry.decrypt_sensitive_data(data['encrypted'])
        
        return jsonify({
            'success': True,
            'decrypted': decrypted
        })
        
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return jsonify({
            'success': False,
            'message': 'Decryption failed'
        }), 500


@advanced_fortress_bp.route('/threat-scan', methods=['POST'])
@require_advanced_security(ThreatLevel.LOW)
def threat_scan():
    """فحص التهديدات"""
    if not ADVANCED_SECURITY_ENABLED:
        return jsonify({'error': 'Advanced security not available'}), 503
    
    try:
        data = request.get_json()
        input_text = data.get('input', '')
        threat_type = data.get('type', 'all')
        
        threat_detected = advanced_security_ministry.detect_threat(input_text, threat_type)
        
        return jsonify({
            'threat_detected': threat_detected,
            'threat_type': threat_type,
            'current_threat_level': advanced_security_ministry.threat_level.name,
            'recommendation': 'Block request' if threat_detected else 'Safe to proceed'
        })
        
    except Exception as e:
        logger.error(f"Threat scan error: {e}")
        return jsonify({
            'error': 'Threat scan failed'
        }), 500


@advanced_fortress_bp.route('/security-test')
@require_advanced_security(ThreatLevel.LOW)
def security_test():
    """صفحة اختبار النظام الأمني المتقدم"""
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <title>اختبار النظام الأمني المتقدم V2</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0c0c0c, #1a1a2e, #16213e);
                color: #fff;
                padding: 20px;
                margin: 0;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255,255,255,0.05);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 {
                text-align: center;
                color: #00d4ff;
                font-size: 2.5em;
                margin-bottom: 30px;
                text-shadow: 0 0 20px rgba(0,212,255,0.5);
            }
            .test-section {
                margin: 30px 0;
                padding: 20px;
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                border: 1px solid rgba(0,212,255,0.3);
            }
            h2 {
                color: #00d4ff;
                margin-bottom: 20px;
            }
            .test-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            input, select, textarea, button {
                padding: 12px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(0,212,255,0.5);
                color: #fff;
                border-radius: 8px;
                font-size: 16px;
            }
            button {
                background: linear-gradient(135deg, #00d4ff, #0099cc);
                color: #000;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,212,255,0.3);
            }
            .result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                display: none;
            }
            .result.success {
                background: rgba(0,255,0,0.2);
                border: 1px solid #0f0;
            }
            .result.danger {
                background: rgba(255,0,0,0.2);
                border: 1px solid #f00;
            }
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .stat-card {
                background: rgba(255,255,255,0.05);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                border: 1px solid rgba(0,212,255,0.3);
            }
            .stat-value {
                font-size: 24px;
                color: #00d4ff;
                font-weight: bold;
            }
            .stat-label {
                font-size: 12px;
                color: rgba(255,255,255,0.7);
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏰 اختبار النظام الأمني المتقدم V2</h1>
            
            <div class="dashboard" id="dashboard">
                <div class="stat-card">
                    <div class="stat-value" id="threatLevel">-</div>
                    <div class="stat-label">مستوى التهديد</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="activeSessions">-</div>
                    <div class="stat-label">جلسات نشطة</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="blockedIps">-</div>
                    <div class="stat-label">IP محظورة</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="trustScore">-</div>
                    <div class="stat-label">نقاط الثقة</div>
                </div>
            </div>
            
            <div class="test-section">
                <h2>🔍 فحص التهديدات</h2>
                <div class="test-form">
                    <select id="threatType">
                        <option value="all">جميع التهديدات</option>
                        <option value="xss">XSS</option>
                        <option value="sql_injection">SQL Injection</option>
                        <option value="path_traversal">Path Traversal</option>
                        <option value="command_injection">Command Injection</option>
                    </select>
                    <textarea id="threatInput" placeholder="أدخل النص للفحص..." rows="3"></textarea>
                    <button onclick="scanThreat()">🔍 فحص التهديدات</button>
                </div>
                <div id="threatResult" class="result"></div>
            </div>
            
            <div class="test-section">
                <h2>🔐 التشفير وفك التشفير</h2>
                <div class="test-form">
                    <textarea id="encryptInput" placeholder="أدخل النص للتشفير..." rows="2"></textarea>
                    <button onclick="encryptData()">🔒 تشفير</button>
                    <textarea id="encryptedOutput" placeholder="النص المشفر..." rows="2" readonly></textarea>
                    <button onclick="decryptData()">🔓 فك التشفير</button>
                    <textarea id="decryptedOutput" placeholder="النص بعد فك التشفير..." rows="2" readonly></textarea>
                </div>
            </div>
            
            <div class="test-section">
                <h2>🛡️ اختبار المصادقة</h2>
                <div class="test-form">
                    <input type="text" id="username" placeholder="اسم المستخدم">
                    <input type="password" id="password" placeholder="كلمة المرور">
                    <input type="text" id="mfaCode" placeholder="رمز MFA (123456)">
                    <button onclick="testAuth()">🔑 تسجيل الدخول</button>
                </div>
                <div id="authResult" class="result"></div>
            </div>
        </div>
        
        <script>
            // تحديث لوحة المعلومات
            function updateDashboard() {
                fetch('/fortress/v2/dashboard')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('threatLevel').textContent = 
                            data.system_info.threat_level;
                        document.getElementById('activeSessions').textContent = 
                            data.statistics.active_sessions;
                        document.getElementById('blockedIps').textContent = 
                            data.statistics.blocked_ips;
                        document.getElementById('trustScore').textContent = 
                            Math.round(data.statistics.average_trust_score);
                    })
                    .catch(error => console.error('Dashboard error:', error));
            }
            
            // فحص التهديدات
            function scanThreat() {
                const type = document.getElementById('threatType').value;
                const input = document.getElementById('threatInput').value;
                
                fetch('/fortress/v2/threat-scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ type: type, input: input })
                })
                .then(response => response.json())
                .then(data => {
                    const result = document.getElementById('threatResult');
                    result.style.display = 'block';
                    
                    if (data.threat_detected) {
                        result.className = 'result danger';
                        result.innerHTML = '🚨 تم اكتشاف تهديد!<br>' + 
                            'النوع: ' + data.threat_type + '<br>' +
                            'التوصية: ' + data.recommendation;
                    } else {
                        result.className = 'result success';
                        result.innerHTML = '✅ آمن!<br>لم يتم اكتشاف أي تهديدات';
                    }
                })
                .catch(error => {
                    console.error('Threat scan error:', error);
                });
            }
            
            // تشفير البيانات
            function encryptData() {
                const input = document.getElementById('encryptInput').value;
                
                fetch('/fortress/v2/encrypt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: input })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('encryptedOutput').value = data.encrypted;
                    }
                })
                .catch(error => console.error('Encryption error:', error));
            }
            
            // فك التشفير
            function decryptData() {
                const encrypted = document.getElementById('encryptedOutput').value;
                
                fetch('/fortress/v2/decrypt', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ encrypted: encrypted })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('decryptedOutput').value = data.decrypted;
                    }
                })
                .catch(error => console.error('Decryption error:', error));
            }
            
            // اختبار المصادقة
            function testAuth() {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const mfaCode = document.getElementById('mfaCode').value;
                
                fetch('/fortress/v2/authenticate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: username,
                        password: password,
                        mfa_code: mfaCode
                    })
                })
                .then(response => response.json())
                .then(data => {
                    const result = document.getElementById('authResult');
                    result.style.display = 'block';
                    
                    if (data.success) {
                        result.className = 'result success';
                        result.innerHTML = '✅ تم تسجيل الدخول بنجاح!<br>' +
                            'Session: ' + data.session_token + '<br>' +
                            'Trust Score: ' + data.trust_score;
                    } else {
                        result.className = 'result danger';
                        result.innerHTML = '❌ فشل تسجيل الدخول<br>' + data.message;
                    }
                })
                .catch(error => console.error('Auth error:', error));
            }
            
            // تحديث لوحة المعلومات كل 5 ثواني
            updateDashboard();
            setInterval(updateDashboard, 5000);
        </script>
    </body>
    </html>
    '''


@advanced_fortress_bp.route('/emergency-status')
@require_advanced_security(ThreatLevel.EMERGENCY)
def emergency_status():
    """حالة الطوارئ - يتطلب أعلى مستوى أمان"""
    return jsonify({
        'status': 'EMERGENCY',
        'message': 'System in emergency mode',
        'threat_level': advanced_security_ministry.threat_level.name,
        'active_threats': len([e for e in advanced_security_ministry.security_events
                              if e.threat_level == ThreatLevel.CRITICAL])
    })