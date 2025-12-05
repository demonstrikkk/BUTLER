"""Zomato-specific web automation."""
import time
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from .base_automator import BaseAutomator
from config.settings import settings


class ZomatoAutomator(BaseAutomator):
    """Automates order placement on Zomato."""
    
    def __init__(self, headless: bool = None):
        """Initialize Zomato automator."""
        super().__init__(headless)
        self.base_url = settings.ZOMATO_URL
    
    def open_zomato(self) -> bool:
        """Open Zomato homepage."""
        try:
            self.navigate_to(self.base_url)
            print("✅ Opened Zomato")
            return True
        except Exception as e:
            print(f"❌ Failed to open Zomato: {e}")
            return False
    
    def set_location(self, location: str) -> bool:
        """Set delivery location on Zomato."""
        try:
            time.sleep(2)
            location_input = self.find_element(
                By.XPATH,
                "//input[contains(@placeholder, 'location') or contains(@placeholder, 'Location')]",
                timeout=10
            )
            
            if location_input:
                self.click_element(location_input)
                self.type_text(location_input, location)
                time.sleep(2)
                
                # Select first suggestion
                first_suggestion = self.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'suggestion')]//div[1]",
                    timeout=5
                )
                if first_suggestion:
                    self.click_element(first_suggestion)
                    time.sleep(2)
                
            print(f"✅ Location set to: {location}")
            return True
        except Exception as e:
            print(f"❌ Failed to set location: {e}")
            return False
    
    def search_restaurant(self, restaurant_name: str) -> bool:
        """Search for a restaurant on Zomato."""
        try:
            search_box = self.find_element(
                By.XPATH,
                "//input[contains(@placeholder, 'Search') or contains(@class, 'search')]",
                timeout=10
            )
            
            if not search_box:
                return False
            
            self.click_element(search_box)
            self.type_text(search_box, restaurant_name)
            time.sleep(2)
            
            print(f"✅ Searched for: {restaurant_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to search: {e}")
            return False
    
    def select_restaurant(self, restaurant_name: str) -> bool:
        """Select restaurant from results."""
        try:
            time.sleep(2)
            restaurant = self.find_element(
                By.XPATH,
                f"//h4[contains(text(), '{restaurant_name}')] | //div[contains(text(), '{restaurant_name}')]",
                timeout=10
            )
            
            if restaurant:
                self.click_element(restaurant)
                time.sleep(3)
                print(f"✅ Selected: {restaurant_name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to select restaurant: {e}")
            return False
    
    def add_item_to_cart(self, item_name: str, quantity: int = 1) -> bool:
        """Add item to cart on Zomato."""
        try:
            print(f"🛒 Adding {quantity}x {item_name}...")
            
            # Find ADD button
            add_button = self.find_element(
                By.XPATH,
                f"//div[contains(text(), '{item_name}')]//ancestor::div[contains(@class, 'item')]//button[contains(text(), 'ADD')]",
                timeout=10
            )
            
            if not add_button:
                add_button = self.find_element(By.XPATH, "//button[contains(text(), 'ADD')]", timeout=5)
            
            if add_button:
                self.click_element(add_button)
                time.sleep(2)
                
                # Increment quantity
                for i in range(1, quantity):
                    plus_btn = self.find_element(By.XPATH, "//button[contains(text(), '+')]", timeout=3)
                    if plus_btn:
                        self.click_element(plus_btn)
                        time.sleep(1)
                
                print(f"✅ Added {quantity}x {item_name}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to add item: {e}")
            return False
    
    def proceed_to_checkout(self) -> bool:
        """Navigate to checkout."""
        try:
            checkout_btn = self.find_element(
                By.XPATH,
                "//button[contains(text(), 'Checkout') or contains(text(), 'VIEW CART')]",
                timeout=10
            )
            
            if checkout_btn:
                self.click_element(checkout_btn)
                time.sleep(3)
                print("✅ Navigated to checkout")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to checkout: {e}")
            return False
    
    def place_order_workflow(
        self,
        location: str,
        restaurant: str,
        item: str,
        quantity: int = 1
    ) -> Dict:
        """Complete order workflow for Zomato."""
        print(f"\n{'='*50}")
        print(f"🚀 Starting Zomato Order Workflow")
        print(f"📍 Location: {location}")
        print(f"🏪 Restaurant: {restaurant}")
        print(f"🍔 Item: {item} x{quantity}")
        print(f"{'='*50}\n")
        
        try:
            if not self.open_zomato():
                return {"success": False, "error": "Failed to open Zomato"}
            
            if not self.set_location(location):
                print("⚠️ Location setting failed")
            
            if not self.search_restaurant(restaurant):
                return {"success": False, "error": "Restaurant search failed"}
            
            if not self.select_restaurant(restaurant):
                return {"success": False, "error": "Restaurant selection failed"}
            
            if not self.add_item_to_cart(item, quantity):
                return {"success": False, "error": "Failed to add item"}
            
            if not self.proceed_to_checkout():
                return {"success": False, "error": "Checkout failed"}
            
            print("\n✅ Zomato order ready for payment!")
            return {
                "success": True,
                "platform": "Zomato",
                "restaurant": restaurant,
                "items": [{"name": item, "quantity": quantity}]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
