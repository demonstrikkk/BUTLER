/**
 * Zomato Content Script
 * Runs on Zomato pages to enhance automation and data extraction
 */

console.log('BUTLER: Zomato content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Zomato content script received message:', message);
  
  switch (message.action) {
    case 'EXTRACT_PAGE_DATA':
      extractZomatoData().then(sendResponse);
      return true;
      
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
 * Extract data from current Zomato page
 */
async function extractZomatoData() {
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
    console.error('Error extracting Zomato data:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Detect current page type
 */
function detectPageType() {
  const url = window.location.href;
  if (url.includes('/search')) return 'search';
  if (url.includes('/order')) return 'restaurant';
  if (url.includes('/checkout')) return 'cart';
  return 'home';
}

/**
 * Extract data from home page
 */
async function extractHomePage() {
  const restaurants = [];
  
  // Zomato selectors - adjust based on current UI
  const restaurantCards = document.querySelectorAll('[class*="sc-"][class*="Restaurant"]');
  
  restaurantCards.forEach(card => {
    const name = card.querySelector('h4, [class*="name"]')?.textContent?.trim();
    const cuisine = card.querySelector('[class*="cuisine"]')?.textContent?.trim();
    const rating = card.querySelector('[class*="rating"]')?.textContent?.trim();
    const deliveryTime = card.querySelector('[class*="time"]')?.textContent?.trim();
    const priceForTwo = card.querySelector('[class*="cost"]')?.textContent?.trim();
    
    if (name) {
      restaurants.push({
        name,
        cuisine,
        rating: parseFloat(rating) || 0,
        deliveryTime,
        priceForTwo,
        platform: 'zomato'
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
  
  const resultCards = document.querySelectorAll('[class*="search-result"], [class*="SearchCard"]');
  
  resultCards.forEach(card => {
    const name = card.querySelector('h4, [class*="title"]')?.textContent?.trim();
    const cuisine = card.querySelector('[class*="cuisine"]')?.textContent?.trim();
    const rating = card.querySelector('[class*="rating"]')?.textContent?.trim();
    const price = card.querySelector('[class*="price"], [class*="cost"]')?.textContent?.trim();
    
    if (name) {
      results.push({
        name,
        cuisine,
        rating: parseFloat(rating) || 0,
        price,
        platform: 'zomato'
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
  const restaurantName = document.querySelector('h1, [class*="res-name"]')?.textContent?.trim();
  const rating = document.querySelector('[class*="rating"]')?.textContent?.trim();
  const cuisine = document.querySelector('[class*="res-info-cuisine"]')?.textContent?.trim();
  
  const menuItems = [];
  const itemCards = document.querySelectorAll('[class*="item-card"], [class*="MenuItem"]');
  
  itemCards.forEach(card => {
    const itemName = card.querySelector('[class*="item-name"], h4')?.textContent?.trim();
    const price = card.querySelector('[class*="item-price"]')?.textContent?.trim();
    const description = card.querySelector('[class*="item-desc"]')?.textContent?.trim();
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
    const name = card.querySelector('[class*="name"], h4')?.textContent?.trim();
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
  
  const total = document.querySelector('[class*="total-price"]')?.textContent?.trim();
  
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
    const searchInput = document.querySelector('input[placeholder*="Search"]') || 
                        document.querySelector('input[type="text"][class*="search"]');
    
    if (!searchInput) {
      return { success: false, error: 'Search input not found' };
    }
    
    searchInput.value = '';
    searchInput.focus();
    searchInput.value = query;
    
    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    searchInput.dispatchEvent(new Event('change', { bubbles: true }));
    
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
  return { success: true, data: {} };
}

/**
 * Add item to cart
 */
async function addToCart(itemId, quantity = 1) {
  try {
    const addButton = document.querySelector(`[data-item-id="${itemId}"] button[class*="add"]`) ||
                      document.querySelector(`button:contains("Add")`);
    
    if (!addButton) {
      return { success: false, error: 'Add button not found' };
    }
    
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
  platform: 'zomato',
  url: window.location.href
});
