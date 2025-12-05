"""User preferences management."""
import json
from typing import List, Dict, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from config.settings import settings


class UserPreferencesModel(BaseModel):
    """User preferences data model."""
    user_id: str
    dietary: List[str] = Field(default_factory=list)  # ["vegetarian", "vegan", "gluten-free", etc.]
    allergies: List[str] = Field(default_factory=list)  # ["nuts", "dairy", "eggs", etc.]
    favorite_cuisines: List[str] = Field(default_factory=list)  # ["Indian", "Italian", "Chinese", etc.]
    disliked_foods: List[str] = Field(default_factory=list)
    budget: Dict[str, int] = Field(default_factory=lambda: {"min": 50, "max": 500})
    preferred_platforms: List[str] = Field(default_factory=lambda: ["Swiggy", "Zomato", "Blinkit"])
    location: Optional[str] = None
    spice_preference: str = "medium"  # "mild", "medium", "spicy"
    meal_times: Dict[str, str] = Field(default_factory=lambda: {
        "breakfast": "08:00-11:00",
        "lunch": "12:00-15:00",
        "snacks": "16:00-18:00",
        "dinner": "19:00-23:00"
    })


class UserPreferences:
    """Manages user preferences with persistence."""
    
    def __init__(self, user_id: str):
        """Initialize user preferences.
        
        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        self.file_path = settings.get_user_file(user_id)
        self.preferences = self._load()
    
    def _load(self) -> UserPreferencesModel:
        """Load user preferences from file or create default."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserPreferencesModel(**data)
            except Exception as e:
                print(f"Error loading preferences: {e}")
                return UserPreferencesModel(user_id=self.user_id)
        else:
            return UserPreferencesModel(user_id=self.user_id)
    
    def save(self) -> bool:
        """Save preferences to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences.model_dump(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def update_dietary(self, dietary: List[str]) -> None:
        """Update dietary preferences."""
        self.preferences.dietary = dietary
        self.save()
    
    def add_allergy(self, allergy: str) -> None:
        """Add an allergy."""
        if allergy not in self.preferences.allergies:
            self.preferences.allergies.append(allergy)
            self.save()
    
    def add_favorite_cuisine(self, cuisine: str) -> None:
        """Add a favorite cuisine."""
        if cuisine not in self.preferences.favorite_cuisines:
            self.preferences.favorite_cuisines.append(cuisine)
            self.save()
    
    def set_budget(self, min_budget: int, max_budget: int) -> None:
        """Set budget range."""
        self.preferences.budget = {"min": min_budget, "max": max_budget}
        self.save()
    
    def set_location(self, location: str) -> None:
        """Set user location."""
        self.preferences.location = location
        self.save()
    
    def set_spice_preference(self, preference: str) -> None:
        """Set spice preference."""
        if preference in ["mild", "medium", "spicy"]:
            self.preferences.spice_preference = preference
            self.save()
    
    def get_summary(self) -> str:
        """Get a human-readable summary of preferences."""
        p = self.preferences
        summary = []
        
        if p.dietary:
            summary.append(f"Dietary: {', '.join(p.dietary)}")
        if p.allergies:
            summary.append(f"⚠️ Allergies: {', '.join(p.allergies)}")
        if p.favorite_cuisines:
            summary.append(f"Favorite Cuisines: {', '.join(p.favorite_cuisines[:5])}")
        summary.append(f"Budget: ₹{p.budget['min']}-₹{p.budget['max']}")
        if p.location:
            summary.append(f"Location: {p.location}")
        summary.append(f"Spice Level: {p.spice_preference}")
        
        return " | ".join(summary)
    
    def to_dict(self) -> dict:
        """Convert preferences to dictionary."""
        return self.preferences.model_dump()
