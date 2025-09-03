"""
👤 معالج الملف الشخصي
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class ProfileManager:
    """مدير الملفات الشخصية"""
    
    def __init__(self, db_manager):
        """تهيئة مدير الملفات"""
        self.db = db_manager
    
    async def show_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الملف الشخصي"""
        query = update.callback_query
        if query:
            await query.answer()
            
        user = update.effective_user
        
        # جلب بيانات المستخدم
        user_data = await self.db.get_user_by_telegram_id(user.id)
        
        if not user_data:
            text = "❌ لم تقم بالتسجيل بعد!\n\nاضغط /register للبدء"
            if query:
                await query.edit_message_text(text)
            else:
                await update.message.reply_text(text)
            return
        
        # إخفاء رقم البطاقة
        card_masked = "****-****-****-" + user_data.get('card_number_encrypted', '')[-4:]
        
        profile_text = f"""
👤 **حسابك الشخصي**

🆔 **رقم العضوية:** #{user_data['id']}
📅 **تاريخ التسجيل:** {user_data['created_at'][:10]}

**البيانات الأساسية:**
🎮 **المنصة:** {user_data['platform'].title()}
📱 **واتساب:** {user_data['whatsapp']}
💳 **طريقة الدفع:** {user_data['payment_method'].replace('_', ' ').title()}
📞 **الهاتف:** {user_data['phone']}
💳 **البطاقة:** {card_masked}
🔗 **انستا باي:** {user_data.get('instapay_link', 'لا يوجد')}
📧 **الإيميلات:** {', '.join(user_data.get('emails', [])) if user_data.get('emails') else 'لا يوجد'}

⭐ **Trust Score:** {user_data.get('trust_score', 50)}/100
✅ **الحالة:** {'نشط' if user_data.get('is_active') else 'غير نشط'}
"""
        
        keyboard = [
            [
                InlineKeyboardButton("✏️ تعديل البيانات", callback_data="edit_profile"),
                InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")
            ],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            await query.edit_message_text(
                profile_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                profile_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )