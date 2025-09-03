# validators.py - وزارة التحقق المعزولة
"""
🔥 وزارة التحقق - FC 26 Profile System
========================================
مسؤولة عن جميع عمليات التحقق من صحة البيانات
- التحقق من أرقام الواتساب المصرية
- التحقق من طرق الدفع المختلفة
- معالجة الروابط والبطاقات
- تنظيف وتطبيع البيانات
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup
import numpy as np
from urllib.parse import urlparse


class DataValidator:
    """الكلاس الأساسي لجميع عمليات التحقق"""
    
    def __init__(self):
        self.egyptian_carriers = {
            '010': {'name': 'فودافون مصر', 'carrier_en': 'Vodafone Egypt'},
            '011': {'name': 'اتصالات مصر', 'carrier_en': 'Etisalat Egypt'},
            '012': {'name': 'أورانج مصر', 'carrier_en': 'Orange Egypt'},
            '015': {'name': 'وي مصر', 'carrier_en': 'WE Egypt (Telecom Egypt)'}
        }
    
    def sanitize_input(self, text):
        """تنظيف المدخلات من الأكواد الضارة"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()


class WhatsAppValidator(DataValidator):
    """وحدة التحقق من أرقام الواتساب"""
    
    def validate_egyptian_mobile_instant(self, phone_input):
        """🔥 تحقق فوري من الرقم المصري - نظام المحافظ الرقمية (11 رقم فقط)"""
        if not phone_input:
            return {
                'is_valid': False,
                'error': 'يرجى إدخال رقم الهاتف',
                'code': 'empty_input'
            }
        
        # إزالة كل شيء عدا الأرقام
        clean_digits = re.sub(r'[^\d]', '', str(phone_input).strip())
        
        # 🚫 رفض فوري إذا لم يكن 11 رقم بالضبط
        if len(clean_digits) != 11:
            return {
                'is_valid': False,
                'error': f'يجب أن يكون 11 رقماً بالضبط (تم إدخال {len(clean_digits)} رقم)',
                'code': 'invalid_length',
                'entered_length': len(clean_digits),
                'expected_length': 11
            }
        
        # 🚫 التحقق من بداية الرقم - يجب أن يبدأ بـ 01
        if not clean_digits.startswith('01'):
            return {
                'is_valid': False,
                'error': 'يجب أن يبدأ الرقم بـ 01 (رقم مصري)',
                'code': 'invalid_country_prefix'
            }
        
        # 🚫 التحقق من كود الشركة - يجب أن يكون 010/011/012/015
        carrier_code = clean_digits[:3]
        if carrier_code not in ['010', '011', '012', '015']:
            return {
                'is_valid': False,
                'error': f'كود الشركة {carrier_code} غير صحيح - يجب أن يكون 010/011/012/015',
                'code': 'invalid_carrier_code',
                'entered_carrier': carrier_code,
                'valid_carriers': ['010', '011', '012', '015']
            }
        
        # ✅ الرقم صحيح - معلومات الشركة
        carrier_info = self.egyptian_carriers.get(carrier_code, {
            'name': 'غير معروف',
            'carrier_en': 'Unknown'
        })
        
        # ✅ إرجاع النتيجة النهائية للرقم الصحيح
        return {
            'is_valid': True,
            'clean_number': clean_digits,
            'formatted_number': f"+2{clean_digits}",
            'display_number': f"0{clean_digits[1:3]} {clean_digits[3:6]} {clean_digits[6:]}",
            'carrier_code': carrier_code,
            'carrier_name': carrier_info['name'],
            'carrier_en': carrier_info['carrier_en'],
            'country': 'مصر',
            'country_code': '+2',
            'validation_type': 'instant_wallet_style',
            'message': f'✅ رقم {carrier_info["name"]} صحيح',
            'code': 'valid_egyptian_mobile'
        }
    
    def normalize_phone_number(self, phone):
        """تطبيع رقم الهاتف - نظام المحافظ (11 رقم فقط)"""
        if not phone:
            return ""
        
        # 🔥 استخدام التحقق الفوري الجديد
        validation_result = self.validate_egyptian_mobile_instant(phone)
        
        # إرجاع الرقم المنسق أو فارغ في حالة الخطأ
        if validation_result['is_valid']:
            return validation_result['formatted_number']
        else:
            return ""  # رفض تام للأرقام غير الصحيحة
    
    def check_whatsapp_ultimate_method(self, phone_number):
        """🔥 الطريقة النهائية المبتكرة - تجمع كل الحلول الذكية"""
        results = []
        clean_phone = phone_number.replace('+', '').replace(' ', '')
        
        # الطريقة 1: Advanced Scraping
        try:
            time.sleep(random.uniform(0.1, 0.5))  # محاكاة سلوك إنساني
            
            url = f"https://wa.me/{clean_phone}?text=Test"
            session_req = requests.Session()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ar,en;q=0.9',
                'Connection': 'keep-alive'
            }
            
            response = session_req.get(url, headers=headers, timeout=8, allow_redirects=True)
            
            # تحليل محتوى متقدم
            soup = BeautifulSoup(response.text, 'html.parser')
            page_content = response.text.lower()
            
            success_indicators = ['continue to chat', 'المتابعة إلى الدردشة', 'open whatsapp', 'whatsapp://send']
            error_indicators = ['phone number shared via url is invalid', 'رقم الهاتف غير صحيح', 'invalid phone']
            
            scraping_result = None
            for indicator in success_indicators:
                if indicator.lower() in page_content:
                    scraping_result = True
                    break
                    
            if scraping_result is None:
                for indicator in error_indicators:
                    if indicator.lower() in page_content:
                        scraping_result = False
                        break
            
            results.append({
                'method': 'advanced_scraping',
                'result': scraping_result,
                'confidence': 0.8 if scraping_result is not None else 0.3
            })
            
        except:
            results.append({
                'method': 'advanced_scraping',
                'result': None,
                'confidence': 0.1
            })
        
        # الطريقة 2: Multiple Endpoints
        try:
            endpoints = [
                f"https://wa.me/{clean_phone}",
                f"https://api.whatsapp.com/send?phone={clean_phone}",
                f"https://web.whatsapp.com/send?phone={clean_phone}"
            ]
            
            success_count = 0
            total_count = 0
            
            for endpoint in endpoints:
                try:
                    resp = requests.head(endpoint, timeout=3, allow_redirects=True)
                    total_count += 1
                    if resp.status_code in [200, 302]:
                        success_count += 1
                except:
                    total_count += 1
            
            endpoint_result = success_count > (total_count / 2) if total_count > 0 else None
            endpoint_confidence = (success_count / total_count) if total_count > 0 else 0.1
            
            results.append({
                'method': 'multiple_endpoints',
                'result': endpoint_result,
                'confidence': endpoint_confidence
            })
            
        except:
            results.append({
                'method': 'multiple_endpoints',
                'result': None,
                'confidence': 0.1
            })
        
        # الطريقة 3: AI Pattern Recognition
        try:
            # خصائص للتحليل
            features = []
            features.append(len(clean_phone))  # طول الرقم
            
            # تحليل كود البلد
            egypt_patterns = ['2010', '2011', '2012', '2015']
            has_egypt_pattern = any(clean_phone.startswith(pattern) for pattern in egypt_patterns)
            features.append(int(has_egypt_pattern))
            
            # تحليل الأرقام
            if len(clean_phone) > 0:
                digits = [int(d) for d in clean_phone if d.isdigit()]
                if digits:
                    features.extend([
                        np.mean(digits),
                        len(set(digits)),
                        int(len(clean_phone) >= 10 and len(clean_phone) <= 15)
                    ])
                else:
                    features.extend([0, 0, 0])
            else:
                features.extend([0, 0, 0])
            
            # حساب نقاط الثقة بناءً على الخصائص
            ai_score = 0.5  # قيمة افتراضية
            
            # للأرقام المصرية الصحيحة
            if has_egypt_pattern and len(clean_phone) == 12:
                ai_score = 0.9
            elif len(clean_phone) >= 10 and len(clean_phone) <= 15:
                ai_score = 0.7
            elif len(clean_phone) < 8 or len(clean_phone) > 16:
                ai_score = 0.2
            
            ai_result = ai_score > 0.6
            
            results.append({
                'method': 'ai_pattern',
                'result': ai_result,
                'confidence': ai_score
            })
            
        except:
            results.append({
                'method': 'ai_pattern',
                'result': None,
                'confidence': 0.1
            })
        
        # تحليل النتائج النهائية
        valid_results = [r for r in results if r['result'] is not None]
        
        if not valid_results:
            return {
                'exists': None,
                'method': 'ultimate_combined',
                'confidence': 'very_low',
                'details': results,
                'message': 'لا يمكن التحقق من الرقم - جميع الطرق فشلت'
            }
        
        # حساب النتيجة المرجحة
        positive_weight = sum(r['confidence'] for r in valid_results if r['result'] is True)
        negative_weight = sum(r['confidence'] for r in valid_results if r['result'] is False)
        total_weight = positive_weight + negative_weight
        
        if total_weight == 0:
            final_result = None
            confidence_level = 'very_low'
        else:
            final_score = positive_weight / total_weight
            final_result = final_score > 0.5
            
            if final_score > 0.8:
                confidence_level = 'very_high'
            elif final_score > 0.6:
                confidence_level = 'high'
            elif final_score > 0.4:
                confidence_level = 'medium'
            else:
                confidence_level = 'low'
        
        return {
            'exists': final_result,
            'method': 'ultimate_combined',
            'confidence': confidence_level,
            'score': round(positive_weight / total_weight * 100, 1) if total_weight > 0 else 0,
            'methods_used': len(results),
            'successful_methods': len(valid_results),
            'details': results,
            'message': f'تحليل شامل: {len(valid_results)} طرق نجحت من {len(results)} - نسبة الثقة {round(positive_weight / total_weight * 100, 1) if total_weight > 0 else 0}%'
        }
    
    def validate_whatsapp_ultimate(self, phone):
        """🔥 التحقق النهائي من الواتساب - نظام المحافظ الرقمية (11 رقم فقط)"""
        
        # 🚀 التحقق الفوري السريع مثل المحافظ الرقمية
        instant_validation = self.validate_egyptian_mobile_instant(phone)
        
        # ❌ في حالة فشل التحقق الفوري
        if not instant_validation['is_valid']:
            return {
                'is_valid': False,
                'error': instant_validation['error'],
                'error_code': instant_validation['code'],
                'validation_details': instant_validation,
                'validation_type': 'instant_wallet_rejection'
            }
        
        # ✅ الرقم نجح في التحقق الفوري
        mobile_data = instant_validation
        normalized_phone = mobile_data['formatted_number']
        
        # 📱 طباعة إشعار التحقق السريع
        print(f"⚡ تم التحقق الفوري من الرقم: {mobile_data['display_number']} ({mobile_data['carrier_name']})")
        
        # 🔍 التحقق من الواتساب بالطرق المتقدمة
        whatsapp_check = self.check_whatsapp_ultimate_method(normalized_phone)
        
        # 📊 تحضير النتيجة النهائية الشاملة
        base_result = {
            'is_valid': True,
            'formatted': normalized_phone,
            'display_number': mobile_data['display_number'],
            'clean_number': mobile_data['clean_number'],
            'country': mobile_data['country'],
            'country_code': mobile_data['country_code'],
            'carrier': mobile_data['carrier_name'],
            'carrier_en': mobile_data['carrier_en'],
            'carrier_code': mobile_data['carrier_code'],
            'validation_type': 'wallet_style_instant',
            'instant_check_passed': True,
            'mobile_validation': mobile_data,
            'verification_method': whatsapp_check['method'],
            'methods_analysis': whatsapp_check.get('details', [])
        }
        
        # 🟢 واتساب موجود
        if whatsapp_check['exists'] is True:
            return {
                **base_result,
                'whatsapp_status': f'موجود ✅ ({whatsapp_check["confidence"]})',
                'confidence': whatsapp_check['confidence'],
                'score': whatsapp_check.get('score', 0),
                'message': f'✅ رقم {mobile_data["carrier_name"]} صحيح - {whatsapp_check["message"]}',
                'whatsapp_exists': True
            }
        
        # 🔴 واتساب غير موجود
        elif whatsapp_check['exists'] is False:
            return {
                **base_result,
                'is_valid': False,
                'error': f"واتساب غير موجود ❌ ({whatsapp_check['confidence']}) - {whatsapp_check['message']}",
                'whatsapp_status': f'غير موجود ❌ ({whatsapp_check["confidence"]})',
                'confidence': whatsapp_check['confidence'],
                'message': f'❌ رقم {mobile_data["carrier_name"]} صحيح لكن الواتساب غير موجود',
                'whatsapp_exists': False
            }
        
        # ⚠️ واتساب غير مؤكد
        else:
            return {
                **base_result,
                'whatsapp_status': f'غير مؤكد ⚠️ ({whatsapp_check["confidence"]})',
                'confidence': whatsapp_check['confidence'],
                'message': f'⚠️ رقم {mobile_data["carrier_name"]} صحيح - {whatsapp_check["message"]}',
                'whatsapp_exists': None,
                'warning': 'لا يمكن التأكد من وجود الواتساب'
            }


class PaymentValidator(DataValidator):
    """وحدة التحقق من طرق الدفع"""
    
    def validate_mobile_payment(self, payment_number):
        """التحقق من صحة رقم الدفع المحمول"""
        if not payment_number:
            return False
        clean_number = re.sub(r'\D', '', payment_number)
        return len(clean_number) == 11 and clean_number.startswith(('010', '011', '012', '015'))
    
    def validate_card_number(self, card_number):
        """التحقق من صحة رقم البطاقة"""
        if not card_number:
            return False
        clean_number = re.sub(r'\D', '', card_number)
        return len(clean_number) == 16 and clean_number.isdigit()
    
    def validate_instapay_link(self, input_text):
        """استخلاص وتحقق ذكي من روابط InstaPay"""
        if not input_text:
            return False, ""
        
        # تنظيف النص من الأسطر الجديدة والمسافات الزائدة
        clean_text = input_text.strip().replace('\n', ' ').replace('\r', ' ')
        
        # أنماط البحث المتقدمة لروابط InstaPay
        instapay_patterns = [
            # الأنماط الأساسية
            r'https?://(?:www\.)?ipn\.eg/S/[^/\s]+/instapay/[A-Za-z0-9]+',
            r'https?://(?:www\.)?instapay\.com\.eg/[^\s<>"{}|\\^`\[\]]+',
            r'https?://(?:www\.)?app\.instapay\.com\.eg/[^\s<>"{}|\\^`\[\]]+',
            r'https?://(?:www\.)?instapay\.app/[^\s<>"{}|\\^`\[\]]+',
            
            # أنماط متقدمة للروابط المختصرة
            r'https?://(?:www\.)?ipn\.eg/[^\s<>"{}|\\^`\[\]]+',
            r'https?://(?:www\.)?pay\.instapay\.com\.eg/[^\s<>"{}|\\^`\[\]]+',
            
            # أنماط للروابط مع معاملات
            r'https?://[^\s<>"{}|\\^`\[\]]*instapay[^\s<>"{}|\\^`\[\]]*',
        ]
        
        extracted_links = []
        
        # البحث باستخدام كل نمط
        for pattern in instapay_patterns:
            matches = re.findall(pattern, clean_text, re.IGNORECASE)
            extracted_links.extend(matches)
        
        # إزالة المكررات والاحتفاظ بالترتيب
        unique_links = list(dict.fromkeys(extracted_links))
        
        # فلترة الروابط وتنظيفها
        valid_links = []
        for link in unique_links:
            # تنظيف الرابط من العلامات في النهاية
            cleaned_link = re.sub(r'[.,;!?]+$', '', link.strip())
            
            # التحقق من صحة الرابط
            if self.is_valid_instapay_url(cleaned_link):
                valid_links.append(cleaned_link)
        
        # إرجاع أفضل رابط موجود
        if valid_links:
            best_link = self.select_best_instapay_link(valid_links)
            return True, best_link
        
        return False, ""
    
    def is_valid_instapay_url(self, url):
        """التحقق من صحة رابط InstaPay"""
        if not url or not url.startswith(('http://', 'https://')):
            return False
        
        # قائمة النطاقات الصحيحة
        valid_domains = [
            'ipn.eg',
            'instapay.com.eg',
            'app.instapay.com.eg',
            'instapay.app',
            'pay.instapay.com.eg'
        ]
        
        try:
            parsed = urlparse(url.lower())
            domain = parsed.netloc.replace('www.', '')
            
            # التحقق من النطاق
            domain_valid = any(valid_domain in domain for valid_domain in valid_domains)
            
            # التحقق من طول الرابط (ليس قصير جداً)
            length_valid = len(url) >= 20
            
            # التحقق من وجود معرف في الرابط
            has_identifier = len(parsed.path) > 3
            
            return domain_valid and length_valid and has_identifier
            
        except:
            return False
    
    def select_best_instapay_link(self, links):
        """اختيار أفضل رابط من القائمة"""
        if not links:
            return ""
        
        # ترتيب الأولويات
        priority_domains = [
            'ipn.eg/S/',  # الأولوية العليا
            'instapay.com.eg',
            'app.instapay.com.eg',
            'instapay.app'
        ]
        
        # البحث عن رابط بأولوية عالية
        for priority in priority_domains:
            for link in links:
                if priority in link.lower():
                    return link
        
        # إذا لم يوجد، إرجاع الأول
        return links[0]
    
    def extract_instapay_info(self, url):
        """استخلاص معلومات إضافية من رابط InstaPay"""
        info = {
            'url': url,
            'domain': '',
            'username': '',
            'code': '',
            'type': 'unknown'
        }
        
        try:
            parsed = urlparse(url)
            info['domain'] = parsed.netloc.replace('www.', '')
            
            # استخلاص اسم المستخدم والكود من رابط ipn.eg
            if 'ipn.eg' in info['domain']:
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 4 and path_parts[0] == 'S':
                    info['username'] = path_parts[1]
                    info['code'] = path_parts[3] if len(path_parts) > 3 else ''
                    info['type'] = 'standard'
            
        except:
            pass
        
        return info


# إنشاء instances للاستخدام المباشر
whatsapp_validator = WhatsAppValidator()
payment_validator = PaymentValidator()

# تصدير الدوال للتوافق مع الكود الأصلي
def validate_whatsapp_ultimate(phone):
    return whatsapp_validator.validate_whatsapp_ultimate(phone)

def validate_mobile_payment(payment_number):
    return payment_validator.validate_mobile_payment(payment_number)

def validate_card_number(card_number):
    return payment_validator.validate_card_number(card_number)

def validate_instapay_link(input_text):
    return payment_validator.validate_instapay_link(input_text)

def sanitize_input(text):
    return whatsapp_validator.sanitize_input(text)

def normalize_phone_number(phone):
    return whatsapp_validator.normalize_phone_number(phone)
