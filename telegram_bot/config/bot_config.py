"""
⚙️ إعدادات البوت
"""

import os
from pathlib import Path

class BotConfig:
    """إعدادات البوت المركزية"""
    
    # توكن البوت
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7607085569:AAHHE4ddOM4LqJNocOHz0htE7x5zHeqyhRE')
    
    # معرف الأدمن
    ADMIN_ID = 1124247595  # Palestine ID
    
    # قاعدة البيانات
    DB_PATH = Path(__file__).parent.parent / 'data' / 'fc26_bot.db'
    
    # مجلد البيانات
    DATA_DIR = Path(__file__).parent.parent / 'data'
    DATA_DIR.mkdir(exist_ok=True)
    
    # منصات اللعب
    PLATFORMS = {
        'playstation': {'name': 'PlayStation', 'emoji': '🎮'},
        'xbox': {'name': 'Xbox', 'emoji': '🎯'},
        'pc': {'name': 'PC', 'emoji': '💻'}
    }
    
    # طرق الدفع
    PAYMENT_METHODS = {
        'vodafone_cash': {'name': 'فودافون كاش', 'emoji': '📱'},
        'orange_cash': {'name': 'أورانج كاش', 'emoji': '🟠'},
        'etisalat_cash': {'name': 'اتصالات كاش', 'emoji': '🟢'},
        'we_cash': {'name': 'WE كاش', 'emoji': '🟡'},
        'instapay': {'name': 'انستا باي', 'emoji': '🏦'},
        'card': {'name': 'بطاقة بنكية', 'emoji': '💳'}
    }
    
    # الأسعار
    PRICES = {
        'buy': {  # نشتري من العميل
            'playstation': 0.09,
            'xbox': 0.08,
            'pc': 0.07
        },
        'sell': {  # نبيع للعميل
            'playstation': 0.11,
            'xbox': 0.10,
            'pc': 0.09
        }
    }
    
    # رسائل النظام
    MESSAGES = {
        'welcome': "أهلاً بك في بوت FC 26! 🎮",
        'registration_complete': "تم تسجيل حسابك بنجاح! 🎉",
        'error': "حدث خطأ، الرجاء المحاولة مرة أخرى",
        'support': "للدعم الفني: @fc26support"
    }