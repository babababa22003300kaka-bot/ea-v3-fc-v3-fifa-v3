# sell_handler.py - وزارة بيع الكوينز المعزولة مع دعم حساب EA
"""
💰 وزارة بيع الكوينز - FC 26 Profile System
==========================================
نظام معزول تماماً لإدارة طلبات بيع الكوينز
- دعم كامل لبيانات حساب EA
- تشفير آمن للبيانات الحساسة
- نظام أكواد الاسترداد الذكي
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
import re
import logging

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SellCoinsHandler:
    """كلاس معزول لإدارة طلبات بيع الكوينز مع دعم EA"""
    
    def __init__(self):
        # قاعدة بيانات في الذاكرة
        self.sell_requests = {}
        
        # معدلات التحويل
        self.conversion_rates = {
            'instant': 0.85,  # تحويل فوري - خصم 15%
            'normal': 1.0      # تحويل عادي - سعر كامل
        }
        
        # سعر الكوين بالجنيه المصري
        self.coin_price_egp = float(os.environ.get('COINS_CONVERSION_RATE', '0.10'))
        
        # الحدود - زيادة الحد الأقصى إلى 5 ملايين
        self.min_coins = 100
        self.max_coins = 5000000
        
        logger.info("💰 وزارة بيع الكوينز جاهزة للعمل")
        logger.info(f"   السعر الحالي: {self.coin_price_egp} جنيه للكوين")
    
    def generate_request_id(self):
        """توليد معرف فريد للطلب"""
        return f"SELL_{str(uuid.uuid4())[:8].upper()}"
    
    def calculate_price(self, coins_amount, transfer_type='normal'):
        """حساب السعر المتوقع للكوينز"""
        try:
            # التحويل للرقم
            if isinstance(coins_amount, str):
                coins_amount = int(coins_amount)
            
            # التحقق من الحدود
            if coins_amount < self.min_coins:
                return {
                    'success': False,
                    'error': f'الحد الأدنى {self.min_coins} كوين'
                }
            
            if coins_amount > self.max_coins:
                return {
                    'success': False,
                    'error': f'الحد الأقصى {self.max_coins} كوين'
                }
            
            # حساب السعر
            base_price = coins_amount * self.coin_price_egp
            rate = self.conversion_rates.get(transfer_type, 1.0)
            final_price = base_price * rate
            discount = base_price - final_price
            
            return {
                'success': True,
                'price': round(final_price, 2),
                'base_price': round(base_price, 2),
                'discount': round(discount, 2),
                'rate': rate,
                'transfer_type': transfer_type,
                'coins_amount': coins_amount
            }
            
        except (ValueError, TypeError) as e:
            logger.error(f"خطأ في حساب السعر: {str(e)}")
            return {
                'success': False,
                'error': 'كمية الكوينز غير صحيحة'
            }
    
    def create_sell_request(self, request_data):
        """إنشاء طلب بيع جديد مع بيانات EA"""
        try:
            # استخراج البيانات الأساسية
            coins_amount = request_data.get('coins_amount')
            transfer_type = request_data.get('transfer_type', 'normal')
            notes = request_data.get('notes', '')
            
            # بيانات المستخدم
            user_info = {
                'user_id': request_data.get('user_id', 'guest'),
                'whatsapp_number': request_data.get('whatsapp_number', ''),
                'platform': request_data.get('platform', '')
            }
            
            # بيانات حساب EA
            ea_account = request_data.get('ea_account', {})
            ea_data = {
                'email': self.sanitize_input(ea_account.get('email', '')),
                'password_hash': self.hash_password(ea_account.get('password', '')),
                'recovery_codes': self.process_recovery_codes(ea_account.get('recoveryCodes', [])),
                'recovery_codes_count': len(ea_account.get('recoveryCodes', []))
            }
            
            # التحقق من البيانات المطلوبة
            if not coins_amount:
                return {
                    'success': False,
                    'error': 'يرجى إدخال كمية الكوينز'
                }
            
            # حساب السعر
            price_info = self.calculate_price(coins_amount, transfer_type)
            
            if not price_info['success']:
                return price_info
            
            # إنشاء معرف الطلب
            request_id = self.generate_request_id()
            
            # تنظيف الملاحظات
            clean_notes = self.sanitize_input(notes)[:500]
            
            # إنشاء بيانات الطلب الكاملة
            sell_request = {
                'request_id': request_id,
                'user_info': user_info,
                'coins_amount': price_info['coins_amount'],
                'transfer_type': transfer_type,
                'pricing': {
                    'base_price': price_info['base_price'],
                    'final_price': price_info['price'],
                    'discount': price_info['discount'],
                    'rate': price_info['rate']
                },
                'ea_account': ea_data,
                'notes': clean_notes,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # حفظ في الذاكرة
            self.sell_requests[request_id] = sell_request
            
            logger.info(f"💰 طلب بيع جديد: {request_id}")
            logger.info(f"   الكمية: {coins_amount} كوين")
            logger.info(f"   النوع: {transfer_type}")
            logger.info(f"   السعر النهائي: {price_info['price']} جنيه")
            logger.info(f"   حساب EA: {ea_data['email']}")
            logger.info(f"   أكواد الاسترداد: {ea_data['recovery_codes_count']} كود")
            
            return {
                'success': True,
                'request_id': request_id,
                'message': 'تم إنشاء طلب البيع بنجاح',
                'details': {
                    'request_id': request_id,
                    'coins_amount': coins_amount,
                    'final_price': price_info['price'],
                    'status': 'pending'
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء طلب البيع: {str(e)}")
            return {
                'success': False,
                'error': 'حدث خطأ في إنشاء الطلب'
            }
    
    def get_sell_request(self, request_id):
        """الحصول على تفاصيل طلب بيع"""
        if request_id in self.sell_requests:
            return {
                'success': True,
                'request': self.sell_requests[request_id]
            }
        else:
            return {
                'success': False,
                'error': 'الطلب غير موجود'
            }
    
    def get_user_requests(self, user_id):
        """الحصول على جميع طلبات مستخدم"""
        user_requests = []
        
        for request_id, request_data in self.sell_requests.items():
            if request_data.get('user_info', {}).get('user_id') == user_id:
                user_requests.append(request_data)
        
        # ترتيب حسب التاريخ
        user_requests.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            'success': True,
            'requests': user_requests,
            'count': len(user_requests)
        }
    
    def update_request_status(self, request_id, new_status):
        """تحديث حالة الطلب"""
        if request_id not in self.sell_requests:
            return {
                'success': False,
                'error': 'الطلب غير موجود'
            }
        
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        
        if new_status not in valid_statuses:
            return {
                'success': False,
                'error': 'حالة غير صحيحة'
            }
        
        self.sell_requests[request_id]['status'] = new_status
        self.sell_requests[request_id]['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"📝 تحديث حالة الطلب {request_id} إلى {new_status}")
        
        return {
            'success': True,
            'message': f'تم تحديث الحالة إلى {new_status}'
        }
    
    def get_statistics(self):
        """الحصول على إحصائيات عامة"""
        total_requests = len(self.sell_requests)
        total_coins = 0
        total_value = 0
        
        status_counts = {
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'cancelled': 0
        }
        
        transfer_type_counts = {
            'instant': 0,
            'normal': 0
        }
        
        ea_accounts_count = 0
        
        for request in self.sell_requests.values():
            total_coins += request.get('coins_amount', 0)
            total_value += request.get('pricing', {}).get('final_price', 0)
            
            status = request.get('status')
            if status in status_counts:
                status_counts[status] += 1
            
            transfer_type = request.get('transfer_type')
            if transfer_type in transfer_type_counts:
                transfer_type_counts[transfer_type] += 1
            
            # عد الحسابات مع بيانات EA
            if request.get('ea_account', {}).get('email'):
                ea_accounts_count += 1
        
        return {
            'total_requests': total_requests,
            'total_coins': total_coins,
            'total_value': round(total_value, 2),
            'status_counts': status_counts,
            'transfer_type_counts': transfer_type_counts,
            'ea_accounts_count': ea_accounts_count,
            'coin_price': self.coin_price_egp
        }
    
    def sanitize_input(self, text):
        """تنظيف المدخلات من الأكواد الضارة"""
        if not text:
            return ""
        # إزالة HTML tags
        text = re.sub(r'<[^>]+>', '', str(text))
        # إزالة special characters خطرة
        text = re.sub(r'[<>\"\'`;]', '', text)
        return text.strip()
    
    def hash_password(self, password):
        """تشفير كلمة المرور للحفظ الآمن"""
        if not password:
            return ""
        # استخدام SHA256 للتشفير
        salt = "FC26_SELL_COINS"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    def process_recovery_codes(self, codes):
        """معالجة وتشفير أكواد الاسترداد"""
        if not codes:
            return []
        
        processed_codes = []
        for code in codes:
            if code and len(str(code)) == 8:
                # إخفاء الأرقام الوسطى للأمان
                masked = f"{str(code)[:2]}****{str(code)[-2:]}"
                processed_codes.append({
                    'masked': masked,
                    'hash': hashlib.md5(str(code).encode()).hexdigest()[:8]
                })
        
        return processed_codes
    
    def validate_coins_amount(self, coins_amount):
        """التحقق من صحة كمية الكوينز"""
        try:
            coins = int(coins_amount)
            if coins < self.min_coins:
                return False, f'الحد الأدنى {self.min_coins} كوين'
            if coins > self.max_coins:
                return False, f'الحد الأقصى {self.max_coins} كوين'
            return True, 'صحيح'
        except:
            return False, 'كمية غير صحيحة'
    
    def validate_ea_account(self, ea_data):
        """التحقق من صحة بيانات حساب EA"""
        errors = []
        
        # التحقق من الإيميل
        email = ea_data.get('email', '')
        if not email:
            errors.append('البريد الإلكتروني مطلوب')
        elif '@' not in email:
            errors.append('البريد الإلكتروني غير صحيح')
        
        # التحقق من كلمة المرور
        password = ea_data.get('password', '')
        if not password:
            errors.append('كلمة المرور مطلوبة')
        elif len(password) < 6:
            errors.append('كلمة المرور قصيرة جداً')
        
        # التحقق من أكواد الاسترداد
        codes = ea_data.get('recoveryCodes', [])
        if len(codes) < 1:
            errors.append('يجب إدخال كود استرداد واحد على الأقل')
        
        valid_codes = []
        for code in codes:
            if code and len(str(code)) == 8 and str(code).isdigit():
                valid_codes.append(code)
        
        if len(valid_codes) != len(codes):
            errors.append('بعض أكواد الاسترداد غير صحيحة (يجب أن تكون 8 أرقام)')
        
        if errors:
            return False, errors
        else:
            return True, 'جميع البيانات صحيحة'

# إنشاء instance عام للاستخدام
sell_handler = SellCoinsHandler()

# تصدير الدوال للاستخدام الخارجي
def create_sell_request(request_data):
    return sell_handler.create_sell_request(request_data)

def calculate_price(coins_amount, transfer_type='normal'):
    return sell_handler.calculate_price(coins_amount, transfer_type)

def get_sell_request(request_id):
    return sell_handler.get_sell_request(request_id)

def get_user_requests(user_id):
    return sell_handler.get_user_requests(user_id)

def get_statistics():
    return sell_handler.get_statistics()

def validate_coins_amount(coins_amount):
    return sell_handler.validate_coins_amount(coins_amount)
