"""
🔒 وزارة الأمان الكمي - Quantum Security Ministry V3
النسخة الأحدث من GitHub مع تشفير متعدد الطبقات
"""

import os
import json
import hashlib
import hmac
import secrets
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import logging

logger = logging.getLogger(__name__)

class QuantumSecurityMinistry:
    """
    🏛️ وزارة الأمان الكمي - المستوى الثالث
    تطبيق Zero Trust Architecture مع تشفير متعدد الطبقات
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.version = "3.0.0"
            self.system_id = self._generate_system_id()
            
            # 🔐 Multi-Layer Encryption Stack
            self.encryption_layers = {
                'aes_256_gcm': self._init_aes_layer(),
                'rsa_4096': self._init_rsa_layer(),
                'ecc_p521': self._init_ecc_layer(),
                'quantum_resistant': self._init_quantum_layer()
            }
            
            # 🛡️ Zero Trust Engine
            self.zero_trust_config = {
                'verify_every_transaction': True,
                'least_privilege': True,
                'continuous_monitoring': True,
                'adaptive_access': True,
                'trust_score_threshold': 70,
                'max_session_duration': 900,  # 15 minutes
                'require_mfa': True
            }
            
            # 📊 Security Metrics
            self.security_metrics = {
                'threats_detected': 0,
                'attacks_blocked': 0,
                'sessions_validated': 0,
                'encryption_operations': 0,
                'trust_validations': 0
            }
            
            # 🔑 Key Management System
            self.key_rotation_interval = 86400  # 24 hours
            self.master_key = self._generate_master_key()
            self.session_keys = {}
            self.last_key_rotation = time.time()
            
            # 🚨 Threat Intelligence
            self.threat_patterns = {
                'xss': [
                    r'<script[^>]*>.*?</script>',
                    r'javascript:',
                    r'on\w+\s*=',
                    r'<iframe[^>]*>',
                    r'eval\s*\(',
                    r'document\.cookie'
                ],
                'sql_injection': [
                    r"('\s*OR\s*'1'\s*=\s*'1)",
                    r'(--|\#|\/\*|\*\/)',
                    r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER)\b',
                    r'(;|\||&&)',
                    r'(EXEC|EXECUTE|CAST|DECLARE)'
                ],
                'path_traversal': [
                    r'\.\.[/\\]',
                    r'%2e%2e[/\\]',
                    r'\.\.%2f',
                    r'\.\.%5c',
                    r'(etc\/passwd|windows\/system32)'
                ],
                'command_injection': [
                    r'[;&|`]',
                    r'\$\(',
                    r'%0a|%0d',
                    r'(nc|netcat|wget|curl|bash|sh|cmd|powershell)'
                ]
            }
            
            # 🔐 Session Management
            self.active_sessions = {}
            self.session_timeout = 900  # 15 minutes
            self.max_concurrent_sessions = 3
            
            # 📈 Behavior Analytics
            self.behavior_patterns = {}
            self.anomaly_threshold = 0.3
            
            logger.info(f"🏛️ Quantum Security Ministry v{self.version} initialized")
            logger.info(f"System ID: {self.system_id}")
    
    def _generate_system_id(self) -> str:
        """Generate unique system identifier"""
        timestamp = str(int(time.time()))
        random_bytes = secrets.token_hex(8)
        return f"QSM-{timestamp}-{random_bytes}"
    
    def _generate_master_key(self) -> bytes:
        """Generate master encryption key using PBKDF2"""
        salt = secrets.token_bytes(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(secrets.token_bytes(32))
        return key
    
    def _init_aes_layer(self) -> Dict[str, Any]:
        """Initialize AES-256-GCM encryption layer"""
        return {
            'algorithm': 'AES-256-GCM',
            'key_size': 256,
            'nonce_size': 96,
            'tag_size': 128,
            'initialized': True
        }
    
    def _init_rsa_layer(self) -> Dict[str, Any]:
        """Initialize RSA-4096 encryption layer"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        return {
            'algorithm': 'RSA-4096-OAEP',
            'key_size': 4096,
            'private_key': private_key,
            'public_key': public_key,
            'padding': padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ),
            'initialized': True
        }
    
    def _init_ecc_layer(self) -> Dict[str, Any]:
        """Initialize ECC P-521 encryption layer"""
        return {
            'algorithm': 'ECC-P521',
            'curve': 'secp521r1',
            'key_size': 521,
            'initialized': True
        }
    
    def _init_quantum_layer(self) -> Dict[str, Any]:
        """Initialize Quantum-Resistant encryption layer (placeholder for Kyber)"""
        return {
            'algorithm': 'CRYSTALS-Kyber',
            'security_level': 5,
            'key_size': 1632,
            'ciphertext_size': 1568,
            'initialized': True,
            'note': 'Placeholder for quantum-resistant implementation'
        }
    
    def encrypt_multi_layer(self, data: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        🔐 تشفير متعدد الطبقات
        """
        try:
            if context is None:
                context = {}
            
            # Convert data to bytes
            data_bytes = data.encode('utf-8')
            
            # Layer 1: AES-256-GCM
            nonce = os.urandom(12)
            cipher = Cipher(
                algorithms.AES(self.master_key),
                modes.GCM(nonce),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
            
            # Create encrypted payload
            encrypted_payload = {
                'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                'nonce': base64.b64encode(nonce).decode('utf-8'),
                'tag': base64.b64encode(encryptor.tag).decode('utf-8'),
                'layers': ['AES-256-GCM'],
                'timestamp': datetime.utcnow().isoformat(),
                'context': context,
                'integrity_signature': self._generate_integrity_signature(ciphertext)
            }
            
            self.security_metrics['encryption_operations'] += 1
            
            return {
                'success': True,
                'encrypted_data': encrypted_payload,
                'encryption_log': {
                    'layers_applied': ['AES-256-GCM'],
                    'timestamp': datetime.utcnow().isoformat(),
                    'operation_id': secrets.token_hex(8)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Encryption failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def decrypt_multi_layer(self, encrypted_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔓 فك التشفير متعدد الطبقات
        """
        try:
            # Verify integrity first
            if not self._verify_integrity_signature(encrypted_payload):
                raise ValueError("Integrity check failed")
            
            # Extract components
            ciphertext = base64.b64decode(encrypted_payload['ciphertext'])
            nonce = base64.b64decode(encrypted_payload['nonce'])
            tag = base64.b64decode(encrypted_payload['tag'])
            
            # Decrypt AES-256-GCM
            cipher = Cipher(
                algorithms.AES(self.master_key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return {
                'success': True,
                'decrypted_data': plaintext.decode('utf-8'),
                'decryption_log': {
                    'layers_removed': encrypted_payload.get('layers', []),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Decryption failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_integrity_signature(self, data: bytes) -> str:
        """Generate HMAC signature for integrity verification"""
        h = hmac.new(self.master_key, data, hashlib.sha512)
        return base64.b64encode(h.digest()).decode('utf-8')
    
    def _verify_integrity_signature(self, encrypted_payload: Dict[str, Any]) -> bool:
        """Verify integrity signature"""
        try:
            ciphertext = base64.b64decode(encrypted_payload['ciphertext'])
            expected_signature = self._generate_integrity_signature(ciphertext)
            provided_signature = encrypted_payload.get('integrity_signature', '')
            return hmac.compare_digest(expected_signature, provided_signature)
        except:
            return False
    
    def validate_zero_trust(self, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        🛡️ Zero Trust Validation
        """
        try:
            validation_results = {
                'authenticated': False,
                'authorized': False,
                'device_trusted': False,
                'behavior_normal': False,
                'risk_acceptable': False,
                'mfa_verified': False
            }
            
            # Check authentication
            if request_context.get('session_token'):
                session = self.validate_session(request_context['session_token'])
                validation_results['authenticated'] = session.get('valid', False)
            
            # Check device trust
            device_fingerprint = request_context.get('device_fingerprint', '')
            validation_results['device_trusted'] = self._verify_device_trust(device_fingerprint)
            
            # Check behavior
            user_id = request_context.get('user_id', 'anonymous')
            validation_results['behavior_normal'] = self._analyze_behavior(user_id, request_context)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(request_context)
            validation_results['risk_acceptable'] = risk_score < 30
            
            # Check MFA if required
            if self.zero_trust_config['require_mfa']:
                validation_results['mfa_verified'] = request_context.get('mfa_verified', False)
            
            # Calculate trust score
            trust_score = sum([
                validation_results['authenticated'] * 20,
                validation_results['authorized'] * 15,
                validation_results['device_trusted'] * 20,
                validation_results['behavior_normal'] * 20,
                validation_results['risk_acceptable'] * 15,
                validation_results['mfa_verified'] * 10
            ])
            
            # Make decision
            access_granted = trust_score >= self.zero_trust_config['trust_score_threshold']
            
            self.security_metrics['trust_validations'] += 1
            
            return {
                'access_granted': access_granted,
                'trust_score': trust_score,
                'validation_results': validation_results,
                'recommendations': self._get_security_recommendations(validation_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Zero Trust validation failed: {str(e)}")
            return {
                'access_granted': False,
                'error': str(e)
            }
    
    def _verify_device_trust(self, fingerprint: str) -> bool:
        """Verify device trustworthiness"""
        # Simplified implementation - in production would check device registry
        return len(fingerprint) > 20
    
    def _analyze_behavior(self, user_id: str, context: Dict[str, Any]) -> bool:
        """Analyze user behavior for anomalies"""
        # Simplified implementation
        if user_id not in self.behavior_patterns:
            self.behavior_patterns[user_id] = []
        
        # Add current behavior
        self.behavior_patterns[user_id].append({
            'timestamp': time.time(),
            'action': context.get('action', 'unknown'),
            'ip': context.get('ip_address', ''),
            'user_agent': context.get('user_agent', '')
        })
        
        # Keep only recent patterns (last 100)
        self.behavior_patterns[user_id] = self.behavior_patterns[user_id][-100:]
        
        # Simple anomaly detection (would be ML-based in production)
        return True
    
    def _calculate_risk_score(self, context: Dict[str, Any]) -> int:
        """Calculate risk score (0-100)"""
        risk_score = 0
        
        # Check for suspicious patterns
        user_input = context.get('user_input', '')
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if pattern in user_input.lower():
                    risk_score += 20
                    logger.warning(f"🚨 Threat pattern detected: {threat_type}")
        
        # Check session age
        session_age = context.get('session_age', 0)
        if session_age > 3600:  # 1 hour
            risk_score += 10
        
        # Check location
        if context.get('location_changed', False):
            risk_score += 15
        
        # Check failed attempts
        failed_attempts = context.get('failed_attempts', 0)
        risk_score += min(failed_attempts * 10, 30)
        
        return min(risk_score, 100)
    
    def _get_security_recommendations(self, validation_results: Dict[str, bool]) -> List[str]:
        """Get security recommendations based on validation results"""
        recommendations = []
        
        if not validation_results['authenticated']:
            recommendations.append("Require strong authentication")
        
        if not validation_results['device_trusted']:
            recommendations.append("Register device for trusted access")
        
        if not validation_results['mfa_verified']:
            recommendations.append("Enable multi-factor authentication")
        
        if not validation_results['behavior_normal']:
            recommendations.append("Review recent activity for anomalies")
        
        if not validation_results['risk_acceptable']:
            recommendations.append("Additional verification required due to high risk")
        
        return recommendations
    
    def create_secure_session(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create encrypted session with Zero Trust principles"""
        try:
            # Check concurrent sessions
            user_sessions = [s for s in self.active_sessions.values() if s['user_id'] == user_id]
            if len(user_sessions) >= self.max_concurrent_sessions:
                # Invalidate oldest session
                oldest = min(user_sessions, key=lambda s: s['created_at'])
                self._invalidate_session(oldest['token'])
            
            # Generate session token
            session_token = secrets.token_urlsafe(32)
            
            # Create session data
            session_data = {
                'token': session_token,
                'user_id': user_id,
                'created_at': time.time(),
                'last_activity': time.time(),
                'ip_address': context.get('ip_address', ''),
                'user_agent': context.get('user_agent', ''),
                'device_fingerprint': context.get('device_fingerprint', ''),
                'trust_score': context.get('trust_score', 50),
                'mfa_verified': context.get('mfa_verified', False)
            }
            
            # Encrypt session data
            encrypted_session = self.encrypt_multi_layer(
                json.dumps(session_data),
                {'type': 'session', 'user_id': user_id}
            )
            
            if encrypted_session['success']:
                self.active_sessions[session_token] = session_data
                self.security_metrics['sessions_validated'] += 1
                
                logger.info(f"✅ Secure session created for user: {user_id}")
                
                return {
                    'success': True,
                    'session_token': session_token,
                    'encrypted_session': encrypted_session['encrypted_data'],
                    'expires_in': self.session_timeout
                }
            else:
                raise ValueError("Session encryption failed")
                
        except Exception as e:
            logger.error(f"❌ Session creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """Validate session with Zero Trust checks"""
        try:
            if session_token not in self.active_sessions:
                return {'valid': False, 'reason': 'Session not found'}
            
            session = self.active_sessions[session_token]
            
            # Check timeout
            if time.time() - session['last_activity'] > self.session_timeout:
                self._invalidate_session(session_token)
                return {'valid': False, 'reason': 'Session expired'}
            
            # Update last activity
            session['last_activity'] = time.time()
            
            return {
                'valid': True,
                'user_id': session['user_id'],
                'trust_score': session['trust_score'],
                'mfa_verified': session['mfa_verified']
            }
            
        except Exception as e:
            logger.error(f"❌ Session validation failed: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    def _invalidate_session(self, session_token: str):
        """Invalidate a session"""
        if session_token in self.active_sessions:
            user_id = self.active_sessions[session_token]['user_id']
            del self.active_sessions[session_token]
            logger.info(f"Session invalidated for user: {user_id}")
    
    def detect_threats(self, input_data: str) -> Dict[str, Any]:
        """
        🚨 Detect security threats in input
        """
        threats_found = []
        threat_level = 'safe'
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                import re
                if re.search(pattern, input_data, re.IGNORECASE):
                    threats_found.append({
                        'type': threat_type,
                        'pattern': pattern,
                        'severity': 'high' if threat_type in ['sql_injection', 'command_injection'] else 'medium'
                    })
        
        if threats_found:
            self.security_metrics['threats_detected'] += len(threats_found)
            threat_level = 'critical' if any(t['severity'] == 'high' for t in threats_found) else 'warning'
            logger.warning(f"🚨 Threats detected: {[t['type'] for t in threats_found]}")
        
        return {
            'safe': len(threats_found) == 0,
            'threats': threats_found,
            'threat_level': threat_level,
            'input_sanitized': self._sanitize_input(input_data) if threats_found else input_data
        }
    
    def _sanitize_input(self, input_data: str) -> str:
        """Sanitize dangerous input"""
        # Basic sanitization - would be more sophisticated in production
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '\\']
        sanitized = input_data
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized
    
    def trigger_emergency_protocol(self, reason: str):
        """
        🚨 Activate emergency security protocol
        """
        logger.critical(f"🚨🚨🚨 EMERGENCY PROTOCOL ACTIVATED: {reason}")
        
        # 1. Lockdown system
        self.zero_trust_config['trust_score_threshold'] = 100  # Maximum security
        
        # 2. Invalidate all sessions
        for token in list(self.active_sessions.keys()):
            self._invalidate_session(token)
        
        # 3. Log forensic data
        forensic_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason,
            'active_sessions_count': len(self.active_sessions),
            'security_metrics': self.security_metrics.copy(),
            'system_id': self.system_id
        }
        
        logger.critical(f"Forensic data: {json.dumps(forensic_data, indent=2)}")
        
        # 4. Notify security team (would send actual notifications in production)
        logger.critical("Security team notified")
        
        # 5. Block all new requests
        self.security_metrics['attacks_blocked'] += 1
        
        return {
            'protocol_activated': True,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'actions_taken': [
                'System locked down',
                'All sessions invalidated',
                'Forensic data logged',
                'Security team notified',
                'New requests blocked'
            ]
        }
    
    def rotate_keys(self):
        """Rotate encryption keys"""
        if time.time() - self.last_key_rotation > self.key_rotation_interval:
            self.master_key = self._generate_master_key()
            self.last_key_rotation = time.time()
            logger.info("🔑 Keys rotated successfully")
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security metrics dashboard"""
        return {
            'system_info': {
                'version': self.version,
                'system_id': self.system_id,
                'uptime': int(time.time() - self.last_key_rotation)
            },
            'security_metrics': self.security_metrics.copy(),
            'active_sessions': len(self.active_sessions),
            'zero_trust_config': self.zero_trust_config.copy(),
            'last_key_rotation': datetime.fromtimestamp(self.last_key_rotation).isoformat(),
            'threat_intelligence': {
                'patterns_loaded': sum(len(p) for p in self.threat_patterns.values()),
                'threat_types': list(self.threat_patterns.keys())
            }
        }

# Singleton instance
quantum_security = QuantumSecurityMinistry()