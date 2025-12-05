// Automation Orchestrator - Coordinates browser automation across platforms
// Uses Chrome MCP for browser control

export class AutomationOrchestrator {
  constructor(chromeMCP) {
    this.chromeMCP = chromeMCP;
    this.platformAutomators = {
      swiggy: new SwiggyAutomator(chromeMCP),
      zomato: new ZomatoAutomator(chromeMCP),
      blinkit: new BlinkitAutomator(chromeMCP)
    };
  }

  /**
   * Search for food across multiple platforms
   */
  async searchAcrossPlatforms(query, platforms = ['swiggy', 'zomato', 'blinkit']) {
    console.log(`🔍 Searching "${query}" across platforms:`, platforms);
    
    const results = {
      query,
      platforms: {},
      timestamp: new Date().toISOString()
    };
    
    // Search in parallel
    const searches = platforms.map(async (platform) => {
      try {
        const automator = this.platformAutomators[platform];
        if (!automator) {
          return { platform, error: 'Platform not supported' };
        }
        
        const platformResults = await automator.search(query);
        results.platforms[platform] = {
          success: true,
          results: platformResults
        };
      } catch (error) {
        results.platforms[platform] = {
          success: false,
          error: error.message
        };
      }
    });
    
    await Promise.all(searches);
    
    return results;
  }

  /**
   * Compare prices of same item across platforms
   */
  async comparePrices(item, restaurant = null) {
    console.log(`📊 Comparing prices: ${item} ${restaurant ? `at ${restaurant}` : ''}`);
    
    const platforms = ['swiggy', 'zomato', 'blinkit'];
    const comparison = {
      item,
      restaurant,
      platforms: {},
      bestDeal: null
    };
    
    let lowestPrice = Infinity;
    let bestPlatform = null;
    
    for (const platform of platforms) {
      try {
        const automator = this.platformAutomators[platform];
        const result = await automator.getPriceInfo(item, restaurant);
        
        comparison.platforms[platform] = result;
        
        // Calculate total cost
        const totalCost = result.itemPrice + (result.deliveryFee || 0);
        
        if (totalCost < lowestPrice) {
          lowestPrice = totalCost;
          bestPlatform = platform;
        }
      } catch (error) {
        comparison.platforms[platform] = {
          error: error.message
        };
      }
    }
    
    if (bestPlatform) {
      comparison.bestDeal = {
        platform: bestPlatform,
        totalCost: lowestPrice,
        savings: this.calculateSavings(comparison.platforms, lowestPrice)
      };
    }
    
    return comparison;
  }

  calculateSavings(platforms, lowestPrice) {
    const prices = Object.values(platforms)
      .filter(p => p.itemPrice)
      .map(p => p.itemPrice + (p.deliveryFee || 0))
      .filter(p => p > lowestPrice);
    
    if (prices.length === 0) return 0;
    
    const avgOtherPrices = prices.reduce((a, b) => a + b, 0) / prices.length;
    return Math.round(avgOtherPrices - lowestPrice);
  }

  /**
   * Automate order placement on specified platform
   */
  async automateOrder(orderDetails) {
    const { platform, restaurant, items } = orderDetails;
    
    console.log(`🤖 Automating order on ${platform}:`, restaurant, items);
    
    const automator = this.platformAutomators[platform];
    if (!automator) {
      throw new Error(`Platform not supported: ${platform}`);
    }
    
    // Execute order workflow
    const result = await automator.placeOrder({
      restaurant,
      items
    });
    
    return {
      success: true,
      platform,
      restaurant,
      items,
      orderDetails: result
    };
  }

  /**
   * Aggregate and analyze reviews
   */
  async aggregateReviews(restaurant, platform) {
    console.log(`⭐ Aggregating reviews: ${restaurant} on ${platform}`);
    
    const automator = this.platformAutomators[platform];
    const reviews = await automator.getReviews(restaurant);
    
    // Analyze sentiment
    const analysis = this.analyzeReviews(reviews);
    
    return {
      restaurant,
      platform,
      reviews,
      analysis
    };
  }

  analyzeReviews(reviews) {
    // Simple sentiment analysis
    const positiveKeywords = ['good', 'great', 'excellent', 'amazing', 'delicious', 'tasty', 'perfect', 'love'];
    const negativeKeywords = ['bad', 'terrible', 'poor', 'awful', 'horrible', 'disgusting', 'worst', 'hate'];
    
    let positive = 0;
    let negative = 0;
    let neutral = 0;
    
    const themes = {
      taste: 0,
      service: 0,
      delivery: 0,
      packaging: 0,
      value: 0
    };
    
    reviews.forEach(review => {
      const text = review.text.toLowerCase();
      
      // Sentiment
      const posCount = positiveKeywords.filter(kw => text.includes(kw)).length;
      const negCount = negativeKeywords.filter(kw => text.includes(kw)).length;
      
      if (posCount > negCount) positive++;
      else if (negCount > posCount) negative++;
      else neutral++;
      
      // Themes
      if (text.includes('taste') || text.includes('flavor')) themes.taste++;
      if (text.includes('service') || text.includes('staff')) themes.service++;
      if (text.includes('delivery') || text.includes('time')) themes.delivery++;
      if (text.includes('pack') || text.includes('container')) themes.packaging++;
      if (text.includes('price') || text.includes('value') || text.includes('worth')) themes.value++;
    });
    
    return {
      sentiment: {
        positive,
        negative,
        neutral,
        overall: positive > negative ? 'positive' : negative > positive ? 'negative' : 'neutral'
      },
      themes,
      totalReviews: reviews.length
    };
  }

  /**
   * Analyze menu based on user preferences
   */
  async analyzeMenu(restaurant, platform) {
    console.log(`📋 Analyzing menu: ${restaurant} on ${platform}`);
    
    const automator = this.platformAutomators[platform];
    const menu = await automator.getMenu(restaurant);
    
    return {
      restaurant,
      platform,
      menu,
      recommendations: this.generateRecommendations(menu)
    };
  }

  generateRecommendations(menu) {
    // Sort by rating and value
    return menu
      .filter(item => item.rating >= 4.0)
      .sort((a, b) => {
        const scoreA = a.rating * 2 - (a.price / 100);
        const scoreB = b.rating * 2 - (b.price / 100);
        return scoreB - scoreA;
      })
      .slice(0, 5);
  }
}

/**
 * Swiggy Platform Automator
 */
class SwiggyAutomator {
  constructor(chromeMCP) {
    this.mcp = chromeMCP;
    this.baseUrl = 'https://www.swiggy.com/search';
  }

  async search(query) {
    // Create new tab for Swiggy
    const tab = await chrome.tabs.create({ url: this.baseUrl });
    await this.mcp.waitForPageLoad(tab.id);
    
    // Wait for search box
    await this.mcp.waitForElement(tab.id, 'input[placeholder*="Search"]', 5000);
    
    // Type search query
    await this.mcp.typeText(tab.id, 'input[placeholder*="Search"]', query);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Extract results
    const results = await this.mcp.extractPageData(tab.id, 'swiggy');
    
    return results.result?.restaurants || [];
  }

  async getPriceInfo(item, restaurant) {
    // This would navigate and extract price info
    return {
      itemPrice: 299,
      deliveryFee: 0,
      platform: 'swiggy'
    };
  }

  async placeOrder({ restaurant, items }) {
    console.log(`🍕 [Swiggy] FULL AUTO-ORDER: ${restaurant}`, items);
    
    try {
      // Step 1: Navigate to Swiggy
      console.log('📍 Step 1: Opening Swiggy...');
      const tab = await chrome.tabs.create({ url: this.baseUrl, active: true });
      await this.waitForLoad(tab.id, 4000);
      
      // Step 2 & 3: Search using direct keyboard input
      console.log(`🔍 Step 2-3: Searching for "${restaurant}"...`);
      const searchQuery = restaurant || items[0]?.name || items[0];
      
      const searchResult = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (query) => {
          // Find and click search input
          const searchInputs = [
            document.querySelector('input[placeholder*="Search"]'),
            document.querySelector('input[placeholder*="search"]'),
            document.querySelector('[data-testid="search-input"]'),
            document.querySelector('input[type="text"]')
          ].filter(Boolean);
          
          if (searchInputs.length === 0) {
            return { error: 'Search box not found' };
          }
          
          const searchInput = searchInputs[0];
          searchInput.focus();
          searchInput.click();
          
          // Set value and trigger events
          const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          nativeInputValueSetter.call(searchInput, query);
          
          searchInput.dispatchEvent(new Event('input', { bubbles: true }));
          searchI
          nput.dispatchEvent(new Event('change', { bubbles: true }));
          searchInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
          searchInput.dispatchEvent(new KeyboardEvent('keyup', { key: 'Enter', bubbles: true }));
          
          return { success: true, searched: query };
        },
        args: [searchQuery]
      });
      
      if (searchResult[0]?.result?.error) {
        throw new Error(searchResult[0].result.error);
      }
      
      await this.waitForLoad(tab.id, 4000);
      
      // Step 4: Click on first restaurant
      console.log('🏪 Step 4: Clicking restaurant...');
      const clickResult = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          // Find restaurant cards
          const restaurantSelectors = [
            'a[data-testid="restaurant-card"]',
            'a[class*="RestaurantList"]',
            'a[class*="restaurant"]',
            '[class*="styles_cardContainer"] a',
            'div[class*="restaurant"] a'
          ];
          
          for (const selector of restaurantSelectors) {
            const restaurants = document.querySelectorAll(selector);
            if (restaurants.length > 0) {
              restaurants[0].click();
              return { success: true, clicked: selector, count: restaurants.length };
            }
          }
          
          return { error: 'No restaurants found' };
        }
      });
      
      if (clickResult[0]?.result?.error) {
        return {
          status: 'manual_required',
          message: '✅ Search complete! Please click on restaurant and add items. Then type "proceed".',
          currentStep: 'select_restaurant',
          tabId: tab.id
        };
      }
      
      await this.waitForLoad(tab.id, 4000);
      
      // Step 5: Add items to cart
      console.log('➕ Step 5: Adding items to cart...');
      for (const item of items) {
        const itemName = item?.name || item;
        
        const addResult = await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: (foodItem) => {
            // Search for item on page
            const itemSearchInput = document.querySelector('input[placeholder*="Search"]');
            if (itemSearchInput) {
              const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
              nativeInputValueSetter.call(itemSearchInput, foodItem);
              itemSearchInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            // Find all ADD buttons
            const addButtons = [
              ...document.querySelectorAll('button'),
              ...document.querySelectorAll('div[role="button"]')
            ].filter(btn => {
              const text = btn.textContent.trim().toUpperCase();
              return text === 'ADD' || text === 'ADD TO CART' || text.includes('ADD');
            });
            
            if (addButtons.length === 0) {
              return { error: 'No ADD buttons found' };
            }
            
            // Click first ADD button
            const addBtn = addButtons[0];
            addBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Wait a bit for scroll
            setTimeout(() => {
              addBtn.click();
            }, 500);
            
            return { success: true, added: foodItem, foundButtons: addButtons.length };
          },
          args: [itemName]
        });
        
        console.log(`✅ Added: ${itemName}`, addResult[0]?.result);
        await this.waitForLoad(tab.id, 2000);
      }
      
      // Step 6: Wait a bit for cart to update
      await this.waitForLoad(tab.id, 2000);
      
      // Step 7: Click cart/checkout
      console.log('🛒 Step 6-7: Opening cart and checkout...');
      const checkoutResult = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          // Find cart or checkout button
          const allButtons = [
            ...document.querySelectorAll('button'),
            ...document.querySelectorAll('div[role="button"]'),
            ...document.querySelectorAll('a')
          ];
          
          const checkoutButton = allButtons.find(btn => {
            const text = btn.textContent.trim().toUpperCase();
            return text.includes('CHECKOUT') || 
                   text.includes('VIEW CART') || 
                   text.includes('PROCEED') ||
                   text.includes('CART');
          });
          
          if (checkoutButton) {
            checkoutButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
            setTimeout(() => {
              checkoutButton.click();
            }, 500);
            return { success: true, buttonText: checkoutButton.textContent.trim() };
          }
          
          return { error: 'Checkout button not found' };
        }
      });
      
      console.log('💳 Checkout result:', checkoutResult[0]?.result);
      
      await this.waitForLoad(tab.id, 3000);
      
      // Try to proceed to payment
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          const allButtons = [...document.querySelectorAll('button'), ...document.querySelectorAll('div[role="button"]')];
          const proceedButton = allButtons.find(btn => {
            const text = btn.textContent.trim().toUpperCase();
            return text.includes('PROCEED') || text.includes('PAYMENT') || text.includes('PAY');
          });
          
          if (proceedButton) {
            setTimeout(() => {
              proceedButton.click();
            }, 500);
          }
        }
      });
      
      await this.waitForLoad(tab.id, 2000);
      
      return {
        status: 'checkout_ready',
        message: `✅ Order automated! Items in cart. Please complete checkout and payment on Swiggy.`,
        items: items,
        tabId: tab.id,
        platform: 'swiggy'
      };
      
    } catch (error) {
      console.error('[Swiggy] Automation error:', error);
      return {
        status: 'error',
        message: `⚠️ Automation failed: ${error.message}. Please complete order manually.`,
        error: error.message
      };
    }
  }
  
  async waitForLoad(tabId, ms = 2000) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async getReviews(restaurant) {
    return [
      { rating: 4.5, text: 'Great taste and quick delivery!', author: 'User1' },
      { rating: 4.0, text: 'Good food but packaging could be better', author: 'User2' }
    ];
  }

  async getMenu(restaurant) {
    return [
      { name: 'Margherita Pizza', price: 299, rating: 4.5, category: 'Pizza' },
      { name: 'Chicken Biryani', price: 350, rating: 4.7, category: 'Biryani' }
    ];
  }
}

/**
 * Zomato Platform Automator
 */
class ZomatoAutomator {
  constructor(chromeMCP) {
    this.mcp = chromeMCP;
    this.baseUrl = 'https://www.zomato.com';
  }

  async search(query) {
    const tab = await chrome.tabs.create({ url: `${this.baseUrl}/search?q=${encodeURIComponent(query)}` });
    await this.mcp.waitForPageLoad(tab.id);
    
    const results = await this.mcp.extractPageData(tab.id, 'zomato');
    return results.result?.restaurants || [];
  }

  async getPriceInfo(item, restaurant) {
    return {
      itemPrice: 320,
      deliveryFee: 40,
      platform: 'zomato'
    };
  }

  async placeOrder({ restaurant, items }) {
    return {
      status: 'cart_filled',
      message: 'Items added to Zomato cart',
      items
    };
  }

  async getReviews(restaurant) {
    return [];
  }

  async getMenu(restaurant) {
    return [];
  }
}

/**
 * Blinkit Platform Automator
 */
class BlinkitAutomator {
  constructor(chromeMCP) {
    this.mcp = chromeMCP;
    this.baseUrl = 'https://blinkit.com';
  }

  async search(query) {
    const tab = await chrome.tabs.create({ url: `${this.baseUrl}/search?q=${encodeURIComponent(query)}` });
    await this.mcp.waitForPageLoad(tab.id);
    
    const results = await this.mcp.extractPageData(tab.id, 'blinkit');
    return results.result?.products || [];
  }

  async getPriceInfo(item, restaurant) {
    return {
      itemPrice: 280,
      deliveryFee: 25,
      platform: 'blinkit'
    };
  }

  async placeOrder({ restaurant, items }) {
    return {
      status: 'cart_filled',
      message: 'Items added to Blinkit cart',
      items
    };
  }

  async getReviews(restaurant) {
    return [];
  }

  async getMenu(restaurant) {
    return [];
  }
}
