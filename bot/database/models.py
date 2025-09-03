#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات - نظام متطور
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

class Database:
    """مدير قاعدة البيانات الرئيسي"""
    
    def __init__(self, db_path='fc26_bot.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """إنشاء جميع جداول قاعدة البيانات"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول المستخدمين الرئيسي
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                telegram_username TEXT,
                full_name TEXT,
                registration_status TEXT DEFAULT 'incomplete',
                registration_step INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0
            )
        ''')
        
        # جدول بيانات التسجيل
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registration_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                gaming_platform TEXT,
                whatsapp_number TEXT,
                payment_method TEXT,
                phone_number TEXT,
                card_last_four TEXT,
                card_hash TEXT,
                instapay_link TEXT,
                emails TEXT,
                additional_data TEXT,
                completed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول التسجيل المؤقت (للحفظ التلقائي)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_registration (
                telegram_id INTEGER PRIMARY KEY,
                current_step TEXT NOT NULL,
                step_number INTEGER DEFAULT 0,
                data TEXT NOT NULL,
                last_update DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المحفظة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet (
                wallet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                coin_balance INTEGER DEFAULT 0,
                cash_balance REAL DEFAULT 0.0,
                loyalty_points INTEGER DEFAULT 100,
                total_purchased INTEGER DEFAULT 0,
                total_sold INTEGER DEFAULT 0,
                frozen_balance REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول المستويات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                level INTEGER DEFAULT 1,
                level_name TEXT DEFAULT 'مبتدئ',
                experience_points INTEGER DEFAULT 0,
                total_transactions INTEGER DEFAULT 0,
                badges TEXT DEFAULT '[]',
                achievements TEXT DEFAULT '[]',
                perks TEXT DEFAULT '[]',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول المعاملات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount INTEGER,
                price REAL,
                payment_method TEXT,
                status TEXT DEFAULT 'pending',
                reference_number TEXT UNIQUE,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول الإشعارات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                read_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول سجل النشاطات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # جدول العروض والخصومات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offers (
                offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL,
                value REAL NOT NULL,
                min_purchase REAL,
                max_uses INTEGER,
                uses_count INTEGER DEFAULT 0,
                valid_from DATETIME,
                valid_until DATETIME,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الإحالات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER NOT NULL,
                referral_code TEXT,
                bonus_given BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ========== وظائف التسجيل ==========
    
    def save_temp_registration(self, telegram_id: int, step: str, step_number: int, data: Dict):
        """حفظ بيانات التسجيل المؤقتة (للحفظ التلقائي)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO temp_registration 
            (telegram_id, current_step, step_number, data, last_update)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (telegram_id, step, step_number, json.dumps(data)))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_temp_registration(self, telegram_id: int) -> Optional[Dict]:
        """استرجاع بيانات التسجيل المؤقتة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT current_step, step_number, data, last_update 
            FROM temp_registration 
            WHERE telegram_id = ?
        ''', (telegram_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'current_step': row['current_step'],
                'step_number': row['step_number'],
                'data': json.loads(row['data']),
                'last_update': row['last_update']
            }
        return None
    
    def clear_temp_registration(self, telegram_id: int):
        """مسح بيانات التسجيل المؤقتة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM temp_registration WHERE telegram_id = ?', (telegram_id,))
        
        conn.commit()
        conn.close()
    
    # ========== وظائف المستخدمين ==========
    
    def create_user(self, telegram_id: int, username: str = None, full_name: str = None) -> int:
        """إنشاء مستخدم جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (telegram_id, telegram_username, full_name)
                VALUES (?, ?, ?)
            ''', (telegram_id, username, full_name))
            
            user_id = cursor.lastrowid
            
            # إنشاء محفظة للمستخدم
            cursor.execute('''
                INSERT INTO wallet (user_id, loyalty_points)
                VALUES (?, 100)
            ''', (user_id,))
            
            # إنشاء مستوى للمستخدم
            cursor.execute('''
                INSERT INTO user_levels (user_id)
                VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return user_id
            
        except sqlite3.IntegrityError:
            # المستخدم موجود بالفعل
            conn.close()
            return self.get_user_by_telegram_id(telegram_id)['user_id']
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """الحصول على بيانات المستخدم"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM users WHERE telegram_id = ?
        ''', (telegram_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def complete_registration(self, telegram_id: int, registration_data: Dict) -> bool:
        """إكمال عملية التسجيل"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # الحصول على معرف المستخدم
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                return False
            
            user_id = user['user_id']
            
            # تشفير البيانات الحساسة
            card_hash = None
            if registration_data.get('card_last_four'):
                card_hash = hashlib.sha256(
                    f"{telegram_id}_{registration_data['card_last_four']}".encode()
                ).hexdigest()
            
            # حفظ بيانات التسجيل
            cursor.execute('''
                INSERT OR REPLACE INTO registration_data (
                    user_id, gaming_platform, whatsapp_number,
                    payment_method, phone_number, card_last_four,
                    card_hash, instapay_link, emails, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                registration_data.get('platform'),
                registration_data.get('whatsapp'),
                registration_data.get('payment_method'),
                registration_data.get('phone'),
                registration_data.get('card_last_four'),
                card_hash,
                registration_data.get('instapay'),
                json.dumps(registration_data.get('emails', [])),
            ))
            
            # تحديث حالة المستخدم
            cursor.execute('''
                UPDATE users 
                SET registration_status = 'complete',
                    is_verified = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            
            # إضافة إشعار ترحيبي
            cursor.execute('''
                INSERT INTO notifications (user_id, type, title, message)
                VALUES (?, 'welcome', 'مرحباً بك!', 'تم تسجيلك بنجاح في FC 26 Bot')
            ''', (user_id,))
            
            # إضافة نقاط الولاء الترحيبية
            cursor.execute('''
                UPDATE wallet 
                SET loyalty_points = loyalty_points + 100
                WHERE user_id = ?
            ''', (user_id,))
            
            # سجل النشاط
            cursor.execute('''
                INSERT INTO activity_log (user_id, action, details)
                VALUES (?, 'registration_complete', 'User completed registration')
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            # مسح البيانات المؤقتة
            self.clear_temp_registration(telegram_id)
            
            return True
            
        except Exception as e:
            conn.close()
            print(f"Error completing registration: {e}")
            return False
    
    def get_user_profile(self, telegram_id: int) -> Optional[Dict]:
        """الحصول على الملف الشخصي الكامل"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # بيانات المستخدم الأساسية
        cursor.execute('''
            SELECT u.*, r.*, w.*, l.*
            FROM users u
            LEFT JOIN registration_data r ON u.user_id = r.user_id
            LEFT JOIN wallet w ON u.user_id = w.user_id
            LEFT JOIN user_levels l ON u.user_id = l.user_id
            WHERE u.telegram_id = ?
        ''', (telegram_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        profile = dict(row)
        
        # عدد المعاملات
        cursor.execute('''
            SELECT COUNT(*) as transaction_count
            FROM transactions
            WHERE user_id = ?
        ''', (profile['user_id'],))
        
        profile['transaction_count'] = cursor.fetchone()['transaction_count']
        
        conn.close()
        
        return profile
    
    def delete_user_account(self, telegram_id: int) -> bool:
        """حذف حساب المستخدم من جميع الجداول"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # الحصول على معرف المستخدم
            cursor.execute('SELECT user_id FROM users WHERE telegram_id = ?', (telegram_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False
            
            user_id = user['user_id']
            
            # حذف من جميع الجداول
            tables_to_delete = [
                'activity_log',
                'notifications',
                'referrals',
                'user_sessions',
                'transactions',
                'user_levels',
                'wallet',
                'email_data',
                'payment_info',
                'registration_data',
                'temp_registration',
                'users'
            ]
            
            for table in tables_to_delete:
                if table == 'temp_registration':
                    cursor.execute(f'DELETE FROM {table} WHERE telegram_id = ?', (telegram_id,))
                else:
                    cursor.execute(f'DELETE FROM {table} WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error deleting user account: {e}")
            return False