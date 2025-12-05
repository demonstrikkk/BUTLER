"""Blinkit-specific web automation."""
import time
from typing import Dict, Optional
from selenium.webdriver.common.by import By
from .base_automator import BaseAutomator
from config.settings import settings


class BlinkitAutomator(BaseAutomator):
    """Automates order placement on Blinkit (for groceries/quick commerce)."""
    
    def __init__(self, headless: bool = None):
        """Initialize Blinkit automator."""
        super().__init__(headless)
        self.base_url = settings.BLINKIT_URL
    
    def open_blinkit(self) -> bool:
        """Open Blinkit homepage."""
        try:
            self.navigate_to(self.base_url)
            print("✅ Opened Blinkit")
            return True
        except Exception as e:
            print(f"❌ Failed to open Blinkit: {e}")
            return False
    
    def set_location(self, location: str) -> bool:
        """Set delivery location."""
        try:
            time.sleep(2)
            location_input = self.find_element(
                By.XPATH,
                "//input[contains(@placeholder, 'location') or contains(@placeholder, 'address')]",
                timeout=10
            )
            
            if location_input:
                self.click_element(location_input)
                self.type_text(location_input, location)
                time.sleep(2)
                
                # Select first suggestion
                first_suggestion = self.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'LocationSearchList')]//div[1]",
                    timeout=5
                )
                if first_suggestion:
                    self.click_element(first_suggestion)
                    time.sleep(2)
            
            print(f"✅ Location set: {location}")
            return True
        except Exception as e:
            print(f"❌ Location setting failed: {e}")
            return False
    
    def search_item(self, item_name: str) -> bool:
        """Search for an item."""
        try:
            search_box = self.find_element(
                By.XPATH,
                "//input[contains(@placeholder, 'Search')]",
                timeout=10
            )
            
            if not search_box:
                return False
            
            self.click_element(search_box)
            self.type_text(search_box, item_name)
            time.sleep(2)
            
            print(f"✅ Searched for: {item_name}")
            return True
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return False
    
    def add_item_to_cart(self, item_name: str, quantity: int = 1) -> bool:
        """Add item to cart."""
        try:
            print(f"🛒 Adding {quantity}x {item_name}...")
            
            # Find and click ADD button
            add_button = self.find_element(
                By.XPATH,
                "//button[contains(text(), 'ADD') or contains(@class, 'AddButton')]",
                timeout=10
            )
            
            if not add_button:
                return False
            
            self.click_element(add_button)
            time.sleep(2)
            
            # Increment quantity if needed
            for i in range(1, quantity):
                plus_btn = self.find_element(
                    By.XPATH,
                    "//button[contains(text(), '+')]",
                    timeout=3
                )
                if plus_btn:
                    self.click_element(plus_btn)
                    time.sleep(1)
            
            print(f"✅ Added {quantity}x {item_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to add item: {e}")
            return False
    
    def proceed_to_checkout(self) -> bool:
        """Navigate to checkout."""
        try:
            # Look for cart icon or checkout button
            cart_button = self.find_element(
                By.XPATH,
                "//button[contains(text(), 'View Cart') or contains(@class, 'ViewCart')]",
                timeout=10
            )
            
            if cart_button:
                self.click_element(cart_button)
                time.sleep(2)
                print("✅ Navigated to cart")
                return True
            return False
        except Exception as e:
            print(f"❌ Checkout failed: {e}")
            return False
    
    def place_order_workflow(
        self,
        location: str,
        item: str,
        quantity: int = 1
    ) -> Dict:
        """Complete order workflow for Blinkit."""
        print(f"\n{'='*50}")
        print(f"🚀 Starting Blinkit Order Workflow")
        print(f"📍 Location: {location}")
        print(f"🛒 Item: {item} x{quantity}")
        print(f"{'='*50}\n")
        
        try:
            if not self.open_blinkit():
                return {"success": False, "error": "Failed to open Blinkit"}
            
            if not self.set_location(location):
                print("⚠️ Location setting failed")
            
            if not self.search_item(item):
                return {"success": False, "error": "Item search failed"}
            
            if not self.add_item_to_cart(item, quantity):
                return {"success": False, "error": "Failed to add item"}
            
            if not self.proceed_to_checkout():
                return {"success": False, "error": "Checkout failed"}
            
            print("\n✅ Blinkit order ready for payment!")
            return {
                "success": True,
                "platform": "Blinkit",
                "items": [{"name": item, "quantity": quantity}]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
