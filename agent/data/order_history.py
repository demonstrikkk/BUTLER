"""Order history tracking and management."""
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from config.settings import settings


class OrderItemModel(BaseModel):
    """Individual order item model."""
    name: str
    quantity: int
    price: float
    customizations: Dict = Field(default_factory=dict)


class OrderModel(BaseModel):
    """Order data model."""
    order_id: str
    timestamp: str
    platform: str  # "Swiggy", "Zomato", "Blinkit"
    restaurant: str
    items: List[OrderItemModel]
    item_total: float
    delivery_fee: float
    taxes: float
    total: float
    location: str
    delivery_time: Optional[str] = None
    user_rating: Optional[int] = None  # 1-5
    user_feedback: Optional[str] = None
    status: str = "completed"  # "placed", "completed", "cancelled"


class OrderHistory:
    """Manages user order history with persistence."""
    
    def __init__(self, user_id: str):
        """Initialize order history.
        
        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        self.file_path = settings.USERS_DIR / f"{user_id}_orders.json"
        self.orders: List[OrderModel] = self._load()
    
    def _load(self) -> List[OrderModel]:
        """Load order history from file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [OrderModel(**order) for order in data]
            except Exception as e:
                print(f"Error loading order history: {e}")
                return []
        return []
    
    def save(self) -> bool:
        """Save order history to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                data = [order.model_dump() for order in self.orders]
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving order history: {e}")
            return False
    
    def add_order(self, order: Dict) -> str:
        """Add a new order to history.
        
        Args:
            order: Order dictionary with all details
            
        Returns:
            Generated order ID
        """
        # Generate order ID
        order_id = f"ord_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        order['order_id'] = order_id
        order['timestamp'] = datetime.now().isoformat()
        
        # Convert items to OrderItemModel
        if 'items' in order:
            order['items'] = [
                OrderItemModel(**item) if isinstance(item, dict) else item
                for item in order['items']
            ]
        
        order_model = OrderModel(**order)
        self.orders.append(order_model)
        self.save()
        return order_id
    
    def get_recent_orders(self, limit: int = 10) -> List[OrderModel]:
        """Get recent orders.
        
        Args:
            limit: Maximum number of orders to return
            
        Returns:
            List of recent orders
        """
        return sorted(self.orders, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_favorite_restaurants(self, limit: int = 5) -> List[Dict[str, any]]:
        """Get most frequently ordered restaurants.
        
        Args:
            limit: Maximum number of restaurants to return
            
        Returns:
            List of restaurants with order count
        """
        restaurant_counts = {}
        for order in self.orders:
            if order.status == "completed":
                restaurant_counts[order.restaurant] = restaurant_counts.get(order.restaurant, 0) + 1
        
        sorted_restaurants = sorted(
            restaurant_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [{"restaurant": name, "order_count": count} for name, count in sorted_restaurants]
    
    def get_favorite_dishes(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get most frequently ordered dishes.
        
        Args:
            limit: Maximum number of dishes to return
            
        Returns:
            List of dishes with order count
        """
        dish_counts = {}
        for order in self.orders:
            if order.status == "completed":
                for item in order.items:
                    dish_counts[item.name] = dish_counts.get(item.name, 0) + item.quantity
        
        sorted_dishes = sorted(
            dish_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [{"dish": name, "order_count": count} for name, count in sorted_dishes]
    
    def get_spending_summary(self) -> Dict[str, float]:
        """Get spending summary.
        
        Returns:
            Dictionary with spending statistics
        """
        completed_orders = [o for o in self.orders if o.status == "completed"]
        if not completed_orders:
            return {"total": 0, "average": 0, "count": 0}
        
        total = sum(order.total for order in completed_orders)
        return {
            "total": total,
            "average": total / len(completed_orders),
            "count": len(completed_orders)
        }
    
    def get_summary_for_ai(self) -> str:
        """Get a summary formatted for AI consumption.
        
        Returns:
            Human-readable summary of order history
        """
        if not self.orders:
            return "No previous orders found."
        
        recent = self.get_recent_orders(5)
        favorites = self.get_favorite_dishes(5)
        fav_restaurants = self.get_favorite_restaurants(3)
        spending = self.get_spending_summary()
        
        summary = []
        summary.append(f"Total Orders: {spending['count']}, Average Order Value: ₹{spending['average']:.0f}")
        
        if fav_restaurants:
            rest_list = ", ".join([f"{r['restaurant']} ({r['order_count']}x)" for r in fav_restaurants])
            summary.append(f"Favorite Restaurants: {rest_list}")
        
        if favorites:
            dish_list = ", ".join([f"{d['dish']} ({d['order_count']}x)" for d in favorites[:3]])
            summary.append(f"Favorite Dishes: {dish_list}")
        
        if recent:
            last_order = recent[0]
            summary.append(f"Last Order: {last_order.restaurant} - {last_order.items[0].name} ({last_order.timestamp[:10]})")
        
        return " | ".join(summary)
    
    def update_rating(self, order_id: str, rating: int, feedback: Optional[str] = None) -> bool:
        """Update order rating and feedback.
        
        Args:
            order_id: Order ID to update
            rating: Rating (1-5)
            feedback: Optional text feedback
            
        Returns:
            True if successful, False otherwise
        """
        for order in self.orders:
            if order.order_id == order_id:
                order.user_rating = rating
                order.user_feedback = feedback
                return self.save()
        return False
