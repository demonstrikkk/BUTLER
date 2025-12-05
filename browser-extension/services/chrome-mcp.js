// Chrome DevTools Model Context Protocol (MCP) Service
// Provides browser automation tools using Chrome DevTools Protocol

export class ChromeDevToolsMCP {
  constructor() {
    this.debuggerSessions = new Map();
  }

  /**
   * Navigate to a URL using chrome.navigate
   * @param {number} tabId - Tab ID
   * @param {string} url - URL to navigate to
   */
  async navigate(tabId, url) {
    console.log(`🔗 #chrome.navigate: ${url}`);
    
    try {
      await chrome.tabs.update(tabId, { url });
      
      // Wait for page load
      await this.waitForPageLoad(tabId);
      
      return { success: true, url };
    } catch (error) {
      console.error('Navigation error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Execute JavaScript in page context
   * @param {number} tabId - Tab ID
   * @param {string} code - JavaScript code to execute
   */
  async executeScript(tabId, code) {
    console.log(`⚙️ #chrome.executeScript on tab ${tabId}`);
    
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: new Function(code)
      });
      
      return {
        success: true,
        result: results[0]?.result
      };
    } catch (error) {
      console.error('Script execution error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Click an element using DevTools Protocol
   * @param {number} tabId - Tab ID
   * @param {string} selector - CSS selector
   */
  async clickElement(tabId, selector) {
    console.log(`👆 #chrome.click: ${selector}`);
    
    return await this.executeInContent(tabId, (sel) => {
      const element = document.querySelector(sel);
      if (!element) {
        throw new Error(`Element not found: ${sel}`);
      }
      
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Simulate real click with mouse events
      const rect = element.getBoundingClientRect();
      const clickEvent = new MouseEvent('click', {
        view: window,
        bubbles: true,
        cancelable: true,
        clientX: rect.left + rect.width / 2,
        clientY: rect.top + rect.height / 2
      });
      
      element.dispatchEvent(clickEvent);
      element.click();
      
      return { clicked: true, selector: sel };
    }, selector);
  }

  /**
   * Type text into an input field
   * @param {number} tabId - Tab ID
   * @param {string} selector - CSS selector
   * @param {string} text - Text to type
   */
  async typeText(tabId, selector, text) {
    console.log(`⌨️ #chrome.type: ${selector} = "${text}"`);
    
    return await this.executeInContent(tabId, (sel, txt) => {
      const element = document.querySelector(sel);
      if (!element) {
        throw new Error(`Element not found: ${sel}`);
      }
      
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.focus();
      
      // Clear existing value
      element.value = '';
      
      // Type character by character (more human-like)
      const chars = txt.split('');
      let currentValue = '';
      
      chars.forEach((char, index) => {
        currentValue += char;
        element.value = currentValue;
        
        // Trigger input events
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
      });
      
      // Trigger blur
      element.blur();
      
      return { typed: true, selector: sel, text: txt };
    }, selector, text);
  }

  /**
   * Extract text content from elements
   * @param {number} tabId - Tab ID
   * @param {string} selector - CSS selector
   */
  async extractText(tabId, selector) {
    console.log(`📄 #chrome.extract: ${selector}`);
    
    return await this.executeInContent(tabId, (sel) => {
      const elements = document.querySelectorAll(sel);
      if (elements.length === 0) {
        return { found: false, selector: sel };
      }
      
      const texts = Array.from(elements).map(el => ({
        text: el.textContent.trim(),
        html: el.innerHTML,
        visible: el.offsetParent !== null
      }));
      
      return {
        found: true,
        count: texts.length,
        items: texts
      };
    }, selector);
  }

  /**
   * Wait for an element to appear
   * @param {number} tabId - Tab ID
   * @param {string} selector - CSS selector
   * @param {number} timeout - Timeout in milliseconds
   */
  async waitForElement(tabId, selector, timeout = 10000) {
    console.log(`⏳ #chrome.waitFor: ${selector}`);
    
    return await this.executeInContent(tabId, (sel, maxTime) => {
      return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const check = () => {
          const element = document.querySelector(sel);
          
          if (element && element.offsetParent !== null) {
            resolve({
              found: true,
              selector: sel,
              waitTime: Date.now() - startTime
            });
            return;
          }
          
          if (Date.now() - startTime > maxTime) {
            reject(new Error(`Timeout waiting for: ${sel}`));
            return;
          }
          
          setTimeout(check, 100);
        };
        
        check();
      });
    }, selector, timeout);
  }

  /**
   * Take a screenshot of the page
   * @param {number} tabId - Tab ID
   */
  async screenshot(tabId) {
    console.log(`📸 #chrome.screenshot`);
    
    try {
      const dataUrl = await chrome.tabs.captureVisibleTab(null, {
        format: 'png'
      });
      
      return {
        success: true,
        dataUrl
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get page performance metrics
   * @param {number} tabId - Tab ID
   */
  async getPerformanceMetrics(tabId) {
    console.log(`⚡ #chrome.performance on tab ${tabId}`);
    
    return await this.executeInContent(tabId, () => {
      const perfData = window.performance.timing;
      const navigation = window.performance.getEntriesByType('navigation')[0];
      
      return {
        loadTime: perfData.loadEventEnd - perfData.navigationStart,
        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
        firstPaint: navigation?.fetchStart || 0,
        lcp: 0, // Would need PerformanceObserver for real LCP
        metrics: {
          dns: perfData.domainLookupEnd - perfData.domainLookupStart,
          tcp: perfData.connectEnd - perfData.connectStart,
          request: perfData.responseStart - perfData.requestStart,
          response: perfData.responseEnd - perfData.responseStart,
          dom: perfData.domComplete - perfData.domLoading
        }
      };
    });
  }

  /**
   * Extract page data based on platform
   * @param {number} tabId - Tab ID
   * @param {string} platform - Platform name (swiggy/zomato/blinkit)
   */
  async extractPageData(tabId, platform) {
    console.log(`📊 Extracting data from ${platform}`);
    
    const extractors = {
      swiggy: this.extractSwiggyData.bind(this),
      zomato: this.extractZomatoData.bind(this),
      blinkit: this.extractBlinkitData.bind(this)
    };
    
    const extractor = extractors[platform];
    if (!extractor) {
      throw new Error(`No extractor for platform: ${platform}`);
    }
    
    return await extractor(tabId);
  }

  async extractSwiggyData(tabId) {
    return await this.executeInContent(tabId, () => {
      const data = {
        restaurants: [],
        currentPage: window.location.pathname
      };
      
      // Extract restaurant cards
      const cards = document.querySelectorAll('[class*="RestaurantList"] [class*="restaurant"]');
      
      cards.forEach(card => {
        const name = card.querySelector('[class*="name"]')?.textContent?.trim();
        const rating = card.querySelector('[class*="rating"]')?.textContent?.trim();
        const cuisine = card.querySelector('[class*="cuisine"]')?.textContent?.trim();
        const price = card.querySelector('[class*="price"]')?.textContent?.trim();
        const time = card.querySelector('[class*="time"]')?.textContent?.trim();
        
        if (name) {
          data.restaurants.push({
            name,
            rating,
            cuisine,
            price,
            deliveryTime: time
          });
        }
      });
      
      return data;
    });
  }

  async extractZomatoData(tabId) {
    return await this.executeInContent(tabId, () => {
      const data = {
        restaurants: [],
        currentPage: window.location.pathname
      };
      
      // Extract restaurant cards from Zomato
      const cards = document.querySelectorAll('[class*="sc-"][class*="card"]');
      
      cards.forEach(card => {
        const name = card.querySelector('h4, [class*="name"]')?.textContent?.trim();
        const rating = card.querySelector('[class*="rating"]')?.textContent?.trim();
        const cuisine = card.querySelector('[class*="cuisine"]')?.textContent?.trim();
        
        if (name) {
          data.restaurants.push({
            name,
            rating,
            cuisine
          });
        }
      });
      
      return data;
    });
  }

  async extractBlinkitData(tabId) {
    return await this.executeInContent(tabId, () => {
      const data = {
        products: [],
        currentPage: window.location.pathname
      };
      
      // Extract product cards
      const cards = document.querySelectorAll('[class*="Product"]');
      
      cards.forEach(card => {
        const name = card.querySelector('[class*="name"]')?.textContent?.trim();
        const price = card.querySelector('[class*="price"]')?.textContent?.trim();
        
        if (name) {
          data.products.push({
            name,
            price
          });
        }
      });
      
      return data;
    });
  }

  /**
   * Helper to execute function in content script context
   */
  async executeInContent(tabId, func, ...args) {
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: func,
        args: args
      });
      
      return {
        success: true,
        result: results[0]?.result
      };
    } catch (error) {
      console.error('Content execution error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Wait for page to fully load
   */
  async waitForPageLoad(tabId, timeout = 30000) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      
      const checkLoading = async () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error('Page load timeout'));
          return;
        }
        
        try {
          const tab = await chrome.tabs.get(tabId);
          
          if (tab.status === 'complete') {
            // Wait a bit more for dynamic content
            setTimeout(() => resolve(), 1000);
          } else {
            setTimeout(checkLoading, 500);
          }
        } catch (error) {
          reject(error);
        }
      };
      
      checkLoading();
    });
  }

  /**
   * Scroll page to element or position
   */
  async scroll(tabId, options = {}) {
    const { selector, behavior = 'smooth', block = 'center' } = options;
    
    return await this.executeInContent(tabId, (sel, beh, blk) => {
      if (sel) {
        const element = document.querySelector(sel);
        if (element) {
          element.scrollIntoView({ behavior: beh, block: blk });
          return { scrolled: true, selector: sel };
        }
        return { scrolled: false, error: 'Element not found' };
      } else {
        window.scrollTo({ top: document.body.scrollHeight, behavior: beh });
        return { scrolled: true, position: 'bottom' };
      }
    }, selector, behavior, block);
  }
}
