// Popup UI Logic

document.addEventListener('DOMContentLoaded', async () => {
  console.log('🍔 BUTLER popup loaded');
  
  // Initialize UI
  await initializePopup();
  
  // Set up event listeners
  setupEventListeners();
});

async function initializePopup() {
  // Get status from background
  const response = await chrome.runtime.sendMessage({ type: 'GET_STATUS' });
  
  if (response.success) {
    updateStatus(response.data);
  }
  
  // Load stats
  await loadStats();
  
  // Detect current platform
  await detectPlatform();
}

function setupEventListeners() {
  // Open side panel
  document.getElementById('openSidePanel').addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.sidePanel.open({ windowId: tab.windowId });
      window.close();
    } catch (error) {
      console.error('Failed to open side panel:', error);
    }
  });
  
  // Quick search
  document.getElementById('quickSearch').addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.sidePanel.open({ windowId: tab.windowId });
      // Switch to search tab after opening
      setTimeout(() => {
        chrome.runtime.sendMessage({ type: 'SWITCH_TAB', data: { tab: 'search' } });
      }, 300);
      window.close();
    } catch (error) {
      console.error('Failed to open side panel:', error);
    }
  });
  
  // Compare prices
  document.getElementById('comparePrices').addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.sidePanel.open({ windowId: tab.windowId });
      setTimeout(() => {
        chrome.runtime.sendMessage({ type: 'SWITCH_TAB', data: { tab: 'compare' } });
      }, 300);
      window.close();
    } catch (error) {
      console.error('Failed to open side panel:', error);
    }
  });
  
  // Settings
  document.getElementById('openSettings').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
    window.close();
  });
  
  // Help
  document.getElementById('openHelp').addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://github.com/yourrepo/BUTLER#readme' });
    window.close();
  });
  
  // Platform actions
  document.getElementById('extractItems')?.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const response = await chrome.runtime.sendMessage({
      type: 'EXTRACT_PAGE_DATA',
      data: { tabId: tab.id }
    });
    
    if (response.success) {
      alert(`Extracted ${response.data.restaurants?.length || response.data.products?.length || 0} items`);
    }
  });
  
  document.getElementById('analyzeReviews')?.addEventListener('click', async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      await chrome.sidePanel.open({ windowId: tab.windowId });
      window.close();
    } catch (error) {
      console.error('Failed to open side panel:', error);
    }
  });
}

function updateStatus(data) {
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  
  if (data.isInitialized && data.hasApiKey) {
    statusDot.style.background = '#52C41A';
    statusText.textContent = 'Ready!';
  } else if (!data.hasApiKey) {
    statusDot.style.background = '#F5222D';
    statusText.textContent = 'No API key';
  } else {
    statusDot.style.background = '#FAAD14';
    statusText.textContent = 'Initializing...';
  }
}

async function loadStats() {
  const stats = await chrome.storage.local.get({
    savedAmount: 0,
    ordersCount: 0
  });
  
  document.getElementById('savedAmount').textContent = `₹${stats.savedAmount}`;
  document.getElementById('ordersCount').textContent = stats.ordersCount;
}

async function detectPlatform() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab || !tab.url) return;
  
  const platformInfo = document.getElementById('platformInfo');
  const platformIcon = document.getElementById('platformIcon');
  const platformName = document.getElementById('platformName');
  const platformActions = document.getElementById('platformActions');
  
  let platform = null;
  
  if (tab.url.includes('swiggy.com')) {
    platform = 'Swiggy';
    platformIcon.textContent = '🍕';
  } else if (tab.url.includes('zomato.com')) {
    platform = 'Zomato';
    platformIcon.textContent = '🍔';
  } else if (tab.url.includes('blinkit.com')) {
    platform = 'Blinkit';
    platformIcon.textContent = '🛒';
  }
  
  if (platform) {
    platformName.textContent = `On ${platform}`;
    platformActions.style.display = 'flex';
  } else {
    platformName.textContent = 'No platform detected';
    platformActions.style.display = 'none';
  }
}

// Listen for platform detection updates
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'PLATFORM_DETECTED') {
    detectPlatform();
  }
});
