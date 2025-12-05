// Side Panel UI Logic

let currentTab = 'chat';
let chatHistory = [];

// Utility function
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('🍔 BUTLER sidepanel loaded');
  
  setupTabs();
  setupChatInterface();
  setupSearchInterface();
  setupCompareInterface();
  setupHistoryInterface();
  
  // Listen for messages from background
  chrome.runtime.onMessage.addListener(handleBackgroundMessage);
});

function setupTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab;
      
      // Update active states
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      
      btn.classList.add('active');
      document.getElementById(`${tabName}Tab`).classList.add('active');
      
      currentTab = tabName;
    });
  });
}

function setupChatInterface() {
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const suggestionsContainer = document.getElementById('suggestions');
  
  // Send message
  const sendMessage = async () => {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Check if user is proceeding to checkout
    if (message.toLowerCase() === 'proceed' && window.pendingCheckout) {
      chatInput.value = '';
      chatInput.style.height = 'auto';
      addMessage('user', message);
      await proceedToCheckout();
      return;
    }
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Add user message to chat
    addMessage('user', message);
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
      // Send to background
      const response = await chrome.runtime.sendMessage({
        type: 'CHAT_MESSAGE',
        data: { message, context: await getContext() }
      });
      
      // Remove typing indicator
      removeTypingIndicator(typingId);
      
      if (response.success) {
        // Add AI response
        addMessage('bot', response.data.message);
        
        // Handle function calls if any
        if (response.data.functionCalls) {
          handleFunctionCallResults(response.data.functionCalls, response.data.functionResults);
        }
      } else {
        addMessage('bot', `Sorry, I encountered an error: ${response.error}`);
      }
    } catch (error) {
      removeTypingIndicator(typingId);
      addMessage('bot', `Sorry, something went wrong: ${error.message}`);
    }
  };
  
  sendBtn.addEventListener('click', sendMessage);
  
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  
  // Auto-resize textarea
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });
  
  // Suggestion chips
  suggestionsContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('suggestion-chip')) {
      chatInput.value = e.target.textContent.replace(/[🍕🍔🍜]/g, '').trim();
      sendMessage();
    }
  });
}

function setupSearchInterface() {
  const searchBtn = document.getElementById('executeSearch');
  const searchQuery = document.getElementById('searchQuery');
  
  searchBtn.addEventListener('click', async () => {
    const query = searchQuery.value.trim();
    if (!query) return;
    
    // Get selected platforms
    const platformCheckboxes = document.querySelectorAll('.platform-checkbox input:checked');
    const platforms = Array.from(platformCheckboxes).map(cb => cb.value);
    
    if (platforms.length === 0) {
      alert('Please select at least one platform');
      return;
    }
    
    // Show loading
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span>🔄</span><span>Searching...</span>';
    
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'SEARCH_FOOD',
        data: { query, platforms }
      });
      
      if (response.success) {
        displaySearchResults(response.data);
      } else {
        alert('Search failed: ' + response.error);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      searchBtn.disabled = false;
      searchBtn.innerHTML = '<span>🔍</span><span>Search All Platforms</span>';
    }
  });
  
  // Enter to search
  searchQuery.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      searchBtn.click();
    }
  });
}

function setupCompareInterface() {
  // Comparison interface will be populated by search results
}

function setupHistoryInterface() {
  const clearHistoryBtn = document.getElementById('clearHistory');
  
  clearHistoryBtn.addEventListener('click', async () => {
    if (confirm('Clear all order history?')) {
      await chrome.storage.local.set({ orderHistory: [] });
      loadHistory();
    }
  });
  
  loadHistory();
}

async function getContext() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const platform = detectPlatform(tab?.url);
  
  const settings = await chrome.storage.sync.get({
    preferences: {},
    location: ''
  });
  
  return {
    platform,
    userPreferences: settings.preferences,
    location: settings.location
  };
}

function detectPlatform(url) {
  if (!url) return null;
  if (url.includes('swiggy.com')) return 'swiggy';
  if (url.includes('zomato.com')) return 'zomato';
  if (url.includes('blinkit.com')) return 'blinkit';
  return null;
}

function addMessage(role, text) {
  const chatMessages = document.getElementById('chatMessages');
  
  // Remove welcome message if exists
  const welcomeMsg = chatMessages.querySelector('.welcome-message');
  if (welcomeMsg) {
    welcomeMsg.remove();
  }
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${role}`;
  
  const avatar = document.createElement('div');
  avatar.className = 'message-avatar';
  avatar.textContent = role === 'bot' ? '🤖' : '👤';
  
  const content = document.createElement('div');
  content.className = 'message-content';
  
  const textDiv = document.createElement('div');
  textDiv.className = 'message-text';
  textDiv.textContent = text;
  
  content.appendChild(textDiv);
  messageDiv.appendChild(avatar);
  messageDiv.appendChild(content);
  
  chatMessages.appendChild(messageDiv);
  
  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  // Store in history
  chatHistory.push({ role, text });
}

function addTypingIndicator() {
  const chatMessages = document.getElementById('chatMessages');
  const typingDiv = document.createElement('div');
  const id = 'typing-' + Date.now();
  typingDiv.id = id;
  typingDiv.className = 'message bot';
  typingDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-text">Thinking...</div>
    </div>
  `;
  
  chatMessages.appendChild(typingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  return id;
}

function removeTypingIndicator(id) {
  const typingDiv = document.getElementById(id);
  if (typingDiv) {
    typingDiv.remove();
  }
}

function handleFunctionCallResults(calls, results) {
  // Display function execution results in chat
  calls.forEach((call, index) => {
    const result = results[index];
    
    if (call.name === 'search_food' && result.result) {
      // Display Google search results
      displayGoogleSearchResults(result.result);
    } else if (call.name === 'compare_prices' && result.result) {
      // Switch to compare tab
      document.querySelector('[data-tab="compare"]').click();
      displayComparison(result.result);
    }
  });
}

function displayGoogleSearchResults(data) {
  const resultsContainer = document.getElementById('searchResults');
  resultsContainer.innerHTML = '';
  
  if (!data.searchResults || data.searchResults.length === 0) {
    resultsContainer.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>No results found</p></div>';
    return;
  }
  
  // Add header
  const header = document.createElement('div');
  header.className = 'search-header';
  header.innerHTML = `
    <h3>🔍 Google Search Results</h3>
    <p>Found ${data.searchResults.length} results for "${data.query || ''}"</p>
  `;
  resultsContainer.appendChild(header);
  
  // Group by platform
  const groupedResults = {};
  data.searchResults.forEach(result => {
    if (!groupedResults[result.platform]) {
      groupedResults[result.platform] = [];
    }
    groupedResults[result.platform].push(result);
  });
  
  // Display by platform
  ['swiggy', 'zomato', 'blinkit'].forEach(platform => {
    if (groupedResults[platform] && groupedResults[platform].length > 0) {
      const platformSection = document.createElement('div');
      platformSection.className = 'platform-results';
      platformSection.innerHTML = `
        <h4 class="platform-title ${platform}">${platform.toUpperCase()}</h4>
        <div class="results-list"></div>
      `;
      
      const resultsList = platformSection.querySelector('.results-list');
      
      groupedResults[platform].forEach(result => {
        const card = createGoogleResultCard(result);
        resultsList.appendChild(card);
      });
      
      resultsContainer.appendChild(platformSection);
    }
  });
  
  // Add event listeners to order buttons
  resultsContainer.querySelectorAll('.order-now-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const url = btn.dataset.url;
      const platform = btn.dataset.platform;
      const title = btn.dataset.title;
      orderFromGoogleResult(url, platform, title);
    });
  });
}

function createGoogleResultCard(result) {
  const card = document.createElement('div');
  card.className = 'google-result-card';
  
  card.innerHTML = `
    <div class="result-header">
      <h5 class="result-title">${result.title}</h5>
      <span class="result-rank">#${result.rank}</span>
    </div>
    <p class="result-snippet">${result.snippet}</p>
    <div class="result-actions">
      <button class="order-now-btn" 
              data-url="${result.url}" 
              data-platform="${result.platform}"
              data-title="${result.title}">
        🚀 Order Now
      </button>
      <a href="${result.url}" target="_blank" class="view-link">View Page →</a>
    </div>
  `;
  
  return card;
}

async function orderFromGoogleResult(url, platform, restaurantName) {
  console.log(`🚀 Starting automated order from ${platform}:`, restaurantName);
  
  // Add message to chat
  addMessage('bot', `🤖 Starting automated ordering from ${restaurantName} on ${platform.toUpperCase()}...`);
  
  // Switch to chat tab to show progress
  document.querySelector('[data-tab="chat"]').click();
  
  try {
    // Step 1: Open the restaurant page
    addMessage('bot', `📱 Opening ${restaurantName}...`);
    const tab = await chrome.tabs.create({ url: url });
    
    await sleep(3000); // Wait for page to load
    
    // Step 2: Let user add items to cart
    addMessage('bot', `✅ Page opened! Please:
1. Add items to your cart
2. Click "Proceed to Checkout"
3. I'll help complete the order

Type "proceed" when ready to checkout!`);
    
    // Set up listener for "proceed" command
    listenForCheckoutProceed(tab.id, platform);
    
  } catch (error) {
    addMessage('bot', `❌ Error: ${error.message}. Please try ordering manually.`);
  }
}

function listenForCheckoutProceed(tabId, platform) {
  // This will be handled in the chat interface
  // User types "proceed" to continue to checkout
  window.pendingCheckout = { tabId, platform };
}

async function proceedToCheckout() {
  if (!window.pendingCheckout) {
    return false;
  }
  
  const { tabId, platform } = window.pendingCheckout;
  
  try {
    addMessage('bot', `🛒 Proceeding to checkout...`);
    
    // Use background service to automate checkout
    const response = await chrome.runtime.sendMessage({
      type: 'PROCEED_TO_CHECKOUT',
      data: { tabId, platform }
    });
    
    if (response.success) {
      addMessage('bot', `✅ ${response.message || 'Ready for payment! Please complete the payment to finish your order.'}`);
    } else {
      addMessage('bot', `⚠️ ${response.error || 'Please complete checkout manually.'}`);
    }
    
    window.pendingCheckout = null;
    return true;
    
  } catch (error) {
    addMessage('bot', `❌ Checkout error: ${error.message}`);
    return false;
  }
}

function displaySearchResults(data) {
  const resultsContainer = document.getElementById('searchResults');
  resultsContainer.innerHTML = '';
  
  if (!data.platforms || Object.keys(data.platforms).length === 0) {
    resultsContainer.innerHTML = '<div class="empty-state"><div class="empty-icon">🔍</div><p>No results found</p></div>';
    return;
  }
  
  // Display results by platform
  Object.entries(data.platforms).forEach(([platform, platformData]) => {
    if (!platformData.success) return;
    
    const platformSection = document.createElement('div');
    platformSection.className = 'platform-results';
    platformSection.innerHTML = `
      <h3>${platform.charAt(0).toUpperCase() + platform.slice(1)} Results</h3>
      <div class="results-grid"></div>
    `;
    
    const grid = platformSection.querySelector('.results-grid');
    
    (platformData.results || []).forEach(item => {
      const card = createResultCard(item, platform);
      grid.appendChild(card);
    });
    
    resultsContainer.appendChild(platformSection);
  });
}

function createResultCard(item, platform) {
  const card = document.createElement('div');
  card.className = 'result-card';
  card.innerHTML = `
    <h4>${item.name}</h4>
    <div class="result-info">
      ${item.rating ? `<span>⭐ ${item.rating}</span>` : ''}
      ${item.price ? `<span>💰 ${item.price}</span>` : ''}
      ${item.deliveryTime ? `<span>🕒 ${item.deliveryTime}</span>` : ''}
    </div>
    ${item.cuisine ? `<p class="cuisine">${item.cuisine}</p>` : ''}
    <button class="order-btn" data-platform="${platform}" data-restaurant="${item.name}">
      Order Now
    </button>
  `;
  
  return card;
}

function displayComparison(data) {
  const comparisonContainer = document.getElementById('comparisonResults');
  comparisonContainer.innerHTML = '';
  
  const comparisonCard = document.createElement('div');
  comparisonCard.className = 'comparison-card';
  comparisonCard.innerHTML = `
    <h3>${data.item} ${data.restaurant ? `at ${data.restaurant}` : ''}</h3>
    <div class="comparison-table">
      ${Object.entries(data.platforms).map(([platform, info]) => `
        <div class="comparison-row ${data.bestDeal?.platform === platform ? 'best-deal' : ''}">
          <div class="platform-name">${platform}</div>
          <div class="price-info">
            ${info.itemPrice ? `
              <span>Item: ₹${info.itemPrice}</span>
              <span>Delivery: ₹${info.deliveryFee || 0}</span>
              <strong>Total: ₹${info.itemPrice + (info.deliveryFee || 0)}</strong>
            ` : '<span>Not available</span>'}
          </div>
        </div>
      `).join('')}
    </div>
    ${data.bestDeal ? `
      <div class="best-deal-banner">
        🏆 Best Deal: ${data.bestDeal.platform} - Save ₹${data.bestDeal.savings}!
      </div>
    ` : ''}
  `;
  
  comparisonContainer.appendChild(comparisonCard);
}

async function loadHistory() {
  const { orderHistory = [] } = await chrome.storage.local.get('orderHistory');
  const historyList = document.getElementById('historyList');
  
  if (orderHistory.length === 0) {
    historyList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📜</div>
        <p>No order history yet</p>
        <p class="empty-hint">Your tracked orders will appear here</p>
      </div>
    `;
    return;
  }
  
  historyList.innerHTML = orderHistory.map(order => `
    <div class="history-item">
      <div class="history-header">
        <strong>${order.restaurant}</strong>
        <span>${order.platform}</span>
      </div>
      <div class="history-details">
        <span>${order.items.length} items</span>
        <span>₹${order.total}</span>
        <span>${new Date(order.timestamp).toLocaleDateString()}</span>
      </div>
    </div>
  `).join('');
}

function handleBackgroundMessage(message) {
  if (message.type === 'SEARCH_RESULTS') {
    displaySearchResults(message.data);
    document.querySelector('[data-tab="search"]').click();
  } else if (message.type === 'PLATFORM_DETECTED') {
    updatePlatformIndicator(message.data.platform);
  } else if (message.type === 'SWITCH_TAB') {
    // Switch to requested tab
    const tabName = message.data.tab;
    const tabBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (tabBtn) {
      tabBtn.click();
    }
  }
}

function updatePlatformIndicator(platform) {
  const platformIndicator = document.getElementById('platformIndicator');
  const platformText = document.getElementById('platformText');
  
  const platformEmojis = {
    swiggy: '🍕',
    zomato: '🍔',
    blinkit: '🛒'
  };
  
  if (platform) {
    platformIndicator.textContent = platformEmojis[platform] || '🌐';
    platformText.textContent = `On ${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
  } else {
    platformIndicator.textContent = '🌐';
    platformText.textContent = 'Ready to help!';
  }
}

// Settings button
document.getElementById('settingsBtn').addEventListener('click', () => {
  chrome.runtime.openOptionsPage();
});

// Refresh button
document.getElementById('refreshBtn').addEventListener('click', () => {
  location.reload();
});
