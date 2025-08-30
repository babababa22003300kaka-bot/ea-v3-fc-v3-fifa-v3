"""
🏰 Fortress Routes - المسارات المحمية
نظام مسارات محمي بالكامل مع Zero Trust
"""

from flask import Blueprint, render_template, request, jsonify, session
from functools import wraps
import logging

# استيراد وزارة الأمان
try:
    from ministries.security_ministry import security_ministry, zero_trust
    SECURITY_ENABLED = True
except ImportError:
    SECURITY_ENABLED = False
    security_ministry = None
    zero_trust = None

# إنشاء Blueprint
fortress_bp = Blueprint('fortress', __name__, url_prefix='/fortress')

# إعداد نظام السجلات
logger = logging.getLogger('FortressRoutes')


def require_fortress_security(f):
    """Decorator للتحقق من الأمان قبل الوصول للمسار"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SECURITY_ENABLED:
            return jsonify({'error': 'Security system not available'}), 503
            
        # التحقق من الجلسة
        user_id = session.get('user_id')
        token = session.get('security_token')
        
        if not user_id or not token:
            # توليد جلسة جديدة للمستخدمين الجدد
            import uuid
            user_id = str(uuid.uuid4())
            token = security_ministry.generate_session_token(user_id)
            session['user_id'] = user_id
            session['security_token'] = token
            
        # التحقق من صحة الجلسة
        if not security_ministry.validate_session(user_id, token):
            return jsonify({'error': 'Invalid session'}), 401
            
        # التحقق من حد المعدل
        ip_address = request.remote_addr
        if not security_ministry.check_rate_limit(ip_address):
            return jsonify({'error': 'Rate limit exceeded'}), 429
            
        # التحقق من IP المحظور
        if security_ministry.is_ip_blocked(ip_address):
            return jsonify({'error': 'Access denied'}), 403
            
        return f(*args, **kwargs)
    return decorated_function


@fortress_bp.route('/')
@require_fortress_security
def fortress_home():
    """الصفحة الرئيسية المحمية"""
    return render_template('fortress/secure_index.html')


@fortress_bp.route('/security-status')
@require_fortress_security
def security_status():
    """الحصول على حالة النظام الأمني"""
    if not SECURITY_ENABLED:
        return jsonify({
            'status': 'disabled',
            'message': 'Security system not available'
        })
        
    user_id = session.get('user_id')
    trust_score = security_ministry.trust_scores.get(user_id, 50)
    
    return jsonify({
        'status': 'active',
        'trust_score': trust_score,
        'security_level': 'maximum',
        'features': {
            'encryption': 'AES-256-GCM',
            'zero_trust': True,
            'threat_detection': True,
            'ai_protection': True
        },
        'stats': {
            'active_sessions': len(security_ministry.session_keys),
            'blocked_ips': len(security_ministry.blocked_ips),
            'security_events': len(security_ministry.security_events)
        }
    })


@fortress_bp.route('/validate', methods=['POST'])
@require_fortress_security
def validate_secure_data():
    """التحقق من البيانات بنظام Zero Trust"""
    if not SECURITY_ENABLED:
        return jsonify({
            'success': False,
            'message': 'Security system not available'
        }), 503
        
    try:
        # الحصول على البيانات
        data = request.form.to_dict()
        
        # إعداد بيانات الطلب للتحقق
        request_data = {
            'user_id': session.get('user_id'),
            'token': session.get('security_token'),
            'ip_address': request.remote_addr,
            'data': data,
            'required_role': 'user',
            'user_role': session.get('user_role', 'user'),
            'min_trust_score': 30
        }
        
        # التحقق بنظام Zero Trust
        is_valid, message = zero_trust.validate_request(request_data)
        
        if not is_valid:
            # تسجيل محاولة فاشلة
            user_id = session.get('user_id')
            security_ministry.calculate_trust_score(user_id, 'invalid_request')
            
            return jsonify({
                'success': False,
                'message': f'Validation failed: {message}'
            }), 400
            
        # معالجة البيانات (هنا يمكن إضافة المنطق الخاص بك)
        whatsapp = data.get('whatsapp', '')
        payment_method = data.get('payment_method', '')
        payment_details = data.get('payment_details', '')
        
        # التحقق من الواتساب
        if not whatsapp or not whatsapp.startswith('+'):
            return jsonify({
                'success': False,
                'message': 'رقم الواتساب غير صحيح'
            }), 400
            
        # تحديث نقاط الثقة للمستخدم
        user_id = session.get('user_id')
        security_ministry.calculate_trust_score(user_id, 'valid_request')
        
        # إرجاع النجاح
        return jsonify({
            'success': True,
            'message': 'تم التحقق بنجاح',
            'data': {
                'whatsapp': whatsapp,
                'payment_method': payment_method,
                'trust_score': security_ministry.trust_scores.get(user_id, 50)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in validation: {e}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ في المعالجة'
        }), 500


@fortress_bp.route('/security-report')
@require_fortress_security
def security_report():
    """الحصول على تقرير أمني شامل"""
    if not SECURITY_ENABLED:
        return jsonify({
            'error': 'Security system not available'
        }), 503
        
    # التحقق من الصلاحيات (للمسؤولين فقط)
    user_role = session.get('user_role', 'user')
    if user_role != 'admin':
        return jsonify({
            'error': 'Insufficient permissions'
        }), 403
        
    report = security_ministry.get_security_report()
    return jsonify(report)


@fortress_bp.route('/test-security', methods=['GET', 'POST'])
@require_fortress_security
def test_security():
    """صفحة اختبار النظام الأمني"""
    if request.method == 'POST':
        # اختبار أنواع مختلفة من الهجمات
        test_type = request.form.get('test_type')
        test_data = request.form.get('test_data', '')
        
        results = {
            'test_type': test_type,
            'blocked': False,
            'reason': ''
        }
        
        if test_type == 'sql_injection':
            if security_ministry.detect_sql_injection(test_data):
                results['blocked'] = True
                results['reason'] = 'SQL Injection detected and blocked'
                
        elif test_type == 'xss':
            if security_ministry.detect_xss(test_data):
                results['blocked'] = True
                results['reason'] = 'XSS attempt detected and blocked'
                
        elif test_type == 'rate_limit':
            # محاولة تجاوز حد المعدل
            ip = request.remote_addr
            for _ in range(101):
                if not security_ministry.check_rate_limit(ip + '_test'):
                    results['blocked'] = True
                    results['reason'] = 'Rate limit exceeded'
                    break
                    
        return jsonify(results)
        
    # عرض صفحة الاختبار
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <title>اختبار النظام الأمني</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #1a1a2e;
                color: #fff;
                padding: 20px;
            }
            .test-container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 20px;
            }
            h1 {
                text-align: center;
                color: #00d4ff;
            }
            .test-form {
                margin: 20px 0;
            }
            select, input, button {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                background: rgba(255,255,255,0.1);
                border: 1px solid #00d4ff;
                color: #fff;
                border-radius: 5px;
            }
            button {
                background: #00d4ff;
                color: #000;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover {
                background: #0099cc;
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
        </style>
    </head>
    <body>
        <div class="test-container">
            <h1>🛡️ اختبار النظام الأمني</h1>
            <div class="test-form">
                <select id="testType">
                    <option value="">اختر نوع الاختبار</option>
                    <option value="sql_injection">SQL Injection</option>
                    <option value="xss">XSS Attack</option>
                    <option value="rate_limit">Rate Limiting</option>
                </select>
                <input type="text" id="testData" placeholder="أدخل بيانات الاختبار">
                <button onclick="runTest()">🚀 تشغيل الاختبار</button>
            </div>
            <div id="result" class="result"></div>
        </div>
        
        <script>
            function runTest() {
                const testType = document.getElementById('testType').value;
                const testData = document.getElementById('testData').value;
                const resultDiv = document.getElementById('result');
                
                if (!testType) {
                    alert('اختر نوع الاختبار أولاً');
                    return;
                }
                
                const formData = new FormData();
                formData.append('test_type', testType);
                formData.append('test_data', testData);
                
                fetch('/fortress/test-security', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    resultDiv.style.display = 'block';
                    if (data.blocked) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = '✅ النظام يعمل بنجاح!<br>' + data.reason;
                    } else {
                        resultDiv.className = 'result danger';
                        resultDiv.innerHTML = '❌ لم يتم حظر الهجوم';
                    }
                })
                .catch(error => {
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result danger';
                    resultDiv.innerHTML = '❌ خطأ في الاختبار: ' + error;
                });
            }
        </script>
    </body>
    </html>
    '''