# 🍔 BUTLER - AI Food Ordering Agent

An intelligent AI agent powered by Google Gemini that helps you discover, compare, and order food across multiple delivery platforms (Swiggy, Zomato, Blinkit) with automated order placement.

---

## 🚨 GETTING "API KEY NOT VALID" ERROR?

**👉 See [QUICK_START.md](QUICK_START.md) for the solution!**

Or run this for automatic setup:
```powershell
python setup_api_key.py
```

---

## ✨ Features

### 🤖 AI-Powered Assistance
- **Intelligent Meal Suggestions**: Get personalized meal recommendations based on:
  - Your dietary preferences and restrictions
  - Past order history
  - Time of day
  - Budget constraints
  - Current mood and special requests

### 🔍 Multi-Platform Search & Comparison
- **Search Across Platforms**: Automatically search for restaurants and dishes on:
  - Swiggy
  - Zomato
  - Blinkit (for groceries/quick commerce)

- **Price Comparison**: Beautiful side-by-side comparison showing:
  - Item prices
  - Delivery fees
  - Total costs
  - Ratings
  - Best deal highlighting

### 📝 Review Aggregation
- Curated reviews from multiple sources
- Sentiment analysis (Pros vs Cons)
- Common themes extraction
- Overall rating summaries

### 🤖 Automated Order Placement
- **Full Workflow Automation**:
  1. Set delivery location
  2. Search for restaurant
  3. Find specific items
  4. Handle customizations (drinks, toppings, etc.)
  5. Add  to cart with correct quantity
  6. Navigate to checkout
  7. **STOP before payment** (for security)

### 🔒 Security First
- ✅ Never handles payment information
- ✅ Never stores credentials
- ✅ Transparent automation (visible browser)
- ✅ User completes final payment step

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Google Gemini API Key**: Get free at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Chrome Browser**: Required for web automation
- **Windows OS**: Tested on Windows (should work on Mac/Linux with minor adjustments)

## 🚀 Installation

### 1. Clone/Download the Project

```bash
cd c:\Users\asus\Downloads\order_adk_agent
```

### 2. Create Virtual Environment (Recommended)

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file:

```powershell
copy .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

**Get your API key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey) and create a new API key (it's free!).

## 🎯 Usage

### 🚀 Quick Start (All Platforms)

**Step 1: Launch Chrome with Debugging**

The bot needs to connect to your Chrome browser. Use our cross-platform launcher:

```bash
# Works on Windows, Linux, macOS, and WSL!
python3 launch_chrome_debug.py
```

This will:
- ✅ Automatically detect your OS (Windows/Linux/macOS/WSL)
- ✅ Close existing Chrome instances
- ✅ Launch Chrome with remote debugging on port 9222
- ✅ Use your existing Chrome profile (stay logged in!)

**Step 2: Login to Food Delivery Sites**

In the Chrome window that just opened:
1. Go to Swiggy/Zomato/Blinkit
2. Login to your account
3. Set your delivery location

**Step 3: Run the Agent**

```bash
python3 run_agent.py
```

Now you can order food and the bot will automate it in your logged-in Chrome!

---

### 🖥️ Platform-Specific Notes

<details>
<summary><b>🪟 Windows (Native)</b></summary>

Run directly in PowerShell or Command Prompt:
```powershell
python launch_chrome_debug.py
python run_agent.py
```
</details>

<details>
<summary><b>🐧 WSL (Windows Subsystem for Linux)</b></summary>

The script automatically detects WSL and uses your Windows Chrome:
```bash
# In WSL terminal
python3 launch_chrome_debug.py
python3 run_agent.py
```

Chrome will open on your Windows desktop with your profile!
</details>

<details>
<summary><b>🐧 Linux (Native)</b></summary>

Make sure Chrome is installed:
```bash
sudo apt-get install google-chrome-stable
python3 launch_chrome_debug.py
python3 run_agent.py
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

Install Chrome if needed:
```bash
brew install --cask google-chrome
python3 launch_chrome_debug.py
python3 run_agent.py
```
</details>

---

### Basic Conversation

```
You: I want pizza for dinner
🤖 BUTLER: Great choice! Based on your location in MG Road, Bangalore, 
here are my top pizza suggestions:

1. Margherita Pizza from Domino's - ₹299
2. Pepperoni Pizza from Pizza Hut - ₹399
3. Farmhouse Pizza from Domino's - ₹349

Would you like me to search for prices across Swiggy, Zomato, and Blinkit?
```

### Comparing Prices

```
You: Yes, compare prices for Margherita Pizza
🤖 BUTLER: Searching across all platforms...

📊 Price Comparison for Margherita Pizza

┌──────────────────────────────────────────────────────────────┐
│ Platform  │ Restaurant │ Price │ Delivery │ Total │ Rating  │
├──────────────────────────────────────────────────────────────┤
│🏆 Swiggy   │ Domino's   │ ₹299  │ ₹0       │ ₹299  │ 4.5⭐   │
│   Zomato   │ Domino's   │ ₹299  │ ₹49      │ ₹348  │ 4.3⭐   │
└──────────────────────────────────────────────────────────────┘

✅ Best Deal: Domino's on Swiggy - Free Delivery!
```

### Placing an Order

#### Method 1: Through Conversation

```
You: Order 2 Margherita pizzas from Domino's on Swiggy
🤖 BUTLER: 
🛒 Order Summary:
- Restaurant: Domino's
- Item: Margherita Pizza x2
- Platform: Swiggy
- Total: ₹598

Proceed with order? (yes/no)

You: yes
🤖 BUTLER: Starting automated order placement...
```

#### Method 2: Direct Command

```
You: place order: Swiggy, McDonald's, McAloo Tikki Burger, 4
```

Format: `place order: <platform>, <restaurant>, <item>, <quantity>`

### Special Commands

```
/help              - Show all commands
/history           - View your order history
/preferences       - View your preferences
/location          - View saved locations
/set_location <loc> - Update location
/set_budget <min> <max> - Set budget range
```

## 📁 Project Structure

```
order_adk_agent/
├── agent/
│   ├── main_agent.py          # Core AI agent
│   ├── tools/
│   │   ├── price_comparator.py
│   │   └── review_aggregator.py
│   ├── automation/
│   │   ├── base_automator.py
│   │   ├── swiggy_automator.py
│   │   ├── zomato_automator.py
│   │   └── blinkit_automator.py
│   └── data/
│       ├── user_preferences.py
│       ├── order_history.py
│       └── location_manager.py
├── config/
│   ├── settings.py
│   └── prompts.py
├── data/
│   ├── users/                 # User data (JSON)
│   └── cache/                 # Search cache
├── requirements.txt
├── .env                       # Your configuration
├── run_agent.py              # Main entry point
└── README.md
```

## 🎬 Demo Mode

Try the demo without an API key to see the order workflow:

```powershell
python run_agent.py --demo
```

## 🔧 Configuration

### Environment Variables (.env)

```
# Google Gemini API
GEMINI_API_KEY=your_key_here

# Browser Settings
HEADLESS_MODE=false              # Set to 'true' for headless browser  
BROWSER_TIMEOUT=30

# Platform URLs (default values shown)
SWIGGY_URL=https://www.swiggy.com
ZOMATO_URL=https://www.zomato.com
BLINKIT_URL=https://www.blinkit.com

# User Settings
DEFAULT_USER_ID=user_001

# Cache
ENABLE_CACHE=true
CACHE_EXPIRY_HOURS=24

# Logging
LOG_LEVEL=INFO
```

### Headless Mode

For automation without visible browser:

```
HEADLESS_MODE=true
```

**Note**: Recommended to keep it `false` initially to see the automation in action!

## 💡 Example Workflows

### Workflow 1: Discovery to Order

```
1. You: "I'm hungry, suggest something for lunch"
2. Bot: [Suggests 5 options based on your preferences]
3. You: "Show me options for biryani"
4. Bot: [Searches across platforms, shows price comparison]
5. You: "Order the Hyderabadi Biryani from Paradise on Swiggy"
6. Bot: [Confirms order details]
7. You: "yes"
8. Bot: [Automates the order, browser opens]
9. Browser navigates through Swiggy automatically
10. Bot: "Order ready! Please complete payment"
11. You: [Complete payment in browser]
```

### Workflow 2: Quick Reorder

```
You: /history
Bot: [Shows your past orders]
You: "Reorder my last order"
Bot: "You ordered 4x McAloo Tikki from McDonald's. Shall I place the same order?"
You: "yes"
Bot: [Automates the order]
```

### Workflow 3: Budget-Conscious Search

```
You: "I have ₹200, what can I get?"
Bot: [Suggests options within budget, sorted by value]
You: "Compare prices for option 1"
Bot: [Shows which platform has best deal]
```

## 🐛 Troubleshooting

### Issue: "GEMINI_API_KEY not found"

**Solution**: 
1. Create `.env` file from `.env.example`
2. Add your Gemini API key
3. Restart the application

### Issue: "ChromeDriver not found"

**Solution**: Install webdriver-manager:
```powershell
pip install webdriver-manager
```
It will auto-download ChromeDriver on first run.

### Issue: "Element not found" during automation

**Cause**: Website UI changed

**Solution**:
- Platform UIs change frequently
- The automation uses flexible selectors but may need updates
- Try different platforms
- Report the issue for updates

### Issue: Browser closes immediately

**Solution**: Check `HEADLESS_MODE` in `.env`:
```
HEADLESS_MODE=false
```

## 🔐 Privacy & Security

### What Data is Stored?

- **User Preferences**: Dietary restrictions, budget, favorite cuisines (stored locally in JSON)
- **Order History**: Past orders for recommendations (stored locally)
- **Locations**: Delivery addresses (stored locally)

### What's Never Stored?

- ❌ Payment information
- ❌ Login credentials
- ❌ Credit/debit card details
- ❌ Passwords

### Data Location

All user data is stored in:
```
data/users/<user_id>.json
data/users/<user_id>_orders.json
data/users/<user_id>_locations.json
```

You can delete these files anytime to reset your profile.

## 🚧Development Roadmap

### Current Features (v1.0)
- ✅ AI meal suggestions
- ✅ Multi-platform search
- ✅ Price comparison
- ✅ Review aggregation
- ✅ Automated order placement (Swiggy, Zomato, Blinkit)

### Planned Features (v2.0)
- [ ] Voice interface
- [ ] WhatsApp bot integration
- [ ] Scheduled orders ("Order my usual breakfast at 8 AM daily")
- [ ] Group orders
- [ ] Nutritional analysis
- [ ] Cost tracking & budgeting
- [ ] Restaurant recommendations based on time/weather

## 📝 License

This project is for educational and personal use.

## 🙏 Acknowledgments

- **Google Gemini**: For the amazing AI capabilities
- **Selenium**: For web automation
- **Rich**: For beautiful terminal UI

## 📧 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments
3. Test with demo mode first

## 🎉 Happy Ordering!

Enjoy discovering and ordering delicious food with the power of AI! 🍕🍔🍜

---

**Made with ❤️ and 🤖 by the power of Google ADK (Agent Development Kit)**
