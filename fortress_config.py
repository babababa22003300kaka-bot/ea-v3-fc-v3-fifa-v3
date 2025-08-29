#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏰 Fort Knox Digital Identity Phase 2 - Enhanced Configuration
================================================================
ملف التكوين المتقدم لنظام Fort Knox المرحلة الثانية
================================================================
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class FortKnoxConfig:
    """
    🏰 إعدادات Fort Knox المتقدمة
    ============================
    """
    
    # 🔐 الأمان المتقدم
    SECRET_KEY = os.getenv('SECRET_KEY', 'fort_knox_fallback_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_fallback_key')
    ENCRYPTION_SALT = os.getenv('ENCRYPTION_SALT', 'fc26_fallback_salt')
    
    # 🏰 إعدادات القلعة
    FORTRESS_MODE = os.getenv('FORTRESS_MODE', 'maximum_security')
    IIFE_ISOLATION = os.getenv('IIFE_ISOLATION', 'military_grade')
    CRYPTO_ENGINE_VERSION = os.getenv('CRYPTO_ENGINE_VERSION', '2.1')
    
    # 🕵️ الهوية الصامتة
    SILENT_IDENTITY_ENABLED = os.getenv('SILENT_IDENTITY_ENABLED', 'true').lower() == 'true'
    IDENTITY_LENGTH = 32
    IDENTITY_TIMEOUT = timedelta(hours=24)
    
    # 🗄️ قاعدة البيانات
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///fc26_fortress_main_database.db')
    DATABASE_BACKUP_ENABLED = os.getenv('DATABASE_BACKUP_ENABLED', 'true').lower() == 'true'
    DATABASE_ENCRYPTION_ENABLED = os.getenv('DATABASE_ENCRYPTION_ENABLED', 'true').lower() == 'true'
    
    # 🤖 التليجرام
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    TELEGRAM_ALERTS_ENABLED = os.getenv('TELEGRAM_ALERTS_ENABLED', 'true').lower() == 'true'
    TELEGRAM_BACKUP_ENABLED = os.getenv('TELEGRAM_BACKUP_ENABLED', 'true').lower() == 'true'
    
    # 🔒 الحماية المتقدمة
    RATE_LIMITING_ENABLED = os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '100'))
    BRUTE_FORCE_PROTECTION = os.getenv('BRUTE_FORCE_PROTECTION', 'enabled') == 'enabled'
    THREAT_DETECTION = os.getenv('THREAT_DETECTION', 'active') == 'active'
    
    # 📊 المراقبة
    PERFORMANCE_MONITORING = os.getenv('PERFORMANCE_MONITORING', 'enabled') == 'enabled'
    SECURITY_AUDIT_LOG = os.getenv('SECURITY_AUDIT_LOG', 'enabled') == 'enabled'
    REAL_TIME_ALERTS = os.getenv('REAL_TIME_ALERTS', 'enabled') == 'enabled'
    
    # 🚀 الأداء
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    COMPRESSION_ENABLED = os.getenv('COMPRESSION_ENABLED', 'true').lower() == 'true'
    ASYNC_PROCESSING = os.getenv('ASYNC_PROCESSING', 'enabled') == 'enabled'
    
    # 📱 التطبيق المتقدم
    PWA_ENABLED = os.getenv('PWA_ENABLED', 'true').lower() == 'true'
    OFFLINE_MODE_SUPPORTED = os.getenv('OFFLINE_MODE_SUPPORTED', 'true').lower() == 'true'
    SERVICE_WORKER_ENABLED = os.getenv('SERVICE_WORKER_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def get_security_level(cls):
        """
        🛡️ الحصول على مستوى الأمان الحالي
        """
        levels = {
            'basic': 1,
            'standard': 2,
            'advanced': 3,
            'maximum_security': 4,
            'military_grade': 5
        }
        return levels.get(cls.FORTRESS_MODE, 4)
    
    @classmethod
    def is_production_ready(cls):
        """
        🚀 فحص جاهزية النظام للإنتاج
        """
        required_settings = [
            cls.SECRET_KEY != 'fort_knox_fallback_key',
            cls.JWT_SECRET_KEY != 'jwt_fallback_key',
            cls.ENCRYPTION_SALT != 'fc26_fallback_salt',
            cls.FORTRESS_MODE in ['maximum_security', 'military_grade'],
            cls.SILENT_IDENTITY_ENABLED,
            cls.DATABASE_BACKUP_ENABLED,
            cls.THREAT_DETECTION,
            cls.SECURITY_AUDIT_LOG
        ]
        
        return all(required_settings)
    
    @classmethod
    def get_fortress_status(cls):
        """
        🏰 الحصول على حالة القلعة
        """
        return {
            'fortress_mode': cls.FORTRESS_MODE,
            'security_level': cls.get_security_level(),
            'iife_isolation': cls.IIFE_ISOLATION,
            'crypto_version': cls.CRYPTO_ENGINE_VERSION,
            'silent_identity': cls.SILENT_IDENTITY_ENABLED,
            'telegram_enabled': bool(cls.TELEGRAM_BOT_TOKEN),
            'production_ready': cls.is_production_ready(),
            'monitoring_active': cls.PERFORMANCE_MONITORING,
            'threat_detection': cls.THREAT_DETECTION
        }

class DevelopmentConfig(FortKnoxConfig):
    """
    🛠️ إعدادات التطوير
    """
    DEBUG = True
    TESTING = False
    
class ProductionConfig(FortKnoxConfig):
    """
    🚀 إعدادات الإنتاج
    """
    DEBUG = False
    TESTING = False
    
    # إعدادات إضافية للإنتاج
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

class TestingConfig(FortKnoxConfig):
    """
    🧪 إعدادات الاختبار
    """
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///test_fortress.db'

# اختيار التكوين حسب البيئة
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """
    🎯 الحصول على التكوين المناسب
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])

# تصدير التكوين الافتراضي
Config = get_config()

if __name__ == "__main__":
    # عرض حالة النظام عند التشغيل المباشر
    print("🏰 Fort Knox Digital Identity Phase 2 - Configuration Status")
    print("=" * 60)
    
    fortress_status = Config.get_fortress_status()
    for key, value in fortress_status.items():
        status_emoji = "✅" if value else "❌"
        print(f"{status_emoji} {key}: {value}")
    
    print("=" * 60)
    print(f"🚀 Production Ready: {'✅ YES' if Config.is_production_ready() else '❌ NO'}")
    print(f"🔐 Security Level: {Config.get_security_level()}/5")