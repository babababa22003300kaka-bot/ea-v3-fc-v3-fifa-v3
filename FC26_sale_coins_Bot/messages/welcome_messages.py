# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎮 FC26 WELCOME MESSAGES - رسائل الترحيب                   ║
# ║                      Welcome & Greeting Messages                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict

class WelcomeMessages:
    """Welcome and greeting messages for the bot"""
    
    @staticmethod
    def get_start_message() -> str:
        """Get main start/welcome message"""
        return """🎮 **مرحباً بك في FC26**
منصة الألعاب الاحترافية

🚀 **اختر منصتك المفضلة للبدء:**

**🎯 خطوات التسجيل:**

1️⃣ اختيار المنصة
2️⃣ تأكيد رقم الواتساب
3️⃣ اختيار طريقة الدفع
4️⃣ إدخال تفاصيل الدفع
5️⃣ إتمام التسجيل

🔥 **ابدأ رحلتك الآن!**"""
    
    @staticmethod
    def get_platform_selected_message(platform_name: str) -> str:
        """Get platform selection success message"""
        return f"""✅ **تم اختيار المنصة بنجاح!**

🎮 **المنصة المختارة:** {platform_name}

**📱 تأكيد رقم الواتساب**

🔹 أرسل رقم الواتساب الخاص بك
🔹 **مثال:** 01012345678
🔹 **يجب أن يبدأ بـ:** 010, 011, 012, أو 015

⚠️ **تأكد من صحة الرقم لأنه سيتم التواصل معك عليه**"""
    
    @staticmethod
    def get_whatsapp_confirmed_message(phone_display: str) -> str:
        """Get WhatsApp confirmation message"""
        return f"""✅ **تم تأكيد رقم الواتساب بنجاح!**

📱 **الواتساب:** `{phone_display}`

**💳 اختيار طريقة الدفع**

🔹 **اختر الطريقة المناسبة لك:**

**📋 قائمة طرق الدفع الكاملة:**

⭕️ **فودافون كاش** - رقم 11 خانة يبدأ بـ 010/011/012/015
🟢 **اتصالات كاش** - رقم 11 خانة يبدأ بـ 010/011/012/015
🍊 **أورانج كاش** - رقم 11 خانة يبدأ بـ 010/011/012/015
🟣 **وي كاش** - رقم 11 خانة يبدأ بـ 010/011/012/015
🏦 **محفظة بنكية** - رقم 11 خانة لأي شبكة مصرية
💳 **تيلدا** - رقم كارت 16 رقماً بالضبط
🔗 **إنستا باي** - رابط كامل يحتوي على instapay.com.eg أو ipn.eg"""
    
    @staticmethod
    def get_payment_method_selected_message(payment_name: str, instruction: str) -> str:
        """Get payment method selection message"""
        return f"""✅ **تم اختيار طريقة الدفع بنجاح!**

💳 **طريقة الدفع:** {payment_name}

**📝 إدخال التفاصيل**

🔹 {instruction}

⚠️ **تأكد من صحة البيانات قبل الإرسال**"""
    
    @staticmethod
    def get_continue_registration_message(step: str, context: Dict = None) -> str:
        """Get continue registration message based on current step"""
        base_message = "🔄 **استكمال التسجيل**\n\n"
        
        if step == "choosing_platform":
            return base_message + """🎮 **اختر منصتك المفضلة:**

📍 **موضعك الحالي:** اختيار المنصة"""
        
        elif step == "entering_whatsapp" and context:
            return base_message + f"""🎮 **المنصة:** {context.get('platform_name', 'غير محدد')}

**📱 أرسل رقم الواتساب الخاص بك:**

🔹 **مثال:** 01012345678
🔹 **يجب أن يبدأ بـ:** 010, 011, 012, أو 015

📍 **موضعك الحالي:** تأكيد رقم الواتساب"""
        
        elif step == "choosing_payment" and context:
            return base_message + f"""📱 **الواتساب:** `{context.get('whatsapp', 'غير محدد')}`

**💳 اختر طريقة الدفع:**

📍 **موضعك الحالي:** اختيار طريقة الدفع"""
        
        elif step == "entering_payment_details" and context:
            return base_message + f"""💳 **طريقة الدفع:** {context.get('payment_name', 'غير محدد')}

**📝 أرسل تفاصيل الدفع:**

🔹 {context.get('instruction', 'أدخل التفاصيل')}

📍 **موضعك الحالي:** إدخال تفاصيل الدفع"""
        
        else:
            return base_message + "📍 **موضعك الحالي:** غير محدد"
    
    @staticmethod
    def get_help_message() -> str:
        """Get help message"""
        return """📚 **مساعدة FC26 Gaming Bot**

**🎮 المنصات المدعومة:**
• PlayStation (PS4/PS5)
• Xbox (One/Series X|S)
• PC (Origin/Steam)

**💳 طرق الدفع المدعومة:**
• فودافون كاش (010)
• اتصالات كاش (011)
• أورانج كاش (012)
• وي كاش (015)
• محفظة بنكية (أي شبكة)
• كارت تيلدا (16 رقم)
• إنستا باي (رابط كامل)

**📱 أرقام الهاتف:**
• يجب أن تبدأ بـ 010/011/012/015
• يجب أن تتكون من 11 رقماً بالضبط
• لا تضع كود الدولة (+20)

**🔗 روابط إنستاباي:**
• يجب أن تحتوي على instapay.com.eg
• أو ipn.eg
• مثال: https://instapay.com.eg/abc123

**📞 للدعم الفني:**
تواصل مع فريق الدعم إذا واجهت أي مشكلة"""
    
    @staticmethod
    def get_about_message() -> str:
        """Get about bot message"""
        return """ℹ️ **حول FC26 Gaming Bot**

🎮 **عن المنصة:**
FC26 هي منصة احترافية لألعاب FIFA و EA Sports FC، نوفر خدمات متنوعة للاعبين في المنطقة العربية.

🚀 **خدماتنا:**
• شراء وبيع العملات
• تجارة اللاعبين
• خدمات التطوير
• دعم فني متخصص

🔐 **الأمان:**
• حماية كاملة للبيانات
• معاملات آمنة ومضمونة
• دعم فني على مدار الساعة

💎 **الجودة:**
• فريق محترف ومتخصص
• أسعار تنافسية
• خدمة سريعة وموثوقة

📞 **التواصل:**
نحن هنا لخدمتك في أي وقت"""