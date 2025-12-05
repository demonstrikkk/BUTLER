// Gemini AI Service with Function Calling for Browser Extension
// Provides AI capabilities for food ordering automation

export class GeminiAIService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.apiUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';
    this.chatHistory = [];
    this.model = null;
  }

  async initialize() {
    console.log('🤖 Initializing Gemini AI...');
    
    // Define available functions/tools
    this.tools = this.defineTools();
    
    // Set up system prompt
    this.systemPrompt = this.getSystemPrompt();
    
    console.log('✅ Gemini AI initialized with function calling');
  }

  defineTools() {
    return [
      {
        name: 'search_food',
        description: 'Search for food items or restaurants across delivery platforms (Swiggy, Zomato, Blinkit). Use this when user wants to find food, restaurants, or specific dishes.',
        parameters: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'The food item, dish name, or restaurant to search for (e.g., "biryani", "Dominos pizza", "best burgers")'
            },
            platforms: {
              type: 'array',
              items: { type: 'string', enum: ['swiggy', 'zomato', 'blinkit'] },
              description: 'Which platforms to search on. Default: all platforms'
            },
            filters: {
              type: 'object',
              properties: {
                cuisine: { type: 'string' },
                dietary: { type: 'string', enum: ['veg', 'non-veg', 'eggitarian', 'vegan'] },
                maxPrice: { type: 'number' },
                minRating: { type: 'number' }
              }
            }
          },
          required: ['query']
        }
      },
      {
        name: 'compare_prices',
        description: 'Compare prices of the same food item across different platforms. Use this when user wants to find the best deal or cheapest option.',
        parameters: {
          type: 'object',
          properties: {
            item: {
              type: 'string',
              description: 'The food item to compare (e.g., "Margherita Pizza", "Chicken Biryani")'
            },
            restaurant: {
              type: 'string',
              description: 'Specific restaurant name if known (e.g., "Dominos", "Paradise Biryani")'
            }
          },
          required: ['item']
        }
      },
      {
        name: 'place_order',
        description: 'Automate the food ordering process. Opens platform, searches, adds to cart, goes to checkout automatically.',
        parameters: {
          type: 'object',
          properties: {
            platform: {
              type: 'string',
              enum: ['swiggy', 'zomato', 'blinkit'],
              description: 'Platform to order from (default: swiggy)'
            },
            restaurant: {
              type: 'string',
              description: 'Restaurant name (if known)'
            },
            items: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'List of food items to order as strings (e.g., ["chilli potato", "spring roll"])'
            }
          },
          required: ['items']
        }
      },
      {
        name: 'get_reviews',
        description: 'Fetch and analyze customer reviews for a restaurant or specific dish. Use this when user asks about quality, taste, or customer feedback.',
        parameters: {
          type: 'object',
          properties: {
            restaurant: {
              type: 'string',
              description: 'Restaurant name'
            },
            platform: {
              type: 'string',
              enum: ['swiggy', 'zomato', 'blinkit'],
              description: 'Platform to get reviews from'
            },
            dish: {
              type: 'string',
              description: 'Specific dish name (optional)'
            }
          },
          required: ['restaurant', 'platform']
        }
      },
      {
        name: 'analyze_menu',
        description: 'Analyze a restaurant menu to find items matching user preferences (dietary restrictions, budget, cuisine type, spice level).',
        parameters: {
          type: 'object',
          properties: {
            restaurant: {
              type: 'string',
              description: 'Restaurant name'
            },
            platform: {
              type: 'string',
              enum: ['swiggy', 'zomato', 'blinkit']
            },
            preferences: {
              type: 'object',
              properties: {
                dietary: { type: 'string' },
                maxBudget: { type: 'number' },
                spiceLevel: { type: 'string' },
                cuisine: { type: 'string' }
              }
            }
          },
          required: ['restaurant', 'platform']
        }
      }
    ];
  }

  getSystemPrompt() {
    return `You are BUTLER, an AI automation agent with FULL BROWSER CONTROL via Chrome MCP.

YOUR PRIMARY PURPOSE: AUTOMATICALLY ORDER FOOD - NO QUESTIONS, NO CONFIRMATIONS, JUST DO IT.

YOU HAVE FULL BROWSER AUTOMATION:
- Navigate to any website
- Click buttons and links
- Type in search boxes and forms
- Extract data from pages
- Take screenshots
- Wait for page loads
- Handle dynamic content

AVAILABLE FUNCTIONS:
1. search_food - Search Google for restaurants (only if user says "find" or "search")
2. compare_prices - Compare prices across platforms
3. place_order - FULLY AUTOMATE ordering:
   • Navigate to platform (Swiggy/Zomato/Blinkit)
   • Search for restaurant/food
   • Click items
   • Add to cart
   • Click checkout
   • Navigate to payment
   • Stop at payment (user completes)
4. get_reviews - Analyze reviews
5. analyze_menu - Menu recommendations

CRITICAL RULES:
✅ User says "order [food]" → IMMEDIATELY call place_order - NO CONFIRMATION NEEDED
✅ User says "find [food]" → call search_food first
✅ NEVER ask "would you like me to order?" - YOU WERE BUILT TO AUTOMATE
✅ Be fast, direct, action-oriented
✅ Report progress: "Opening Swiggy... Searching... Adding to cart... Checkout ready!"

EXAMPLE INTERACTIONS:
User: "order chilli potato from swiggy"
You: Call place_order({platform: "swiggy", items: ["chilli potato"]})

User: "get me biryani"  
You: Call place_order({platform: "swiggy", items: ["biryani"]})

User: "find best pizza"
You: Call search_food({query: "pizza"})

You are an AUTOMATION AGENT, not a chatbot. The user created you to TAKE ACTION. So TAKE ACTION! 🚀🤖`;
  }

  async chat(message, context = {}) {
    console.log('💬 Gemini chat:', message);
    
    // Build messages array
    const messages = [
      {
        role: 'user',
        parts: [{ text: this.buildContextualMessage(message, context) }]
      }
    ];
    
    // Append chat history
    messages.push(...this.chatHistory);
    
    // Make API request
    const response = await this.makeRequest({
      contents: messages,
      tools: [{ function_declarations: this.tools }],
      systemInstruction: {
        parts: [{ text: this.systemPrompt }]
      }
    });
    
    // Parse response
    const result = this.parseResponse(response);
    
    // Store in history
    this.chatHistory.push({
      role: 'user',
      parts: [{ text: message }]
    });
    
    if (result.text) {
      this.chatHistory.push({
        role: 'model',
        parts: [{ text: result.text }]
      });
    }
    
    return result;
  }

  async continueChat(functionResults) {
    console.log('🔄 Continuing chat with function results');
    
    // Add function results to history
    const functionParts = functionResults.map(fr => ({
      functionResponse: {
        name: fr.name,
        response: fr.result || { error: fr.error }
      }
    }));
    
    this.chatHistory.push({
      role: 'function',
      parts: functionParts
    });
    
    // Get final response from AI
    const response = await this.makeRequest({
      contents: this.chatHistory,
      tools: [{ function_declarations: this.tools }],
      systemInstruction: {
        parts: [{ text: this.systemPrompt }]
      }
    });
    
    const result = this.parseResponse(response);
    
    if (result.text) {
      this.chatHistory.push({
        role: 'model',
        parts: [{ text: result.text }]
      });
    }
    
    return result;
  }

  buildContextualMessage(message, context) {
    let fullMessage = message;
    
    if (context.platform) {
      fullMessage += `\n\n[Context: User is currently on ${context.platform}]`;
    }
    
    if (context.userPreferences) {
      const prefs = context.userPreferences;
      fullMessage += `\n[User preferences: Dietary: ${prefs.dietary}, Budget: ₹${prefs.budget?.min}-₹${prefs.budget?.max}, Spice: ${prefs.spiceLevel}]`;
    }
    
    if (context.location) {
      fullMessage += `\n[Location: ${context.location}]`;
    }
    
    return fullMessage;
  }

  async makeRequest(body) {
    const response = await fetch(`${this.apiUrl}?key=${this.apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Gemini API error: ${error.error?.message || response.statusText}`);
    }
    
    return await response.json();
  }

  parseResponse(apiResponse) {
    const result = {
      text: '',
      functionCalls: []
    };
    
    console.log('📥 Gemini API Response:', JSON.stringify(apiResponse, null, 2));
    
    if (!apiResponse.candidates || apiResponse.candidates.length === 0) {
      // Check for error in response
      if (apiResponse.error) {
        throw new Error(`Gemini API error: ${apiResponse.error.message}`);
      }
      throw new Error('No response from Gemini - API key may be invalid or quota exceeded');
    }
    
    const candidate = apiResponse.candidates[0];
    
    // Check for blocked content
    if (candidate.finishReason === 'SAFETY' || candidate.finishReason === 'RECITATION') {
      result.text = "I can't process that request. Please try rephrasing your message.";
      return result;
    }
    
    const parts = candidate.content?.parts || [];
    
    for (const part of parts) {
      if (part.text) {
        result.text += part.text;
      }
      
      if (part.functionCall) {
        result.functionCalls.push({
          name: part.functionCall.name,
          args: part.functionCall.args
        });
      }
    }
    
    return result;
  }

  clearHistory() {
    this.chatHistory = [];
  }

  getHistory() {
    return this.chatHistory;
  }
}
