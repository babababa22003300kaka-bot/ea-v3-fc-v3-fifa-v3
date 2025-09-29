# ╔══════════════════════════════════════════════════════════════════════════╗
# ║         💰 FC26 SELL CONVERSATION HANDLER - معالج محادثة البيع          ║
# ║                    Sell Conversation Logic Handler                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

from states.sell_states import SellStates


class SellConversationHandler:
    """معالج محادثة البيع البسيط"""
    
    @staticmethod
    def parse_amount(text: str):
        """تحليل كمية الكوينز - أرقام فقط (2-5 أرقام)"""
        if not text or not isinstance(text, str):
            return None

        text = text.strip()

        # التحقق من وجود k أو m - ممنوع
        if "k" in text.lower() or "m" in text.lower():
            return "invalid_format"

        try:
            if not text.isdigit():
                return None

            number = int(text)

            # التحقق من عدد الأرقام (2-5 أرقام)
            if len(text) < 2 or len(text) > 5:
                return "invalid_length"

            return number

        except (ValueError, TypeError):
            return None

    @staticmethod
    def format_amount(amount: int) -> str:
        """تنسيق عرض الكمية"""
        if not isinstance(amount, (int, float)):
            return "0"

        amount = int(amount)

        if 100 <= amount <= 999:
            return f"{amount} K"
        elif 1000 <= amount <= 20000:
            formatted = f"{amount:,}".replace(",", "٬")
            return f"{formatted} M"
        else:
            return str(amount)

    @staticmethod
    def calculate_price(amount, transfer_type="normal"):
        """حساب السعر حسب الكمية ونوع التحويل"""
        base_price_per_1000 = 5  # 5 جنيه لكل 1000 كوين
        
        # حساب السعر الأساسي
        base_price = (amount / 1000) * base_price_per_1000
        
        # إضافة رسوم حسب نوع التحويل
        if transfer_type == "instant":
            base_price *= 1.2  # زيادة 20% للتحويل الفوري
        
        return int(base_price)

    @staticmethod
    def validate_amount(amount, min_amount=50, max_amount=20000):
        """التحقق من صحة الكمية"""
        if amount < min_amount:
            return False, f"الكمية قليلة جداً! الحد الأدنى: {min_amount:,} كوين"
        
        if amount > max_amount:
            return False, f"الكمية كبيرة جداً! الحد الأقصى: {max_amount:,} كوين"
        
        return True, "كمية صحيحة"

    @staticmethod
    def get_platform_name(platform: str) -> str:
        """جلب اسم المنصة للعرض"""
        platforms = {
            "playstation": "🎮 PlayStation", 
            "xbox": "🎮 Xbox",
            "pc": "🖥️ PC"
        }
        return platforms.get(platform, platform)
    
    @staticmethod
    def get_transfer_type_name(transfer_type: str) -> str:
        """جلب اسم نوع التحويل للعرض"""
        types = {
            "normal": "📅 تحويل عادي",
            "instant": "⚡ تحويل فوري"
        }
        return types.get(transfer_type, transfer_type)