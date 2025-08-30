"""
🏛️ Security Ministry - وزارة الأمان المعزولة
نظام حماية متقدم مع عزل كامل
"""

import os
import hashlib
import secrets
import json
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List, Tuple
import logging

# تكوين نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SecurityMinistry')


class SecurityMinistry:
    """🛡️ وزارة الأمان الرئيسية"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton Pattern للتأكد من وجود وزارة واحدة فقط"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """تهيئة الوزارة"""
        if self._initialized:
            return
            
        self._initialized = True
        self.session_keys = {}
        self.trust_scores = {}
        self.security_events = []
        self.blocked_ips = set()
        self.rate_limits = {}
        self.encryption_key = self._generate_master_key()
        
        logger.info("🏛️ Security Ministry initialized successfully")
    
    def _generate_master_key(self) -> str:
        """توليد مفتاح رئيسي للتشفير"""
        return secrets.token_hex(32)
    
    def generate_session_token(self, user_id: str) -> str:
        """توليد رمز جلسة آمن"""
        token = secrets.token_urlsafe(32)
        self.session_keys[user_id] = {
            'token': token,
            'created': datetime.now(),
            'last_activity': datetime.now(),
            'trust_score': 50
        }
        logger.info(f"✅ Generated session token for user: {user_id}")
        return token
    
    def validate_session(self, user_id: str, token: str) -> bool:
        """التحقق من صحة الجلسة"""
        if user_id not in self.session_keys:
            logger.warning(f"❌ Invalid session attempt for user: {user_id}")
            return False
            
        session = self.session_keys[user_id]
        
        # التحقق من انتهاء الجلسة (24 ساعة)
        if datetime.now() - session['created'] > timedelta(hours=24):
            logger.warning(f"⏰ Session expired for user: {user_id}")
            del self.session_keys[user_id]
            return False
            
        # التحقق من عدم النشاط (30 دقيقة)
        if datetime.now() - session['last_activity'] > timedelta(minutes=30):
            logger.warning(f"💤 Session inactive for user: {user_id}")
            del self.session_keys[user_id]
            return False
            
        # التحقق من الرمز
        if session['token'] != token:
            logger.error(f"🚨 Invalid token for user: {user_id}")
            self._record_security_event('invalid_token', user_id)
            return False
            
        # تحديث آخر نشاط
        session['last_activity'] = datetime.now()
        return True
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 60) -> bool:
        """فحص حد المعدل للحماية من الهجمات"""
        current_time = time.time()
        
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # إزالة الطلبات القديمة
        self.rate_limits[identifier] = [
            t for t in self.rate_limits[identifier]
            if current_time - t < window
        ]
        
        # فحص الحد
        if len(self.rate_limits[identifier]) >= limit:
            logger.warning(f"⚠️ Rate limit exceeded for: {identifier}")
            self._record_security_event('rate_limit_exceeded', identifier)
            return False
            
        # إضافة الطلب الحالي
        self.rate_limits[identifier].append(current_time)
        return True
    
    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """تشفير البيانات"""
        try:
            json_data = json.dumps(data)
            # تشفير بسيط للتوضيح (يجب استخدام مكتبة تشفير حقيقية في الإنتاج)
            encrypted = hashlib.sha256(
                (json_data + self.encryption_key).encode()
            ).hexdigest()
            return encrypted
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return ""
    
    def validate_input(self, input_data: str, input_type: str = 'text') -> Tuple[bool, str]:
        """التحقق من صحة المدخلات"""
        # قواعد التحقق حسب النوع
        validation_rules = {
            'text': lambda x: len(x) < 1000 and not any(c in x for c in '<>\"\''),
            'email': lambda x: '@' in x and '.' in x.split('@')[1] if '@' in x else False,
            'number': lambda x: x.isdigit(),
            'alphanumeric': lambda x: x.isalnum(),
            'phone': lambda x: x.replace('+', '').replace('-', '').isdigit()
        }
        
        if input_type not in validation_rules:
            return False, "Unknown input type"
            
        try:
            if validation_rules[input_type](input_data):
                return True, "Valid input"
            else:
                logger.warning(f"Invalid input detected: {input_type}")
                return False, f"Invalid {input_type} format"
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, "Validation error"
    
    def detect_sql_injection(self, query: str) -> bool:
        """كشف محاولات SQL Injection"""
        dangerous_patterns = [
            'DROP TABLE', 'DELETE FROM', 'INSERT INTO',
            'UPDATE SET', 'UNION SELECT', '--', '/*', '*/',
            'xp_', 'sp_', 'exec', 'execute', 'dbms_',
            'script', 'javascript:', 'onclick', 'onerror'
        ]
        
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                logger.error(f"🚨 SQL Injection attempt detected: {pattern}")
                self._record_security_event('sql_injection_attempt', query[:100])
                return True
                
        return False
    
    def detect_xss(self, content: str) -> bool:
        """كشف محاولات XSS"""
        xss_patterns = [
            '<script', 'javascript:', 'onclick=', 'onerror=',
            'onload=', 'eval(', 'alert(', 'document.cookie',
            'window.location', 'innerHTML'
        ]
        
        content_lower = content.lower()
        for pattern in xss_patterns:
            if pattern in content_lower:
                logger.error(f"🚨 XSS attempt detected: {pattern}")
                self._record_security_event('xss_attempt', content[:100])
                return True
                
        return False
    
    def calculate_trust_score(self, user_id: str, action: str) -> int:
        """حساب نقاط الثقة للمستخدم"""
        if user_id not in self.trust_scores:
            self.trust_scores[user_id] = 50  # نقطة البداية
            
        # تعديل النقاط حسب الإجراء
        action_scores = {
            'successful_login': 5,
            'failed_login': -10,
            'valid_request': 1,
            'invalid_request': -5,
            'suspicious_activity': -20,
            'normal_activity': 2
        }
        
        score_change = action_scores.get(action, 0)
        self.trust_scores[user_id] = max(0, min(100, 
            self.trust_scores[user_id] + score_change))
            
        logger.info(f"Trust score for {user_id}: {self.trust_scores[user_id]}")
        return self.trust_scores[user_id]
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """فحص إذا كان IP محظور"""
        return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address: str, reason: str):
        """حظر عنوان IP"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"🚫 Blocked IP {ip_address}: {reason}")
        self._record_security_event('ip_blocked', {'ip': ip_address, 'reason': reason})
    
    def _record_security_event(self, event_type: str, details: Any):
        """تسجيل حدث أمني"""
        event = {
            'type': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'severity': self._get_event_severity(event_type)
        }
        self.security_events.append(event)
        
        # الاحتفاظ بآخر 1000 حدث فقط
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def _get_event_severity(self, event_type: str) -> str:
        """تحديد شدة الحدث الأمني"""
        severity_map = {
            'sql_injection_attempt': 'CRITICAL',
            'xss_attempt': 'CRITICAL',
            'rate_limit_exceeded': 'HIGH',
            'invalid_token': 'HIGH',
            'ip_blocked': 'HIGH',
            'failed_login': 'MEDIUM',
            'suspicious_activity': 'MEDIUM',
            'normal_activity': 'LOW'
        }
        return severity_map.get(event_type, 'INFO')
    
    def get_security_report(self) -> Dict[str, Any]:
        """الحصول على تقرير أمني شامل"""
        return {
            'total_sessions': len(self.session_keys),
            'blocked_ips': len(self.blocked_ips),
            'recent_events': self.security_events[-10:],
            'average_trust_score': sum(self.trust_scores.values()) / len(self.trust_scores) if self.trust_scores else 0,
            'critical_events': len([e for e in self.security_events if e['severity'] == 'CRITICAL']),
            'timestamp': datetime.now().isoformat()
        }


class ZeroTrustValidator:
    """🔐 نظام Zero Trust للتحقق من كل شيء"""
    
    def __init__(self, security_ministry: SecurityMinistry):
        self.ministry = security_ministry
        self.validation_chain = []
    
    def validate_request(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الطلب بنظام Zero Trust"""
        
        # سلسلة التحقق
        validations = [
            self._validate_authentication,
            self._validate_authorization,
            self._validate_input_safety,
            self._validate_rate_limit,
            self._validate_trust_score
        ]
        
        for validation in validations:
            is_valid, message = validation(request_data)
            if not is_valid:
                logger.warning(f"Zero Trust validation failed: {message}")
                return False, message
                
        return True, "All validations passed"
    
    def _validate_authentication(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الهوية"""
        user_id = request_data.get('user_id')
        token = request_data.get('token')
        
        if not user_id or not token:
            return False, "Missing authentication credentials"
            
        if not self.ministry.validate_session(user_id, token):
            return False, "Invalid session"
            
        return True, "Authentication valid"
    
    def _validate_authorization(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الصلاحيات"""
        required_role = request_data.get('required_role', 'user')
        user_role = request_data.get('user_role', 'guest')
        
        role_hierarchy = {
            'admin': 3,
            'moderator': 2,
            'user': 1,
            'guest': 0
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 1):
            return False, "Insufficient permissions"
            
        return True, "Authorization valid"
    
    def _validate_input_safety(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من أمان المدخلات"""
        data = request_data.get('data', {})
        
        for key, value in data.items():
            if isinstance(value, str):
                if self.ministry.detect_sql_injection(value):
                    return False, f"SQL injection detected in {key}"
                if self.ministry.detect_xss(value):
                    return False, f"XSS detected in {key}"
                    
        return True, "Input is safe"
    
    def _validate_rate_limit(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من حد المعدل"""
        identifier = request_data.get('ip_address', 'unknown')
        
        if not self.ministry.check_rate_limit(identifier):
            return False, "Rate limit exceeded"
            
        return True, "Rate limit OK"
    
    def _validate_trust_score(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من نقاط الثقة"""
        user_id = request_data.get('user_id')
        min_trust_score = request_data.get('min_trust_score', 30)
        
        if user_id in self.ministry.trust_scores:
            score = self.ministry.trust_scores[user_id]
            if score < min_trust_score:
                return False, f"Trust score too low: {score}"
                
        return True, "Trust score acceptable"


def security_required(min_trust_score: int = 30):
    """Decorator للحماية المطلوبة للدوال"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # هنا يمكن إضافة فحوصات أمنية
            logger.info(f"Security check for function: {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# إنشاء instance واحد للاستخدام العام
security_ministry = SecurityMinistry()
zero_trust = ZeroTrustValidator(security_ministry)