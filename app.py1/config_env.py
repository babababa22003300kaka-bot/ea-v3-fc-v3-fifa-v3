# config_env.py - إدارة متغيرات البيئة لـ Fort Knox Phase 2
"""
🔧 إدارة متغيرات البيئة والإعدادات الآمنة
==============================================
هذا الملف يدير متغيرات البيئة بطريقة آمنة للنشر على Render
- قراءة المتغيرات من البيئة أو القيم الافتراضية
- إعدادات أمان Fort Knox Phase 2
- إعدادات قواعد البيانات والتليجرام
- إعدادات PWA والتخزين المتقدم
"""

import os
from pathlib import Path

# 🏰 إعدادات Fort Knox الأساسية
FORTRESS_MODE = os.getenv('FORTRESS_MODE', 'maximum_security')
IIFE_ISOLATION = os.getenv('IIFE_ISOLATION', 'military_grade')
SILENT_IDENTITY_ENABLED = os.getenv('SILENT_IDENTITY_ENABLED', 'true').lower() == 'true'

# 🔐 إعدادات الأمان المتقدمة
SECURITY_LEVEL = int(os.getenv('SECURITY_LEVEL', '5'))
CROSS_DEVICE_SYNC = os.getenv('CROSS_DEVICE_SYNC', 'enabled') == 'enabled'
ENCRYPTION_ALGORITHM = os.getenv('ENCRYPTION_ALGORITHM', 'AES-256-GCM')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production-fort-knox-secure')

# 📱 إعدادات التليجرام
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', '')

# 🗄️ إعدادات قاعدة البيانات
DATABASE_PATH = os.getenv('DATABASE_PATH', 'fc26_identities.db')
DATABASE_POOL_SIZE = int(os.getenv('DATABASE_POOL_SIZE', '10'))
DATABASE_TIMEOUT = int(os.getenv('DATABASE_TIMEOUT', '30'))

# 📱 إعدادات PWA
PWA_ENABLED = os.getenv('PWA_ENABLED', 'true').lower() == 'true'
PWA_NAME = os.getenv('PWA_NAME', 'Fort Knox FC26')
PWA_SHORT_NAME = os.getenv('PWA_SHORT_NAME', 'FC26')
PWA_DESCRIPTION = os.getenv('PWA_DESCRIPTION', 'Fort Knox Digital Identity System')

# ⚡ إعدادات الأداء
CACHE_STRATEGY = os.getenv('CACHE_STRATEGY', 'multi_level')
SERVICE_WORKER_ENABLED = os.getenv('SERVICE_WORKER_ENABLED', 'true').lower() == 'true'
BACKGROUND_SYNC_ENABLED = os.getenv('BACKGROUND_SYNC_ENABLED', 'true').lower() == 'true'

# 🌐 إعدادات الخادم
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '5000'))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

# 📊 إعدادات المراقبة
MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'true').lower() == 'true'
PERFORMANCE_TRACKING = os.getenv('PERFORMANCE_TRACKING', 'enabled') == 'enabled'
ERROR_REPORTING = os.getenv('ERROR_REPORTING', 'enabled') == 'enabled'

# 🔄 إعدادات المزامنة والنسخ الاحتياطي
AUTO_BACKUP_ENABLED = os.getenv('AUTO_BACKUP_ENABLED', 'true').lower() == 'true'
BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
SYNC_INTERVAL_MINUTES = int(os.getenv('SYNC_INTERVAL_MINUTES', '15'))

# 🌍 إعدادات اللغة والتوطين
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'ar')
RTL_SUPPORT = os.getenv('RTL_SUPPORT', 'enabled') == 'enabled'
TIMEZONE = os.getenv('TIMEZONE', 'Africa/Cairo')

class FortKnoxConfig:
    """
    🏰 كلاس إعدادات Fort Knox Phase 2 المتقدمة
    """
    
    # إعدادات الأمان الأساسية
    FORTRESS_MODE = FORTRESS_MODE
    IIFE_ISOLATION = IIFE_ISOLATION
    SILENT_IDENTITY_ENABLED = SILENT_IDENTITY_ENABLED
    SECURITY_LEVEL = SECURITY_LEVEL
    
    # التليجرام
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID
    TELEGRAM_BOT_USERNAME = TELEGRAM_BOT_USERNAME
    
    # قاعدة البيانات
    DATABASE_PATH = DATABASE_PATH
    DATABASE_POOL_SIZE = DATABASE_POOL_SIZE
    DATABASE_TIMEOUT = DATABASE_TIMEOUT
    
    # PWA
    PWA_ENABLED = PWA_ENABLED
    PWA_NAME = PWA_NAME
    PWA_SHORT_NAME = PWA_SHORT_NAME
    PWA_DESCRIPTION = PWA_DESCRIPTION
    
    # Flask
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    HOST = HOST
    PORT = PORT
    
    @classmethod
    def get_security_level(cls):
        """الحصول على مستوى الأمان الرقمي"""
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
        """فحص جاهزية الإنتاج"""
        checks = {
            'telegram_configured': bool(cls.TELEGRAM_BOT_TOKEN and cls.TELEGRAM_CHAT_ID),
            'security_level_high': cls.get_security_level() >= 4,
            'fortress_enabled': cls.SILENT_IDENTITY_ENABLED,
            'secret_key_secure': cls.SECRET_KEY != 'dev-key-change-in-production-fort-knox-secure'
        }
        return all(checks.values()), checks
    
    @classmethod
    def get_fortress_status(cls):
        """الحصول على حالة القلعة"""
        return {
            'fortress_mode': cls.FORTRESS_MODE,
            'security_level': cls.get_security_level(),
            'silent_identity': cls.SILENT_IDENTITY_ENABLED,
            'cross_device_sync': CROSS_DEVICE_SYNC,
            'pwa_enabled': cls.PWA_ENABLED,
            'monitoring': MONITORING_ENABLED,
            'environment': ENVIRONMENT
        }

# إعدادات للتصدير
__all__ = [
    'FortKnoxConfig',
    'FORTRESS_MODE',
    'IIFE_ISOLATION', 
    'SILENT_IDENTITY_ENABLED',
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_CHAT_ID',
    'TELEGRAM_BOT_USERNAME',
    'DATABASE_PATH',
    'PWA_ENABLED',
    'SECRET_KEY',
    'HOST',
    'PORT',
    'DEBUG'
]