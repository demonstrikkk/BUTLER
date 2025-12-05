# 🚀 BUTLER Extension - Complete Installation & Usage Guide

## ✅ What You Just Got

A **complete, production-ready Chrome extension** with:

- ✨ Beautiful blue-beige UI (popup, side panel, settings)
- 🤖 Gemini AI integration with function calling
- 🔧 Chrome DevTools MCP for browser automation
- 🔍 Multi-platform search (Swiggy, Zomato, Blinkit)
- 📊 Price comparison and review analysis
- ⚙️ Comprehensive settings and preferences
- 🎯 Full automation workflow

---

## 📦 Installation (5 Minutes)

### Step 1: Get Your Gemini API Key (FREE)

1. Open: https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Click **"Create API Key"**
4. Click **"Create API key in new project"**
5. **Copy the API key** (starts with `AIza...`)

> ⏰ Takes 30 seconds!

### Step 2: Load Extension in Chrome

**From Windows:**
1. Open Chrome
2. Go to: `chrome://extensions/`
3. Toggle **"Developer mode"** ON (top right)
4. Click **"Load unpacked"**
5. Navigate to: `C:\Users\asus\Downloads\order_adk_agent\browser-extension`
6. Click **"Select Folder"**
7. ✅ Extension loaded!

**From WSL:**
```bash
# Launch Windows Chrome
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" &

# Then follow Windows steps above in the Chrome window
```

### Step 3: Configure Extension (2 Minutes)

1. Click the **BUTLER icon** in Chrome toolbar
   - If you don't see it, click the puzzle icon and pin BUTLER

2. Click **"Settings"** (⚙️ button)

3. Enter your configuration:
   ```
   ✅ Gemini API Key: AIza... (paste your key)
   ✅ Location: Rohini Sector 11, Delhi (or your area)
   ✅ Dietary: Eggitarian (or your preference)
   ✅ Budget: ₹0 - ₹2000
   ✅ Spice Level: Medium
   ```

4. Click **"Test Connection"** to verify API key

5. Click **"💾 Save Settings"**

6. ✅ You're ready to go!

---

## 🎯 How to Use

### Method 1: Quick Actions (Popup)

1. **Click extension icon**
2. Choose action:
   - 💬 **Open Chat** - Full AI conversation
   - 🔍 **Quick Search** - Search all platforms
   - 📊 **Compare** - Price comparison

### Method 2: Side Panel (Recommended)

1. **Open side panel**: Click extension icon → "Open Chat"

2. **Chat with AI**:
   ```
   You: Find best biryani restaurants near me
   
   AI: 🔍 Searching across Swiggy, Zomato, and Blinkit...
   
   Here are the top biryani options:
   
   1. Paradise Biryani (Swiggy)
      ⭐ 4.5 | 💰 ₹350 | 🕒 30 min
      
   2. Biryani Blues (Zomato)
      ⭐ 4.3 | 💰 ₹380 | 🕒 35 min
   
   Would you like me to compare prices?
   ```

3. **Compare Prices**:
   ```
   You: Yes, compare prices for Chicken Biryani
   
   AI: 📊 Here's the comparison:
   
   🏆 Best Deal: Paradise on Swiggy - ₹350
   💰 Save ₹80 compared to Zomato!
   
   Want me to place the order?
   ```

4. **Automate Order**:
   ```
   You: Yes, order 1 Chicken Biryani from Paradise on Swiggy
   
   AI: 🤖 Starting automation...
   
   ✅ Navigated to Swiggy
   ✅ Searched for Paradise Biryani
   ✅ Found restaurant
   ✅ Added Chicken Biryani to cart
   
   📦 Cart ready! Please complete payment at checkout.
   ```

---

## 🔥 Example Conversations

### Example 1: Quick Dinner

```
You: I want pizza for dinner under ₹500

AI: 🍕 Great choice! Based on your budget and location:

Top 3 Options:
1. Domino's Margherita - ₹299 (Swiggy) ⭐ 4.5
2. Pizza Hut Veggie Supreme - ₹399 (Zomato) ⭐ 4.3
3. Oven Story Farmhouse - ₹349 (Blinkit) ⭐ 4.6

Would you like me to:
- Compare these prices?
- Show reviews?
- Place an order?
```

### Example 2: Health-Conscious

```
You: Suggest healthy dinner options with low calories

AI: 🥗 Based on your eggitarian preference, here are healthy options:

1. Grilled Paneer Salad - Freshii (₹280)
   • Protein-rich
   • ~350 calories
   • ⭐ 4.4 rating

2. Quinoa Buddha Bowl - The Bowl Company (₹320)
   • High fiber
   • ~400 calories
   • ⭐ 4.6 rating

Which one sounds good?
```

### Example 3: Comparing Deals

```
You: Where can I get the cheapest burger combo?

AI: 🔍 Searching burger combos across platforms...

📊 Best Deals:

🏆 McDonald's McAloo Tikki Combo:
   • Swiggy: ₹149 (Free delivery) ← BEST DEAL
   • Zomato: ₹149 + ₹40 delivery = ₹189
   • Blinkit: Not available

💰 Save ₹40 by ordering on Swiggy!

Order now?
```

---

## 🎨 UI Features

### Popup (Quick Access)
- **Status Indicator**: Shows AI connection status
- **Platform Detection**: Knows which site you're on
- **Quick Stats**: Your savings and order count
- **Fast Actions**: One-click to chat, search, or compare

### Side Panel (Main Interface)
- **Chat Tab** 💬: Full AI conversation with context
- **Search Tab** 🔍: Multi-platform search with filters
- **Compare Tab** 📊: Side-by-side price comparison
- **History Tab** 📜: Track your orders and savings

### Settings Page
- **API Configuration**: Manage Gemini API key
- **User Preferences**: Location, diet, budget, spice
- **Automation Settings**: Control automation behavior
- **Data Management**: Clear history, reset settings

---

## 🤖 Chrome MCP Automation

The extension uses **Chrome DevTools Protocol** for automation:

### What MCP Does:

1. **Navigate** - Opens platform websites
   ```javascript
   #chrome.navigate → "https://www.swiggy.com"
   ```

2. **Search** - Types in search boxes
   ```javascript
   #chrome.type → input[placeholder="Search"] → "biryani"
   ```

3. **Click** - Clicks buttons and links
   ```javascript
   #chrome.click → button[aria-label="ADD TO CART"]
   ```

4. **Extract** - Reads data from pages
   ```javascript
   #chrome.extract → .restaurant-card → [names, prices, ratings]
   ```

5. **Monitor** - Tracks performance
   ```javascript
   #chrome.performance → {loadTime, LCP, etc.}
   ```

### Automation Flow:

```
🔍 Search Query
    ↓
🌐 Navigate to Platform
    ↓
⌨️  Type Search Term
    ↓
⏳ Wait for Results
    ↓
📊 Extract Data
    ↓
🤖 AI Analyzes
    ↓
👆 Click Restaurant
    ↓
➕ Add to Cart
    ↓
✅ Ready for Checkout
```

---

## 🎯 Pro Tips

### 💰 Save Money
1. **Always compare** before ordering
2. Use the **Compare Tab** for side-by-side prices
3. Check **"Best Deal"** highlighted in comparisons
4. Track your **monthly savings** in the popup

### ⚡ Speed Up Ordering
1. Set your **default location** in settings
2. Use **suggestion chips** for common searches
3. Right-click text → **"Search with BUTLER"**
4. Create **keyboard shortcuts** in `chrome://extensions/shortcuts`

### 🎨 Customize Experience
1. Set **dietary restrictions** to filter results
2. Adjust **budget range** for relevant suggestions
3. Set **spice level** for accurate recommendations
4. Enable/disable platforms based on preferences

### 🔒 Privacy & Security
1. API key stored **locally** in your browser
2. No data sent to third parties
3. All automation happens **in your browser**
4. Clear history anytime from settings

---

## 🐛 Troubleshooting

### Extension Not Showing Up?
- Click puzzle icon → Pin BUTLER
- Refresh `chrome://extensions/` page
- Check "Errors" section in extensions page

### AI Not Responding?
- Verify API key in Settings → Test Connection
- Check internet connection
- Open DevTools (F12) → Console for errors
- Try clearing chat history in Settings

### Automation Not Working?
- Make sure you're logged into the platform
- Enable "Browser Automation" in Settings
- Check if page loaded completely
- Platform UI may have changed (update selectors)

### Can't Save Settings?
- Check browser storage permissions
- Try incognito mode
- Clear browser cache
- Reinstall extension

---

## 🚀 Advanced Usage

### Custom Automations

You can extend the extension with custom commands. Edit `services/automation-orchestrator.js`:

```javascript
// Add custom platform
async customPlatformSearch(query) {
  const tab = await chrome.tabs.create({ 
    url: 'https://custom-platform.com' 
  });
  
  await this.mcp.waitForPageLoad(tab.id);
  await this.mcp.typeText(tab.id, '#search', query);
  await this.mcp.clickElement(tab.id, 'button[type="submit"]');
  
  return await this.mcp.extractPageData(tab.id, 'custom');
}
```

### Add New AI Functions

Edit `services/gemini-service.js` to add custom tools:

```javascript
{
  name: 'track_nutrition',
  description: 'Track nutritional information for ordered food',
  parameters: {
    type: 'object',
    properties: {
      foodItem: { type: 'string' },
      calories: { type: 'number' }
    }
  }
}
```

---

## 📊 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI**: Google Gemini 1.5 Flash (Function Calling)
- **Automation**: Chrome DevTools Protocol (CDP)
- **Architecture**: MV3 Service Worker
- **Storage**: Chrome Storage API (sync + local)
- **UI Framework**: Vanilla JS (no dependencies!)

---

## 🎉 You're All Set!

Your BUTLER extension is ready to:
- 🔍 Search across multiple platforms
- 📊 Compare prices automatically
- 🤖 Automate food ordering
- 💰 Save you money
- ⏰ Save you time

**Next Steps:**
1. Try ordering your favorite food
2. Explore the side panel features
3. Customize your preferences
4. Check your savings stats

---

**Happy Food Ordering! 🍕🍔🍜**

Need help? Check the console logs or open an issue!
