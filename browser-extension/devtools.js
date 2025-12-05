// DevTools Panel for BUTLER
// Provides debugging and monitoring capabilities

chrome.devtools.panels.create(
  'BUTLER',
  'icons/icon48.png',
  'devtools-panel.html',
  (panel) => {
    console.log('BUTLER DevTools panel created');
  }
);

// Monitor network requests for food delivery APIs
chrome.devtools.network.onRequestFinished.addListener((request) => {
  const url = request.request.url;
  
  // Detect platform API calls
  if (url.includes('swiggy.com/api') || 
      url.includes('zomato.com/api') || 
      url.includes('blinkit.com/api')) {
    
    console.log('📡 Platform API Call:', {
      url,
      method: request.request.method,
      status: request.response.status
    });
    
    // Send to background for analysis
    chrome.runtime.sendMessage({
      type: 'API_CALL_DETECTED',
      data: {
        url,
        method: request.request.method,
        status: request.response.status
      }
    });
  }
});
