"""
🛡️ API Routes - مسارات API الأمنية
يوفر نقاط نهاية API للنظام الأمني المتقدم
"""

from flask import Blueprint, jsonify, request, session
from datetime import datetime
import hashlib
import json
import os

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# System status
SYSTEM_STATUS = {
    'version': '3.0.0',
    'status': 'operational',
    'security_level': 'high',
    'last_update': datetime.utcnow().isoformat()
}

@api_bp.route('/system/status', methods=['GET'])
def system_status():
    """
    الحصول على حالة النظام
    """
    try:
        # Update timestamp
        SYSTEM_STATUS['last_update'] = datetime.utcnow().isoformat()
        
        # Add session info if available
        if 'user_id' in session:
            SYSTEM_STATUS['session_active'] = True
            SYSTEM_STATUS['user_authenticated'] = True
        else:
            SYSTEM_STATUS['session_active'] = False
            SYSTEM_STATUS['user_authenticated'] = False
        
        # Add security metrics
        SYSTEM_STATUS['security_metrics'] = {
            'threats_blocked': session.get('threats_blocked', 0),
            'requests_processed': session.get('requests_processed', 0),
            'active_sessions': session.get('active_sessions', 0)
        }
        
        return jsonify(SYSTEM_STATUS), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to get system status',
            'message': str(e)
        }), 500

@api_bp.route('/security/verify', methods=['POST'])
def verify_security():
    """
    التحقق من الأمان
    """
    try:
        data = request.get_json()
        
        # Verify required fields
        required_fields = ['token', 'fingerprint', 'timestamp']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'valid': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Verify timestamp (not older than 5 minutes)
        try:
            timestamp = int(data['timestamp'])
            current_time = int(datetime.now().timestamp() * 1000)
            if abs(current_time - timestamp) > 300000:  # 5 minutes
                return jsonify({
                    'valid': False,
                    'error': 'Request timestamp is too old'
                }), 401
        except:
            return jsonify({
                'valid': False,
                'error': 'Invalid timestamp'
            }), 400
        
        # Verify token (simplified for demo)
        expected_token = hashlib.sha256(
            f"{data['fingerprint']}{timestamp}".encode()
        ).hexdigest()[:16]
        
        if data['token'] == expected_token:
            return jsonify({
                'valid': True,
                'message': 'Security verification successful'
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': 'Invalid security token'
            }), 401
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': 'Verification failed',
            'message': str(e)
        }), 500

@api_bp.route('/security/token', methods=['GET'])
def get_security_token():
    """
    الحصول على رمز أمان جديد
    """
    try:
        # Generate secure token
        token = hashlib.sha256(os.urandom(32)).hexdigest()[:32]
        
        # Store in session
        session['security_token'] = token
        session['token_timestamp'] = datetime.now().isoformat()
        
        return jsonify({
            'token': token,
            'expires_in': 3600,  # 1 hour
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate token',
            'message': str(e)
        }), 500

@api_bp.route('/security/csrf', methods=['GET'])
def get_csrf_token():
    """
    الحصول على CSRF token
    """
    try:
        # Generate CSRF token
        if 'csrf_token' not in session:
            session['csrf_token'] = hashlib.sha256(os.urandom(32)).hexdigest()[:32]
        
        return jsonify({
            'csrf_token': session['csrf_token'],
            'timestamp': int(datetime.now().timestamp() * 1000)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate CSRF token',
            'message': str(e)
        }), 500

@api_bp.route('/security/threat', methods=['POST'])
def report_threat():
    """
    الإبلاغ عن تهديد أمني
    """
    try:
        data = request.get_json()
        
        # Log threat
        threat_info = {
            'type': data.get('type', 'unknown'),
            'severity': data.get('severity', 'medium'),
            'message': data.get('message', ''),
            'source': data.get('source', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'ip': request.remote_addr,
            'user_agent': request.user_agent.string
        }
        
        # Increment threat counter
        session['threats_blocked'] = session.get('threats_blocked', 0) + 1
        
        # Log to console (in production, log to file/database)
        print(f"🚨 Security Threat Detected: {threat_info}")
        
        # Take action based on severity
        if threat_info['severity'] == 'critical':
            # In production: trigger emergency protocol
            response = {
                'action': 'emergency_protocol',
                'message': 'Critical threat detected. Emergency protocol activated.'
            }
        elif threat_info['severity'] == 'high':
            response = {
                'action': 'enhanced_monitoring',
                'message': 'High severity threat detected. Enhanced monitoring enabled.'
            }
        else:
            response = {
                'action': 'logged',
                'message': 'Threat has been logged and will be monitored.'
            }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to process threat report',
            'message': str(e)
        }), 500

@api_bp.route('/security/session', methods=['GET'])
def get_session_info():
    """
    الحصول على معلومات الجلسة
    """
    try:
        session_info = {
            'id': session.get('session_id', None),
            'authenticated': 'user_id' in session,
            'created': session.get('created', None),
            'last_activity': session.get('last_activity', datetime.now().isoformat()),
            'trust_score': session.get('trust_score', 50),
            'threats_blocked': session.get('threats_blocked', 0),
            'requests_processed': session.get('requests_processed', 0)
        }
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        session['requests_processed'] = session.get('requests_processed', 0) + 1
        
        return jsonify(session_info), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to get session info',
            'message': str(e)
        }), 500

@api_bp.route('/security/validate', methods=['POST'])
def validate_request():
    """
    التحقق من صحة الطلب
    """
    try:
        data = request.get_json()
        
        # Check CSRF token
        if 'csrf_token' in data:
            if data['csrf_token'] != session.get('csrf_token'):
                return jsonify({
                    'valid': False,
                    'error': 'Invalid CSRF token'
                }), 403
        
        # Check security headers
        required_headers = ['X-Requested-With', 'X-Nonce']
        missing_headers = []
        
        for header in required_headers:
            if header not in request.headers:
                missing_headers.append(header)
        
        if missing_headers:
            return jsonify({
                'valid': False,
                'error': 'Missing security headers',
                'missing': missing_headers
            }), 400
        
        # Validate nonce
        nonce = request.headers.get('X-Nonce')
        if len(nonce) < 32:
            return jsonify({
                'valid': False,
                'error': 'Invalid nonce'
            }), 400
        
        # All checks passed
        return jsonify({
            'valid': True,
            'message': 'Request validation successful',
            'trust_score': session.get('trust_score', 50)
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': 'Validation failed',
            'message': str(e)
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    فحص صحة API
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0'
    }), 200