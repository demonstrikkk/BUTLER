"""Main food ordering agent using Google Gemini."""
import os
import time
import json
from typing import Dict, List, Optional
from datetime import datetime

# Google Generative AI
import google.generativeai as genai

# Local imports
from config.settings import settings
from config.prompts import (
    AGENT_SYSTEM_PROMPT,
    MEAL_SUGGESTION_PROMPT,
    PRICE_COMPARISON_PROMPT,
    ORDER_CONFIRMATION_PROMPT
)
from agent.data.user_preferences import UserPreferences
from agent.data.order_history import OrderHistory
from agent.data.location_manager import LocationManager
from agent.automation.swiggy_automator import SwiggyAutomator
from agent.automation.zomato_automator import ZomatoAutomator
from agent.automation.blinkit_automator import BlinkitAutomator
from agent.tools.price_comparator import compare_prices, format_price_comparison
from agent.tools.review_aggregator import format_review_summary


class FoodOrderingAgent:
    """Main AI agent for food ordering assistance."""
    
    def __init__(self, user_id: str = None):
        """Initialize the food ordering agent.
        
        Args:
            user_id: Optional user ID (default: from settings)
        """
        self.user_id = user_id or settings.DEFAULT_USER_ID
        
        # Initialize data managers
        self.preferences = UserPreferences(self.user_id)
        self.order_history = OrderHistory(self.user_id)
        self.location_manager = LocationManager(self.user_id)
        
        # Initialize Gemini
        self._init_gemini()
        
        # Conversation history
        self.conversation_history = []
        
        # Current order context
        self.current_order_context = {}
        
        print(f"🤖 BUTLER initialized for user: {self.user_id}")
        self._print_user_summary()
    
    def _init_gemini(self):
        """Initialize Google Gemini model with function calling."""
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "❌ GEMINI_API_KEY not found!\n"
                "Please set it in .env file:\n"
                "GEMINI_API_KEY=your_api_key_here\n\n"
                "Get your free API key from: https://aistudio.google.com/apikey"
            )
        
        # Check for placeholder value
        if settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError(
                "❌ GEMINI_API_KEY is still set to placeholder value!\n"
                "Please update your .env file with a real API key.\n\n"
                "Steps:\n"
                "1. Go to https://aistudio.google.com/apikey\n"
                "2. Click 'Create API Key'\n"
                "3. Copy the entire key (starts with AIza)\n"
                "4. Replace 'your_gemini_api_key_here' in .env file\n"
                "5. Save and run again"
            )
        
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY.strip())
            
            # Define function tools for Gemini
            tools = [
                {
                    "function_declarations": [
                        {
                            "name": "search_food",
                            "description": "Search for restaurants and food items across delivery platforms (Swiggy, Zomato, Blinkit). Use this when user asks about food options.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "What to search for (e.g., 'pizza', 'Dominos', 'biryani')"
                                    },
                                    "platform": {
                                        "type": "string",
                                        "description": "Platform to search on: 'Swiggy', 'Zomato', 'Blinkit', or 'all'",
                                        "enum": ["Swiggy", "Zomato", "Blinkit", "all"]
                                    }
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "compare_prices",
                            "description": "Compare prices for a specific item across multiple platforms. Use this to help users find the best deal.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "item": {
                                        "type": "string",
                                        "description": "Food item to compare (e.g., 'Margherita Pizza')"
                                    },
                                    "restaurant": {
                                        "type": "string",
                                        "description": "Restaurant name (e.g., 'Dominos')"
                                    }
                                },
                                "required": ["item", "restaurant"]
                            }
                        },
                        {
                            "name": "place_order",
                            "description": "Automatically place an order on a delivery platform. ONLY call this after user explicitly confirms they want to place the order. This will open a browser and automate the ordering process.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "platform": {
                                        "type": "string",
                                        "description": "Platform to order from",
                                        "enum": ["Swiggy", "Zomato", "Blinkit"]
                                    },
                                    "restaurant": {
                                        "type": "string",
                                        "description": "Restaurant name"
                                    },
                                    "item": {
                                        "type": "string",
                                        "description": "Item to order"
                                    },
                                    "quantity": {
                                        "type": "integer",
                                        "description": "Quantity to order (default: 1)"
                                    }
                                },
                                "required": ["platform", "restaurant", "item"]
                            }
                        },
                        {
                            "name": "get_user_preferences",
                            "description": "Get user's saved preferences including dietary restrictions, favorite cuisines, budget, etc.",
                            "parameters": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_order_history",
                            "description": "Get user's recent order history to understand their preferences and suggest similar items.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "limit": {
                                        "type": "integer",
                                        "description": "Number of recent orders to retrieve (default: 5)"
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
            
            # Configure model with function calling
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                },
                tools=tools
            )
            
            # Start chat session
            self.chat = self.model.start_chat(
                history=[],
                enable_automatic_function_calling=False  # We'll handle function calls manually for better control
            )
            
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "400" in error_msg:
                raise ValueError(
                    "❌ Invalid API Key!\n\n"
                    "Your API key is not valid. Please:\n"
                    "1. Go to https://aistudio.google.com/apikey\n"
                    "2. Create a NEW API key\n"
                    "3. Copy the ENTIRE key\n"
                    "4. Update .env file: GEMINI_API_KEY=your_new_key\n"
                    "5. Make sure there are NO quotes or extra spaces\n\n"
                    f"Original error: {error_msg}"
                )
            else:
                raise
        
        # Send system prompt
        system_message = self._build_system_prompt()
        self.chat.send_message(system_message)
    
    def _build_system_prompt(self) -> str:
        """Build personalized system prompt with user context.
        
        Returns:
            System prompt string
        """
        prompt_parts = [AGENT_SYSTEM_PROMPT]
        
        # Add user context
        prompt_parts.append("\n\n**User Context:**")
        prompt_parts.append(f"- User ID: {self.user_id}")
        prompt_parts.append(f"- Preferences: {self.preferences.get_summary()}")
        prompt_parts.append(f"- Order History: {self.order_history.get_summary_for_ai()}")
        prompt_parts.append(f"- Location: {self.location_manager.get_current_location_string()}")
        
        return "\n".join(prompt_parts)
    
    def _print_user_summary(self):
        """Print user summary."""
        print("\n" + "=" * 60)
        print("👤 USER PROFILE")
        print("=" * 60)
        print(f"Preferences: {self.preferences.get_summary()}")
        print(f"Order History: {self.order_history.get_summary_for_ai()}")
        print(f"Location: {self.location_manager.get_current_location_string()}")
        print("=" * 60 + "\n")
    
    def _execute_function_call(self, function_call) -> Dict:
        """Execute a function call from Gemini.
        
        Args:
            function_call: Function call object from Gemini
            
        Returns:
            Function result as dictionary
        """
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        print(f"\n🔧 AI is calling function: {function_name}")
        print(f"   Arguments: {function_args}")
        
        try:
            if function_name == "search_food":
                return self._handle_search_food(**function_args)
            
            elif function_name == "compare_prices":
                return self._handle_compare_prices(**function_args)
            
            elif function_name == "place_order":
                return self._handle_place_order(**function_args)
            
            elif function_name == "get_user_preferences":
                return self._handle_get_preferences()
            
            elif function_name == "get_order_history":
                return self._handle_get_history(**function_args)
            
            else:
                return {"error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_search_food(self, query: str, platform: str = "all") -> Dict:
        """Handle search_food function call.
        
        Args:
            query: Search query
            platform: Platform to search on
            
        Returns:
            Search results
        """
        print(f"   🔍 Searching for '{query}' on {platform}...")
        
        # In production, this would make actual API calls or web scraping
        # For now, return simulated results
        results = {
            "query": query,
            "platform": platform,
            "location": self.location_manager.get_current_location_string(),
            "results": [
                {
                    "platform": "Swiggy",
                    "restaurant": f"Restaurant for {query}",
                    "items": [f"{query} - ₹299", f"Deluxe {query} - ₹399"],
                    "rating": 4.2,
                    "delivery_time": "30-35 mins",
                    "delivery_fee": 40
                },
                {
                    "platform": "Zomato",
                    "restaurant": f"Best {query} Place",
                    "items": [f"{query} Special - ₹279", f"Combo {query} - ₹449"],
                    "rating": 4.5,
                    "delivery_time": "25-30 mins",
                    "delivery_fee": 35
                }
            ],
            "message": f"Found options for '{query}' across platforms"
        }
        
        return results
    
    def _handle_compare_prices(self, item: str, restaurant: str) -> Dict:
        """Handle compare_prices function call.
        
        Args:
            item: Item to compare
            restaurant: Restaurant name
            
        Returns:
            Price comparison
        """
        print(f"   💰 Comparing prices for '{item}' from {restaurant}...")
        
        # Simulated price comparison
        comparison = {
            "item": item,
            "restaurant": restaurant,
            "platforms": [
                {
                    "platform": "Swiggy",
                    "item_price": 299,
                    "delivery_fee": 40,
                    "taxes": 30,
                    "total": 369,
                    "available": True
                },
                {
                    "platform": "Zomato",
                    "item_price": 279,
                    "delivery_fee": 35,
                    "taxes": 28,
                    "total": 342,
                    "available": True
                },
                {
                    "platform": "Blinkit",
                    "available": False,
                    "message": "Not available on Blinkit"
                }
            ],
            "best_deal": "Zomato",
            "savings": 27
        }
        
        return comparison
    
    def _handle_place_order(self, platform: str, restaurant: str, item: str, quantity: int = 1) -> Dict:
        """Handle place_order function call - triggers automation.
        
        Args:
            platform: Platform to order from
            restaurant: Restaurant name
            item: Item to order
            quantity: Quantity
            
        Returns:
            Order result
        """
        print(f"\n🚀 Initiating automated order placement...")
        print(f"   Platform: {platform}")
        print(f"   Restaurant: {restaurant}")
        print(f"   Item: {item} x{quantity}")
        
        # Call the actual automation
        result = self.place_order(platform, restaurant, item, quantity)
        
        return result
    
    def _handle_get_preferences(self) -> Dict:
        """Handle get_user_preferences function call.
        
        Returns:
            User preferences
        """
        prefs = self.preferences.preferences
        
        return {
            "dietary": prefs.dietary,
            "allergies": prefs.allergies,
            "favorite_cuisines": prefs.favorite_cuisines,
            "disliked_foods": prefs.disliked_foods,
            "budget": prefs.budget,
            "spice_preference": prefs.spice_preference,
            "preferred_platforms": prefs.preferred_platforms
        }
    
    def _handle_get_history(self, limit: int = 5) -> Dict:
        """Handle get_order_history function call.
        
        Args:
            limit: Number of recent orders
            
        Returns:
            Order history
        """
        recent = self.order_history.get_recent_orders(limit)
        
        history = []
        for order in recent:
            history.append({
                "restaurant": order.restaurant,
                "platform": order.platform,
                "items": [{"name": item.name, "quantity": item.quantity} for item in order.items],
                "total": order.total,
                "date": order.timestamp[:10],
                "rating": order.user_rating
            })
        
        return {"orders": history, "total_orders": len(history)}
    
    def chat_with_agent(self, user_message: str) -> str:
        """Chat with the agent with function calling support.
        
        Args:
            user_message: User's message
            
        Returns:
            Agent's response
        """
        try:
            # Check for special commands
            if user_message.lower().startswith("/"):
                return self._handle_command(user_message)
            
            # Add timestamp context
            current_time = datetime.now().strftime("%H:%M")
            day_period = self._get_day_period()
            
            enriched_message = f"[Time: {current_time}, {day_period}] {user_message}"
            
            # Send to Gemini and handle function calls
            response = self.chat.send_message(enriched_message)
            
            # Check if Gemini wants to call a function
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                # Check for function calls in the response
                if response.candidates[0].content.parts:
                    function_calls = []
                    text_parts = []
                    
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            function_calls.append(part.function_call)
                        elif hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    
                    # If there are function calls, execute them
                    if function_calls:
                        function_responses = []
                        
                        for function_call in function_calls:
                            # Execute the function
                            result = self._execute_function_call(function_call)
                            
                            # Create function response
                            function_response = genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=function_call.name,
                                    response={"result": result}
                                )
                            )
                            function_responses.append(function_response)
                        
                        # Send function results back to Gemini
                        response = self.chat.send_message(function_responses)
                        iteration += 1
                        continue
                    
                    # No more function calls, return text response
                    if text_parts:
                        agent_response = "".join(text_parts)
                        break
                    elif hasattr(response, 'text'):
                        agent_response = response.text
                        break
                    else:
                        agent_response = "I've completed the requested actions."
                        break
                else:
                    agent_response = response.text if hasattr(response, 'text') else "Response received."
                    break
            
            # Store in history
            self.conversation_history.append({
                "user": user_message,
                "agent": agent_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return agent_response
            
        except Exception as e:
            error_msg = f"❌ Error communicating with agent: {e}"
            print(error_msg)
            return error_msg
    
    def _handle_command(self, command: str) -> str:
        """Handle special commands.
        
        Args:
            command: Command string
            
        Returns:
            Command response
        """
        cmd = command.lower().strip()
        
        if cmd == "/help":
            return self._get_help_text()
        elif cmd == "/history":
            return self._format_order_history()
        elif cmd == "/preferences":
            return self._format_preferences()
        elif cmd == "/location":
            return self._format_locations()
        elif cmd.startswith("/set_location"):
            parts = command.split(maxsplit=1)
            if len(parts) > 1:
                return self._update_location(parts[1])
            return "Usage: /set_location <location>"
        elif cmd.startswith("/set_budget"):
            parts = command.split()
            if len(parts) == 3:
                try:
                    min_b = int(parts[1])
                    max_b = int(parts[2])
                    self.preferences.set_budget(min_b, max_b)
                    return f"✅ Budget updated to ₹{min_b}-₹{max_b}"
                except ValueError:
                    return "❌ Invalid budget format. Use: /set_budget <min> <max>"
            return "Usage: /set_budget <min> <max>"
        else:
            return f"❌ Unknown command: {command}\nType /help for available commands."
    
    def _get_help_text(self) -> str:
        """Get help text."""
        return """
🤖 **BUTLER Commands**

**Chat Commands:**
- Just type naturally to chat with me!
- "I want pizza" - Get meal suggestions
- "Show me options for biryani" - Search across platforms
- "Place order" - Start order placement

**Special Commands:**
- /help - Show this help
- /history - View order history
- /preferences - View your preferences
- /location - View saved locations
- /set_location <location> - Update location
- /set_budget <min> <max> - Set budget (e.g., /set_budget 100 500)

**Order Flow:**
1. Tell me what you want to eat
2. I'll search across Swiggy, Zomato, Blinkit
3. I'll compare prices and show reviews
4. Confirm the order
5. I'll automate the ordering process
6. You complete the payment
"""
    
    def _get_day_period(self) -> str:
        """Get current day period."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"
    
    def _extract_order_context(self, user_msg: str, agent_msg: str):
        """Extract order context from conversation."""
        # This is a simplified extraction - in real scenario,
        # use Gemini function calling or structured output
        self.current_order_context = {
            "user_request": user_msg,
            "agent_response": agent_msg,
            "timestamp": datetime.now().isoformat()
        }
    
    def search_across_platforms(
        self,
        query: str,
        location: Optional[str] = None
    ) -> Dict:
        """Search for food items across all platforms.
        
        This is a simplified version - in production, would use Google Search API
        
        Args:
            query: Search query
            location: Optional location override
            
        Returns:
            Search results dictionary
        """
        loc = location or self.location_manager.get_current_location_string()
        
        # Simulated search results (in production, use Google Search API)
        results = {
            "query": query,
            "location": loc,
            "platforms": {
                "Swiggy": "Available",
                "Zomato": "Available",
                "Blinkit": "Check grocery items"
            },
            "message": f"Searched for '{query}' in {loc} across all platforms"
        }
        
        return results
    
    def place_order(
        self,
        platform: str,
        restaurant: str,
        item: str,
        quantity: int = 1,
        customizations: Optional[Dict] = None
    ) -> Dict:
        """Place an order using web automation.
        
        Args:
            platform: Platform name ("Swiggy", "Zomato", "Blinkit")
            restaurant: Restaurant name
            item: Item name
            quantity: Quantity
            customizations: Optional customizations
            
        Returns:
            Order result dictionary
        """
        location = self.location_manager.get_current_location_string()
        
        print(f"\n{'='*60}")
        print(f"🚀 INITIATING ORDER PLACEMENT")
        print(f"{'='*60}")
        print(f"Platform: {platform}")
        print(f"Restaurant: {restaurant}")
        print(f"Item: {item} x{quantity}")
        print(f"Location: {location}")
        print(f"{'='*60}\n")
        
        try:
            result = {}
            
            if platform.lower() == "swiggy":
                print("🌐 Initializing browser for Swiggy automation...")
                with SwiggyAutomator(headless=settings.HEADLESS_MODE) as automator:
                    result = automator.place_order_workflow(
                        location=location,
                        restaurant=restaurant,
                        item=item,
                        quantity=quantity,
                        customizations=customizations
                    )
            
            elif platform.lower() == "zomato":
                print("🌐 Initializing browser for Zomato automation...")
                with ZomatoAutomator(headless=settings.HEADLESS_MODE) as automator:
                    result = automator.place_order_workflow(
                        location=location,
                        restaurant=restaurant,
                        item=item,
                        quantity=quantity
                    )
            
            elif platform.lower() == "blinkit":
                print("🌐 Initializing browser for Blinkit automation...")
                with BlinkitAutomator(headless=settings.HEADLESS_MODE) as automator:
                    result = automator.place_order_workflow(
                        location=location,
                        item=item,
                        quantity=quantity
                    )
            
            else:
                return {"success": False, "error": f"Unknown platform: {platform}"}
            
            # If successful, log to order history
            if result.get("success"):
                self._log_order(result, platform, restaurant, item, quantity)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ AUTOMATION ERROR: {error_msg}")
            print(f"Error type: {type(e).__name__}")
            
            # Check for common issues
            if "chrome" in error_msg.lower() or "driver" in error_msg.lower():
                print("\n💡 This looks like a Chrome/ChromeDriver issue!")
                print("   Solutions:")
                print("   1. Install Chrome: sudo apt-get install google-chrome-stable")
                print("   2. Or run on Windows (not WSL)")
                print("   3. Or set HEADLESS_MODE=true in .env")
            
            import traceback
            traceback.print_exc()
            
            return {"success": False, "error": error_msg}
    
    def _log_order(
        self,
        result: Dict,
        platform: str,
        restaurant: str,
        item: str,
        quantity: int
    ):
        """Log order to history.
        
        Args:
            result: Order result from automation
            platform: Platform name
            restaurant: Restaurant name
            item: Item name
            quantity: Quantity
        """
        order_data = {
            "platform": platform,
            "restaurant": restaurant,
            "items": [{"name": item, "quantity": quantity, "price": result.get("item_total", 0)}],
            "item_total": result.get("item_total", 0),
            "delivery_fee": result.get("delivery_fee", 0),
            "taxes": result.get("taxes", 0),
            "total": result.get("total", 0),
            "location": self.location_manager.get_current_location_string(),
            "status": "placed"  # User will complete payment
        }
        
        order_id = self.order_history.add_order(order_data)
        print(f"\n✅ Order logged with ID: {order_id}")
    
    def _format_order_history(self) -> str:
        """Format order history for display."""
        recent = self.order_history.get_recent_orders(10)
        
        if not recent:
            return "No order history found."
        
        output = ["\n📦 **Recent Orders**\n"]
        
        for order in recent:
            output.append(f"**{order.restaurant}** ({order.platform})")
            output.append(f"  • {', '.join([f'{item.name} x{item.quantity}' for item in order.items])}")
            output.append(f"  • ₹{order.total:.0f} • {order.timestamp[:10]}")
            if order.user_rating:
                output.append(f"  • Your Rating: {order.user_rating}⭐")
            output.append("")
        
        spending = self.order_history.get_spending_summary()
        output.append(f"\n💰 **Total Spending**: ₹{spending['total']:.0f} ({spending['count']} orders)")
        output.append(f"📊 **Average Order**: ₹{spending['average']:.0f}")
        
        return "\n".join(output)
    
    def _format_preferences(self) -> str:
        """Format preferences for display."""
        prefs = self.preferences.preferences
        
        output = ["\n⚙️ **Your Preferences**\n"]
        
        if prefs.dietary:
            output.append(f"🥗 Dietary: {', '.join(prefs.dietary)}")
        if prefs.allergies:
            output.append(f"⚠️ Allergies: {', '.join(prefs.allergies)}")
        if prefs.favorite_cuisines:
            output.append(f"❤️ Favorite Cuisines: {', '.join(prefs.favorite_cuisines)}")
        if prefs.disliked_foods:
            output.append(f"👎 Disliked: {', '.join(prefs.disliked_foods)}")
        
        output.append(f"💰 Budget: ₹{prefs.budget['min']}-₹{prefs.budget['max']}")
        output.append(f"🌶️ Spice Preference: {prefs.spice_preference}")
        output.append(f"📱 Preferred Platforms: {', '.join(prefs.preferred_platforms)}")
        
        return "\n".join(output)
    
    def _format_locations(self) -> str:
        """Format locations for display."""
        locations = self.location_manager.list_locations()
        
        if not locations:
            return "No saved locations."
        
        output = ["\n📍 **Saved Locations**\n"]
        
        for loc in locations:
            default = "⭐ " if loc['is_default'] else "   "
            output.append(f"{default}{loc['name']}: {loc['full_address']}")
        
        return "\n".join(output)
    
    def _update_location(self, location_str: str) -> str:
        """Update user location.
        
        Args:
            location_str: Location string
            
        Returns:
            Confirmation message
        """
        # Parse location (simplified)
        self.location_manager.add_location(
            name="Current",
            full_address=location_str,
            area=location_str,
            city="",
            is_default=True
        )
        
        return f"✅ Location updated to: {location_str}"
