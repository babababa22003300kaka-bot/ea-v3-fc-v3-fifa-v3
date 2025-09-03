"""
💾 مدير قاعدة البيانات
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self):
        """تهيئة قاعدة البيانات"""
        self.db_path = Path(__file__).parent.parent / 'data' / 'fc26_bot.db'
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """إنشاء الجداول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE,
                username TEXT,
                first_name TEXT,
                platform TEXT,
                whatsapp TEXT,
                payment_method TEXT,
                phone TEXT,
                card_number_encrypted TEXT,
                instapay_link TEXT,
                emails TEXT,
                created_at TEXT,
                updated_at TEXT,
                is_active INTEGER DEFAULT 1,
                trust_score INTEGER DEFAULT 50
            )
        """)
        
        # جدول التسجيل المؤقت
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temp_registrations (
                telegram_id BIGINT PRIMARY KEY,
                data TEXT,
                step INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # جدول النشاطات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT,
                activity_type TEXT,
                details TEXT,
                created_at TEXT
            )
        """)
        
        # جدول المعاملات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                platform TEXT,
                amount REAL,
                coins INTEGER,
                status TEXT,
                created_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialized")
    
    def encrypt_card(self, card_number):
        """تشفير رقم البطاقة"""
        # تشفير بسيط - في الإنتاج استخدم تشفير أقوى
        return hashlib.sha256(card_number.encode()).hexdigest()
    
    async def save_user(self, registration_data):
        """حفظ مستخدم جديد"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # تشفير البطاقة
            encrypted_card = self.encrypt_card(registration_data.get('card_number', ''))
            
            # تحويل الإيميلات لنص JSON
            emails_json = json.dumps(registration_data.get('emails', []))
            
            cursor.execute("""
                INSERT OR REPLACE INTO users (
                    telegram_id, username, first_name, platform,
                    whatsapp, payment_method, phone, card_number_encrypted,
                    instapay_link, emails, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                registration_data['telegram_id'],
                registration_data.get('username'),
                registration_data.get('first_name'),
                registration_data['platform'],
                registration_data['whatsapp'],
                registration_data['payment_method'],
                registration_data['phone'],
                encrypted_card,
                registration_data.get('instapay_link'),
                emails_json,
                registration_data.get('created_at', datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # حذف التسجيل المؤقت
            await self.delete_temp_registration(registration_data['telegram_id'])
            
            logger.info(f"✅ Saved user {registration_data['telegram_id']}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            raise
    
    async def save_temp_registration(self, data):
        """حفظ التسجيل المؤقت"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO temp_registrations (
                    telegram_id, data, step, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                data['telegram_id'],
                json.dumps(data),
                data.get('step', 1),
                data.get('start_time', datetime.now().isoformat()),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving temp registration: {e}")
    
    async def delete_temp_registration(self, telegram_id):
        """حذف التسجيل المؤقت"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM temp_registrations WHERE telegram_id = ?", (telegram_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error deleting temp registration: {e}")
    
    async def get_user_by_telegram_id(self, telegram_id):
        """جلب مستخدم بمعرف تليجرام"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user = dict(row)
                # فك تشفير الإيميلات
                if user.get('emails'):
                    user['emails'] = json.loads(user['emails'])
                return user
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def log_activity(self, telegram_id, activity_type, details):
        """تسجيل نشاط"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO activities (telegram_id, activity_type, details, created_at)
                VALUES (?, ?, ?, ?)
            """, (telegram_id, activity_type, details, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")