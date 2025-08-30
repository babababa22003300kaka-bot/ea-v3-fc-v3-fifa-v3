"""
🧪 Fortress Security Tests - اختبارات نظام الحماية الشامل
"""

import sys
import os
import unittest
import json
from datetime import datetime, timedelta

# إضافة المسار الرئيسي
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# استيراد الوحدات المطلوبة
from ministries.security_ministry import SecurityMinistry, ZeroTrustValidator


class TestSecurityMinistry(unittest.TestCase):
    """اختبارات وزارة الأمان"""
    
    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        self.ministry = SecurityMinistry()
        self.zero_trust = ZeroTrustValidator(self.ministry)
    
    def test_singleton_pattern(self):
        """التأكد من أن الوزارة singleton"""
        ministry2 = SecurityMinistry()
        self.assertIs(self.ministry, ministry2)
    
    def test_session_token_generation(self):
        """اختبار توليد رموز الجلسة"""
        user_id = "test_user_1"
        token = self.ministry.generate_session_token(user_id)
        
        self.assertIsNotNone(token)
        self.assertIn(user_id, self.ministry.session_keys)
        self.assertEqual(self.ministry.session_keys[user_id]['token'], token)
    
    def test_session_validation(self):
        """اختبار التحقق من الجلسة"""
        user_id = "test_user_2"
        token = self.ministry.generate_session_token(user_id)
        
        # جلسة صحيحة
        self.assertTrue(self.ministry.validate_session(user_id, token))
        
        # جلسة خاطئة
        self.assertFalse(self.ministry.validate_session(user_id, "wrong_token"))
        self.assertFalse(self.ministry.validate_session("wrong_user", token))
    
    def test_rate_limiting(self):
        """اختبار حد المعدل"""
        identifier = "test_ip_1"
        
        # أول 100 طلب يجب أن ينجحوا
        for i in range(100):
            self.assertTrue(
                self.ministry.check_rate_limit(identifier),
                f"Request {i+1} should pass"
            )
        
        # الطلب 101 يجب أن يفشل
        self.assertFalse(self.ministry.check_rate_limit(identifier))
    
    def test_sql_injection_detection(self):
        """اختبار كشف SQL Injection"""
        # نصوص آمنة
        safe_queries = [
            "John Doe",
            "user@example.com",
            "123456789"
        ]
        
        for query in safe_queries:
            self.assertFalse(
                self.ministry.detect_sql_injection(query),
                f"'{query}' should be safe"
            )
        
        # نصوص خطرة
        dangerous_queries = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin' --",
            "UNION SELECT * FROM passwords"
        ]
        
        for query in dangerous_queries:
            self.assertTrue(
                self.ministry.detect_sql_injection(query),
                f"'{query}' should be detected as SQL injection"
            )
    
    def test_xss_detection(self):
        """اختبار كشف XSS"""
        # نصوص آمنة
        safe_content = [
            "Hello World",
            "This is a normal text",
            "Email: user@example.com"
        ]
        
        for content in safe_content:
            self.assertFalse(
                self.ministry.detect_xss(content),
                f"'{content}' should be safe"
            )
        
        # نصوص خطرة
        xss_content = [
            "<script>alert('XSS')</script>",
            "javascript:alert(1)",
            "<img onerror='alert(1)' src='x'>",
            "onclick='malicious()'"
        ]
        
        for content in xss_content:
            self.assertTrue(
                self.ministry.detect_xss(content),
                f"'{content}' should be detected as XSS"
            )
    
    def test_trust_score_calculation(self):
        """اختبار حساب نقاط الثقة"""
        user_id = "test_user_3"
        
        # نقطة البداية
        initial_score = self.ministry.calculate_trust_score(user_id, 'normal_activity')
        self.assertEqual(initial_score, 52)  # 50 + 2
        
        # إجراءات إيجابية
        score = self.ministry.calculate_trust_score(user_id, 'successful_login')
        self.assertEqual(score, 57)  # 52 + 5
        
        # إجراءات سلبية
        score = self.ministry.calculate_trust_score(user_id, 'failed_login')
        self.assertEqual(score, 47)  # 57 - 10
        
        # التأكد من عدم تجاوز الحدود
        for _ in range(20):
            self.ministry.calculate_trust_score(user_id, 'suspicious_activity')
        score = self.ministry.trust_scores[user_id]
        self.assertEqual(score, 0)  # لا يقل عن 0
        
        for _ in range(30):
            self.ministry.calculate_trust_score(user_id, 'successful_login')
        score = self.ministry.trust_scores[user_id]
        self.assertLessEqual(score, 100)  # لا يزيد عن 100
    
    def test_ip_blocking(self):
        """اختبار حظر عناوين IP"""
        ip = "192.168.1.100"
        
        # IP غير محظور في البداية
        self.assertFalse(self.ministry.is_ip_blocked(ip))
        
        # حظر IP
        self.ministry.block_ip(ip, "Suspicious activity")
        
        # IP محظور الآن
        self.assertTrue(self.ministry.is_ip_blocked(ip))
    
    def test_input_validation(self):
        """اختبار التحقق من المدخلات"""
        # نص عادي
        valid, msg = self.ministry.validate_input("Hello World", "text")
        self.assertTrue(valid)
        
        # بريد إلكتروني صحيح
        valid, msg = self.ministry.validate_input("user@example.com", "email")
        self.assertTrue(valid)
        
        # بريد إلكتروني خاطئ
        valid, msg = self.ministry.validate_input("not-an-email", "email")
        self.assertFalse(valid)
        
        # رقم صحيح
        valid, msg = self.ministry.validate_input("123456", "number")
        self.assertTrue(valid)
        
        # رقم خاطئ
        valid, msg = self.ministry.validate_input("abc123", "number")
        self.assertFalse(valid)
    
    def test_security_report(self):
        """اختبار تقرير الأمان"""
        # إضافة بعض البيانات
        self.ministry.generate_session_token("user1")
        self.ministry.generate_session_token("user2")
        self.ministry.block_ip("192.168.1.1", "Test")
        self.ministry.calculate_trust_score("user1", "normal_activity")
        
        report = self.ministry.get_security_report()
        
        self.assertIn('total_sessions', report)
        self.assertIn('blocked_ips', report)
        self.assertIn('recent_events', report)
        self.assertIn('average_trust_score', report)
        self.assertIn('critical_events', report)
        self.assertIn('timestamp', report)
        
        self.assertEqual(report['total_sessions'], 2)
        self.assertEqual(report['blocked_ips'], 1)


class TestZeroTrustValidator(unittest.TestCase):
    """اختبارات نظام Zero Trust"""
    
    def setUp(self):
        """إعداد البيئة"""
        self.ministry = SecurityMinistry()
        self.validator = ZeroTrustValidator(self.ministry)
    
    def test_authentication_validation(self):
        """اختبار التحقق من الهوية"""
        user_id = "test_user"
        token = self.ministry.generate_session_token(user_id)
        
        # طلب صحيح
        request_data = {
            'user_id': user_id,
            'token': token,
            'ip_address': '192.168.1.1',
            'data': {},
            'user_role': 'user'
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertTrue(is_valid)
        
        # طلب بدون هوية
        request_data_no_auth = {
            'ip_address': '192.168.1.1',
            'data': {}
        }
        
        is_valid, message = self.validator.validate_request(request_data_no_auth)
        self.assertFalse(is_valid)
        self.assertIn("authentication", message.lower())
    
    def test_authorization_validation(self):
        """اختبار التحقق من الصلاحيات"""
        user_id = "test_admin"
        token = self.ministry.generate_session_token(user_id)
        
        # مستخدم عادي يحاول الوصول لصلاحيات مسؤول
        request_data = {
            'user_id': user_id,
            'token': token,
            'ip_address': '192.168.1.1',
            'data': {},
            'required_role': 'admin',
            'user_role': 'user'
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertFalse(is_valid)
        self.assertIn("permissions", message.lower())
    
    def test_input_safety_validation(self):
        """اختبار أمان المدخلات"""
        user_id = "test_user"
        token = self.ministry.generate_session_token(user_id)
        
        # طلب مع SQL injection
        request_data = {
            'user_id': user_id,
            'token': token,
            'ip_address': '192.168.1.1',
            'data': {
                'username': "admin'; DROP TABLE users; --"
            },
            'user_role': 'user'
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertFalse(is_valid)
        self.assertIn("sql injection", message.lower())
    
    def test_rate_limit_validation(self):
        """اختبار حد المعدل في Zero Trust"""
        user_id = "test_user"
        token = self.ministry.generate_session_token(user_id)
        ip = '192.168.1.100'
        
        # ملء حد المعدل
        for _ in range(100):
            self.ministry.check_rate_limit(ip)
        
        request_data = {
            'user_id': user_id,
            'token': token,
            'ip_address': ip,
            'data': {},
            'user_role': 'user'
        }
        
        is_valid, message = self.validator.validate_request(request_data)
        self.assertFalse(is_valid)
        self.assertIn("rate limit", message.lower())


def run_security_tests():
    """تشغيل جميع الاختبارات"""
    # إنشاء مجموعة الاختبارات
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # إضافة اختبارات الوزارة
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityMinistry))
    
    # إضافة اختبارات Zero Trust
    suite.addTests(loader.loadTestsFromTestCase(TestZeroTrustValidator))
    
    # تشغيل الاختبارات
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # طباعة النتائج
    print("\n" + "="*60)
    print("📊 نتائج الاختبارات النهائية:")
    print("="*60)
    print(f"✅ نجح: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ فشل: {len(result.failures)}")
    print(f"🚨 أخطاء: {len(result.errors)}")
    print(f"📈 نسبة النجاح: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)