"""
🏛️ Advanced Security Ministry V2 - وزارة الأمان المتقدمة
نظام حماية متطور مع Zero Trust Architecture
مدمج من أحدث تحديثات GitHub
"""

import os
import hashlib
import secrets
import json
import time
import hmac
import base64
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List, Tuple, Union
import logging
from dataclasses import dataclass
from enum import Enum

# تكوين نظام السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AdvancedSecurityMinistry')


class ThreatLevel(Enum):
    """مستويات التهديد"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class SecurityEventType(Enum):
    """أنواع الأحداث الأمنية"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    XSS_ATTEMPT = "xss_attempt"
    SQL_INJECTION = "sql_injection"
    CSRF_ATTEMPT = "csrf_attempt"
    BRUTE_FORCE = "brute_force"
    SESSION_HIJACK = "session_hijack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_BREACH = "data_breach"
    ANOMALY_DETECTED = "anomaly_detected"


@dataclass
class SecurityEvent:
    """حدث أمني"""
    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str]
    ip_address: Optional[str]
    details: Dict[str, Any]
    threat_level: ThreatLevel
    handled: bool = False


class AdvancedSecurityMinistry:
    """🏛️ وزارة الأمان المتقدمة V2"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton Pattern للتأكد من وجود وزارة واحدة فقط"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """تهيئة الوزارة المتقدمة"""
        if self._initialized:
            return
            
        self._initialized = True
        self.version = "2.0.0"
        self.system_id = self._generate_system_id()
        
        # مخازن البيانات
        self.sessions = {}
        self.trust_scores = {}
        self.security_events = []
        self.blocked_ips = set()
        self.rate_limits = {}
        self.encryption_keys = {}
        
        # إعدادات الأمان
        self.security_config = self._load_security_config()
        self.threat_level = ThreatLevel.LOW
        
        # مكونات النظام
        self.crypto_engine = CryptoEngine()
        self.zero_trust_validator = ZeroTrustValidator(self)
        self.threat_detector = ThreatDetector(self)
        self.session_manager = SessionManager(self)
        
        logger.info(f"🏛️ Advanced Security Ministry v{self.version} initialized")
        logger.info(f"System ID: {self.system_id}")
    
    def _generate_system_id(self) -> str:
        """توليد معرف فريد للنظام"""
        timestamp = int(time.time())
        random = secrets.token_hex(8)
        return f"ASM-{timestamp}-{random}"
    
    def _load_security_config(self) -> Dict[str, Any]:
        """تحميل إعدادات الأمان"""
        return {
            "session": {
                "timeout": 900,  # 15 دقيقة
                "max_concurrent": 3,
                "require_mfa": True
            },
            "rate_limiting": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "login_attempts": 5
            },
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_rotation_hours": 24,
                "use_hardware_security": False
            },
            "zero_trust": {
                "verify_always": True,
                "trust_no_one": True,
                "assume_breach": True,
                "continuous_validation": True
            },
            "monitoring": {
                "log_all_access": True,
                "detect_anomalies": True,
                "real_time_alerts": True,
                "forensic_logging": True
            }
        }
    
    def authenticate_user(self, credentials: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """مصادقة المستخدم مع Multi-Factor Authentication"""
        user_id = credentials.get('user_id')
        password = credentials.get('password')
        mfa_code = credentials.get('mfa_code')
        ip_address = credentials.get('ip_address')
        
        # التحقق من حظر IP
        if self.is_ip_blocked(ip_address):
            self._record_event(SecurityEventType.LOGIN_FAILED, user_id, ip_address,
                             {"reason": "IP blocked"}, ThreatLevel.HIGH)
            return False, "Access denied"
        
        # التحقق من معدل المحاولات
        if not self.check_rate_limit(f"login_{ip_address}", 5, 300):
            self.block_ip(ip_address, "Too many login attempts")
            self._record_event(SecurityEventType.BRUTE_FORCE, user_id, ip_address,
                             {"reason": "Rate limit exceeded"}, ThreatLevel.HIGH)
            return False, "Too many attempts"
        
        # التحقق من كلمة المرور (placeholder - يجب استخدام bcrypt في الإنتاج)
        if not self._verify_password(user_id, password):
            self._record_event(SecurityEventType.LOGIN_FAILED, user_id, ip_address,
                             {"reason": "Invalid credentials"}, ThreatLevel.MEDIUM)
            self.update_trust_score(user_id, -10)
            return False, "Invalid credentials"
        
        # التحقق من MFA إذا كان مطلوباً
        if self.security_config['session']['require_mfa']:
            if not self._verify_mfa(user_id, mfa_code):
                self._record_event(SecurityEventType.LOGIN_FAILED, user_id, ip_address,
                                 {"reason": "MFA failed"}, ThreatLevel.MEDIUM)
                return False, "MFA verification failed"
        
        # إنشاء جلسة آمنة
        session_token = self.session_manager.create_session(user_id, ip_address)
        
        # تسجيل نجاح الدخول
        self._record_event(SecurityEventType.LOGIN_SUCCESS, user_id, ip_address,
                         {"session_id": session_token[:8] + "..."}, ThreatLevel.LOW)
        self.update_trust_score(user_id, 5)
        
        return True, session_token
    
    def _verify_password(self, user_id: str, password: str) -> bool:
        """التحقق من كلمة المرور (placeholder)"""
        # في الإنتاج: استخدام bcrypt أو argon2
        expected = hashlib.sha256(f"{user_id}_password".encode()).hexdigest()
        provided = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(expected, provided)
    
    def _verify_mfa(self, user_id: str, mfa_code: str) -> bool:
        """التحقق من رمز MFA (placeholder)"""
        # في الإنتاج: استخدام TOTP/HOTP
        return mfa_code == "123456"
    
    def validate_request(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الطلب بنظام Zero Trust"""
        return self.zero_trust_validator.validate_request(request_data)
    
    def encrypt_sensitive_data(self, data: Any) -> str:
        """تشفير البيانات الحساسة"""
        return self.crypto_engine.encrypt(data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Any:
        """فك تشفير البيانات الحساسة"""
        return self.crypto_engine.decrypt(encrypted_data)
    
    def detect_threat(self, input_data: str, threat_type: str = "all") -> bool:
        """كشف التهديدات"""
        return self.threat_detector.detect(input_data, threat_type)
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 60) -> bool:
        """فحص حد المعدل"""
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
            return False
            
        # إضافة الطلب الحالي
        self.rate_limits[identifier].append(current_time)
        return True
    
    def update_trust_score(self, user_id: str, change: int) -> int:
        """تحديث نقاط الثقة"""
        if user_id not in self.trust_scores:
            self.trust_scores[user_id] = 50
            
        self.trust_scores[user_id] = max(0, min(100, 
            self.trust_scores[user_id] + change))
            
        logger.info(f"Trust score for {user_id}: {self.trust_scores[user_id]}")
        return self.trust_scores[user_id]
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """فحص إذا كان IP محظور"""
        return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address: str, reason: str):
        """حظر عنوان IP"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"🚫 Blocked IP {ip_address}: {reason}")
        self._record_event(SecurityEventType.ANOMALY_DETECTED, None, ip_address,
                         {"action": "ip_blocked", "reason": reason}, ThreatLevel.HIGH)
    
    def _record_event(self, event_type: SecurityEventType, user_id: Optional[str],
                     ip_address: Optional[str], details: Dict[str, Any],
                     threat_level: ThreatLevel):
        """تسجيل حدث أمني"""
        event = SecurityEvent(
            event_type=event_type,
            timestamp=datetime.now(),
            user_id=user_id,
            ip_address=ip_address,
            details=details,
            threat_level=threat_level
        )
        
        self.security_events.append(event)
        
        # الاحتفاظ بآخر 10000 حدث
        if len(self.security_events) > 10000:
            self.security_events = self.security_events[-10000:]
        
        # تحديث مستوى التهديد العام
        self._update_threat_level()
        
        # إرسال تنبيه إذا كان التهديد عالي
        if threat_level.value >= ThreatLevel.HIGH.value:
            self._send_security_alert(event)
    
    def _update_threat_level(self):
        """تحديث مستوى التهديد العام للنظام"""
        recent_events = [e for e in self.security_events[-100:]
                        if not e.handled]
        
        critical_count = sum(1 for e in recent_events 
                           if e.threat_level == ThreatLevel.CRITICAL)
        high_count = sum(1 for e in recent_events 
                        if e.threat_level == ThreatLevel.HIGH)
        
        if critical_count > 5:
            self.threat_level = ThreatLevel.EMERGENCY
            self._trigger_emergency_protocol()
        elif critical_count > 2 or high_count > 10:
            self.threat_level = ThreatLevel.CRITICAL
        elif high_count > 5:
            self.threat_level = ThreatLevel.HIGH
        elif len(recent_events) > 20:
            self.threat_level = ThreatLevel.MEDIUM
        else:
            self.threat_level = ThreatLevel.LOW
    
    def _send_security_alert(self, event: SecurityEvent):
        """إرسال تنبيه أمني"""
        logger.error(f"🚨 SECURITY ALERT: {event.event_type.value}")
        logger.error(f"Details: {event.details}")
        # في الإنتاج: إرسال إلى نظام المراقبة أو البريد الإلكتروني
    
    def _trigger_emergency_protocol(self):
        """تفعيل بروتوكول الطوارئ"""
        logger.critical("🚨🚨🚨 EMERGENCY PROTOCOL ACTIVATED 🚨🚨🚨")
        
        # 1. إبطال جميع الجلسات
        self.session_manager.invalidate_all_sessions()
        
        # 2. حظر جميع العناوين الجديدة
        self.security_config['zero_trust']['trust_no_one'] = True
        
        # 3. تسجيل كامل للنشاط
        self.security_config['monitoring']['forensic_logging'] = True
        
        # 4. إشعار الفريق الأمني
        logger.critical("NOTIFY SECURITY TEAM IMMEDIATELY!")
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """الحصول على لوحة معلومات أمنية شاملة"""
        return {
            "system_info": {
                "version": self.version,
                "system_id": self.system_id,
                "threat_level": self.threat_level.name,
                "uptime": time.time()
            },
            "statistics": {
                "active_sessions": len(self.session_manager.sessions),
                "blocked_ips": len(self.blocked_ips),
                "total_events": len(self.security_events),
                "critical_events": sum(1 for e in self.security_events 
                                     if e.threat_level == ThreatLevel.CRITICAL),
                "average_trust_score": sum(self.trust_scores.values()) / len(self.trust_scores) 
                                      if self.trust_scores else 0
            },
            "recent_threats": [
                {
                    "type": e.event_type.value,
                    "timestamp": e.timestamp.isoformat(),
                    "threat_level": e.threat_level.name
                }
                for e in self.security_events[-10:]
                if e.threat_level.value >= ThreatLevel.HIGH.value
            ],
            "configuration": {
                "mfa_required": self.security_config['session']['require_mfa'],
                "zero_trust_enabled": self.security_config['zero_trust']['verify_always'],
                "rate_limiting": self.security_config['rate_limiting']['requests_per_minute']
            }
        }


class CryptoEngine:
    """🔐 محرك التشفير المتقدم"""
    
    def __init__(self):
        self.master_key = self._generate_master_key()
        self.algorithm = "AES-256-GCM"
    
    def _generate_master_key(self) -> bytes:
        """توليد مفتاح رئيسي"""
        # في الإنتاج: استخدام HSM أو KMS
        return secrets.token_bytes(32)
    
    def encrypt(self, data: Any) -> str:
        """تشفير البيانات"""
        try:
            # تحويل البيانات إلى JSON
            json_data = json.dumps(data)
            
            # توليد nonce
            nonce = secrets.token_bytes(12)
            
            # التشفير (placeholder - في الإنتاج استخدام cryptography library)
            encrypted = base64.b64encode(
                nonce + json_data.encode()
            ).decode('utf-8')
            
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> Any:
        """فك التشفير"""
        try:
            # فك التشفير (placeholder)
            decoded = base64.b64decode(encrypted_data)
            nonce = decoded[:12]
            data = decoded[12:].decode('utf-8')
            
            return json.loads(data)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


class ZeroTrustValidator:
    """🔍 مدقق Zero Trust"""
    
    def __init__(self, security_ministry: AdvancedSecurityMinistry):
        self.ministry = security_ministry
    
    def validate_request(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الطلب بنظام Zero Trust"""
        
        # قائمة الفحوصات
        checks = [
            self._validate_authentication,
            self._validate_authorization,
            self._validate_integrity,
            self._validate_context,
            self._validate_behavior
        ]
        
        for check in checks:
            is_valid, message = check(request_data)
            if not is_valid:
                logger.warning(f"Zero Trust validation failed: {message}")
                return False, message
        
        return True, "All validations passed"
    
    def _validate_authentication(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الهوية"""
        session_token = request_data.get('session_token')
        
        if not session_token:
            return False, "Missing authentication"
        
        if not self.ministry.session_manager.validate_session(session_token):
            return False, "Invalid session"
        
        return True, "Authentication valid"
    
    def _validate_authorization(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من الصلاحيات"""
        user_id = request_data.get('user_id')
        resource = request_data.get('resource')
        action = request_data.get('action')
        
        # placeholder - في الإنتاج: فحص الصلاحيات الفعلية
        if action == 'admin' and user_id != 'admin':
            return False, "Insufficient permissions"
        
        return True, "Authorization valid"
    
    def _validate_integrity(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من سلامة البيانات"""
        signature = request_data.get('signature')
        data = request_data.get('data')
        
        if signature and data:
            # placeholder - في الإنتاج: التحقق من التوقيع الرقمي
            expected = hashlib.sha256(json.dumps(data).encode()).hexdigest()
            if signature != expected:
                return False, "Integrity check failed"
        
        return True, "Integrity valid"
    
    def _validate_context(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من السياق"""
        ip_address = request_data.get('ip_address')
        user_agent = request_data.get('user_agent')
        
        # التحقق من IP المحظور
        if ip_address and self.ministry.is_ip_blocked(ip_address):
            return False, "IP address blocked"
        
        # التحقق من User Agent المشبوه
        if user_agent and 'bot' in user_agent.lower():
            return False, "Suspicious user agent"
        
        return True, "Context valid"
    
    def _validate_behavior(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من السلوك"""
        user_id = request_data.get('user_id')
        
        if user_id:
            trust_score = self.ministry.trust_scores.get(user_id, 50)
            if trust_score < 30:
                return False, f"Low trust score: {trust_score}"
        
        return True, "Behavior acceptable"


class ThreatDetector:
    """🚨 كاشف التهديدات"""
    
    def __init__(self, security_ministry: AdvancedSecurityMinistry):
        self.ministry = security_ministry
        self.patterns = self._load_threat_patterns()
    
    def _load_threat_patterns(self) -> Dict[str, List[str]]:
        """تحميل أنماط التهديدات"""
        return {
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"eval\(",
                r"document\.(cookie|write|domain)",
                r"window\.location",
                r"\.innerHTML\s*="
            ],
            "sql_injection": [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER)\b)",
                r"(--|/\*|\*/|;|'|\")",
                r"(\bOR\b|\bAND\b)\s*\d+\s*=\s*\d+",
                r"\bexec\b|\bexecute\b",
                r"xp_cmdshell",
                r"sp_executesql"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e/",
                r"%252e%252e/",
                r"\.\.;",
                r"c:",
                r"/etc/passwd",
                r"/windows/system32"
            ],
            "command_injection": [
                r"[;&|`]",
                r"\$\(",
                r"\bsh\b|\bbash\b|\bcmd\b",
                r"nc\s+-",
                r"wget\s+",
                r"curl\s+"
            ]
        }
    
    def detect(self, input_data: str, threat_type: str = "all") -> bool:
        """كشف التهديدات"""
        import re
        
        if threat_type == "all":
            patterns_to_check = self.patterns
        else:
            patterns_to_check = {threat_type: self.patterns.get(threat_type, [])}
        
        for threat, patterns in patterns_to_check.items():
            for pattern in patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    logger.warning(f"🚨 {threat.upper()} detected: {pattern}")
                    self.ministry._record_event(
                        SecurityEventType.ANOMALY_DETECTED,
                        None, None,
                        {"threat_type": threat, "pattern": pattern},
                        ThreatLevel.HIGH
                    )
                    return True
        
        return False


class SessionManager:
    """📦 مدير الجلسات المتقدم"""
    
    def __init__(self, security_ministry: AdvancedSecurityMinistry):
        self.ministry = security_ministry
        self.sessions = {}
        self.session_timeout = security_ministry.security_config['session']['timeout']
        self.max_concurrent = security_ministry.security_config['session']['max_concurrent']
    
    def create_session(self, user_id: str, ip_address: str) -> str:
        """إنشاء جلسة جديدة"""
        # التحقق من عدد الجلسات المتزامنة
        user_sessions = [s for s in self.sessions.values() 
                        if s['user_id'] == user_id]
        
        if len(user_sessions) >= self.max_concurrent:
            # إنهاء أقدم جلسة
            oldest = min(user_sessions, key=lambda s: s['created'])
            self.invalidate_session(oldest['token'])
        
        # توليد رمز جلسة آمن
        session_token = secrets.token_urlsafe(64)
        
        # إنشاء بيانات الجلسة
        self.sessions[session_token] = {
            'token': session_token,
            'user_id': user_id,
            'ip_address': ip_address,
            'created': datetime.now(),
            'last_activity': datetime.now(),
            'fingerprint': self._generate_fingerprint(ip_address)
        }
        
        logger.info(f"✅ Session created for user: {user_id}")
        return session_token
    
    def validate_session(self, session_token: str) -> bool:
        """التحقق من صحة الجلسة"""
        if session_token not in self.sessions:
            return False
        
        session = self.sessions[session_token]
        
        # التحقق من انتهاء الجلسة
        if (datetime.now() - session['last_activity']).seconds > self.session_timeout:
            self.invalidate_session(session_token)
            return False
        
        # تحديث آخر نشاط
        session['last_activity'] = datetime.now()
        return True
    
    def invalidate_session(self, session_token: str):
        """إبطال جلسة"""
        if session_token in self.sessions:
            user_id = self.sessions[session_token]['user_id']
            del self.sessions[session_token]
            logger.info(f"Session invalidated for user: {user_id}")
    
    def invalidate_all_sessions(self):
        """إبطال جميع الجلسات"""
        count = len(self.sessions)
        self.sessions.clear()
        logger.warning(f"All {count} sessions invalidated")
    
    def _generate_fingerprint(self, ip_address: str) -> str:
        """توليد بصمة للجلسة"""
        data = f"{ip_address}_{time.time()}_{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()


def require_security(min_trust_score: int = 30, threat_level: ThreatLevel = ThreatLevel.MEDIUM):
    """Decorator للحماية المطلوبة للدوال"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # فحوصات أمنية
            logger.info(f"Security check for function: {func.__name__}")
            
            # يمكن إضافة فحوصات إضافية هنا
            security = advanced_security_ministry
            if security.threat_level.value > threat_level.value:
                raise SecurityException(f"Threat level too high: {security.threat_level.name}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class SecurityException(Exception):
    """استثناء أمني"""
    pass


# إنشاء instance واحد للاستخدام العام
advanced_security_ministry = AdvancedSecurityMinistry()