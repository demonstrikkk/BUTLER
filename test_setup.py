"""Simple test script to verify the agent setup."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from config.settings import settings
        print("✅ Config module loaded")
        
        from agent.data.user_preferences import UserPreferences
        from agent.data.order_history import OrderHistory
        from agent.data.location_manager import LocationManager
        print("✅ Data modules loaded")
        
        from agent.automation.base_automator import BaseAutomator
        from agent.automation.swiggy_automator import SwiggyAutomator
        from agent.automation.zomato_automator import ZomatoAutomator
        from agent.automation.blinkit_automator import BlinkitAutomator
        print("✅ Automation modules loaded")
        
        from agent.tools.price_comparator import compare_prices, format_price_comparison
        from agent.tools.review_aggregator import aggregate_reviews
        print("✅ Tool modules loaded")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        return False


def test_data_managers():
    """Test data manager functionality."""
    print("\nTesting data managers...")
    
    try:
        from agent.data.user_preferences import UserPreferences
        from agent.data.order_history import OrderHistory
        from agent.data.location_manager import LocationManager
        
        # Test user preferences
        prefs = UserPreferences("test_user")
        prefs.set_budget(100, 500)
        prefs.add_favorite_cuisine("Italian")
        print("✅ UserPreferences working")
        
        # Test order history
        history = OrderHistory("test_user")
        print("✅ OrderHistory working")
        
        # Test location manager
        locations = LocationManager("test_user")
        print("✅ LocationManager working")
        
        print("\n✅ All data managers working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Data manager test failed: {e}")
        return False


def test_tools():
    """Test tool functionality."""
    print("\nTesting tools...")
    
    try:
        from agent.tools.price_comparator import compare_prices, format_price_comparison
        from agent.tools.review_aggregator import aggregate_reviews, format_review_summary
        
        # Test price comparison
        test_results = [
            {"platform": "Swiggy", "restaurant": "Test", "price": 200, "delivery_fee": 50, "rating": 4.5},
            {"platform": "Zomato", "restaurant": "Test", "price": 180, "delivery_fee": 0, "rating": 4.3},
        ]
        compared = compare_prices(test_results)
        formatted = format_price_comparison(compared)
        print("✅ Price comparison working")
        
        # Test review aggregation
        test_reviews = ["Great food!", "Delicious pizza", "Slow delivery", "Amazing taste"]
        aggregated = aggregate_reviews(test_reviews)
        formatted_reviews = format_review_summary(test_reviews, 4.2)
        print("✅ Review aggregation working")
        
        print("\n✅ All tools working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Tool test failed: {e}")
        return False


def test_configuration():
    """Test configuration."""
    print("\nTesting configuration...")
    
    try:
        from config.settings import settings
        from config.prompts import AGENT_SYSTEM_PROMPT
        
        print(f"Base directory: {settings.BASE_DIR}")
        print(f"Data directory: {settings.DATA_DIR}")
        print(f"Headless mode: {settings.HEADLESS_MODE}")
        print(f"Browser timeout: {settings.BROWSER_TIMEOUT}")
        
        if settings.GEMINI_API_KEY:
            print(f"✅ Gemini API key configured")
        else:
            print(f"⚠️ Gemini API key not set (required for full functionality)")
        
        print("\n✅ Configuration loaded!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("🧪 BUTLER - Component Test Suite")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Data Managers", test_data_managers),
        ("Tools", test_tools),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        results.append((name, test_func()))
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! The agent is ready to use.")
        print("\nNext steps:")
        print("1. Set your Gemini API key in .env file")
        print("2. Run: python run_agent.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
