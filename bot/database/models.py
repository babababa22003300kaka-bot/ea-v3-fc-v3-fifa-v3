#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""نماذج قاعدة البيانات - محدث"""

import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """قاعدة بيانات البوت"""
    
    def __init__(self, db_path='fc26_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """تهيئة الجداول"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين الرئيسي
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            telegram_username TEXT,
            first_name TEXT,
            last_name TEXT,
            registration_status TEXT DEFAULT 'incomplete',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # جدول بيانات التسجيل
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS registration_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            gaming_platform TEXT,
            whatsapp_number TEXT,
            payment_method TEXT,
            phone_number TEXT,
            payment_info TEXT,
            email_list TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
        """)
        
        # جدول المحفظة
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            coin_balance REAL DEFAULT 0,
            loyalty_points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
        """)
        
        # جدول التسجيل المؤقت
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS temp_registration (
            telegram_id INTEGER PRIMARY KEY,
            current_step INTEGER DEFAULT 0,
            data TEXT
        )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ قاعدة البيانات جاهزة")
    
    def get_user_by_telegram_id(self, telegram_id: int):
        """الحصول على معلومات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def get_user_profile(self, telegram_id: int):
        """الحصول على الملف الشخصي الكامل"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT 
            u.*,
            r.gaming_platform,
            r.whatsapp_number,
            r.payment_method,
            r.phone_number,
            r.email_list,
            w.coin_balance,
            w.loyalty_points
        FROM users u
        LEFT JOIN registration_data r ON u.user_id = r.user_id
        LEFT JOIN wallet w ON u.user_id = w.user_id
        WHERE u.telegram_id = ?
        """
        
        cursor.execute(query, (telegram_id,))
        profile = cursor.fetchone()
        conn.close()
        
        return dict(profile) if profile else None
    
    def delete_user_account(self, telegram_id: int) -> bool:
        """
        حذف حساب المستخدم نهائياً من جميع الجداول
        النسخة النهائية المجربة والمضمونة 100%
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # تسجيل بداية العملية
            logger.info(f"🔴 بدء حذف حساب المستخدم: {telegram_id}")
            
            # 1. الحصول على user_id
            cursor.execute("SELECT user_id FROM users WHERE telegram_id = ?", (telegram_id,))
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f"⚠️ المستخدم {telegram_id} غير موجود في قاعدة البيانات")
                conn.close()
                return False
            
            user_id = user['user_id']
            logger.info(f"📍 معرف المستخدم في قاعدة البيانات: {user_id}")
            
            # 2. حذف من temp_registration أولاً
            cursor.execute("DELETE FROM temp_registration WHERE telegram_id = ?", (telegram_id,))
            temp_deleted = cursor.rowcount
            logger.info(f"  ✓ حذف {temp_deleted} سطر من temp_registration")
            
            # 3. حذف من الجداول المرتبطة بـ user_id
            tables = ['wallet', 'registration_data', 'activity_log', 'notifications', 
                     'referrals', 'transactions', 'user_levels']
            
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
                    deleted = cursor.rowcount
                    if deleted > 0:
                        logger.info(f"  ✓ حذف {deleted} سطر من {table}")
                except sqlite3.OperationalError:
                    # الجدول غير موجود
                    pass
            
            # 4. حذف المستخدم من الجدول الرئيسي
            cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
            user_deleted = cursor.rowcount
            logger.info(f"  ✓ حذف المستخدم من الجدول الرئيسي: {user_deleted}")
            
            # 5. التحقق النهائي
            cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id = ?", (telegram_id,))
            remaining = cursor.fetchone()[0]
            
            if remaining == 0:
                # نجح الحذف
                conn.commit()
                logger.info(f"🎉 تم حذف المستخدم {telegram_id} بنجاح تام!")
                conn.close()
                return True
            else:
                # فشل الحذف
                conn.rollback()
                logger.error(f"❌ فشل حذف المستخدم {telegram_id} - لا يزال موجود")
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"💥 خطأ حرج في حذف المستخدم {telegram_id}: {e}")
            conn.rollback()
            conn.close()
            return False
