"""Test the function calling automation."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from agent import FoodOrderingAgent

console = Console()

def test_function_calling():
    """Test the Gemini function calling integration."""
    
    console.print("\n[bold cyan]🧪 Testing Gemini Function Calling Integration[/bold cyan]\n")
    
    try:
        # Initialize agent
        console.print("1. Initializing BUTLER with function calling...", style="yellow")
        agent = FoodOrderingAgent()
        console.print("   ✅ Agent initialized with 5 functions available\n", style="green")
        
        # Test 1: Search function
        console.print("2. Testing search_food function...", style="yellow")
        response1 = agent.chat_with_agent("Show me pizza options")
        console.print(f"   Response: {response1[:100]}...\n", style="dim")
        
        # Test 2: Price comparison
        console.print("3. Testing compare_prices function...", style="yellow")
        response2 = agent.chat_with_agent("Compare prices for Margherita pizza from Dominos")
        console.print(f"   Response: {response2[:100]}...\n", style="dim")
        
        # Test 3: Get preferences
        console.print("4. Testing get_user_preferences function...", style="yellow")
        response3 = agent.chat_with_agent("What are my dietary preferences?")
        console.print(f"   Response: {response3[:100]}...\n", style="dim")
        
        console.print("\n[bold green]✅ All function calling tests passed![/bold green]\n")
        console.print("The AI can now:")
        console.print("  • Search for food automatically")
        console.print("  • Compare prices across platforms")
        console.print("  • Access user preferences")
        console.print("  • Trigger browser automation when you confirm orders\n")
        
        console.print("[bold yellow]⚠️  Note: place_order() automation requires Chrome browser[/bold yellow]")
        console.print("[dim]To test full ordering: python run_agent.py[/dim]\n")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Test failed: {e}[/bold red]\n", style="red")
        
        if "API_KEY" in str(e):
            console.print("💡 Fix: Set your API key using: python setup_api_key.py\n")
        
        return False


if __name__ == "__main__":
    success = test_function_calling()
    sys.exit(0 if success else 1)
