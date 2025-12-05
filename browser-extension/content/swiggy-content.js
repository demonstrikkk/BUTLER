/**
 * Swiggy Content Script
 * Runs on Swiggy pages to enhance automation and data extraction
 */

console.log('BUTLER: Swiggy content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Swiggy content script received message:', message);
  
  switch (message.action) {
    case 'EXTRACT_PAGE_DATA':
      extractSwiggyData().then(sendResponse);
      return true; // Keep channel open for async response
      
    case 'SEARCH_FOOD':
      searchFood(message.query).then(sendResponse);
      return true;
      
    case 'GET_RESTAURANT_INFO':
      getRestaurantInfo(message.restaurantId).then(sendResponse);
      return true;
      
    case 'ADD_TO_CART':
      addToCart(message.itemId, message.quantity).then(sendResponse);
      return true;
      
    case 'GET_CART_ITEMS':
      getCartItems().then(sendResponse);
      return true;
      
    default:
      sendResponse({ success: false, error: 'Unknown action' });
  }
});

/**
 * Extract data from current Swiggy page
 */
async function extractSwiggyData() {
  try {
    const pageType = detectPageType();
    
    switch (pageType) {
      case 'home':
        return await extractHomePage();
      case 'search':
        return await extractSearchResults();
      case 'restaurant':
        return await extractRestaurantPage();
      case 'cart':
        return await extractCartPage();
      default:
        return { success: true, pageType, data: {} };
    }
  } catch (error) {
    console.error('Error extracting Swiggy data:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Detect current page type
 */
function detectPageType() {
  const url = window.location.href;
  if (url.includes('/search')) return 'search';
  if (url.includes('/restaurants/')) return 'restaurant';
  if (url.includes('/checkout')) return 'cart';
  return 'home';
}

/**
 * Extract data from home page
 */
async function extractHomePage() {
  const restaurants = [];
  
  // Swiggy uses different selectors - adjust based on current UI
  const restaurantCards = document.querySelectorAll('[class*="RestaurantList"] [class*="styles_card"]');
  
  restaurantCards.forEach(card => {
    const name = card.querySelector('[class*="name"]')?.textContent?.trim();
    const cuisine = card.querySelector('[class*="cuisine"]')?.textContent?.trim();
    const rating = card.querySelector('[class*="rating"]')?.textContent?.trim();
    const deliveryTime = card.querySelector('[class*="time"]')?.textContent?.trim();
    const priceForTwo = card.querySelector('[class*="price"]')?.textContent?.trim();
    
    if (name) {
      restaurants.push({
        name,
        cuisine,
        rating: parseFloat(rating) || 0,
        deliveryTime,
        priceForTwo,
        platform: 'swiggy'
      });
    }
  });
  
  return {
    success: true,
    pageType: 'home',
    data: { restaurants }
  };
}

/**
 * Extract search results
 */
async function extractSearchResults() {
  const results = [];
  
  // Search results selector - adjust based on Swiggy's current UI
  const resultCards = document.querySelectorAll('[class*="search"] [class*="RestaurantCard"]');
  
  resultCards.forEach(card => {
    const name = card.querySelector('[class*="name"]')?.textContent?.trim();
    const cuisine = card.querySelector('[class*="cuisine"]')?.textContent?.trim();
    const rating = card.querySelector('[class*="rating"]')?.textContent?.trim();
    const price = card.querySelector('[class*="price"]')?.textContent?.trim();
    
    if (name) {
      results.push({
        name,
        cuisine,
        rating: parseFloat(rating) || 0,
        price,
        platform: 'swiggy'
      });
    }
  });
  
  return {
    success: true,
    pageType: 'search',
    data: { results }
  };
}

/**
 * Extract restaurant page data
 */
async function extractRestaurantPage() {
  const restaurantName = document.querySelector('[class*="restaurant-name"]')?.textContent?.trim();
  const rating = document.querySelector('[class*="rating"]')?.textContent?.trim();
  const cuisine = document.querySelector('[class*="cuisine"]')?.textContent?.trim();
  
  const menuItems = [];
  const itemCards = document.querySelectorAll('[class*="MenuItem"]');
  
  itemCards.forEach(card => {
    const itemName = card.querySelector('[class*="item-name"]')?.textContent?.trim();
    const price = card.querySelector('[class*="price"]')?.textContent?.trim();
    const description = card.querySelector('[class*="description"]')?.textContent?.trim();
    const itemRating = card.querySelector('[class*="rating"]')?.textContent?.trim();
    
    if (itemName && price) {
      menuItems.push({
        name: itemName,
        price: price.replace(/[^\d]/g, ''),
        description,
        rating: parseFloat(itemRating) || 0
      });
    }
  });
  
  return {
    success: true,
    pageType: 'restaurant',
    data: {
      restaurant: {
        name: restaurantName,
        rating: parseFloat(rating) || 0,
        cuisine
      },
      menuItems
    }
  };
}

/**
 * Extract cart page data
 */
async function extractCartPage() {
  const cartItems = [];
  const itemCards = document.querySelectorAll('[class*="cart-item"]');
  
  itemCards.forEach(card => {
    const name = card.querySelector('[class*="name"]')?.textContent?.trim();
    const quantity = card.querySelector('[class*="quantity"]')?.textContent?.trim();
    const price = card.querySelector('[class*="price"]')?.textContent?.trim();
    
    if (name) {
      cartItems.push({
        name,
        quantity: parseInt(quantity) || 1,
        price: price.replace(/[^\d]/g, '')
      });
    }
  });
  
  const total = document.querySelector('[class*="total"]')?.textContent?.trim();
  
  return {
    success: true,
    pageType: 'cart',
    data: {
      items: cartItems,
      total: total?.replace(/[^\d]/g, '')
    }
  };
}

/**
 * Search for food items
 */
async function searchFood(query) {
  try {
    // Find search input
    const searchInput = document.querySelector('input[placeholder*="Search"]') || 
                        document.querySelector('input[type="search"]');
    
    if (!searchInput) {
      return { success: false, error: 'Search input not found' };
    }
    
    // Clear and type query
    searchInput.value = '';
    searchInput.focus();
    searchInput.value = query;
    
    // Trigger input event
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    searchInput.dispatchEvent(new Event('change', { bubbles: true }));
    
    // Press enter
    const enterEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      bubbles: true
    });
    searchInput.dispatchEvent(enterEvent);
    
    return { success: true, message: 'Search initiated' };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Get restaurant information
 */
async function getRestaurantInfo(restaurantId) {
  // Implementation depends on Swiggy's data structure
  return { success: true, data: {} };
}

/**
 * Add item to cart
 */
async function addToCart(itemId, quantity = 1) {
  try {
    // Find add button for the item
    const addButton = document.querySelector(`[data-item-id="${itemId}"] button[class*="ADD"]`) ||
                      document.querySelector(`button:contains("ADD")`);
    
    if (!addButton) {
      return { success: false, error: 'Add button not found' };
    }
    
    // Click add button
    for (let i = 0; i < quantity; i++) {
      addButton.click();
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    return { success: true, message: `Added ${quantity} item(s) to cart` };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Get cart items
 */
async function getCartItems() {
  return await extractCartPage();
}

// Notify background that content script is ready
chrome.runtime.sendMessage({
  action: 'CONTENT_SCRIPT_READY',
  platform: 'swiggy',
  url: window.location.href
});
