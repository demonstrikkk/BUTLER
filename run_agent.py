"""Main entry point for the Food Ordering Agent."""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from agent import FoodOrderingAgent
from config.settings import settings

console = Console()


def print_welcome():
    """Print welcome banner."""
    welcome_text = """
[bold cyan]🍔 BUTLER - Your AI Food Ordering Assistant[/bold cyan]

Powered by Google Gemini AI

Features:
✅ Intelligent meal suggestions based on your preferences
✅ Search across Swiggy, Zomato, and Blinkit
✅ Compare prices and find the best deals
✅ Curated reviews to help you decide
✅ Automated order placement (you handle payment)

Type [bold yellow]/help[/bold yellow] for commands or just chat naturally!
    """
    console.print(Panel(welcome_text, border_style="cyan"))


def setup_environment():
    """Check and setup environment."""
    if not settings.validate():
        console.print("\n[bold red]⚠️ Configuration Error![/bold red]\n", style="red")
        console.print("GEMINI_API_KEY not found in environment variables.\n")
        console.print("To fix this:")
        console.print("1. Copy .env.example to .env")
        console.print("2. Add your Gemini API key: GEMINI_API_KEY=your_key_here")
        console.print("3. Get a free API key from: https://makersuite.google.com/app/apikey\n")
        
        # Ask if they want to set it now
        set_now = Prompt.ask(
            "Would you like to set your Gemini API key now?",
            choices=["y", "n"],
            default="n"
        )
        
        if set_now == "y":
            api_key = Prompt.ask("Enter your Gemini API key", password=False)
            
            # Create .env file
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                content = content.replace("your_gemini_api_key_here", api_key)
                with open(env_file, 'w') as f:
                    f.write(content)
            else:
                with open(env_file, 'w') as f:
                    f.write(f"GEMINI_API_KEY={api_key}\n")
            
            console.print("\n✅ API key saved! Please restart the application.\n", style="green")
            return False
        else:
            return False
    
    return True


def setup_first_time(agent: FoodOrderingAgent):
    """First-time setup for new users."""
    # Check if user has location set
    if not agent.location_manager.get_default_location():
        console.print("\n[bold yellow]👋 Welcome! Let's set up your profile.[/bold yellow]\n")
        
        location = Prompt.ask("📍 What's your location? (e.g., 'MG Road, Bangalore')")
        
        # Parse location (simplified)
        parts = [p.strip() for p in location.split(',')]
        area = parts[0] if parts else location
        city = parts[1] if len(parts) > 1 else ""
        
        agent.location_manager.add_location(
            name="Home",
            full_address=location,
            area=area,
            city=city,
            is_default=True
        )
        console.print(f"✅ Location set to: {location}\n", style="green")
        
        # Budget
        budget_set = Prompt.ask(
            "💰 Set your typical budget? (e.g., '100 500' for ₹100-₹500)",
            default="100 500"
        )
        try:
            min_b, max_b = map(int, budget_set.split())
            agent.preferences.set_budget(min_b, max_b)
            console.print(f"✅ Budget set to ₹{min_b}-₹{max_b}\n", style="green")
        except:
            console.print("⚠️ Invalid format, using default budget\n", style="yellow")
        
        # Dietary preferences
        dietary = Prompt.ask(
            "🥗 Any dietary preferences? (e.g., 'vegetarian, vegan')",
            default=""
        )
        if dietary:
            prefs = [p.strip() for p in dietary.split(',')]
            agent.preferences.update_dietary(prefs)
            console.print(f"✅ Dietary preferences set\n", style="green")


def main():
    """Main application loop."""
    console.clear()
    print_welcome()
    
    # Setup environment
    if not setup_environment():
        return
    
    try:
        # Initialize agent
        console.print("\n[dim]Initializing BUTLER...[/dim]")
        agent = FoodOrderingAgent()
        
        # First-time setup
        setup_first_time(agent)
        
        console.print("\n[bold green]✅ BUTLER is ready! Start chatting below.[/bold green]\n")
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("\n[bold yellow]👋 Goodbye! Enjoy your meal![/bold yellow]\n")
                    break
                
                # Check for order placement command
                if user_input.lower().startswith("place order:"):
                    # Parse order command: place order: platform, restaurant, item, quantity
                    parts = user_input[12:].split(',')
                    if len(parts) >= 3:
                        platform = parts[0].strip()
                        restaurant = parts[1].strip()
                        item = parts[2].strip()
                        quantity = int(parts[3].strip()) if len(parts) > 3 else 1
                        
                        result = agent.place_order(platform, restaurant, item, quantity)
                        
                        if result.get("success"):
                            console.print("\n[bold green]✅ Order ready for payment![/bold green]", style="green")
                            console.print(f"Platform: {platform}")
                            console.print(f"Item: {quantity}x {item}")
                            console.print(f"Total: ₹{result.get('total', 0):.0f}")
                            console.print("\n[bold yellow]🔒 Please complete payment in the browser window.[/bold yellow]\n")
                        else:
                            console.print(f"\n[bold red]❌ Order failed: {result.get('error')}[/bold red]\n", style="red")
                    else:
                        console.print("[red]Invalid format. Use: place order: platform, restaurant, item, quantity[/red]")
                    continue
                
                # Chat with agent
                console.print("\n[dim]BUTLER is thinking...[/dim]")
                response = agent.chat_with_agent(user_input)
                
                # Display response
                console.print(f"\n[bold magenta]🤖 BUTLER:[/bold magenta]\n{response}")
                
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
                continue
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                continue
    
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]\n", style="red")
        return


def demo_mode():
    """Run a demo without requiring API key."""
    console.print("\n[bold cyan]🎬 DEMO MODE[/bold cyan]\n")
    console.print("This demonstrates the order placement workflow without AI chat.\n")
    
    # Example order
    console.print("[bold]Example: Ordering 4x McAloo Tikki Burger from McDonald's on Swiggy[/bold]\n")
    
    console.print("The automation would:")
    console.print("1. ✅ Open Swiggy")
    console.print("2. ✅ Set location")
    console.print("3. ✅ Search for McDonald's")
    console.print("4. ✅ Find McAloo Tikki Burger")
    console.print("5. ✅ Add 4 items to cart")
    console.print("6. ✅ Navigate to checkout")
    console.print("7. 🔒 STOP (you complete payment)")
    
    console.print("\n[dim]To try the full agent, get a Gemini API key from:")
    console.print("https://makersuite.google.com/app/apikey[/dim]\n")


if __name__ == "__main__":
    # Check if demo mode
    if "--demo" in sys.argv:
        demo_mode()
    else:
        main()
