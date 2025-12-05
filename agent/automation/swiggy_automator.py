"""Swiggy-specific web automation."""
import time
from typing import Dict, List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_automator import BaseAutomator
from config.settings import settings


class SwiggyAutomator(BaseAutomator):
    """Automates order placement on Swiggy."""
    
    def __init__(self, headless: bool = None):
        """Initialize Swiggy automator.
        
        Args:
            headless: Whether to run in headless mode
        """
        super().__init__(headless)
        self.base_url = settings.SWIGGY_URL
    
    def open_swiggy(self) -> bool:
        """Open Swiggy homepage.
        
        Returns:
            True if successful
        """
        try:
            self.navigate_to(self.base_url)
            print("✅ Opened Swiggy")
            return True
        except Exception as e:
            print(f"❌ Failed to open Swiggy: {e}")
            return False
    
    def set_location(self, location: str) -> bool:
        """Set delivery location.
        
        Args:
            location: Location string (e.g., "MG Road, Bangalore")
            
        Returns:
            True if successful
        """
        try:
            # Wait for location input
            time.sleep(2)
            
            # Try to find location input field
            location_input = self.find_element(
                By.XPATH,
                "//input[@placeholder='Enter your delivery location' or contains(@placeholder, 'location')]",
                timeout=10
            )
            
            if not location_input:
                print("⚠️ Location already set or input not found")
                return True
            
            # Click and type location
            self.click_element(location_input)
            self.type_text(location_input, location)
            time.sleep(2)
            
            # Select first suggestion
            first_suggestion = self.find_element(
                By.XPATH,
                "//div[contains(@class, 'suggestion') or contains(@class, 'location-list')]//div[1]",
                timeout=5
            )
            
            if first_suggestion:
                self.click_element(first_suggestion)
                time.sleep(2)
                print(f"✅ Location set to: {location}")
                return True
            else:
                print("⚠️ No location suggestions found")
                return False
                
        except Exception as e:
            print(f"❌ Failed to set location: {e}")
            return False
    
    def search_restaurant(self, restaurant_name: str) -> bool:
        """Search for a restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            
        Returns:
            True if successful
        """
        try:
            # Find search box
            search_box = self.find_element(
                By.XPATH,
                "//input[@placeholder='Search for restaurant, item or more' or contains(@placeholder, 'Search')]",
                timeout=10
            )
            
            if not search_box:
                print("❌ Search box not found")
                return False
            
            # Click and type restaurant name
            self.click_element(search_box)
            time.sleep(0.5)
            self.type_text(search_box, restaurant_name)
            time.sleep(2)
            
            print(f"✅ Searched for: {restaurant_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to search restaurant: {e}")
            return False
    
    def select_restaurant(self, restaurant_name: str) -> bool:
        """Select restaurant from search results.
        
        Args:
            restaurant_name: Name of the restaurant
            
        Returns:
            True if successful
        """
        try:
            time.sleep(2)
            
            # Look for restaurant in results
            restaurant_element = self.find_element(
                By.XPATH,
                f"//div[contains(text(), '{restaurant_name}') or contains(@class, 'restaurant')]",
                timeout=10
            )
            
            if not restaurant_element:
                # Try clicking first result
                first_result = self.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'restaurant-list')]//div[1] | //a[contains(@class, 'RestaurantList')]",
                    timeout=5
                )
                if first_result:
                    self.click_element(first_result)
                    time.sleep(3)
                    print(f"✅ Selected first restaurant result")
                    return True
                return False
            
            self.click_element(restaurant_element)
            time.sleep(3)
            print(f"✅ Selected restaurant: {restaurant_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to select restaurant: {e}")
            return False
    
    def search_item(self, item_name: str) -> bool:
        """Search for a specific item in the restaurant menu.
        
        Args:
            item_name: Name of the item
            
        Returns:
            True if successful
        """
        try:
            # Find menu search box
            menu_search = self.find_element(
                By.XPATH,
                "//input[@placeholder='Search for dishes' or contains(@placeholder, 'Search')]",
                timeout=10
            )
            
            if not menu_search:
                print("⚠️ Menu search not available, scrolling to find item")
                return False
            
            self.click_element(menu_search)
            self.type_text(menu_search, item_name)
            time.sleep(2)
            
            print(f"✅ Searched for item: {item_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to search item: {e}")
            return False
    
    def add_item_to_cart(
        self,
        item_name: str,
        quantity: int = 1,
customizations: Optional[Dict] = None
    ) -> bool:
        """Add item to cart with specified quantity.
        
        Args:
            item_name: Name of the item
            quantity: Quantity to add
            customizations: Optional customization choices
            
        Returns:
            True if successful
        """
        try:
            print(f"🛒 Adding {quantity}x {item_name} to cart...")
            
            # Find and click ADD button for the item
            add_button = self.find_element(
                By.XPATH,
                f"//div[contains(text(), '{item_name}')]//ancestor::div[contains(@class, 'item')]//button[contains(text(), 'ADD')]",
                timeout=10
            )
            
            if not add_button:
                # Try generic ADD button
                add_button = self.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'ADD') or contains(@class, 'add-button')]",
                    timeout=5
                )
            
            if not add_button:
                print("❌ ADD button not found")
                return False
            
            self.click_element(add_button)
            time.sleep(2)
            
            # Handle customization modal if it appears
            if self._handle_customization_modal(customizations):
                print("✅ Handled customization")
            
            # Add remaining quantity
            for i in range(1, quantity):
                if self._increment_quantity():
                    print(f"✅ Added item {i + 1}/{quantity}")
                else:
                    print(f"⚠️ Failed to add item {i + 1}/{quantity}")
                    break
            
            time.sleep(1)
            print(f"✅ Added {quantity}x {item_name} to cart")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add item to cart: {e}")
            return False
    
    def _handle_customization_modal(self, customizations: Optional[Dict] = None) -> bool:
        """Handle customization modal that appears when adding items.
        
        Args:
            customizations: Optional customization choices
            
        Returns:
            True if modal was handled
        """
        try:
            # Check if customization modal appeared
            modal = self.find_element(
                By.XPATH,
                "//div[contains(@class, 'modal') or contains(@class, 'customisation')]",
                timeout=3
            )
            
            if not modal:
                return False
            
            print("📋 Customization modal detected")
            
            # If customizations provided, apply them
            if customizations:
                # This is a simplified version - real implementation would need
                # to parse the modal and select appropriate options
                for key, value in customizations.items():
                    option = self.find_element(
                        By.XPATH,
                        f"//div[contains(text(), '{value}')]",
                        timeout=2
                    )
                    if option:
                        self.click_element(option)
            else:
                # Select first default option for each required field
                checkboxes = self.find_elements(
                    By.XPATH,
                    "//input[@type='checkbox' or @type='radio']"
                )
                if checkboxes and not checkboxes[0].is_selected():
                    self.click_element(checkboxes[0])
            
            time.sleep(1)
            
            # Click "Add item" or "Add to cart" button
            add_btn = self.find_element(
                By.XPATH,
                "//button[contains(text(), 'Add item') or contains(text(), 'Add to cart')]",
                timeout=5
            )
            
            if add_btn:
                self.click_element(add_btn)
                time.sleep(2)
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Customization handling: {e}")
            return False
    
    def _increment_quantity(self) -> bool:
        """Increment item quantity by clicking + button.
        
        Returns:
            True if successful
        """
        try:
            time.sleep(1)
            
            # Find + button
            plus_button = self.find_element(
                By.XPATH,
                "//button[contains(text(), '+') or contains(@class, 'increment')]",
                timeout=5
            )
            
            if not plus_button:
                return False
            
            self.click_element(plus_button)
            time.sleep(1)
            
            # Handle "Repeat previous customisation?" modal
            repeat_button = self.find_element(
                By.XPATH,
                "//button[contains(text(), 'Repeat') or contains(text(), 'Yes')]",
                timeout=3
            )
            
            if repeat_button:
                self.click_element(repeat_button)
                time.sleep(1)
                print("🔁 Repeated previous customization")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to increment quantity: {e}")
            return False
    
    def proceed_to_checkout(self) -> bool:
        """Navigate to checkout page.
        
        Returns:
            True if successful
        """
        try:
            # Find and click "VIEW CART" or "CHECKOUT" button
            checkout_button = self.find_element(
                By.XPATH,
                "//button[contains(text(), 'VIEW CART') or contains(text(), 'CHECKOUT') or contains(text(), 'Checkout')]",
                timeout=10
            )
            
            if not checkout_button:
                print("❌ Checkout button not found")
                return False
            
            self.click_element(checkout_button)
            time.sleep(3)
            
            print("✅ Navigated to checkout")
            return True
            
        except Exception as e:
            print(f"❌ Failed to proceed to checkout: {e}")
            return False
    
    def get_order_summary(self) -> Dict:
        """Extract order summary from checkout page.
        
        Returns:
            Dictionary with order details
        """
        try:
            summary = {
                "platform": "Swiggy",
                "items": [],
                "item_total": 0.0,
                "delivery_fee": 0.0,
                "taxes": 0.0,
                "total": 0.0
            }
            
            # Extract item total
            item_total_elem = self.find_element(
                By.XPATH,
                "//div[contains(text(), 'Item Total') or contains(text(), 'Subtotal')]//following-sibling::div",
                timeout=5
            )
            if item_total_elem:
                summary["item_total"] = self._parse_price(item_total_elem.text)
            
            # Extract delivery fee
            delivery_elem = self.find_element(
                By.XPATH,
                "//div[contains(text(), 'Delivery') or contains(text(), 'Delivery Fee')]//following-sibling::div",
                timeout=5
            )
            if delivery_elem:
                summary["delivery_fee"] = self._parse_price(delivery_elem.text)
            
            # Extract total
            total_elem = self.find_element(
                By.XPATH,
                "//div[contains(text(), 'TO PAY') or contains(text(), 'Total')]//following-sibling::div | //div[contains(@class, 'total')]",
                timeout=5
            )
            if total_elem:
                summary["total"] = self._parse_price(total_elem.text)
            
            print(f"📊 Order Summary: Total ₹{summary['total']}")
            return summary
            
        except Exception as e:
            print(f"⚠️ Failed to extract order summary: {e}")
            return summary
    
    def _parse_price(self, price_text: str) -> float:
        """Parse price from text.
        
        Args:
            price_text: Text containing price
            
        Returns:
            Price as float
        """
        try:
            # Remove currency symbol and commas, extract number
            import re
            match = re.search(r'[\d,]+\.?\d*', price_text)
            if match:
                return float(match.group().replace(',', ''))
            return 0.0
        except:
            return 0.0
    
    def place_order_workflow(
        self,
        location: str,
        restaurant: str,
        item: str,
        quantity: int = 1,
        customizations: Optional[Dict] = None
    ) -> Dict:
        """Complete order placement workflow.
        
        Args:
            location: Delivery location
            restaurant: Restaurant name
            item: Item name
            quantity: Quantity to order
            customizations: Optional customizations
            
        Returns:
            Order summary dictionary
        """
        print(f"\n{'='*50}")
        print(f"🚀 Starting Swiggy Order Workflow")
        print(f"📍 Location: {location}")
        print(f"🏪 Restaurant: {restaurant}")
        print(f"🍔 Item: {item} x{quantity}")
        print(f"{'='*50}\n")
        
        try:
            # Step 1: Open Swiggy
            if not self.open_swiggy():
                return {"success": False, "error": "Failed to open Swiggy"}
            
            # Step 2: Set location
            if not self.set_location(location):
                print("⚠️ Location setting failed, continuing anyway")
            
            # Step 3: Search restaurant
            if not self.search_restaurant(restaurant):
                return {"success": False, "error": "Failed to search restaurant"}
            
            # Step 4: Select restaurant
            if not self.select_restaurant(restaurant):
                return {"success": False, "error": "Failed to select restaurant"}
            
            # Step 5: Search item
            if not self.search_item(item):
                print("⚠️ Item search not available, looking in menu")
            
            # Step 6: Add to cart
            if not self.add_item_to_cart(item, quantity, customizations):
                return {"success": False, "error": "Failed to add item to cart"}
            
            # Step 7: Proceed to checkout
            if not self.proceed_to_checkout():
                return {"success": False, "error": "Failed to proceed to checkout"}
            
            # Step 8: Get order summary
            summary = self.get_order_summary()
            summary["success"] = True
            summary["restaurant"] = restaurant
            summary["items"] = [{"name": item, "quantity": quantity}]
            
            print(f"\n{'='*50}")
            print(f"✅ Order Ready for Payment!")
            print(f"📦 {quantity}x {item} from {restaurant}")
            print(f"💰 Total: ₹{summary['total']}")
            print(f"{'='*50}\n")
            
            return summary
            
        except Exception as e:
            print(f"❌ Order workflow failed: {e}")
            return {"success": False, "error": str(e)}
