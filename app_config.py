"""
FC26 Profile System - App Configuration Module
وزارة الإعدادات المركزية - معزولة ومتخصصة
"""

import os
from typing import Dict, List, Tuple, Optional
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppConfig:
    """
    فئة إعدادات التطبيق المركزية
    تدير جميع متغيرات البيئة والإعدادات الأساسية بأمان كامل
    """
    
    def __init__(self):
        """تهيئة إعدادات التطبيق مع قراءة متغيرات البيئة"""
        # الإعدادات الأساسية المطلوبة
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        self.TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        # إعدادات قاعدة البيانات
        self.DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///fc26_profiles.db')
        
        # إعدادات التطبيق
        self.DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        self.PORT = int(os.environ.get('PORT', 5000))
        self.HOST = os.environ.get('HOST', '0.0.0.0')
        
        # إعدادات الأمان
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
        self.PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
        
        # إعدادات التحقق
        self.VALIDATION_RULES = {
            'whatsapp_min_length': 10,
            'whatsapp_max_length': 15,
            'name_min_length': 2,
            'name_max_length': 50,
            'position_max_length': 100,
            'team_max_length': 50
        }
        
        # إعدادات Telegram
        self.TELEGRAM_CONFIG = {
            'parse_mode': 'HTML',
            'timeout': 30,
            'read_timeout': 30,
            'write_timeout': 30
        }
        
        logger.info("✅ تم تحميل إعدادات التطبيق بنجاح")
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """
        التحقق من صحة جميع الإعدادات المطلوبة
        
        Returns:
            Tuple[bool, List[str]]: (هل الإعدادات صحيحة, قائمة الأخطاء)
        """
        errors = []
        
        # التحقق من المتغيرات الأساسية المطلوبة
        required_vars = {
            'SECRET_KEY': self.SECRET_KEY,
            'TELEGRAM_BOT_TOKEN': self.TELEGRAM_BOT_TOKEN
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                errors.append(f"❌ متغير البيئة المطلوب غير موجود: {var_name}")
            elif len(var_value.strip()) == 0:
                errors.append(f"❌ متغير البيئة فارغ: {var_name}")
        
        # التحقق من صحة TELEGRAM_BOT_TOKEN
        if self.TELEGRAM_BOT_TOKEN:
            if not self._validate_telegram_token(self.TELEGRAM_BOT_TOKEN):
                errors.append("❌ تنسيق TELEGRAM_BOT_TOKEN غير صحيح")
        
        # التحقق من إعدادات المنفذ
        if not (1 <= self.PORT <= 65535):
            errors.append(f"❌ رقم المنفذ غير صحيح: {self.PORT}")
        
        # التحقق من قواعد التحقق
        if not self._validate_validation_rules():
            errors.append("❌ قواعد التحقق غير صحيحة")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ جميع إعدادات التطبيق صحيحة")
        else:
            logger.error(f"❌ وُجدت {len(errors)} أخطاء في الإعدادات")
            for error in errors:
                logger.error(error)
        
        return is_valid, errors
    
    def _validate_telegram_token(self, token: str) -> bool:
        """
        التحقق من صحة تنسيق Telegram Bot Token
        
        Args:
            token (str): رمز البوت
            
        Returns:
            bool: صحة التنسيق
        """
        if not token:
            return False
            
        # تنسيق Telegram Bot Token: XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        parts = token.split(':')
        if len(parts) != 2:
            return False
            
        bot_id, auth_token = parts
        
        # التحقق من bot_id (يجب أن يكون رقماً)
        if not bot_id.isdigit():
            return False
            
        # التحقق من auth_token (يجب أن يكون 35 حرف)
        if len(auth_token) != 35:
            return False
            
        return True
    
    def _validate_validation_rules(self) -> bool:
        """
        التحقق من صحة قواعد التحقق المعرّفة
        
        Returns:
            bool: صحة القواعد
        """
        required_rules = [
            'whatsapp_min_length', 'whatsapp_max_length',
            'name_min_length', 'name_max_length',
            'position_max_length', 'team_max_length'
        ]
        
        for rule in required_rules:
            if rule not in self.VALIDATION_RULES:
                return False
            if not isinstance(self.VALIDATION_RULES[rule], int):
                return False
            if self.VALIDATION_RULES[rule] <= 0:
                return False
        
        # التحقق من المنطق (min < max)
        if (self.VALIDATION_RULES['whatsapp_min_length'] >= 
            self.VALIDATION_RULES['whatsapp_max_length']):
            return False
            
        if (self.VALIDATION_RULES['name_min_length'] >= 
            self.VALIDATION_RULES['name_max_length']):
            return False
        
        return True
    
    def get_flask_config(self) -> Dict[str, any]:
        """
        إرجاع إعدادات Flask المطلوبة
        
        Returns:
            Dict[str, any]: قاموس إعدادات Flask
        """
        return {
            'SECRET_KEY': self.SECRET_KEY,
            'DEBUG': self.DEBUG,
            'MAX_CONTENT_LENGTH': self.MAX_CONTENT_LENGTH,
            'PERMANENT_SESSION_LIFETIME': self.PERMANENT_SESSION_LIFETIME,
            'SQLALCHEMY_DATABASE_URI': self.DATABASE_URL,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_timeout': 20,
                'pool_recycle': -1,
                'pool_pre_ping': True
            }
        }
    
    def get_telegram_config(self) -> Dict[str, any]:
        """
        إرجاع إعدادات Telegram
        
        Returns:
            Dict[str, any]: قاموس إعدادات Telegram
        """
        config = self.TELEGRAM_CONFIG.copy()
        config['token'] = self.TELEGRAM_BOT_TOKEN
        return config
    
    def get_validation_rules(self) -> Dict[str, int]:
        """
        إرجاع قواعد التحقق
        
        Returns:
            Dict[str, int]: قاموس قواعد التحقق
        """
        return self.VALIDATION_RULES.copy()
    
    def is_production(self) -> bool:
        """
        التحقق من بيئة الإنتاج
        
        Returns:
            bool: هل نحن في بيئة الإنتاج
        """
        return not self.DEBUG
    
    def get_database_config(self) -> Dict[str, str]:
        """
        إرجاع إعدادات قاعدة البيانات
        
        Returns:
            Dict[str, str]: إعدادات قاعدة البيانات
        """
        return {
            'url': self.DATABASE_URL,
            'track_modifications': False
        }
    
    def get_config_summary(self) -> Dict[str, any]:
        """
        إرجاع ملخص الإعدادات للعرض الإداري
        
        Returns:
            Dict[str, any]: ملخص الإعدادات
        """
        return {
            'secret_key_set': bool(self.SECRET_KEY),
            'telegram_token_set': bool(self.TELEGRAM_BOT_TOKEN),
            'debug_mode': self.DEBUG,
            'port': self.PORT,
            'host': self.HOST,
            'database_type': 'PostgreSQL' if 'postgresql' in self.DATABASE_URL.lower() else 'SQLite',
            'environment': 'Development' if self.DEBUG else 'Production'
        }
    
    def log_config_status(self) -> None:
        """طباعة حالة الإعدادات في السجل"""
        logger.info("=" * 50)
        logger.info("📋 حالة إعدادات FC26 Profile System")
        logger.info("=" * 50)
        logger.info(f"🔐 SECRET_KEY: {'✅ محدد' if self.SECRET_KEY else '❌ غير محدد'}")
        logger.info(f"🤖 TELEGRAM_BOT_TOKEN: {'✅ محدد' if self.TELEGRAM_BOT_TOKEN else '❌ غير محدد'}")
        logger.info(f"🗄️ DATABASE_URL: {self.DATABASE_URL}")
        logger.info(f"🐞 DEBUG Mode: {'✅ مفعل' if self.DEBUG else '❌ مُعطل'}")
        logger.info(f"🌐 Server: {self.HOST}:{self.PORT}")
        logger.info(f"🏗️ Environment: {'Development' if self.DEBUG else 'Production'}")
        logger.info("=" * 50)

# إنشاء مثيل عام للإعدادات
app_config = AppConfig()

# تصدير المتغيرات الأساسية للوصول السريع
SECRET_KEY = app_config.SECRET_KEY
TELEGRAM_BOT_TOKEN = app_config.TELEGRAM_BOT_TOKEN
DEBUG = app_config.DEBUG
PORT = app_config.PORT
HOST = app_config.HOST

def create_flask_app():
    """
    إنشاء تطبيق Flask مع الإعدادات المطلوبة
    
    Returns:
        Flask: مثيل تطبيق Flask مُعد بالكامل
    """
    from flask import Flask
    from datetime import timedelta
    
    # إنشاء التطبيق
    app = Flask(__name__)
    
    # تطبيق الإعدادات من app_config
    flask_config = app_config.get_flask_config()
    app.config.update(flask_config)
    
    # إعدادات إضافية للأمان
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    
    logger.info("✅ تم إنشاء تطبيق Flask بنجاح")
    
    return app

def generate_csrf_token():
    """
    توليد رمز CSRF للأمان
    
    Returns:
        str: رمز CSRF فريد
    """
    import secrets
    import string
    
    # توليد رمز عشوائي آمن
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    logger.debug("🔐 تم توليد رمز CSRF جديد")
    
    return token

# تصدير الدوال للاستخدام الخارجي
__all__ = [
    'AppConfig', 
    'app_config', 
    'SECRET_KEY', 
    'TELEGRAM_BOT_TOKEN', 
    'DEBUG', 
    'PORT', 
    'HOST',
    'create_flask_app',
    'generate_csrf_token',
    'verify_startup_config'
]

# التحقق الفوري من الإعدادات عند التحميل
def verify_startup_config():
    """التحقق من الإعدادات عند بدء التشغيل"""
    is_valid, errors = app_config.validate_config()
    
    if not is_valid:
        logger.critical("🚨 فشل في التحقق من إعدادات التطبيق!")
        for error in errors:
            logger.critical(error)
        raise EnvironmentError("إعدادات التطبيق غير صحيحة")
    
    app_config.log_config_status()
    logger.info("🚀 إعدادات التطبيق جاهزة للتشغيل")

if __name__ == "__main__":
    # تشغيل التحقق عندما يتم تشغيل الملف مباشرة
    verify_startup_config()
