// Options Page Logic

document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  setupEventListeners();
});

async function loadSettings() {
  const settings = await chrome.storage.sync.get({
    apiKey: '',
    location: '',
    preferences: {
      dietary: 'none',
      spiceLevel: 'medium',
      budget: { min: 0, max: 2000 }
    },
    enableAutomation: true,
    confirmBeforeOrder: true,
    saveHistory: true,
    platforms: {
      swiggy: true,
      zomato: true,
      blinkit: true
    }
  });

  // Populate fields
  document.getElementById('apiKey').value = settings.apiKey;
  document.getElementById('location').value = settings.location;
  document.getElementById('dietary').value = settings.preferences.dietary;
  document.getElementById('spiceLevel').value = settings.preferences.spiceLevel;
  document.getElementById('budgetMin').value = settings.preferences.budget.min;
  document.getElementById('budgetMax').value = settings.preferences.budget.max;
  document.getElementById('enableAutomation').checked = settings.enableAutomation;
  document.getElementById('confirmBeforeOrder').checked = settings.confirmBeforeOrder;
  document.getElementById('saveHistory').checked = settings.saveHistory;
  document.getElementById('swiggyEnabled').checked = settings.platforms.swiggy;
  document.getElementById('zomatoEnabled').checked = settings.platforms.zomato;
  document.getElementById('blinkitEnabled').checked = settings.platforms.blinkit;
}

function setupEventListeners() {
  // Save settings
  document.getElementById('saveSettings').addEventListener('click', saveSettings);

  // Test API key
  document.getElementById('testApiKey').addEventListener('click', testApiKey);

  // Clear data buttons
  document.getElementById('clearHistory').addEventListener('click', () => {
    if (confirm('Clear all order history?')) {
      chrome.storage.local.set({ orderHistory: [] });
      showStatus('saveStatus', 'Order history cleared', 'success');
    }
  });

  document.getElementById('clearChat').addEventListener('click', () => {
    if (confirm('Clear all chat history?')) {
      chrome.storage.local.set({ chatHistory: [] });
      showStatus('saveStatus', 'Chat history cleared', 'success');
    }
  });

  document.getElementById('resetAll').addEventListener('click', () => {
    if (confirm('Reset all settings to default?')) {
      chrome.storage.sync.clear();
      chrome.storage.local.clear();
      location.reload();
    }
  });
}

async function saveSettings() {
  const settings = {
    apiKey: document.getElementById('apiKey').value.trim(),
    location: document.getElementById('location').value.trim(),
    preferences: {
      dietary: document.getElementById('dietary').value,
      spiceLevel: document.getElementById('spiceLevel').value,
      budget: {
        min: parseInt(document.getElementById('budgetMin').value) || 0,
        max: parseInt(document.getElementById('budgetMax').value) || 2000
      }
    },
    enableAutomation: document.getElementById('enableAutomation').checked,
    confirmBeforeOrder: document.getElementById('confirmBeforeOrder').checked,
    saveHistory: document.getElementById('saveHistory').checked,
    platforms: {
      swiggy: document.getElementById('swiggyEnabled').checked,
      zomato: document.getElementById('zomatoEnabled').checked,
      blinkit: document.getElementById('blinkitEnabled').checked
    }
  };

  try {
    await chrome.storage.sync.set(settings);
    showStatus('saveStatus', '✅ Settings saved successfully!', 'success');

    // Notify background to reload
    chrome.runtime.sendMessage({ type: 'SETTINGS_UPDATED' });
  } catch (error) {
    showStatus('saveStatus', '❌ Failed to save: ' + error.message, 'error');
  }
}

async function testApiKey() {
  const apiKey = document.getElementById('apiKey').value.trim();

  if (!apiKey) {
    showStatus('apiStatus', 'Please enter an API key', 'error');
    return;
  }

  showStatus('apiStatus', 'Testing connection...', 'info');

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: 'Hello' }] }]
        })
      }
    );

    if (response.ok) {
      showStatus('apiStatus', '✅ API key is valid!', 'success');
    } else {
      const error = await response.json();
      showStatus('apiStatus', '❌ Invalid API key: ' + (error.error?.message || 'Unknown error'), 'error');
    }
  } catch (error) {
    showStatus('apiStatus', '❌ Connection failed: ' + error.message, 'error');
  }
}

function showStatus(elementId, message, type) {
  const statusEl = document.getElementById(elementId);
  statusEl.textContent = message;
  statusEl.className = `status-message ${type}`;

  if (type === 'success') {
    setTimeout(() => {
      statusEl.textContent = '';
      statusEl.className = 'status-message';
    }, 3000);
  }
}
