# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💰 FC26 COIN SELLING PRICING - نظام أسعار بيع الكوينز        ║
# ║                     Coin Selling Price Management                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from typing import Dict, List, Optional, Tuple
from enum import Enum

class Platform(Enum):
    """منصات اللعب المدعومة"""
    PLAYSTATION = "playstation"
    XBOX = "xbox" 
    PC = "pc"

class CoinSellPricing:
    """إدارة أسعار بيع الكوينز"""
    
    # الأسعار الحالية بالجنيه المصري
    CURRENT_PRICES = {
        # PlayStation و Xbox نفس السعر
        Platform.PLAYSTATION.value: {
            100000: 150,    # 100k = 150 ج.م
            200000: 290,    # 200k = 290 ج.م  
            500000: 700,    # 500k = 700 ج.م
            1000000: 1350,  # 1M = 1350 ج.م
            2000000: 2600,  # 2M = 2600 ج.م
            5000000: 6250   # 5M = 6250 ج.م
        },
        Platform.XBOX.value: {
            100000: 150,    # 100k = 150 ج.م
            200000: 290,    # 200k = 290 ج.م  
            500000: 700,    # 500k = 700 ج.م
            1000000: 1350,  # 1M = 1350 ج.م
            2000000: 2600,  # 2M = 2600 ج.م
            5000000: 6250   # 5M = 6250 ج.م
        },
        # PC سعر منفصل (أغلى شوية)
        Platform.PC.value: {
            100000: 180,    # 100k = 180 ج.م
            200000: 350,    # 200k = 350 ج.م  
            500000: 850,    # 500k = 850 ج.م
            1000000: 1650,  # 1M = 1650 ج.م
            2000000: 3200,  # 2M = 3200 ج.م
            5000000: 7800   # 5M = 7800 ج.م
        }
    }
    

    @classmethod
    def get_price(cls, platform: str, coins: int) -> Optional[int]:
        """جلب السعر لكمية كوينز معينة"""
        if platform not in cls.CURRENT_PRICES:
            return None
        
        return cls.CURRENT_PRICES[platform].get(coins)
    
    @classmethod
    def calculate_custom_price(cls, platform: str, coins: int) -> Optional[int]:
        """حساب السعر لكمية مخصصة من الكوينز"""
        if platform not in cls.CURRENT_PRICES:
            return None
        
        platform_prices = cls.CURRENT_PRICES[platform]
        
        # إذا كانت الكمية موجودة في الباقات المحددة
        if coins in platform_prices:
            return platform_prices[coins]
        
        # حساب السعر بناءً على أقرب كمية
        price_per_100k = cls._get_price_per_100k(platform)
        if price_per_100k:
            return int((coins / 100000) * price_per_100k)
        
        return None
    
    @classmethod
    def _get_price_per_100k(cls, platform: str) -> Optional[float]:
        """حساب سعر الـ 100k كوين للمنصة"""
        if platform not in cls.CURRENT_PRICES:
            return None
        
        # استخدام سعر الـ 100k كأساس
        return cls.CURRENT_PRICES[platform].get(100000, 150)
    
    @classmethod
    def _format_coins(cls, coins: int) -> str:
        """تنسيق عرض الكوينز"""
        if coins >= 1000000:
            millions = coins / 1000000
            if millions == int(millions):
                return f"{int(millions)}M"
            else:
                return f"{millions:.1f}M"
        elif coins >= 1000:
            thousands = coins / 1000
            if thousands == int(thousands):
                return f"{int(thousands)}K" 
            else:
                return f"{thousands:.0f}K"
        else:
            return str(coins)
    
    @classmethod
    def get_platform_display_name(cls, platform: str) -> str:
        """جلب اسم المنصة للعرض"""
        platform_names = {
            Platform.PLAYSTATION.value: "🎮 PlayStation",
            Platform.XBOX.value: "🎮 Xbox", 
            Platform.PC.value: "🖥️ PC"
        }
        return platform_names.get(platform, platform)
    
    @classmethod
    def validate_coin_amount(cls, coins: int) -> Tuple[bool, str]:
        """التحقق من صحة كمية الكوينز"""
        if coins < 50000:
            return False, "❌ الحد الأدنى للبيع هو 50,000 كوين"
        
        if coins > 10000000:  # 10M max
            return False, "❌ الحد الأقصى للبيع هو 10,000,000 كوين"
        
        if coins % 10000 != 0:
            return False, "❌ يجب أن تكون الكمية من مضاعفات 10,000 كوين"
        
        return True, "✅ كمية صحيحة"
    
    @classmethod
    def get_discount_info(cls, coins: int) -> Optional[str]:
        """جلب معلومات الخصم إن وجد"""
        if coins >= 2000000:  # 2M+
            return "🎉 خصم خاص للكميات الكبيرة!"
        elif coins >= 1000000:  # 1M+
            return "💰 سعر مميز للمليون كوين!"
        elif coins >= 500000:  # 500K+
            return "⭐ عرض خاص للكميات المتوسطة!"
        
        return None
    
    @classmethod
    def get_all_platforms(cls) -> List[str]:
        """جلب جميع المنصات المدعومة"""
        return list(cls.CURRENT_PRICES.keys())
    
    @classmethod 
    def update_price(cls, platform: str, coins: int, new_price: int) -> bool:
        """تحديث سعر كمية معينة (للإدارة)"""
        if platform not in cls.CURRENT_PRICES:
            return False
        
        cls.CURRENT_PRICES[platform][coins] = new_price
        return True
    
    @classmethod
    def get_price_comparison(cls) -> Dict:
        """مقارنة الأسعار بين المنصات"""
        comparison = {}
        for platform in cls.CURRENT_PRICES:
            comparison[platform] = {
                "platform_name": cls.get_platform_display_name(platform),
                "base_price": cls.CURRENT_PRICES[platform].get(100000, 0),
                "price_tiers": len(cls.CURRENT_PRICES[platform])
            }
        
        return comparison