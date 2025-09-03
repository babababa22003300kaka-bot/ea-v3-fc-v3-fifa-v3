# profile_handler.py - وزارة إدارة البيانات الشخصية
"""
💾 وزارة البيانات - FC 26 Profile System
========================================
مسؤولة عن جميع عمليات إدارة البيانات
- حفظ وتحديث الملفات الشخصية
- معالجة البيانات والتخزين
- إدارة جلسات المستخدمين
- تصدير واستيراد البيانات
"""

import json
import hashlib
from datetime import datetime
import os
import re


class ProfileHandler:
    """الكلاس الأساسي لإدارة الملفات الشخصية"""
    
    def __init__(self):
        # قاعدة بيانات في الذاكرة (يمكن تحويلها لقاعدة بيانات لاحقاً)
        self.users_data = {}
        self.session_data = {}
    
    def sanitize_input(self, text):
        """تنظيف المدخلات من الأكواد الضارة"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()
    
    def generate_user_id(self, whatsapp_number, additional_data=None):
        """توليد معرف فريد للمستخدم"""
        base_string = f"{whatsapp_number}-{datetime.now().isoformat()}"
        if additional_data:
            base_string += f"-{additional_data}"
        return hashlib.md5(base_string.encode()).hexdigest()[:12]
    
    def process_email_addresses(self, email_addresses_json):
        """معالجة عناوين البريد الإلكتروني"""
        try:
            email_addresses = json.loads(email_addresses_json) if email_addresses_json else []
            
            # تنظيف وفلترة الإيميلات
            email_addresses = [email.lower().strip() for email in email_addresses if email and '@' in email and '.' in email]
            
            # إزالة المكررات والحد الأقصى
            email_addresses = list(dict.fromkeys(email_addresses))  # إزالة المكررات مع الحفاظ على الترتيب
            email_addresses = email_addresses[:6]  # الحد الأقصى 6 إيميلات
            
            # التحقق من صحة كل إيميل
            valid_emails = []
            for email in email_addresses:
                if re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                    valid_emails.append(email)
            
            return valid_emails
            
        except Exception as e:
            print(f"خطأ في معالجة الإيميلات: {str(e)}")
            return []
    
    def process_payment_details(self, payment_method, payment_details):
        """معالجة تفاصيل الدفع"""
        processed_payment_details = ""
        
        if payment_method in ['vodafone_cash', 'etisalat_cash', 'orange_cash', 'we_cash', 'bank_wallet']:
            # تنظيف رقم الهاتف
            processed_payment_details = re.sub(r'\D', '', payment_details)
            
        elif payment_method == 'tilda':
            # تنظيف رقم البطاقة من أي شرطات أو مسافات
            processed_payment_details = re.sub(r'[^\d]', '', payment_details)
            
        elif payment_method == 'instapay':
            # استخدام الرابط كما هو (يتم التحقق منه في validators)
            processed_payment_details = payment_details
        
        return processed_payment_details
    
    def create_user_profile(self, form_data, client_ip, user_agent):
        """إنشاء ملف شخصي جديد"""
        try:
            # استخراج البيانات الأساسية
            platform = self.sanitize_input(form_data.get('platform'))
            whatsapp_number = self.sanitize_input(form_data.get('whatsapp_number'))
            payment_method = self.sanitize_input(form_data.get('payment_method'))
            payment_details = self.sanitize_input(form_data.get('payment_details'))
            telegram_username = self.sanitize_input(form_data.get('telegram_username'))
            
            # معالجة الإيميلات
            email_addresses_json = self.sanitize_input(form_data.get('email_addresses', '[]'))
            email_addresses = self.process_email_addresses(email_addresses_json)
            
            # معالجة تفاصيل الدفع
            processed_payment_details = self.process_payment_details(payment_method, payment_details)
            
            # إنشاء معرف المستخدم
            user_id = self.generate_user_id(whatsapp_number)
            
            # إنشاء البيانات الشاملة
            user_data = {
                'user_id': user_id,
                'platform': platform,
                'whatsapp_number': whatsapp_number,
                'payment_method': payment_method,
                'payment_details': processed_payment_details,
                'telegram_username': telegram_username,
                'email_addresses': email_addresses,
                'email_count': len(email_addresses),
                'email_details': {
                    'primary_email': email_addresses[0] if email_addresses else None,
                    'secondary_emails': email_addresses[1:] if len(email_addresses) > 1 else [],
                    'total_count': len(email_addresses),
                    'domains': list(set([email.split('@')[1] for email in email_addresses])) if email_addresses else []
                },
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'ip_address': hashlib.sha256(client_ip.encode()).hexdigest()[:10],
                'user_agent': hashlib.sha256(user_agent.encode()).hexdigest()[:10],
                'profile_complete': True,
                'telegram_linked': False
            }
            
            # حفظ في الذاكرة المؤقتة
            self.users_data[user_id] = user_data
            
            print(f"🔥 New Profile Created (ID: {user_id}):")
            print(f"   📱 WhatsApp: {whatsapp_number}")
            print(f"   🎯 Platform: {platform}")
            print(f"   💳 Payment: {payment_method}")
            print(f"   📧 Emails ({len(email_addresses)}): {email_addresses}")
            
            return {
                'success': True,
                'user_id': user_id,
                'user_data': user_data,
                'message': 'تم إنشاء الملف الشخصي بنجاح'
            }
            
        except Exception as e:
            print(f"خطأ في إنشاء الملف الشخصي: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'فشل في إنشاء الملف الشخصي'
            }
    
    def update_user_profile(self, user_id, update_data):
        """تحديث ملف شخصي موجود"""
        if user_id not in self.users_data:
            return {
                'success': False,
                'message': 'الملف الشخصي غير موجود'
            }
        
        try:
            # تحديث البيانات
            current_data = self.users_data[user_id]
            current_data.update(update_data)
            current_data['updated_at'] = datetime.now().isoformat()
            
            self.users_data[user_id] = current_data
            
            print(f"📝 Profile Updated (ID: {user_id})")
            
            return {
                'success': True,
                'user_data': current_data,
                'message': 'تم تحديث الملف الشخصي بنجاح'
            }
            
        except Exception as e:
            print(f"خطأ في تحديث الملف الشخصي: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'فشل في تحديث الملف الشخصي'
            }
    
    def get_user_profile(self, user_id):
        """الحصول على ملف شخصي"""
        if user_id in self.users_data:
            return {
                'success': True,
                'user_data': self.users_data[user_id]
            }
        else:
            return {
                'success': False,
                'message': 'الملف الشخصي غير موجود'
            }
    
    def search_user_by_whatsapp(self, whatsapp_number):
        """البحث عن مستخدم برقم الواتساب"""
        for user_id, user_data in self.users_data.items():
            if user_data.get('whatsapp_number') == whatsapp_number:
                return {
                    'success': True,
                    'user_id': user_id,
                    'user_data': user_data
                }
        
        return {
            'success': False,
            'message': 'المستخدم غير موجود'
        }
    
    def link_telegram_account(self, user_id, telegram_data):
        """ربط حساب التليجرام بالملف الشخصي"""
        if user_id not in self.users_data:
            return {
                'success': False,
                'message': 'الملف الشخصي غير موجود'
            }
        
        try:
            # تحديث بيانات التليجرام
            telegram_update = {
                'telegram_linked': True,
                'telegram_chat_id': telegram_data.get('chat_id'),
                'telegram_first_name': telegram_data.get('first_name'),
                'telegram_username_actual': telegram_data.get('username'),
                'telegram_linked_at': datetime.now().isoformat()
            }
            
            result = self.update_user_profile(user_id, telegram_update)
            
            if result['success']:
                print(f"🔗 Telegram linked to profile {user_id}")
            
            return result
            
        except Exception as e:
            print(f"خطأ في ربط التليجرام: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'فشل في ربط حساب التليجرام'
            }
    
    def get_all_users(self):
        """الحصول على جميع المستخدمين"""
        return {
            'success': True,
            'users_count': len(self.users_data),
            'users_data': self.users_data
        }
    
    def export_data(self):
        """تصدير البيانات للنسخ الاحتياطي"""
        export_data = {
            'export_date': datetime.now().isoformat(),
            'users_count': len(self.users_data),
            'users_data': self.users_data,
            'session_data': self.session_data
        }
        
        return export_data
    
    def import_data(self, import_data):
        """استيراد البيانات من النسخة الاحتياطية"""
        try:
            if 'users_data' in import_data:
                self.users_data.update(import_data['users_data'])
            
            if 'session_data' in import_data:
                self.session_data.update(import_data['session_data'])
            
            print(f"📥 تم استيراد {len(import_data.get('users_data', {}))} مستخدم")
            
            return {
                'success': True,
                'message': 'تم استيراد البيانات بنجاح'
            }
            
        except Exception as e:
            print(f"خطأ في استيراد البيانات: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'فشل في استيراد البيانات'
            }
    
    def cleanup_old_sessions(self, hours=24):
        """تنظيف الجلسات القديمة"""
        try:
            current_time = datetime.now()
            cleaned_count = 0
            
            for session_id in list(self.session_data.keys()):
                session = self.session_data[session_id]
                if 'created_at' in session:
                    session_time = datetime.fromisoformat(session['created_at'])
                    age_hours = (current_time - session_time).total_seconds() / 3600
                    
                    if age_hours > hours:
                        del self.session_data[session_id]
                        cleaned_count += 1
            
            print(f"🧹 تم تنظيف {cleaned_count} جلسة قديمة")
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'message': f'تم تنظيف {cleaned_count} جلسة'
            }
            
        except Exception as e:
            print(f"خطأ في تنظيف الجلسات: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# إنشاء instance عام للاستخدام
profile_handler = ProfileHandler()

# تصدير الدوال للتوافق مع الكود الأصلي
def create_user_profile(form_data, client_ip, user_agent):
    return profile_handler.create_user_profile(form_data, client_ip, user_agent)

def update_user_profile(user_id, update_data):
    return profile_handler.update_user_profile(user_id, update_data)

def get_user_profile(user_id):
    return profile_handler.get_user_profile(user_id)

def search_user_by_whatsapp(whatsapp_number):
    return profile_handler.search_user_by_whatsapp(whatsapp_number)

def link_telegram_account(user_id, telegram_data):
    return profile_handler.link_telegram_account(user_id, telegram_data)
