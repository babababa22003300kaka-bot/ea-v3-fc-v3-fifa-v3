#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام الملف الشخصي المتقدم للبوت
"""

import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class ProfileSystem:
    """نظام الملف الشخصي المتقدم"""
    
    def __init__(self, db_path='fc26_profiles.db'):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """إنشاء جداول قاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول المستخدمين المحسن
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                whatsapp_number TEXT,
                email TEXT,
                card_number_hash TEXT,
                password_hash TEXT NOT NULL,
                birth_date TEXT,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                profile_image TEXT,
                bio TEXT,
                preferred_language TEXT DEFAULT 'ar'
            )
        ''')
        
        # جدول الرصيد والمحفظة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet (
                wallet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                coin_balance INTEGER DEFAULT 0,
                cash_balance REAL DEFAULT 0,
                total_purchased INTEGER DEFAULT 0,
                total_sold INTEGER DEFAULT 0,
                last_transaction DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول المستويات والنقاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                level_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                level_name TEXT DEFAULT 'مبتدئ',
                level_number INTEGER DEFAULT 1,
                experience_points INTEGER DEFAULT 0,
                loyalty_points INTEGER DEFAULT 0,
                total_transactions INTEGER DEFAULT 0,
                badges TEXT,
                achievements TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول المعاملات المفصل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                price REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                payment_method TEXT,
                transaction_hash TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الإشعارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الإعدادات الشخصية
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                settings_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                receive_notifications BOOLEAN DEFAULT 1,
                email_notifications BOOLEAN DEFAULT 0,
                whatsapp_notifications BOOLEAN DEFAULT 1,
                price_alerts BOOLEAN DEFAULT 1,
                auto_reply BOOLEAN DEFAULT 0,
                privacy_level TEXT DEFAULT 'normal',
                theme TEXT DEFAULT 'default',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول سجل النشاط
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                device_info TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول العروض والخصومات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offers (
                offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                offer_code TEXT UNIQUE,
                discount_percentage REAL,
                valid_until DATETIME,
                times_used INTEGER DEFAULT 0,
                max_uses INTEGER,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user_profile(self, telegram_id: int, data: Dict) -> int:
        """إنشاء ملف شخصي جديد"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # إدراج بيانات المستخدم
            cursor.execute('''
                INSERT INTO users (
                    telegram_id, username, full_name, phone_number, 
                    whatsapp_number, email, card_number_hash, 
                    password_hash, birth_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                telegram_id,
                data.get('username'),
                data['full_name'],
                data['phone_number'],
                data.get('whatsapp_number'),
                data.get('email'),
                self.hash_data(data.get('card_number', '')),
                self.hash_data(data['password']),
                data.get('birth_date')
            ))
            
            user_id = cursor.lastrowid
            
            # إنشاء محفظة
            cursor.execute('''
                INSERT INTO wallet (user_id) VALUES (?)
            ''', (user_id,))
            
            # إنشاء مستوى
            cursor.execute('''
                INSERT INTO user_levels (user_id) VALUES (?)
            ''', (user_id,))
            
            # إنشاء إعدادات
            cursor.execute('''
                INSERT INTO user_settings (user_id) VALUES (?)
            ''', (user_id,))
            
            # إضافة إشعار ترحيب
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                'مرحباً بك في FC 26 Bot!',
                'تم إنشاء حسابك بنجاح. استمتع بأفضل خدمة لبيع وشراء الكوينز.',
                'welcome'
            ))
            
            conn.commit()
            return user_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_profile(self, telegram_id: int) -> Optional[Dict]:
        """الحصول على الملف الشخصي الكامل"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # بيانات المستخدم الأساسية
        cursor.execute('''
            SELECT * FROM users WHERE telegram_id = ?
        ''', (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return None
        
        user_id = user[0]
        
        # بيانات المحفظة
        cursor.execute('''
            SELECT * FROM wallet WHERE user_id = ?
        ''', (user_id,))
        wallet = cursor.fetchone()
        
        # بيانات المستوى
        cursor.execute('''
            SELECT * FROM user_levels WHERE user_id = ?
        ''', (user_id,))
        level = cursor.fetchone()
        
        # آخر المعاملات
        cursor.execute('''
            SELECT * FROM transactions 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 10
        ''', (user_id,))
        transactions = cursor.fetchall()
        
        # الإشعارات غير المقروءة
        cursor.execute('''
            SELECT COUNT(*) FROM notifications 
            WHERE user_id = ? AND is_read = 0
        ''', (user_id,))
        unread_notifications = cursor.fetchone()[0]
        
        # الإعدادات
        cursor.execute('''
            SELECT * FROM user_settings WHERE user_id = ?
        ''', (user_id,))
        settings = cursor.fetchone()
        
        conn.close()
        
        # تجميع البيانات
        profile = {
            'user': {
                'id': user[0],
                'telegram_id': user[1],
                'username': user[2],
                'full_name': user[3],
                'phone': user[4],
                'whatsapp': user[5],
                'email': user[6],
                'birth_date': user[8],
                'registration_date': user[9],
                'last_active': user[10],
                'is_verified': bool(user[12]),
                'bio': user[14],
                'language': user[15]
            },
            'wallet': {
                'coins': wallet[2] if wallet else 0,
                'cash': wallet[3] if wallet else 0,
                'total_purchased': wallet[4] if wallet else 0,
                'total_sold': wallet[5] if wallet else 0
            },
            'level': {
                'name': level[2] if level else 'مبتدئ',
                'number': level[3] if level else 1,
                'exp': level[4] if level else 0,
                'loyalty_points': level[5] if level else 0,
                'total_transactions': level[6] if level else 0
            },
            'recent_transactions': transactions,
            'unread_notifications': unread_notifications,
            'settings': settings
        }
        
        return profile
    
    def update_wallet(self, user_id: int, transaction_type: str, amount: int, price: float):
        """تحديث المحفظة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if transaction_type == 'buy':
                cursor.execute('''
                    UPDATE wallet 
                    SET coin_balance = coin_balance + ?,
                        cash_balance = cash_balance - ?,
                        total_purchased = total_purchased + ?,
                        last_transaction = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (amount, price, amount, user_id))
            else:  # sell
                cursor.execute('''
                    UPDATE wallet 
                    SET coin_balance = coin_balance - ?,
                        cash_balance = cash_balance + ?,
                        total_sold = total_sold + ?,
                        last_transaction = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (amount, price, amount, user_id))
            
            # تحديث نقاط الخبرة
            self.add_experience(user_id, 10)
            
            conn.commit()
        finally:
            conn.close()
    
    def add_experience(self, user_id: int, points: int):
        """إضافة نقاط خبرة"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_levels 
            SET experience_points = experience_points + ?,
                total_transactions = total_transactions + 1
            WHERE user_id = ?
        ''', (points, user_id))
        
        # التحقق من الترقية
        cursor.execute('''
            SELECT experience_points FROM user_levels WHERE user_id = ?
        ''', (user_id,))
        exp = cursor.fetchone()[0]
        
        # نظام المستويات
        new_level = 1
        level_name = 'مبتدئ'
        
        if exp >= 1000:
            new_level = 5
            level_name = 'محترف'
        elif exp >= 500:
            new_level = 4
            level_name = 'متقدم'
        elif exp >= 200:
            new_level = 3
            level_name = 'متوسط'
        elif exp >= 50:
            new_level = 2
            level_name = 'مبتدئ متقدم'
        
        cursor.execute('''
            UPDATE user_levels 
            SET level_number = ?, level_name = ?
            WHERE user_id = ?
        ''', (new_level, level_name, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_statistics(self, user_id: int) -> Dict:
        """الحصول على إحصائيات المستخدم"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # إجمالي المعاملات
        cursor.execute('''
            SELECT COUNT(*), SUM(amount), SUM(price)
            FROM transactions 
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,))
        transactions_stats = cursor.fetchone()
        
        # معاملات الشهر الحالي
        cursor.execute('''
            SELECT COUNT(*), SUM(amount), SUM(price)
            FROM transactions 
            WHERE user_id = ? 
            AND status = 'completed'
            AND created_at >= date('now', 'start of month')
        ''', (user_id,))
        monthly_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'total': {
                'count': transactions_stats[0] or 0,
                'amount': transactions_stats[1] or 0,
                'value': transactions_stats[2] or 0
            },
            'monthly': {
                'count': monthly_stats[0] or 0,
                'amount': monthly_stats[1] or 0,
                'value': monthly_stats[2] or 0
            }
        }
    
    def hash_data(self, data: str) -> str:
        """تشفير البيانات"""
        if not data:
            return ''
        return hashlib.sha256(data.encode()).hexdigest()