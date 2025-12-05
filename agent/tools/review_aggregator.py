"""Review aggregation and curation tool."""
from typing import List, Dict, Optional
import re


def aggregate_reviews(reviews: List[str]) -> Dict[str, List[str]]:
    """Aggregate and categorize reviews into pros and cons.
    
    Args:
        reviews: List of review texts
        
    Returns:
        Dictionary with 'pros' and 'cons' lists
    """
    pros = []
    cons = []
    
    # Keywords for positive and negative sentiments
    positive_keywords = [
        'good', 'great', 'excellent', 'amazing', 'delicious', 'tasty', 'fresh',
        'crispy', 'hot', 'fast', 'quick', 'friendly', 'love', 'best', 'perfect'
    ]
    
    negative_keywords = [
        'bad', 'poor', 'terrible', 'awful', 'cold', 'stale', 'slow', 'late',
        'rude', 'disappointing', 'worst', 'hate', 'soggy', 'burnt', 'raw'
    ]
    
    for review in reviews:
        review_lower = review.lower()
        
        # Count positive and negative keywords
        pos_count = sum(1 for keyword in positive_keywords if keyword in review_lower)
        neg_count = sum(1 for keyword in negative_keywords if keyword in review_lower)
        
        # Categorize based on sentiment
        if pos_count > neg_count:
            if review not in pros:
                pros.append(review[:100])  # Limit length
        elif neg_count > pos_count:
            if review not in cons:
                cons.append(review[:100])
    
    return {
        'pros': pros[:5],  # Top 5 pros
        'cons': cons[:5]   # Top 5 cons
    }


def extract_common_themes(reviews: List[str]) -> List[str]:
    """Extract common themes from reviews.
    
    Args:
        reviews: List of review texts
        
    Returns:
        List of common themes/phrases
    """
    themes = []
    
    # Common food-related phrases to look for
    food_phrases = [
        'portion size', 'portion', 'quantity', 'quality', 'taste', 'flavor',
        'delivery time', 'packaging', 'temperature', 'freshness', 'value for money',
        'spice level', 'authenticity', 'presentation'
    ]
    
    combined_text = ' '.join(reviews).lower()
    
    for phrase in food_phrases:
        if phrase in combined_text:
            themes.append(phrase)
    
    return themes[:3]  # Top 3 themes


def format_review_summary(reviews: List[str], rating: Optional[float] = None) -> str:
    """Format review summary in a user-friendly way.
    
    Args:
        reviews: List of review texts
        rating: Optional overall rating
        
    Returns:
        Formatted review summary
    """
    if not reviews:
        return "No reviews available."
    
    aggregated = aggregate_reviews(reviews)
    themes = extract_common_themes(reviews)
    
    output = []
    output.append("\n📝 **Customer Reviews**\n")
    
    if rating:
        output.append(f"⭐ Overall Rating: {rating:.1f}/5.0\n")
    
    if aggregated['pros']:
        output.append("👍 **Pros:**")
        for pro in aggregated['pros']:
            output.append(f"  • {pro}")
        output.append("")
    
    if aggregated['cons']:
        output.append("👎 **Cons:**")
        for con in aggregated['cons']:
            output.append(f"  • {con}")
        output.append("")
    
    if themes:
        output.append("🔍 **Common Mentions:**")
        output.append(f"  {', '.join(themes)}")
    
    return "\n".join(output)


def calculate_review_score(reviews: List[str]) -> float:
    """Calculate a sentiment score from reviews.
    
    Args:
        reviews: List of review texts
        
    Returns:
        Score between 0-5
    """
    if not reviews:
        return 0.0
    
    positive_keywords = [
        'good', 'great', 'excellent', 'amazing', 'delicious', 'tasty', 'love'
    ]
    negative_keywords = [
        'bad', 'poor', 'terrible', 'awful', 'hate', 'disappointing'
    ]
    
    total_score = 0
    for review in reviews:
        review_lower = review.lower()
        pos_count = sum(1 for kw in positive_keywords if kw in review_lower)
        neg_count = sum(1 for kw in negative_keywords if kw in review_lower)
        
        # Score range: -2 to +2 per review, normalized to 0-5
        review_score = (pos_count - neg_count) + 2
        total_score += min(max(review_score, 0), 4)
    
    avg_score = total_score / len(reviews)
    return min(max(avg_score, 0), 5)  # Clamp to 0-5
