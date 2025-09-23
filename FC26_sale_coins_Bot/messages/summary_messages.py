# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              📊 FC26 SUMMARY MESSAGES - رسائل الملخصات                 ║
# ║                        Summary Messages                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict, List, Any
from datetime import datetime

class SummaryMessages:
    """Summary and informational messages"""
    
    @staticmethod
    def create_user_profile_summary(user_data: Dict, formatted_data: Dict = None) -> str:
        """Create complete user profile summary"""
        
        formatted = formatted_data or {}
        
        return f"""👤 **ملفك الشخصي - FC26**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📋 البيانات الأساسية**

🎮 **المنصة:** {user_data.get('platform_name', 'غير محدد')}
📱 **رقم الواتساب:** {formatted.get('whatsapp_display', user_data.get('whatsapp', 'غير محدد'))}
💳 **طريقة الدفع:** {user_data.get('payment_name', 'غير محدد')}
💰 **بيانات الدفع:** {formatted.get('payment_display', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📊 معلومات الحساب**

✅ **حالة التسجيل:** مكتمل
📅 **تاريخ التسجيل:** {user_data.get('created_at', 'غير محدد')}
🔄 **آخر تحديث:** {user_data.get('updated_at', 'غير محدد')}
🆔 **معرف المستخدم:** {user_data.get('telegram_id', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 **مرحباً بك في مجتمع FC26!**"""
    
    @staticmethod
    def create_registration_progress_summary(step: str, completed_steps: List[str]) -> str:
        """Create registration progress summary"""
        
        all_steps = [
            ('choosing_platform', '1️⃣ اختيار المنصة'),
            ('entering_whatsapp', '2️⃣ تأكيد رقم الواتساب'),
            ('choosing_payment', '3️⃣ اختيار طريقة الدفع'),
            ('entering_payment_details', '4️⃣ إدخال تفاصيل الدفع'),
            ('completed', '5️⃣ إتمام التسجيل')
        ]
        
        progress_text = "📊 **تقدم التسجيل**\n\n"
        
        for step_key, step_name in all_steps:
            if step_key in completed_steps:
                progress_text += f"✅ {step_name}\n"
            elif step_key == step:
                progress_text += f"🔄 {step_name} ← **جاري الآن**\n"
            else:
                progress_text += f"⏳ {step_name}\n"
        
        # Calculate percentage
        total_steps = len(all_steps)
        completed_count = len(completed_steps)
        percentage = int((completed_count / total_steps) * 100)
        
        progress_text += f"\n📈 **نسبة الإنجاز:** {percentage}%"
        
        return progress_text
    
    @staticmethod
    def create_statistics_summary(stats: Dict) -> str:
        """Create bot statistics summary"""
        return f"""📊 **إحصائيات FC26 Bot**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**👥 المستخدمون**

👤 **إجمالي المستخدمين:** {stats.get('total_users', 0):,}
✅ **المسجلين بالكامل:** {stats.get('completed_registrations', 0):,}
🔄 **قيد التسجيل:** {stats.get('pending_registrations', 0):,}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🎮 المنصات الأكثر شعبية**

🥇 **الأول:** {stats.get('top_platform', 'PlayStation')}
🥈 **الثاني:** {stats.get('second_platform', 'Xbox')}
🥉 **الثالث:** {stats.get('third_platform', 'PC')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**💳 طرق الدفع المفضلة**

🥇 **الأكثر استخداماً:** {stats.get('top_payment', 'فودافون كاش')}
📈 **النمو السريع:** {stats.get('trending_payment', 'إنستاباي')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ **آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    @staticmethod
    def create_daily_report(date: str, metrics: Dict) -> str:
        """Create daily activity report"""
        return f"""📅 **تقرير يومي - {date}**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📊 النشاط اليومي**

🆕 **تسجيلات جديدة:** {metrics.get('new_registrations', 0)}
✅ **تسجيلات مكتملة:** {metrics.get('completed_today', 0)}
📱 **رسائل مرسلة:** {metrics.get('messages_sent', 0)}
❌ **أخطاء:** {metrics.get('errors_count', 0)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🎯 معدل النجاح**

📈 **معدل إكمال التسجيل:** {metrics.get('completion_rate', 0):.1f}%
⚡ **متوسط وقت التسجيل:** {metrics.get('avg_registration_time', 'غير محدد')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔝 الذروات**

⏰ **أكثر الأوقات نشاطاً:** {metrics.get('peak_hour', 'غير محدد')}
🎮 **منصة اليوم:** {metrics.get('platform_of_day', 'غير محدد')}"""
    
    @staticmethod
    def create_help_summary() -> str:
        """Create comprehensive help summary"""
        return """📚 **دليل استخدام FC26 Bot**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🚀 البدء**

/start - بدء أو متابعة التسجيل
/help - عرض هذه المساعدة
/profile - عرض الملف الشخصي

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🎮 المنصات المدعومة**

• PlayStation (PS4/PS5)
• Xbox (One/Series X|S)  
• PC (Origin/Steam/Epic)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**💳 طرق الدفع**

• فودافون كاش (010)
• اتصالات كاش (011)
• أورانج كاش (012)
• وي كاش (015)
• محفظة بنكية
• كارت تيلدا
• إنستاباي

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📱 قواعد الأرقام**

✅ يبدأ بـ: 010, 011, 012, 015
✅ طول: 11 رقماً بالضبط
❌ لا تضع: +20 أو مسافات

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔗 روابط إنستاباي**

✅ يجب أن يحتوي على: instapay.com.eg
✅ مثال: https://instapay.com.eg/abc123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**📞 الدعم الفني**

إذا واجهت أي مشكلة، تواصل مع فريق الدعم وستحصل على المساعدة فوراً."""
    
    @staticmethod
    def create_feature_list() -> str:
        """Create bot features list"""
        return """⭐ **مميزات FC26 Bot**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🔥 المميزات الرئيسية**

✨ **تسجيل سريع وسهل** - 4 خطوات بسيطة
🛡️ **أمان عالي** - حماية شاملة للبيانات
📱 **دعم جميع الشبكات** - كل طرق الدفع المصرية
🎮 **دعم كل المنصات** - PS، Xbox، PC
🔄 **متابعة التقدم** - إكمال من آخر خطوة
💬 **واجهة عربية** - بالعربية بالكامل

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**🚀 مميزات متقدمة**

📋 **نسخ بنقرة** - نسخ البيانات بسهولة
🔍 **تحقق ذكي** - فحص تلقائي للبيانات
⚡ **استجابة سريعة** - رد فوري على جميع الرسائل
🎯 **توجيه ذكي** - إرشادات واضحة لكل خطوة
📊 **تتبع مفصل** - متابعة كاملة للعملية

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎮 **FC26 - الخيار الأول للاعبين المحترفين**"""