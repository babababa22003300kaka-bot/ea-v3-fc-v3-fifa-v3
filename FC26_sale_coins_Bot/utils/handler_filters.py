# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                   🎯 SMART FILTERS - منع التضارب الكامل                 ║
# ║              Handler Conflict Prevention - Zero Overlaps                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

"""
فلاتر ذكية لمنع تضارب الـ handlers تماماً

الاستراتيجية:
- كل handler بيشوف رسائله فقط
- الفلاتر بترفض بسرعة لو الرسالة مش ليها
- صفر manual checks داخل الـ handlers
"""

from telegram.ext import filters


class AdminSessionFilter(filters.MessageFilter):
    """
    فلتر الأدمن - يقبل فقط:
    - رسائل من الأدمن
    - الأدمن عنده session نشط
    - الـ session في خطوة "waiting_price"
    """

    def __init__(self, admin_handler):
        """
        Args:
            admin_handler: مرجع لـ AdminHandler instance
        """
        self.admin_handler = admin_handler
        super().__init__()

    def filter(self, message):
        """
        Returns:
            True: رسالة من أدمن مع session نشط
            False: أي حالة تانية (silent rejection)
        """
        # لو مافيش admin handler أصلاً
        if not self.admin_handler:
            return False

        user_id = message.from_user.id

        # 1. هل المستخدم admin؟
        if user_id != self.admin_handler.ADMIN_ID:
            return False

        # 2. هل عنده session نشط؟
        if user_id not in self.admin_handler.user_sessions:
            return False

        # 3. هل الـ session في الخطوة الصحيحة؟
        session = self.admin_handler.user_sessions[user_id]
        if session.get("step") != "waiting_price":
            return False

        # ✅ كل الشروط تمام - قبول!
        print(f"✅ [ADMIN-FILTER] Admin {user_id} session active → ACCEPT")
        return True


class SellSessionFilter(filters.MessageFilter):
    """
    فلتر البيع - يقبل فقط:
    - مستخدمين عندهم sell session نشط
    - الـ session في خطوة إدخال الكمية
    """

    def __init__(self, sell_handler):
        """
        Args:
            sell_handler: مرجع لـ SellCoinsHandler instance
        """
        self.sell_handler = sell_handler
        super().__init__()

    def filter(self, message):
        """
        Returns:
            True: مستخدم مع sell session نشط
            False: أي حالة تانية (silent rejection)
        """
        user_id = message.from_user.id

        # 1. هل عنده sell session؟
        if user_id not in self.sell_handler.user_sessions:
            return False

        # 2. هل الـ session في خطوة إدخال الكمية؟
        session = self.sell_handler.user_sessions[user_id]
        step = session.get("step")

        valid_steps = ["amount_input", "custom_amount_input"]
        if step not in valid_steps:
            return False

        # ✅ عنده session نشط - قبول!
        print(
            f"✅ [SELL-FILTER] User {user_id} sell session active (step: {step}) → ACCEPT"
        )
        return True


class RegistrationFilter(filters.MessageFilter):
    """
    فلتر التسجيل - يقبل فقط:
    - مستخدمين بدون أي sessions أخرى (admin/sell)
    - للتسجيل العادي فقط
    """

    def __init__(self, admin_handler, sell_handler):
        """
        Args:
            admin_handler: مرجع لـ AdminHandler instance
            sell_handler: مرجع لـ SellCoinsHandler instance
        """
        self.admin_handler = admin_handler
        self.sell_handler = sell_handler
        super().__init__()

    def filter(self, message):
        """
        Returns:
            True: مستخدم بدون أي sessions نشطة
            False: عنده session في خدمة تانية
        """
        user_id = message.from_user.id

        # 1. تحقق من admin session
        if self.admin_handler and user_id in self.admin_handler.user_sessions:
            print(f"⏭️ [REG-FILTER] User {user_id} has admin session → REJECT")
            return False

        # 2. تحقق من sell session
        if user_id in self.sell_handler.user_sessions:
            print(f"⏭️ [REG-FILTER] User {user_id} has sell session → REJECT")
            return False

        # ✅ مافيش sessions تانية - قبول!
        print(f"✅ [REG-FILTER] User {user_id} clean (no sessions) → ACCEPT")
        return True


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS - لإنشاء الفلاتر بسهولة
# ═══════════════════════════════════════════════════════════════════════════


class HandlerFilters:
    """Factory class لإنشاء الفلاتر الذكية"""

    @staticmethod
    def create_admin_filter(admin_handler):
        """إنشاء فلتر الأدمن"""
        return AdminSessionFilter(admin_handler)

    @staticmethod
    def create_sell_filter(sell_handler):
        """إنشاء فلتر البيع"""
        return SellSessionFilter(sell_handler)

    @staticmethod
    def create_registration_filter(admin_handler, sell_handler):
        """إنشاء فلتر التسجيل"""
        return RegistrationFilter(admin_handler, sell_handler)
