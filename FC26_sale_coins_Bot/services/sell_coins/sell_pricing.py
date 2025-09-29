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
    
    # الأسعار العادية (التحويل خلال 24 ساعة) بالجنيه المصري
    NORMAL_PRICES = {
        # PlayStation و Xbox نفس السعر
        Platform.PLAYSTATION.value: {
            100000: 5300,    # 100k = 5300 ج.م (السعر العادي)
            200000: 10400,   # 200k = 10400 ج.م  
            500000: 25800,   # 500k = 25800 ج.م
            1000000: 51000,  # 1M = 51000 ج.م
            2000000: 101000, # 2M = 101000 ج.م
            5000000: 250000  # 5M = 250000 ج.م
        },
        Platform.XBOX.value: {
            100000: 5300,    # 100k = 5300 ج.م (السعر العادي)
            200000: 10400,   # 200k = 10400 ج.م  
            500000: 25800,   # 500k = 25800 ج.م
            1000000: 51000,  # 1M = 51000 ج.م
            2000000: 101000, # 2M = 101000 ج.م
            5000000: 250000  # 5M = 250000 ج.م
        },
        # PC سعر منفصل (أغلى شوية)
        Platform.PC.value: {
            100000: 5800,    # 100k = 5800 ج.م (السعر العادي)
            200000: 11400,   # 200k = 11400 ج.م  
            500000: 28300,   # 500k = 28300 ج.م
            1000000: 56000,  # 1M = 56000 ج.م
            2000000: 111000, # 2M = 111000 ج.م
            5000000: 275000  # 5M = 275000 ج.م
        }
    }
    
    # الأسعار الفورية (التحويل خلال ساعة) - أعلى بـ 300 ج.م
    INSTANT_PRICES = {
        # PlayStation و Xbox نفس السعر
        Platform.PLAYSTATION.value: {
            100000: 5600,    # 100k = 5600 ج.م (السعر الفوري +300)
            200000: 10700,   # 200k = 10700 ج.م  
            500000: 26100,   # 500k = 26100 ج.م
            1000000: 51300,  # 1M = 51300 ج.م
            2000000: 101300, # 2M = 101300 ج.م
            5000000: 250300  # 5M = 250300 ج.م
        },
        Platform.XBOX.value: {
            100000: 5600,    # 100k = 5600 ج.م (السعر الفوري +300)
            200000: 10700,   # 200k = 10700 ج.م  
            500000: 26100,   # 500k = 26100 ج.م
            1000000: 51300,  # 1M = 51300 ج.م
            2000000: 101300, # 2M = 101300 ج.م
            5000000: 250300  # 5M = 250300 ج.م
        },
        # PC سعر منفصل (أغلى شوية)
        Platform.PC.value: {
            100000: 6100,    # 100k = 6100 ج.م (السعر الفوري +300)
            200000: 11700,   # 200k = 11700 ج.م  
            500000: 28600,   # 500k = 28600 ج.م
            1000000: 56300,  # 1M = 56300 ج.م
            2000000: 111300, # 2M = 111300 ج.م
            5000000: 275300  # 5M = 275300 ج.م
        }
    }
    
    # للتوافق مع الكود القديم
    CURRENT_PRICES = NORMAL_PRICES
    

    @classmethod
    def get_price(cls, platform: str, coins: int, transfer_type: str = "normal") -> Optional[int]:
        """جلب السعر لكمية كوينز معينة حسب نوع التحويل"""
        price_table = cls.INSTANT_PRICES if transfer_type == "instant" else cls.NORMAL_PRICES
        
        if platform not in price_table:
            return None
        
        return price_table[platform].get(coins)
    
    @classmethod
    def get_transfer_prices(cls, platform: str, coins: int) -> Dict[str, Optional[int]]:
        """جلب أسعار التحويل العادي والفوري لكمية معينة"""
        return {
            "normal": cls.get_price(platform, coins, "normal"),
            "instant": cls.get_price(platform, coins, "instant")
        }
    
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
    def format_price(cls, price: int) -> Dict[str, str]:
        """تنسيق السعر بالجنيه والجذر العشري"""
        if not isinstance(price, (int, float)) or price <= 0:
            return {"egp": "0 ج.م", "decimal": "0.0"}
        
        price = int(price)
        
        # بالجنيه مع الفواصل
        formatted_egp = f"{price:,}".replace(",", "٬") + " ج.م"
        
        # بالجذر العشري (تقريبي)
        if price >= 1000:
            decimal_value = price / 1000
            formatted_decimal = f"{decimal_value:.1f}k"
        else:
            formatted_decimal = str(price)
        
        return {
            "egp": formatted_egp,
            "decimal": formatted_decimal
        }
    
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
        for platform in cls.NORMAL_PRICES:
            comparison[platform] = {
                "platform_name": cls.get_platform_display_name(platform),
                "normal_base_price": cls.NORMAL_PRICES[platform].get(100000, 0),
                "instant_base_price": cls.INSTANT_PRICES[platform].get(100000, 0),
                "price_tiers": len(cls.NORMAL_PRICES[platform])
            }
        
        return comparison
    
    @classmethod
    def get_platform_pricing_message(cls, platform: str) -> str:
        """جلب رسالة أسعار المنصة مع نوعي التحويل"""
        if platform not in cls.NORMAL_PRICES:
            return "❌ منصة غير مدعومة"
        
        platform_name = cls.get_platform_display_name(platform)
        normal_prices = cls.NORMAL_PRICES[platform]
        instant_prices = cls.INSTANT_PRICES[platform]
        
        message = f"💰 **أسعار {platform_name}:**\n\n"
        
        # عرض أسعار الباقات الشائعة
        common_amounts = [100000, 500000, 1000000, 2000000]
        
        for coins in common_amounts:
            if coins in normal_prices and coins in instant_prices:
                coin_display = cls._format_coins(coins)
                normal_price = cls.format_price(normal_prices[coins])
                instant_price = cls.format_price(instant_prices[coins])
                
                message += f"🔸 **{coin_display} كوين:**\n"
                message += f"   📅 عادي: {normal_price['egp']}\n"
                message += f"   ⚡ فوري: {instant_price['egp']}\n\n"
        
        message += "💡 **ملاحظات:**\n"
        message += "📅 التحويل العادي: خلال 24 ساعة\n"
        message += "⚡ التحويل الفوري: خلال ساعة واحدة (+300 ج.م)"
        
        return message