# 🍔 BUTLER - AI Food Ordering Browser Extension

> **Complete AI-powered browser extension for intelligent food ordering across Swiggy, Zomato, and Blinkit**

An intelligent Chrome extension that uses Google Gemini AI and Chrome DevTools MCP (Model Context Protocol) to help you search, compare, and automatically order food across multiple platforms.

---

## ✨ Features

### 🤖 AI-Powered Assistant
- **Intelligent Chat Interface** - Natural language conversations with Gemini AI
- **Function Calling** - AI automatically triggers search, comparison, and automation
- **Context-Aware** - Understands which platform you're on and adapts responses

### 🔍 Smart Search & Comparison
- **Multi-Platform Search** - Search Swiggy, Zomato, and Blinkit simultaneously
- **Price Comparison** - Find the best deals across all platforms
- **Rating Analysis** - Aggregate reviews and sentiment analysis
- **Menu Analysis** - Smart recommendations based on preferences

### 🤖 Browser Automation (Chrome MCP)
- **Automated Ordering** - Full order placement automation using DevTools Protocol
- **Element Interaction** - Click, type, scroll using `#chrome.click`, `#chrome.type`
- **Data Extraction** - Extract restaurant info, prices, reviews from pages
- **Performance Monitoring** - Track page load times and LCP metrics

### 🎨 Beautiful UI (Blue-Beige Theme)
- **Clean Design** - Modern, professional interface
- **Side Panel** - Full-featured chat, search, and comparison interface
- **Quick Actions** - Fast access via popup
- **Settings Page** - Comprehensive configuration options

---

## 🚀 Installation

### Step 1: Clone or Download
```bash
cd /mnt/c/Users/asus/Downloads/order_adk_agent
# The extension is in: browser-extension/
```

### Step 2: Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key (it's free!)

### Step 3: Load Extension in Chrome

#### Method 1: From WSL/Linux
```bash
# Open Chrome from WSL
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" &

# Then follow Method 2 steps
```

#### Method 2: Windows Chrome
1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Navigate to: `C:\Users\asus\Downloads\order_adk_agent\browser-extension`
6. Click "Select Folder"

### Step 4: Configure Extension
1. Click the BUTLER extension icon
2. Click "Settings" (⚙️)
3. Enter your Gemini API key
4. Click "Test Connection" to verify
5. Set your preferences:
   - Location
   - Dietary preferences
   - Budget range
   - Spice level
6. Click "💾 Save Settings"

---

## 📖 Usage Guide

### 🎯 Quick Start

1. **Open Side Panel**
   - Click extension icon → "Open Chat"
   - Or click the side panel icon in Chrome

2. **Chat with AI**
   ```
   You: Find best biryani near me
   AI: Searching across Swiggy, Zomato, and Blinkit...
   [Shows results with prices and ratings]
   ```

3. **Compare Prices**
   ```
   You: Compare prices for Margherita Pizza
   AI: Here's the comparison...
   🏆 Best Deal: Swiggy - ₹299 (Save ₹49!)
   ```

4. **Automate Ordering**
   ```
   You: Order 2 spring rolls from Berco's on Swiggy
   AI: I'll help you with that!
   [Opens Swiggy, searches, adds to cart]
   Ready for payment - please complete checkout
   ```

### 🔍 Search Tab
- Enter food item or restaurant name
- Select platforms (Swiggy/Zomato/Blinkit)
- Click "Search All Platforms"
- View results with prices, ratings, delivery time

### 📊 Compare Tab
- View side-by-side price comparisons
- See best deals highlighted
- Calculate savings

### 📜 History Tab
- Track all your orders
- View savings over time
- Clear history if needed

---

## 🛠️ Chrome DevTools MCP Integration

### Available MCP Tools

The extension uses Chrome DevTools Protocol via MCP for browser automation:

#### Navigation
```javascript
#chrome.navigate - Navigate to URL
await chromeMCP.navigate(tabId, "https://www.swiggy.com");
```

#### Element Interaction
```javascript
#chrome.click - Click element by selector
await chromeMCP.clickElement(tabId, 'button[aria-label="Search"]');

#chrome.type - Type text into input
await chromeMCP.typeText(tabId, 'input[name="search"]', "biryani");

#chrome.waitFor - Wait for element to appear
await chromeMCP.waitForElement(tabId, '.restaurant-card', 10000);
```

#### Data Extraction
```javascript
#chrome.extract - Extract text from elements
const results = await chromeMCP.extractText(tabId, '.restaurant-name');

#chrome.screenshot - Capture page screenshot
const screenshot = await chromeMCP.screenshot(tabId);
```

#### Performance
```javascript
#chrome.performance - Get performance metrics
const metrics = await chromeMCP.getPerformanceMetrics(tabId);
// Returns: loadTime, LCP, FCP, etc.
```

### Automation Workflow Example

```javascript
// Complete automation flow for ordering
async function automateOrder(restaurant, item) {
  // 1. Navigate
  await chromeMCP.navigate(tabId, "https://www.swiggy.com");
  
  // 2. Search
  await chromeMCP.typeText(tabId, 'input[placeholder*="Search"]', restaurant);
  await chromeMCP.waitForElement(tabId, '.restaurant-card');
  
  // 3. Click restaurant
  await chromeMCP.clickElement(tabId, `.restaurant-card:contains("${restaurant}")`);
  
  // 4. Add item to cart
  await chromeMCP.clickElement(tabId, `[data-item="${item}"] button[aria-label="ADD"]`);
  
  // 5. Go to checkout
  await chromeMCP.clickElement(tabId, 'button:contains("VIEW CART")');
  
  // User completes payment manually
}
```

---

## 🎨 Architecture

```
┌─────────────────────────────────────────────────┐
│  BUTLER Extension Architecture               │
└─────────────────────────────────────────────────┘

┌──────────────┐        ┌──────────────┐
│   Popup UI   │◄──────►│  Side Panel  │
│  (Quick      │        │  (Full Chat, │
│   Actions)   │        │   Search,    │
└──────┬───────┘        │   Compare)   │
       │                └──────┬───────┘
       │                       │
       ▼                       ▼
┌─────────────────────────────────────┐
│      Background Service Worker       │
│  ┌─────────────────────────────────┐│
│  │  Message Handler & Orchestrator ││
│  └─────────────────────────────────┘│
│                                      │
│  ┌──────────┐  ┌───────────────┐   │
│  │ Gemini   │  │  Chrome MCP   │   │
│  │   AI     │  │  (DevTools)   │   │
│  │ Service  │  │   Service     │   │
│  └────┬─────┘  └───────┬───────┘   │
│       │                │            │
│       ▼                ▼            │
│  ┌─────────────────────────────┐   │
│  │ Automation Orchestrator     │   │
│  │ ┌─────┐ ┌──────┐ ┌────────┐│   │
│  │ │Swig.│ │Zomat.│ │Blinkit ││   │
│  │ └─────┘ └──────┘ └────────┘│   │
│  └─────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Content Scripts (Platforms)      │
│  ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │ Swiggy  │ │ Zomato  │ │Blinkit ││
│  │ Helper  │ │ Helper  │ │ Helper ││
│  └─────────┘ └─────────┘ └────────┘│
└─────────────────────────────────────┘
```

---

## 🔧 Development

### File Structure
```
browser-extension/
├── manifest.json           # Extension configuration
├── background.js          # Service worker (main orchestrator)
├── popup.html/js          # Quick actions popup
├── sidepanel.html/js      # Main chat interface
├── options.html/js        # Settings page
├── devtools.html/js       # DevTools integration
├── styles/
│   ├── popup.css          # Popup styles
│   ├── sidepanel.css      # Side panel styles
│   └── options.css        # Settings page styles
├── services/
│   ├── gemini-service.js      # Gemini AI integration
│   ├── chrome-mcp.js          # Chrome DevTools MCP
│   └── automation-orchestrator.js  # Platform automation
├── content/
│   ├── swiggy-content.js      # Swiggy page interactions
│   ├── zomato-content.js      # Zomato page interactions
│   └── blinkit-content.js     # Blinkit page interactions
└── icons/                 # Extension icons
```

### Adding New Platforms

1. Create content script in `content/newplatform-content.js`
2. Add to `manifest.json` content_scripts
3. Create automator class in `automation-orchestrator.js`
4. Add platform detection in `background.js`

### Extending AI Capabilities

Add new functions in `services/gemini-service.js`:

```javascript
{
  name: 'new_function',
  description: 'What this function does',
  parameters: {
    type: 'object',
    properties: {
      param1: { type: 'string', description: '...' }
    },
    required: ['param1']
  }
}
```

---

## 🎯 Troubleshooting

### Extension Not Loading
- Make sure you selected the `browser-extension` folder, not the parent folder
- Check Chrome console (F12) for errors
- Verify manifest.json is valid JSON

### AI Not Responding
- Check API key in Settings
- Click "Test Connection" to verify
- Check browser console for errors
- Verify you have internet connection

### Automation Not Working
- Enable "Browser Automation" in Settings
- Make sure you're on the correct platform page
- Check if selectors need updating (platforms change UI frequently)
- Open DevTools Console to see automation logs

### Can't Find Extension Icon
- Click the puzzle icon in Chrome toolbar
- Pin BUTLER extension

---

## 🚀 Future Enhancements

- [ ] Real-time order tracking
- [ ] Coupon code detection and auto-apply
- [ ] Voice ordering support
- [ ] Multi-language support
- [ ] More platforms (Uber Eats, DoorDash)
- [ ] Advanced filters (calories, prep time, etc.)
- [ ] Group ordering coordination
- [ ] Nutrition information tracking

---

## 📝 License

MIT License - Feel free to use, modify, and extend!

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Powering intelligent conversations
- **Chrome DevTools Protocol** - Enabling browser automation
- **Model Context Protocol (MCP)** - Standardized tool integration

---

## 💡 Tips

1. **Save Money** - Always use the Compare tab before ordering
2. **Stay Logged In** - Keep sessions active on all platforms
3. **Set Preferences** - Configure dietary restrictions for better recommendations
4. **Check Reviews** - Ask AI to analyze reviews before ordering
5. **Use Suggestions** - Click suggestion chips for quick searches

---

**Enjoy automated food ordering! 🍕🍔🍜**

Made with ❤️ and AI
