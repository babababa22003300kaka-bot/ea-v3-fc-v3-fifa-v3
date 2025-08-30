"""
🧪 Advanced Security Tests V2 - اختبارات النظام الأمني المتقدم
"""

import sys
import os
import unittest
import json
from datetime import datetime

# إضافة المسار الرئيسي
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# استيراد الوحدات المطلوبة
from ministries.advanced_security_ministry import (
    AdvancedSecurityMinistry,
    ThreatLevel,
    SecurityEventType,
    CryptoEngine,
    ZeroTrustValidator,
    ThreatDetector,
    SessionManager,
    SecurityException
)


class TestAdvancedSecurityMinistry(unittest.TestCase):
    """اختبارات وزارة الأمان المتقدمة"""
    
    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        self.ministry = AdvancedSecurityMinistry()
    
    def test_singleton_pattern(self):
        """التأكد من أن الوزارة singleton"""
        ministry2 = AdvancedSecurityMinistry()
        self.assertIs(self.ministry, ministry2)
    
    def test_system_id_generation(self):
        """اختبار توليد معرف النظام"""
        self.assertIsNotNone(self.ministry.system_id)
        self.assertTrue(self.ministry.system_id.startswith('ASM-'))
    
    def test_authentication_success(self):
        """اختبار نجاح المصادقة"""
        credentials = {
            'user_id': 'test_user',
            'password': 'test_user_password',
            'mfa_code': '123456',
            'ip_address': '192.168.1.1'
        }
        
        success, token = self.ministry.authenticate_user(credentials)
        self.assertTrue(success)
        self.assertIsNotNone(token)
    
    def test_authentication_failure(self):
        """اختبار فشل المصادقة"""
        credentials = {
            'user_id': 'test_user',
            'password': 'wrong_password',
            'mfa_code': '123456',
            'ip_address': '192.168.1.1'
        }
        
        success, message = self.ministry.authenticate_user(credentials)
        self.assertFalse(success)
        self.assertEqual(message, 'Invalid credentials')
    
    def test_rate_limiting(self):
        """اختبار حد المعدل"""
        identifier = 'test_ip'
        
        # أول 60 طلب يجب أن ينجحوا (الحد الافتراضي)
        for i in range(60):
            self.assertTrue(
                self.ministry.check_rate_limit(identifier, 60, 60),
                f"Request {i+1} should pass"
            )
        
        # الطلب 61 يجب أن يفشل
        self.assertFalse(self.ministry.check_rate_limit(identifier, 60, 60))
    
    def test_trust_score_management(self):
        """اختبار إدارة نقاط الثقة"""
        user_id = 'test_user'
        
        # النقطة الافتراضية 50
        initial = self.ministry.update_trust_score(user_id, 0)
        self.assertEqual(initial, 50)
        
        # زيادة النقاط
        increased = self.ministry.update_trust_score(user_id, 20)
        self.assertEqual(increased, 70)
        
        # نقصان النقاط
        decreased = self.ministry.update_trust_score(user_id, -30)
        self.assertEqual(decreased, 40)
        
        # التأكد من عدم تجاوز 100
        self.ministry.update_trust_score(user_id, 200)
        self.assertEqual(self.ministry.trust_scores[user_id], 100)
        
        # التأكد من عدم النزول تحت 0
        self.ministry.update_trust_score(user_id, -200)
        self.assertEqual(self.ministry.trust_scores[user_id], 0)
    
    def test_ip_blocking(self):
        """اختبار حظر عناوين IP"""
        ip = '192.168.1.100'
        
        # IP غير محظور في البداية
        self.assertFalse(self.ministry.is_ip_blocked(ip))
        
        # حظر IP
        self.ministry.block_ip(ip, 'Suspicious activity')
        
        # IP محظور الآن
        self.assertTrue(self.ministry.is_ip_blocked(ip))
    
    def test_security_dashboard(self):
        """اختبار لوحة المعلومات الأمنية"""
        dashboard = self.ministry.get_security_dashboard()
        
        self.assertIn('system_info', dashboard)
        self.assertIn('statistics', dashboard)
        self.assertIn('recent_threats', dashboard)
        self.assertIn('configuration', dashboard)
        
        self.assertEqual(dashboard['system_info']['version'], '2.0.0')
        self.assertEqual(dashboard['system_info']['threat_level'], 'LOW')


class TestCryptoEngine(unittest.TestCase):
    """اختبارات محرك التشفير"""
    
    def setUp(self):
        self.crypto = CryptoEngine()
    
    def test_encryption_decryption(self):
        """اختبار التشفير وفك التشفير"""
        data = {'test': 'data', 'number': 123}
        
        # تشفير
        encrypted = self.crypto.encrypt(data)
        self.assertIsNotNone(encrypted)
        self.assertIsInstance(encrypted, str)
        
        # فك التشفير
        decrypted = self.crypto.decrypt(encrypted)
        self.assertEqual(decrypted, data)
    
    def test_encryption_different_each_time(self):
        """التأكد من أن التشفير مختلف كل مرة"""
        data = {'test': 'data'}
        
        encrypted1 = self.crypto.encrypt(data)
        encrypted2 = self.crypto.encrypt(data)
        
        # التشفير مختلف
        self.assertNotEqual(encrypted1, encrypted2)
        
        # لكن فك التشفير يعطي نفس النتيجة
        self.assertEqual(self.crypto.decrypt(encrypted1), data)
        self.assertEqual(self.crypto.decrypt(encrypted2), data)


class TestThreatDetector(unittest.TestCase):
    """اختبارات كاشف التهديدات"""
    
    def setUp(self):
        ministry = AdvancedSecurityMinistry()
        self.detector = ThreatDetector(ministry)
    
    def test_xss_detection(self):
        """اختبار كشف XSS"""
        xss_samples = [
            "<script>alert('XSS')</script>",
            "javascript:alert(1)",
            "<img onerror='alert(1)' src='x'>",
            "onclick='malicious()'"
        ]
        
        for sample in xss_samples:
            self.assertTrue(
                self.detector.detect(sample, 'xss'),
                f"Should detect XSS in: {sample}"
            )
    
    def test_sql_injection_detection(self):
        """اختبار كشف SQL Injection"""
        sql_samples = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin' --",
            "UNION SELECT * FROM passwords"
        ]
        
        for sample in sql_samples:
            self.assertTrue(
                self.detector.detect(sample, 'sql_injection'),
                f"Should detect SQL injection in: {sample}"
            )
    
    def test_path_traversal_detection(self):
        """اختبار كشف Path Traversal"""
        path_samples = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "%2e%2e/",
            "c:/windows/system32/config"
        ]
        
        for sample in path_samples:
            self.assertTrue(
                self.detector.detect(sample, 'path_traversal'),
                f"Should detect path traversal in: {sample}"
            )
    
    def test_safe_input(self):
        """اختبار المدخلات الآمنة"""
        safe_samples = [
            "Hello World",
            "user@example.com",
            "This is normal text",
            "123456789"
        ]
        
        for sample in safe_samples:
            self.assertFalse(
                self.detector.detect(sample, 'all'),
                f"Should not detect threat in: {sample}"
            )


class TestSessionManager(unittest.TestCase):
    """اختبارات مدير الجلسات"""
    
    def setUp(self):
        ministry = AdvancedSecurityMinistry()
        self.session_manager = SessionManager(ministry)
    
    def test_session_creation(self):
        """اختبار إنشاء جلسة"""
        user_id = 'test_user'
        ip_address = '192.168.1.1'
        
        token = self.session_manager.create_session(user_id, ip_address)
        
        self.assertIsNotNone(token)
        self.assertIn(token, self.session_manager.sessions)
        
        session = self.session_manager.sessions[token]
        self.assertEqual(session['user_id'], user_id)
        self.assertEqual(session['ip_address'], ip_address)
    
    def test_session_validation(self):
        """اختبار التحقق من الجلسة"""
        user_id = 'test_user'
        ip_address = '192.168.1.1'
        
        token = self.session_manager.create_session(user_id, ip_address)
        
        # جلسة صحيحة
        self.assertTrue(self.session_manager.validate_session(token))
        
        # جلسة غير موجودة
        self.assertFalse(self.session_manager.validate_session('invalid_token'))
    
    def test_max_concurrent_sessions(self):
        """اختبار الحد الأقصى للجلسات المتزامنة"""
        user_id = 'test_user'
        ip_address = '192.168.1.1'
        
        # إنشاء 3 جلسات (الحد الأقصى الافتراضي)
        tokens = []
        for i in range(3):
            token = self.session_manager.create_session(user_id, f'192.168.1.{i+1}')
            tokens.append(token)
        
        # التأكد من وجود 3 جلسات
        user_sessions = [s for s in self.session_manager.sessions.values()
                        if s['user_id'] == user_id]
        self.assertEqual(len(user_sessions), 3)
        
        # إنشاء جلسة رابعة - يجب أن تحذف الأقدم
        new_token = self.session_manager.create_session(user_id, '192.168.1.4')
        
        # التأكد من أن الجلسة الأولى حُذفت
        self.assertNotIn(tokens[0], self.session_manager.sessions)
        self.assertIn(new_token, self.session_manager.sessions)
        
        # لا يزال هناك 3 جلسات فقط
        user_sessions = [s for s in self.session_manager.sessions.values()
                        if s['user_id'] == user_id]
        self.assertEqual(len(user_sessions), 3)


class TestZeroTrustValidator(unittest.TestCase):
    """اختبارات مدقق Zero Trust"""
    
    def setUp(self):
        self.ministry = AdvancedSecurityMinistry()
        self.validator = ZeroTrustValidator(self.ministry)
    
    def test_authentication_validation(self):
        """اختبار التحقق من الهوية"""
        # إنشاء جلسة صحيحة
        token = self.ministry.session_manager.create_session('test_user', '192.168.1.1')
        
        # طلب مع مصادقة صحيحة
        request_data = {
            'session_token': token,
            'user_id': 'test_user',
            'ip_address': '192.168.1.1'
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertTrue(is_valid)
        
        # طلب بدون مصادقة
        request_data_no_auth = {
            'user_id': 'test_user',
            'ip_address': '192.168.1.1'
        }
        
        is_valid, message = self.validator.validate_request(request_data_no_auth)
        self.assertFalse(is_valid)
        self.assertIn('authentication', message.lower())
    
    def test_ip_blocking_validation(self):
        """اختبار التحقق من IP المحظور"""
        ip = '192.168.1.100'
        self.ministry.block_ip(ip, 'Test')
        
        request_data = {
            'session_token': 'valid_token',
            'user_id': 'test_user',
            'ip_address': ip
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertFalse(is_valid)
        self.assertIn('blocked', message.lower())
    
    def test_trust_score_validation(self):
        """اختبار التحقق من نقاط الثقة"""
        user_id = 'low_trust_user'
        
        # تقليل نقاط الثقة
        self.ministry.trust_scores[user_id] = 20
        
        request_data = {
            'session_token': 'valid_token',
            'user_id': user_id,
            'ip_address': '192.168.1.1'
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertFalse(is_valid)
        self.assertIn('trust score', message.lower())


def run_advanced_security_tests():
    """تشغيل جميع الاختبارات المتقدمة"""
    # إنشاء مجموعة الاختبارات
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # إضافة اختبارات الوزارة المتقدمة
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedSecurityMinistry))
    suite.addTests(loader.loadTestsFromTestCase(TestCryptoEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestThreatDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestZeroTrustValidator))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # طباعة النتائج
    print("\n" + "="*60)
    print("📊 نتائج اختبارات النظام الأمني المتقدم V2:")
    print("="*60)
    print(f"✅ نجح: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ فشل: {len(result.failures)}")
    print(f"🚨 أخطاء: {len(result.errors)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
    print(f"📈 نسبة النجاح: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 ممتاز! النظام يعمل بكفاءة عالية")
    elif success_rate >= 80:
        print("👍 جيد! النظام يعمل بشكل مقبول")
    else:
        print("⚠️ يحتاج تحسين!")
    
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_advanced_security_tests()
    sys.exit(0 if success else 1)