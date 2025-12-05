"""Location management for delivery address handling."""
import json
from typing import List, Optional, Dict
from pathlib import Path
from pydantic import BaseModel
from config.settings import settings


class LocationModel(BaseModel):
    """Location data model."""
    name: str  # "Home", "Office", etc.
    full_address: str
    area: str
    city: str
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


class LocationManager:
    """Manages user delivery locations."""
    
    def __init__(self, user_id: str):
        """Initialize location manager.
        
        Args:
            user_id: Unique user identifier
        """
        self.user_id = user_id
        self.file_path = settings.USERS_DIR / f"{user_id}_locations.json"
        self.locations: List[LocationModel] = self._load()
    
    def _load(self) -> List[LocationModel]:
        """Load locations from file."""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return [LocationModel(**loc) for loc in data]
            except Exception as e:
                print(f"Error loading locations: {e}")
                return []
        return []
    
    def save(self) -> bool:
        """Save locations to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                data = [loc.model_dump() for loc in self.locations]
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving locations: {e}")
            return False
    
    def add_location(
        self,
        name: str,
        full_address: str,
        area: str,
        city: str,
        pincode: Optional[str] = None,
        is_default: bool = False
    ) -> bool:
        """Add a new location.
        
        Args:
            name: Location name (e.g., "Home", "Office")
            full_address: Complete address
            area: Area/locality name
            city: City name
            pincode: Optional pincode
            is_default: Whether this is the default location
            
        Returns:
            True if successful, False otherwise
        """
        # If setting as default, unset other defaults
        if is_default:
            for loc in self.locations:
                loc.is_default = False
        
        location = LocationModel(
            name=name,
            full_address=full_address,
            area=area,
            city=city,
            pincode=pincode,
            is_default=is_default
        )
        
        self.locations.append(location)
        return self.save()
    
    def get_default_location(self) -> Optional[LocationModel]:
        """Get the default location.
        
        Returns:
            Default location or None if not set
        """
        for loc in self.locations:
            if loc.is_default:
                return loc
        # Return first location if no default set
        return self.locations[0] if self.locations else None
    
    def set_default(self, location_name: str) -> bool:
        """Set a location as default.
        
        Args:
            location_name: Name of the location to set as default
            
        Returns:
            True if successful, False otherwise
        """
        found = False
        for loc in self.locations:
            if loc.name == location_name:
                loc.is_default = True
                found = True
            else:
                loc.is_default = False
        
        if found:
            return self.save()
        return False
    
    def get_location_by_name(self, name: str) -> Optional[LocationModel]:
        """Get location by name.
        
        Args:
            name: Location name
            
        Returns:
            Location model or None if not found
        """
        for loc in self.locations:
            if loc.name.lower() == name.lower():
                return loc
        return None
    
    def list_locations(self) -> List[Dict]:
        """Get list of all locations.
        
        Returns:
            List of location dictionaries
        """
        return [loc.model_dump() for loc in self.locations]
    
    def get_current_location_string(self) -> str:
        """Get current location as a formatted string.
        
        Returns:
            Location string for display/search
        """
        default = self.get_default_location()
        if default:
            return f"{default.area}, {default.city}"
        return "Location not set"
    
    def delete_location(self, name: str) -> bool:
        """Delete a location by name.
        
        Args:
            name: Location name to delete
            
        Returns:
            True if successful, False otherwise
        """
        initial_count = len(self.locations)
        self.locations = [loc for loc in self.locations if loc.name.lower() != name.lower()]
        
        if len(self.locations) < initial_count:
            return self.save()
        return False
