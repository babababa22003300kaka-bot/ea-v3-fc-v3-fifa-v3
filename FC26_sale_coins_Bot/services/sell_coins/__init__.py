# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              💰 FC26 COIN SELLING SERVICE - خدمة بيع الكوينز             ║
# ║                     Coin Selling Service Package                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Import only when telegram is available
def _import_telegram_components():
    """Import telegram-dependent components"""
    try:
        from .sell_handler import SellCoinsHandler
        from .sell_keyboards import SellKeyboards
        return SellCoinsHandler, SellKeyboards
    except ImportError:
        return None, None

# Always available imports (no telegram dependency)
from .sell_pricing import CoinSellPricing, Platform
from .sell_messages import SellMessages

# Conditional imports
SellCoinsHandler, SellKeyboards = _import_telegram_components()

__all__ = [
    'CoinSellPricing',
    'Platform', 
    'SellMessages'
]

# Add telegram-dependent components if available
if SellCoinsHandler is not None:
    __all__.extend(['SellCoinsHandler', 'SellKeyboards'])