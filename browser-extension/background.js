// Background Service Worker - BUTLER Extension
// Handles AI integration, Chrome DevTools MCP, and automation orchestration

import { GeminiAIService } from './services/gemini-service.js';
import { ChromeDevToolsMCP } from './services/chrome-mcp.js';
import { AutomationOrchestrator } from './services/automation-orchestrator.js';
import { GoogleSearchService } from './services/google-search.js';

class BUTLERBackground {
  constructor() {
    this.gemini = null;
    this.chromeMCP = new ChromeDevToolsMCP();
    this.orchestrator = new AutomationOrchestrator(this.chromeMCP);
    this.googleSearch = new GoogleSearchService();
    this.activeTab = null;
    this.isInitialized = false;
    
    this.init();
  }

  async init() {
    console.log('🍔 BUTLER Background Service initializing...');
    
    // Load settings and API key
    const settings = await this.loadSettings();
    
    if (settings.apiKey) {
      this.gemini = new GeminiAIService(settings.apiKey);
      await this.gemini.initialize();
      this.isInitialized = true;
      console.log('✅ BUTLER initialized with Gemini AI');
    } else {
      console.warn('⚠️ No API key found. Please configure in settings.');
    }
    
    // Set up listeners
    this.setupMessageListeners();
    this.setupTabListeners();
    this.setupContextMenus();
  }

  async loadSettings() {
    const result = await chrome.storage.sync.get({
      apiKey: '',
      preferences: {
        dietary: 'none',
        budget: { min: 0, max: 5000 },
        spiceLevel: 'medium'
      },
      location: '',
      enableAutomation: true
    });
    return result;
  }

  setupMessageListeners() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Keep channel open for async response
    });
  }

  async handleMessage(message, sender, sendResponse) {
    console.log('📨 Message received:', message.type);

    try {
      switch (message.type) {
        case 'CHAT_MESSAGE':
          await this.handleChatMessage(message.data, sendResponse);
          break;

        case 'SEARCH_FOOD':
          await this.handleFoodSearch(message.data, sendResponse);
          break;

        case 'COMPARE_PRICES':
          await this.handlePriceComparison(message.data, sendResponse);
          break;

        case 'PLACE_ORDER':
          await this.handlePlaceOrder(message.data, sendResponse);
          break;

        case 'EXTRACT_PAGE_DATA':
          await this.handleExtractPageData(sender.tab, sendResponse);
          break;

        case 'PROCEED_TO_CHECKOUT':
          await this.handleProceedToCheckout(message.data, sendResponse);
          break;

        case 'GET_STATUS':
          sendResponse({
            success: true,
            data: {
              isInitialized: this.isInitialized,
              hasApiKey: !!this.gemini,
              activeTab: this.activeTab
            }
          });
          break;

        case 'SWITCH_TAB':
          // Forward to sidepanel
          chrome.runtime.sendMessage(message);
          sendResponse({ success: true });
          break;

        default:
          sendResponse({ success: false, error: 'Unknown message type' });
      }
    } catch (error) {
      console.error('❌ Error handling message:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async handleChatMessage(data, sendResponse) {
    if (!this.gemini) {
      sendResponse({
        success: false,
        error: 'AI service not initialized. Please add API key in settings.'
      });
      return;
    }

    const { message, context } = data;
    
    // Get current platform context if on food delivery site
    const platform = await this.detectCurrentPlatform();
    
    // Prepare context for AI
    const fullContext = {
      ...context,
      platform: platform,
      userPreferences: await this.getUserPreferences()
    };

    // Get AI response with function calling
    const response = await this.gemini.chat(message, fullContext);
    
    // Handle function calls from AI
    if (response.functionCalls && response.functionCalls.length > 0) {
      const functionResults = await this.executeFunctionCalls(response.functionCalls);
      
      // Send results back to AI for final response
      const finalResponse = await this.gemini.continueChat(functionResults);
      
      sendResponse({
        success: true,
        data: {
          message: finalResponse.text,
          functionCalls: response.functionCalls,
          functionResults: functionResults
        }
      });
    } else {
      sendResponse({
        success: true,
        data: {
          message: response.text
        }
      });
    }
  }

  async handleFoodSearch(data, sendResponse) {
    const { query, platforms } = data;
    
    console.log(`🔍 Searching Google for: ${query} on platforms:`, platforms);
    
    try {
      // Use Google Search (ADK) to find restaurants
      const settings = await this.loadSettings();
      const searchResults = await this.googleSearch.search(query, {
        location: settings.location,
        platforms: platforms || ['swiggy', 'zomato', 'blinkit'],
        dietary: settings.preferences?.dietary
      });
      
      sendResponse({
        success: true,
        data: searchResults
      });
    } catch (error) {
      console.error('Google search error:', error);
      sendResponse({
        success: false,
        error: error.message
      });
    }
  }

  async handlePriceComparison(data, sendResponse) {
    const { item, restaurant } = data;
    
    console.log(`📊 Comparing prices for: ${item} at ${restaurant}`);
    
    const comparison = await this.orchestrator.comparePrices(item, restaurant);
    
    sendResponse({
      success: true,
      data: comparison
    });
  }

  async handlePlaceOrder(data, sendResponse) {
    const { platform, restaurant, items } = data;
    
    console.log(`🚀 Automating order on ${platform}: ${restaurant}`);
    
    try {
      const result = await this.orchestrator.automateOrder({
        platform,
        restaurant,
        items
      });
      
      sendResponse({
        success: true,
        data: result
      });
    } catch (error) {
      sendResponse({
        success: false,
        error: error.message
      });
    }
  }

  async handleProceedToCheckout(data, sendResponse) {
    const { tabId, platform } = data;
    
    console.log(`🛒 Proceeding to checkout on ${platform}, tab: ${tabId}`);
    
    try {
      // Define platform-specific checkout button selectors
      const checkoutSelectors = {
        swiggy: [
          'button[data-testid="checkout-button"]',
          'button:contains("Checkout")',
          'button:contains("Proceed to Checkout")',
          '.checkout-button'
        ],
        zomato: [
          'button:contains("Proceed to Pay")',
          'button[data-e2e="checkout-button"]',
          '.proceed-to-pay',
          'button:contains("Checkout")'
        ],
        blinkit: [
          'button:contains("Proceed")',
          'button:contains("Checkout")',
          '.checkout-btn'
        ]
      };
      
      const selectors = checkoutSelectors[platform] || checkoutSelectors.swiggy;
      
      // Try to find and click checkout button
      let clicked = false;
      for (const selector of selectors) {
        try {
          await this.chromeMCP.clickElement(tabId, selector);
          clicked = true;
          console.log(`✅ Clicked checkout button: ${selector}`);
          break;
        } catch (e) {
          // Try next selector
          continue;
        }
      }
      
      if (clicked) {
        // Wait a bit for navigation
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        sendResponse({
          success: true,
          message: '✅ Proceeding to checkout! Please complete payment to finish your order.'
        });
      } else {
        sendResponse({
          success: false,
          error: 'Could not find checkout button. Please click "Checkout" manually.'
        });
      }
      
    } catch (error) {
      console.error('Checkout error:', error);
      sendResponse({
        success: false,
        error: `Checkout error: ${error.message}. Please complete checkout manually.`
      });
    }
  }

  async handleExtractPageData(tab, sendResponse) {
    if (!tab) {
      sendResponse({ success: false, error: 'No active tab' });
      return;
    }

    const platform = this.detectPlatformFromUrl(tab.url);
    
    if (!platform) {
      sendResponse({ success: false, error: 'Not a supported food delivery platform' });
      return;
    }

    // Use Chrome MCP to extract data
    const pageData = await this.chromeMCP.extractPageData(tab.id, platform);
    
    sendResponse({
      success: true,
      data: {
        platform,
        ...pageData
      }
    });
  }

  async executeFunctionCalls(functionCalls) {
    const results = [];
    
    for (const call of functionCalls) {
      console.log(`🔧 Executing function: ${call.name}`);
      
      try {
        let result;
        
        switch (call.name) {
          case 'search_food':
            // Use Google Search first
            const settings = await this.loadSettings();
            const searchResults = await this.googleSearch.search(
              call.args.query,
              {
                location: settings.location,
                platforms: call.args.platforms || ['swiggy', 'zomato', 'blinkit'],
                dietary: call.args.filters?.dietary || settings.preferences?.dietary
              }
            );
            // Format for AI response
            result = {
              searchResults: searchResults,
              message: `Found ${searchResults.length} results from Google Search`,
              query: call.args.query
            };
            break;
            
          case 'compare_prices':
            result = await this.orchestrator.comparePrices(
              call.args.item,
              call.args.restaurant
            );
            break;
            
          case 'place_order':
            result = await this.orchestrator.automateOrder({
              platform: call.args.platform,
              restaurant: call.args.restaurant,
              items: call.args.items
            });
            break;
            
          case 'get_reviews':
            result = await this.orchestrator.aggregateReviews(
              call.args.restaurant,
              call.args.platform
            );
            break;
            
          case 'analyze_menu':
            result = await this.orchestrator.analyzeMenu(
              call.args.restaurant,
              call.args.platform
            );
            break;
            
          default:
            result = { error: `Unknown function: ${call.name}` };
        }
        
        results.push({
          name: call.name,
          result: result
        });
        
      } catch (error) {
        results.push({
          name: call.name,
          error: error.message
        });
      }
    }
    
    return results;
  }

  setupTabListeners() {
    // Track active tab
    chrome.tabs.onActivated.addListener(async (activeInfo) => {
      const tab = await chrome.tabs.get(activeInfo.tabId);
      this.activeTab = tab;
      
      // Update UI with current platform
      const platform = this.detectPlatformFromUrl(tab.url);
      if (platform) {
        chrome.runtime.sendMessage({
          type: 'PLATFORM_DETECTED',
          data: { platform, url: tab.url }
        });
      }
    });

    // Listen for navigation
    chrome.webNavigation.onCompleted.addListener(async (details) => {
      if (details.frameId === 0) { // Main frame only
        const platform = this.detectPlatformFromUrl(details.url);
        if (platform) {
          console.log(`📍 Navigated to ${platform}:`, details.url);
        }
      }
    });
  }

  setupContextMenus() {
    try {
      chrome.runtime.onInstalled.addListener(() => {
        chrome.contextMenus.create({
          id: 'BUTLER-search',
          title: 'Search with BUTLER',
          contexts: ['selection']
        });

        chrome.contextMenus.create({
          id: 'BUTLER-compare',
          title: 'Compare prices',
          contexts: ['selection']
        });
      });

      chrome.contextMenus.onClicked.addListener((info, tab) => {
        if (info.menuItemId === 'BUTLER-search') {
          this.handleFoodSearch(
            { query: info.selectionText, platforms: ['swiggy', 'zomato', 'blinkit'] },
            (response) => {
              this.openSidePanelWithResults(tab.id, response.data);
            }
          );
        }
      });
    } catch (error) {
      console.warn('Context menus not available:', error);
    }
  }

  detectPlatformFromUrl(url) {
    if (!url) return null;
    
    if (url.includes('swiggy.com')) return 'swiggy';
    if (url.includes('zomato.com')) return 'zomato';
    if (url.includes('blinkit.com')) return 'blinkit';
    
    return null;
  }

  async detectCurrentPlatform() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return this.detectPlatformFromUrl(tab?.url);
  }

  async getUserPreferences() {
    const settings = await this.loadSettings();
    return settings.preferences;
  }

  async openSidePanel(tabId) {
    try {
      // Get the window ID from the tab
      const tab = await chrome.tabs.get(tabId);
      await chrome.sidePanel.open({ windowId: tab.windowId });
    } catch (error) {
      console.error('Failed to open side panel:', error);
    }
  }

  async openSidePanelWithResults(tabId, results) {
    await this.openSidePanel(tabId);
    
    // Send results to side panel
    setTimeout(() => {
      chrome.runtime.sendMessage({
        type: 'SEARCH_RESULTS',
        data: results
      });
    }, 500);
  }
}

// Initialize background service
const BUTLERBackground = new BUTLERBackground();

// Export for testing
export default BUTLERBackground;
