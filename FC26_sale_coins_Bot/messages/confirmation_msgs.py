# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              🎉 FC26 CONFIRMATION MESSAGES - رسائل التأكيد              ║
# ║                      Confirmation Messages                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Any, Dict


class ConfirmationMessages:
    """Payment confirmation and success messages"""

    @staticmethod
    def create_payment_confirmation(
        payment_method: str, validation: Dict, payment_name: str
    ) -> str:
        """Create beautiful payment confirmation message"""

        # Mobile wallets confirmation
        if payment_method in [
            "vodafone_cash",
            "etisalat_cash",
            "orange_cash",
            "we_cash",
            "bank_wallet",
        ]:
            return f"""✅ تم حفظ {payment_name}!

📱 الرقم: {validation['display']}

━━━━━━━━━━━━━━━━"""

        # Telda card confirmation (بدون تشفير)
        elif payment_method == "telda":
            return f"""✅ تم حفظ كارت تيلدا!

💳 رقم الكارت: {validation['display']}

━━━━━━━━━━━━━━━━"""

        # InstaPay confirmation
        elif payment_method == "instapay":
            return f"""✅ تم حفظ رابط إنستاباي!

🔗 الرابط: {validation['display']}

━━━━━━━━━━━━━━━━"""

        # Fallback for unknown methods
        else:
            return f"""✅ تم حفظ {payment_name}!

💰 التفاصيل: {validation.get('display', 'غير محدد')}

━━━━━━━━━━━━━━━━"""

    @staticmethod
    def create_whatsapp_confirmation(validation: Dict) -> str:
        """Create WhatsApp confirmation message"""
        return f"""✅ تم حفظ رقم الواتساب!

📱 الرقم: {validation['display']}

━━━━━━━━━━━━━━━━"""

    @staticmethod
    def create_final_summary(
        user_data: Dict, payment_name: str, validation: Dict, user_info: Dict
    ) -> str:
        """Create enhanced final registration summary"""

        # Format payment details based on method
        if user_data["payment_method"] == "telda":
            # For Telda, show full card number (غير مشفر)
            payment_details_line = f"• رقم الكارت: {validation['display']}"

        elif user_data["payment_method"] == "instapay":
            # For InstaPay, show the clean URL
            payment_details_line = f"• الرابط: {validation['display']}"

        else:
            # For mobile wallets, show the phone number
            payment_details_line = f"• الرقم: {validation['display']}"

        return f"""
✅ تم تحديث بياناتك بنجاح!

📊 ملخص البيانات المحدثة:
━━━━━━━━━━━━━━━━
🎮 المنصة: {user_data.get('platform_name', 'غير محدد')}
📱 واتساب: {user_data['whatsapp']}
💳 طريقة الدفع: {payment_name}
💰 بيانات الدفع:
{payment_details_line}
━━━━━━━━━━━━━━━━

👤 اسم المستخدم: @{user_info.get('username', 'غير متوفر')}
🆔 معرف التليجرام: {user_info['id']}

✨ تم تحديث ملفك الشخصي بنجاح!"""

    @staticmethod
    def create_registration_completed_message(
        user_data: Dict, display_format: Dict
    ) -> str:
        """Create message for already completed registration"""

        return f"""✅ **تسجيلك مكتمل بالفعل!**

📋 **ملخص بياناتك:**

🎮 **المنصة:** {user_data.get('platform_name', 'غير محدد')}
📱 **الواتساب:** {display_format.get('whatsapp_display', user_data.get('whatsapp', 'غير محدد'))}
💳 **الدفع:** {user_data.get('payment_name', 'غير محدد')}
💰 **التفاصيل:** {display_format.get('payment_display', 'غير محدد')}

🚀 **مرحباً بك في عائلة FC26!**"""

    @staticmethod
    def create_data_updated_message() -> str:
        """Create data updated confirmation"""
        return """✅ **تم تحديث بياناتك بنجاح!**

🔄 **ماذا حدث:**
• تم حفظ جميع المعلومات
• تم تحديث ملفك الشخصي
• أصبحت جاهزاً لاستخدام الخدمات

🎮 **الخطوات التالية:**
• يمكنك الآن استخدام جميع خدمات FC26
• تواصل معنا للحصول على المساعدة
• راجع ملفك الشخصي للتأكد من البيانات

🚀 **مرحباً بك في FC26!**"""

    @staticmethod
    def create_step_completed_message(step_name: str, next_step: str = None) -> str:
        """Create step completion message"""
        base_message = f"✅ **تم إكمال: {step_name}**\n\n"

        if next_step:
            base_message += f"➡️ **الخطوة التالية:** {next_step}\n\n"

        base_message += "🎯 **أنت تتقدم بشكل ممتاز!**"

        return base_message

    @staticmethod
    def create_profile_summary(user_data: Dict, formatted_data: Dict = None) -> str:
        """Create complete profile summary"""

        formatted = formatted_data or {}

        return f"""👤 **ملفك الشخصي في FC26**

━━━━━━━━━━━━━━━━
**📋 البيانات الأساسية:**

🎮 **المنصة:** {user_data.get('platform_name', 'غير محدد')}
📱 **الواتساب:** {formatted.get('whatsapp_display', user_data.get('whatsapp', 'غير محدد'))}
💳 **طريقة الدفع:** {user_data.get('payment_name', 'غير محدد')}
💰 **بيانات الدفع:** {formatted.get('payment_display', 'غير محدد')}

━━━━━━━━━━━━━━━━
**⏰ معلومات التسجيل:**

📅 **تاريخ التسجيل:** {user_data.get('created_at', 'غير محدد')}
🔄 **آخر تحديث:** {user_data.get('updated_at', 'غير محدد')}
✅ **حالة التسجيل:** مكتمل

━━━━━━━━━━━━━━━━
🎮 **مرحباً بك في عائلة FC26!**"""

    @staticmethod
    def create_success_animation() -> str:
        """Create animated success message"""
        return """🎉✨🎉✨🎉✨🎉✨🎉

      🏆 **نجح التسجيل!** 🏆

      🎮 FC26 Gaming Community 🎮

🎉✨🎉✨🎉✨🎉✨🎉

✅ **أهلاً بك في الفريق!**"""
