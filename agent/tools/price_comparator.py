"""Price comparison tool for comparing food prices across platforms."""
from typing import List, Dict, Optional


def compare_prices(search_results: List[Dict]) -> List[Dict]:
    """Compare prices across different platforms.
    
    Args:
        search_results: List of search results from different platforms
        Each result should have: platform, restaurant, item, price, delivery_fee, rating
        
    Returns:
        Sorted list with best deals highlighted
    """
    # Add total cost to each result
    for result in search_results:
        result['total'] = result.get('price', 0) + result.get('delivery_fee', 0)
    
    # Sort by total cost (ascending)
    sorted_results = sorted(search_results, key=lambda x: x.get('total', float('inf')))
    
    # Mark the best deal
    if sorted_results:
        sorted_results[0]['is_best_deal'] = True
    
    return sorted_results


def format_price_comparison(results: List[Dict]) -> str:
    """Format price comparison results as a beautiful table.
    
    Args:
        results: List of comparison results
        
    Returns:
        Formatted string with table
    """
    if not results:
        return "No results to compare."
    
    # Build table
    output = []
    output.append("\n📊 **Price Comparison**\n")
    output.append("```")
    output.append("┌" + "─" * 98 + "┐")
    output.append(
        f"│ {'Platform':<12} │ {'Restaurant':<20} │ {'Price':<8} │ {'Delivery':<10} │ {'Total':<8} │ {'Rating':<12} │"
    )
    output.append("├" + "─" * 98 + "┤")
    
    for result in results:
        platform = result.get('platform', 'Unknown')[:12]
        restaurant = result.get('restaurant', 'Unknown')[:20]
        price = f"₹{result.get('price', 0):.0f}"
        delivery = f"₹{result.get('delivery_fee', 0):.0f}"
        total = f"₹{result.get('total', 0):.0f}"
        rating = f"{result.get('rating', 0):.1f}⭐"
        
        prefix = "🏆 " if result.get('is_best_deal') else "   "
        
        output.append(
            f"│{prefix}{platform:<10} │ {restaurant:<20} │ {price:<8} │ {delivery:<10} │ {total:<8} │ {rating:<12} │"
        )
    
    output.append("└" + "─" * 98 + "┘")
    output.append("```\n")
    
    # Add best deal recommendation
    best = results[0] if results else None
    if best:
        output.append(f"\n✅ **Best Deal**: {best['restaurant']} on {best['platform']}")
        output.append(f"💰 Total: ₹{best['total']:.0f}")
        if best.get('delivery_fee', 0) == 0:
            output.append("🎉 Free Delivery!")
    
    return "\n".join(output)


def calculate_savings(results: List[Dict]) -> Optional[Dict]:
    """Calculate potential savings.
    
    Args:
        results: List of price results
        
    Returns:
        Dictionary with savings information
    """
    if len(results) < 2:
        return None
    
    best = results[0]
    worst = results[-1]
    
    savings = worst['total'] - best['total']
    savings_percent = (savings / worst['total']) * 100 if worst['total'] > 0 else 0
    
    return {
        'savings_amount': savings,
        'savings_percent': savings_percent,
        'best_platform': best['platform'],
        'most_expensive_platform': worst['platform']
    }
