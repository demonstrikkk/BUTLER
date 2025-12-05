"""Easy setup helper for BUTLER."""
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def main():
    """Run setup wizard."""
    console.clear()
    
    # Welcome
    console.print(Panel(
        "[bold cyan]🍔 BUTLER Setup Wizard[/bold cyan]\n\n"
        "This wizard will help you set up your API key",
        border_style="cyan"
    ))
    
    # Check if .env exists
    env_file = Path(".env")
    
    if env_file.exists():
        console.print("\n✅ .env file found")
        
        # Check current key
        from dotenv import load_dotenv
        load_dotenv()
        current_key = os.getenv("GEMINI_API_KEY", "")
        
        if current_key and current_key != "your_gemini_api_key_here":
            console.print(f"Current API key: {current_key[:6]}...{current_key[-4:]}")
            
            if not Confirm.ask("Do you want to update it?"):
                console.print("\n✅ Keeping existing API key")
                return
    else:
        console.print("\n📝 Creating .env file...")
        # Copy from example
        example = Path(".env.example")
        if example.exists():
            import shutil
            shutil.copy(example, env_file)
            console.print("✅ .env file created")
        else:
            env_file.write_text("GEMINI_API_KEY=your_gemini_api_key_here\n")
            console.print("✅ .env file created")
    
    # Get API key
    console.print("\n" + "="*60)
    console.print("📋 Steps to get your API key:")
    console.print("="*60)
    console.print("1. Open: [link]https://aistudio.google.com/apikey[/link]")
    console.print("2. Click 'Create API Key' button")
    console.print("3. Select 'Create API key in new project'")
    console.print("4. Copy the ENTIRE key (it starts with 'AIza')")
    console.print("="*60)
    
    console.print("\n[yellow]Press Enter after you've opened the website...[/yellow]")
    input()
    
    # Ask for key
    api_key = Prompt.ask("\n🔑 Paste your API key here", password=False)
    
    # Validate format
    api_key = api_key.strip().strip('"').strip("'")
    
    if not api_key:
        console.print("❌ No API key provided!", style="red")
        return
    
    if not api_key.startswith("AIza"):
        console.print("⚠️  Warning: API key doesn't start with 'AIza' (unusual)", style="yellow")
        if not Confirm.ask("Continue anyway?"):
            return
    
    if len(api_key) < 30:
        console.print("⚠️  Warning: API key seems too short", style="yellow")
        if not Confirm.ask("Continue anyway?"):
            return
    
    # Update .env file
    console.print("\n📝 Updating .env file...")
    
    # Read current content
    content = env_file.read_text() if env_file.exists() else ""
    
    # Replace or add GEMINI_API_KEY
    lines = content.splitlines()
    updated = False
    new_lines = []
    
    for line in lines:
        if line.startswith("GEMINI_API_KEY"):
            new_lines.append(f"GEMINI_API_KEY={api_key}")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        new_lines.insert(0, f"GEMINI_API_KEY={api_key}")
    
    env_file.write_text('\n'.join(new_lines) + '\n')
    console.print("✅ .env file updated!")
    
    # Test the key
    console.print("\n🧪 Testing API key...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say 'Hello'")
        
        console.print("\n✅ ✅ ✅ [bold green]SUCCESS![/bold green] ✅ ✅ ✅\n")
        console.print(f"Test response: {response.text}\n")
        console.print(Panel(
            "[bold green]🎉 Setup Complete![/bold green]\n\n"
            "Your API key is working!\n\n"
            "Run this to start:\n"
            "[bold cyan]python run_agent.py[/bold cyan]",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"\n❌ [bold red]API Key Test Failed![/bold red]\n", style="red")
        console.print(f"Error: {e}\n")
        console.print("Please check:")
        console.print("1. You copied the ENTIRE key")
        console.print("2. The key is from Google AI Studio")
        console.print("3. Try creating a NEW API key")
        console.print("\nVisit: https://aistudio.google.com/apikey")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n❌ Setup cancelled", style="yellow")
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red")
