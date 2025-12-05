"""Web automation modules for different food delivery platforms."""
from .base_automator import BaseAutomator
from .swiggy_automator import SwiggyAutomator
from .zomato_automator import ZomatoAutomator
from .blinkit_automator import BlinkitAutomator

__all__ = ['BaseAutomator', 'SwiggyAutomator', 'ZomatoAutomator', 'BlinkitAutomator']
