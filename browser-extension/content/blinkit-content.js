/**
 * Blinkit Content Script
 * Runs on Blinkit pages to enhance automation and data extraction
 */

console.log('BUTLER: Blinkit content script loaded');

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Blinkit content script received message:', message);
  
  switch (message.action) {
    case 'EXTRACT_PAGE_DATA':
      extractBlinkitData().then(sendResponse);
      return true;
      
    case 'SEARCH_FOOD':
      searchFood(message.query).then(sendResponse);
      return true;
      
    case 'GET_PRODUCT_INFO':
      getProductInfo(message.productId).then(sendResponse);
      return true;
      
    case 'ADD_TO_CART':
      addToCart(message.productId, message.quantity).then(sendResponse);
      return true;
      
    case 'GET_CART_ITEMS':
      getCartItems().then(sendResponse);
      return true;
      
    default:
      sendResponse({ success: false, error: 'Unknown action' });
  }
});

/**
 * Extract data from current Blinkit page
 */
async function extractBlinkitData() {
  try {
    const pageType = detectPageType();
    
    switch (pageType) {
      case 'home':
        return await extractHomePage();
      case 'search':
        return await extractSearchResults();
      case 'product':
        return await extractProductPage();
      case 'cart':
        return await extractCartPage();
      default:
        return { success: true, pageType, data: {} };
    }
  } catch (error) {
    console.error('Error extracting Blinkit data:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Detect current page type
 */
function detectPageType() {
  const url = window.location.href;
  if (url.includes('/search')) return 'search';
  if (url.includes('/product/')) return 'product';
  if (url.includes('/cart')) return 'cart';
  return 'home';
}

/**
 * Extract data from home page
 */
async function extractHomePage() {
  const products = [];
  
  // Blinkit uses different selectors
  const productCards = document.querySelectorAll('[class*="Product__"]');
  
  productCards.forEach(card => {
    const name = card.querySelector('[class*="Product__ProductName"]')?.textContent?.trim();
    const price = card.querySelector('[class*="Product__Price"]')?.textContent?.trim();
    const mrp = card.querySelector('[class*="Product__MRP"]')?.textContent?.trim();
    const weight = card.querySelector('[class*="Product__Weight"]')?.textContent?.trim();
    
    if (name && price) {
      products.push({
        name,
        price: price.replace(/[^\d]/g, ''),
        mrp: mrp?.replace(/[^\d]/g, ''),
        weight,
        platform: 'blinkit'
      });
    }
  });
  
  return {
    success: true,
    pageType: 'home',
    data: { products }
  };
}

/**
 * Extract search results
 */
async function extractSearchResults() {
  const results = [];
  
  const productCards = document.querySelectorAll('[class*="Product"], [class*="product-card"]');
  
  productCards.forEach(card => {
    const name = card.querySelector('[class*="name"], h3, h4')?.textContent?.trim();
    const price = card.querySelector('[class*="price"]')?.textContent?.trim();
    const weight = card.querySelector('[class*="weight"], [class*="quantity"]')?.textContent?.trim();
    const discount = card.querySelector('[class*="discount"]')?.textContent?.trim();
    
    if (name && price) {
      results.push({
        name,
        price: price.replace(/[^\d]/g, ''),
        weight,
        discount,
        platform: 'blinkit'
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
 * Extract product page data
 */
async function extractProductPage() {
  const productName = document.querySelector('[class*="Product__ProductName"], h1')?.textContent?.trim();
  const price = document.querySelector('[class*="Product__Price"]')?.textContent?.trim();
  const mrp = document.querySelector('[class*="Product__MRP"]')?.textContent?.trim();
  const weight = document.querySelector('[class*="Product__Weight"]')?.textContent?.trim();
  const description = document.querySelector('[class*="description"]')?.textContent?.trim();
  
  return {
    success: true,
    pageType: 'product',
    data: {
      product: {
        name: productName,
        price: price?.replace(/[^\d]/g, ''),
        mrp: mrp?.replace(/[^\d]/g, ''),
        weight,
        description
      }
    }
  };
}

/**
 * Extract cart page data
 */
async function extractCartPage() {
  const cartItems = [];
  const itemCards = document.querySelectorAll('[class*="CartItem"], [class*="cart-item"]');
  
  itemCards.forEach(card => {
    const name = card.querySelector('[class*="name"], h4')?.textContent?.trim();
    const quantity = card.querySelector('[class*="quantity"]')?.textContent?.trim();
    const price = card.querySelector('[class*="price"]')?.textContent?.trim();
    
    if (name) {
      cartItems.push({
        name,
        quantity: parseInt(quantity) || 1,
        price: price?.replace(/[^\d]/g, '')
      });
    }
  });
  
  const total = document.querySelector('[class*="total"], [class*="Total"]')?.textContent?.trim();
  
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
                        document.querySelector('input[type="text"]');
    
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
 * Get product information
 */
async function getProductInfo(productId) {
  return { success: true, data: {} };
}

/**
 * Add item to cart
 */
async function addToCart(productId, quantity = 1) {
  try {
    const addButton = document.querySelector(`[data-product-id="${productId}"] button[class*="add"]`) ||
                      document.querySelector(`button[class*="AddToCart"]`);
    
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
  platform: 'blinkit',
  url: window.location.href
});
