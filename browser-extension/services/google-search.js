// Google Search Service using Google ADK (AI Development Kit)
// Provides Google Search integration for finding restaurants and food

export class GoogleSearchService {
  constructor() {
    this.searchEndpoint = 'https://www.google.com/search';
  }

  /**
   * Search Google for restaurants and food using ADK
   * @param {string} query - Search query (e.g., "biryani near me")
   * @param {Object} filters - Optional filters (location, platform, etc.)
   * @returns {Promise<Array>} Search results with restaurant info
   */
  async search(query, filters = {}) {
    console.log(`🔍 Google Search: "${query}"`, filters);

    // Construct enhanced search query
    const enhancedQuery = this.buildSearchQuery(query, filters);
    
    // Open search in new tab
    const tab = await chrome.tabs.create({
      url: `https://www.google.com/search?q=${encodeURIComponent(enhancedQuery)}`,
      active: false
    });

    // Wait for search results to load
    await this.waitForSearchResults(tab.id);

    // Extract search results
    const results = await this.extractSearchResults(tab.id);

    console.log(`✅ Found ${results.length} results`);
    return results;
  }

  /**
   * Build enhanced search query with filters
   */
  buildSearchQuery(query, filters) {
    let searchTerms = [query];

    // Add location
    if (filters.location) {
      searchTerms.push(`near ${filters.location}`);
    } else {
      searchTerms.push('near me');
    }

    // Add platform preference
    if (filters.platforms && filters.platforms.length > 0) {
      const platformNames = filters.platforms.map(p => {
        if (p === 'swiggy') return 'Swiggy';
        if (p === 'zomato') return 'Zomato';
        if (p === 'blinkit') return 'Blinkit';
        return p;
      });
      searchTerms.push(`on ${platformNames.join(' or ')}`);
    }

    // Add dietary filters
    if (filters.dietary) {
      searchTerms.push(filters.dietary);
    }

    return searchTerms.join(' ');
  }

  /**
   * Wait for Google search results to load
   */
  async waitForSearchResults(tabId) {
    return new Promise((resolve) => {
      const checkResults = setInterval(async () => {
        try {
          const results = await chrome.scripting.executeScript({
            target: { tabId },
            func: () => {
              return document.querySelector('#search') !== null;
            }
          });

          if (results && results[0]?.result) {
            clearInterval(checkResults);
            // Wait a bit more for content to stabilize
            setTimeout(resolve, 1000);
          }
        } catch (error) {
          console.error('Error checking search results:', error);
          clearInterval(checkResults);
          resolve();
        }
      }, 500);

      // Timeout after 10 seconds
      setTimeout(() => {
        clearInterval(checkResults);
        resolve();
      }, 10000);
    });
  }

  /**
   * Extract search results from Google page
   */
  async extractSearchResults(tabId) {
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId },
        func: () => {
          const searchResults = [];
          
          // Extract organic search results
          const resultDivs = document.querySelectorAll('.g, .Ww4FFb');
          
          resultDivs.forEach((div, index) => {
            if (index >= 10) return; // Limit to top 10 results
            
            // Extract title and link
            const titleElem = div.querySelector('h3');
            const linkElem = div.querySelector('a');
            const snippetElem = div.querySelector('.VwiC3b, .lEBKkf');
            
            if (titleElem && linkElem) {
              const url = linkElem.href;
              
              // Detect platform from URL
              let platform = 'other';
              if (url.includes('swiggy.com')) platform = 'swiggy';
              else if (url.includes('zomato.com')) platform = 'zomato';
              else if (url.includes('blinkit.com')) platform = 'blinkit';
              
              searchResults.push({
                title: titleElem.textContent.trim(),
                url: url,
                snippet: snippetElem ? snippetElem.textContent.trim() : '',
                platform: platform,
                rank: index + 1
              });
            }
          });
          
          return searchResults;
        }
      });

      // Close the search tab
      await chrome.tabs.remove(tabId);

      return results[0]?.result || [];
    } catch (error) {
      console.error('Error extracting search results:', error);
      try {
        await chrome.tabs.remove(tabId);
      } catch (e) {}
      return [];
    }
  }

  /**
   * Parse restaurant information from search result
   */
  parseRestaurantInfo(result) {
    const info = {
      name: '',
      platform: result.platform,
      url: result.url,
      snippet: result.snippet
    };

    // Extract restaurant name from title
    // Common patterns: "Restaurant Name - Swiggy" or "Order from Restaurant Name"
    const titleMatch = result.title.match(/^([^-|]+)/);
    if (titleMatch) {
      info.name = titleMatch[1].trim();
    }

    // Try to extract rating from snippet
    const ratingMatch = result.snippet.match(/(\d+\.?\d*)\s*(?:star|★|rating)/i);
    if (ratingMatch) {
      info.rating = parseFloat(ratingMatch[1]);
    }

    // Try to extract price info
    const priceMatch = result.snippet.match(/₹\s*(\d+)/);
    if (priceMatch) {
      info.price = parseInt(priceMatch[1]);
    }

    return info;
  }

  /**
   * Filter results by platform
   */
  filterByPlatform(results, platforms) {
    if (!platforms || platforms.length === 0) {
      return results;
    }

    return results.filter(result => 
      platforms.includes(result.platform)
    );
  }

  /**
   * Get the best result based on criteria
   */
  getBestResult(results, criteria = {}) {
    if (results.length === 0) return null;

    // Prefer results from specified platforms
    const platformResults = this.filterByPlatform(
      results, 
      criteria.platforms || ['swiggy', 'zomato', 'blinkit']
    );

    // Return highest ranked platform result
    return platformResults[0] || results[0];
  }
}
