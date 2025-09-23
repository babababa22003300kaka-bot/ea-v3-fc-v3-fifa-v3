# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              ❌ FC26 ERROR MESSAGES - رسائل الأخطاء                     ║
# ║                         Error Messages                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict, Optional

class ErrorMessages:
    """Error and warning messages for the bot"""
    
    @staticmethod
    def get_general_error() -> str:
        """General error message"""
        return "❌ حدث خطأ، حاول مرة أخرى"
    
    @staticmethod
    def get_database_error() -> str:
        """Database error message"""
        return "❌ خطأ في قاعدة البيانات، حاول مرة أخرى"
    
    @staticmethod
    def get_validation_error(details: str = None) -> str:
        """Validation error with optional details"""
        base_message = "❌ البيانات المدخلة غير صحيحة"
        if details:
            return f"{base_message}\n\n📋 **التفاصيل:** {details}"
        return base_message
    
    @staticmethod
    def get_invalid_platform_error() -> str:
        """Invalid platform error"""
        return "❌ منصة غير صحيحة"
    
    @staticmethod
    def get_invalid_payment_error() -> str:
        """Invalid payment method error"""
        return "❌ طريقة دفع غير صحيحة"
    
    @staticmethod
    def get_start_required_error() -> str:
        """Start command required error"""
        return "🚀 اكتب /start للبدء!"
    
    @staticmethod
    def get_restart_required_error() -> str:
        """Restart required error"""
        return "🚀 اكتب /start للبدء من جديد!"
    
    @staticmethod
    def get_phone_validation_error(error_details: str = None) -> str:
        """Phone number validation error with tips"""
        base_error = error_details or "❌ رقم الهاتف غير صحيح"
        
        return f"""{base_error}

💡 **نصائح:**
• تأكد من البدء بـ 010, 011, 012, أو 015
• أدخل 11 رقماً بالضبط
• لا تضع كود الدولة (+20)

🔹 **أمثلة صحيحة:**
• 01012345678
• 01112345678
• 01212345678
• 01512345678"""
    
    @staticmethod
    def get_payment_validation_error(payment_method: str, error_details: str = None) -> str:
        """Payment validation error with method-specific tips"""
        base_error = error_details or "❌ بيانات الدفع غير صحيحة"
        
        tips = {
            'vodafone_cash': "💡 **فودافون كاش:** رقم 11 خانة يبدأ بـ 010",
            'etisalat_cash': "💡 **اتصالات كاش:** رقم 11 خانة يبدأ بـ 011", 
            'orange_cash': "💡 **أورانج كاش:** رقم 11 خانة يبدأ بـ 012",
            'we_cash': "💡 **وي كاش:** رقم 11 خانة يبدأ بـ 015",
            'bank_wallet': "💡 **محفظة بنكية:** رقم 11 خانة لأي شبكة",
            'telda': "💡 **تيلدا:** 16 رقماً بدون مسافات أو شرطات\n**مثال:** 1234567890123456",
            'instapay': "💡 **إنستاباي:** رابط كامل\n**مثال:** https://instapay.com.eg/abc123"
        }
        
        tip = tips.get(payment_method, "💡 تحقق من صحة البيانات المدخلة")
        
        return f"""{base_error}

{tip}"""
    
    @staticmethod
    def get_url_validation_error(error_details: str = None) -> str:
        """URL validation error for InstaPay"""
        base_error = error_details or "❌ رابط إنستاباي غير صحيح"
        
        return f"""{base_error}

💡 **نصائح لرابط إنستاباي:**
• يجب أن يحتوي على instapay.com.eg أو ipn.eg
• انسخ الرابط كاملاً من التطبيق
• تأكد من صحة الرابط

🔹 **مثال صحيح:**
https://instapay.com.eg/abc123"""
    
    @staticmethod
    def get_rate_limit_error() -> str:
        """Rate limiting error"""
        return """⏳ **تم تجاوز الحد المسموح**

🔹 **الرجاء الانتظار قليلاً ثم المحاولة مرة أخرى**
🔹 **هذا للحماية من الاستخدام المفرط**

⏰ **حاول مرة أخرى خلال دقيقة**"""
    
    @staticmethod
    def get_maintenance_error() -> str:
        """Maintenance mode error"""
        return """🔧 **البوت تحت الصيانة**

⏳ **نعتذر للإزعاج، نحن نعمل على تحسين الخدمة**

🔄 **سيعود البوت للعمل قريباً**
📞 **للضرورة القصوى، تواصل مع الدعم الفني**"""
    
    @staticmethod
    def get_user_not_found_error() -> str:
        """User not found error"""
        return """❌ **لم يتم العثور على بياناتك**

🚀 **اكتب /start لبدء التسجيل من جديد**"""
    
    @staticmethod
    def get_session_expired_error() -> str:
        """Session expired error"""
        return """⏰ **انتهت صلاحية الجلسة**

🔄 **الرجاء بدء التسجيل من جديد**
🚀 **اكتب /start للمتابعة**"""
    
    @staticmethod
    def get_security_error() -> str:
        """Security violation error"""
        return """🛡️ **تم اكتشاف نشاط مشبوه**

⚠️ **تم حظر العملية لأسباب أمنية**
📞 **تواصل مع الدعم الفني إذا كان هذا خطأ**"""
    
    @staticmethod
    def get_network_error() -> str:
        """Network/connection error"""
        return """🌐 **مشكلة في الاتصال**

🔄 **الرجاء المحاولة مرة أخرى**
📡 **تأكد من جودة الاتصال بالإنترنت**"""
    
    @staticmethod
    def get_file_error() -> str:
        """File operation error"""
        return """📁 **خطأ في العملية**

❌ **لم يتم حفظ البيانات بنجاح**
🔄 **الرجاء المحاولة مرة أخرى**"""
    
    @staticmethod
    def format_error_with_code(error_code: str, message: str) -> str:
        """Format error message with error code"""
        return f"""❌ **خطأ #{error_code}**

{message}

🔍 **كود الخطأ:** {error_code}
📞 **اذكر هذا الكود عند التواصل مع الدعم**"""
    
    @staticmethod
    def get_custom_error(title: str, message: str, suggestions: list = None) -> str:
        """Create custom error message"""
        error_msg = f"""❌ **{title}**

{message}"""
        
        if suggestions:
            error_msg += "\n\n💡 **اقتراحات:**"
            for suggestion in suggestions:
                error_msg += f"\n• {suggestion}"
        
        return error_msg