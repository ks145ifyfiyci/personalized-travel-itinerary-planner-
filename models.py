"""
Pydantic data models for the Personalized Travel Itinerary Planner SaaS app.
Skill Wallet Capstone Project 4.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, date


class TripPreferences(BaseModel):
    destination: str = Field(default="", description="Destination city or region")
    vibe: str = Field(default="Cultural & Heritage Discovery 🏛️", description="Vibe or mood of trip")
    duration_days: int = Field(default=3, ge=1, le=14, description="Trip duration in days")
    start_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    end_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    budget_level: str = Field(default="Moderate", description="Budget, Moderate, or Luxury")
    currency: str = Field(default="USD", description="Base currency for costs")
    travel_party: str = Field(default="Couple", description="Solo, Couple, Family, Friends")
    pace: str = Field(default="Moderate", description="Relaxed, Moderate, Fast-Paced")
    interests: List[str] = Field(default_factory=lambda: ["Food & Culinary Gems", "History & Ancient Heritage"])
    dietary: str = Field(default="No Restrictions", description="Dietary preference")
    accessibility_notes: Optional[str] = Field(default="", description="Special requirements")


class DestinationRecommendation(BaseModel):
    city: str
    country: str
    match_score: int = Field(ge=50, le=100, description="Match percentage score")
    vibe_tags: List[str]
    weather_season: str
    estimated_daily_usd: float
    why_matched: str
    highlights: List[str]
    best_neighborhoods: List[str] = Field(default_factory=list)


class ActivitySlot(BaseModel):
    slot_id: str  # "morning", "lunch", "afternoon", "evening"
    slot_type: str  # e.g., "Morning Sightseeing", "Lunch Recommendation"
    time: str  # e.g., "09:00 - 12:30"
    title: str
    description: str
    neighborhood: str
    estimated_cost_usd: float = Field(ge=0.0)
    category: str = "Sightseeing"  # Sightseeing, Food, Culture, Entertainment, Transit
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    transit_from_previous: Optional[str] = None
    dietary_options: Optional[str] = None
    insider_tip: Optional[str] = None
    customized: bool = False


class DayPlan(BaseModel):
    day_number: int
    date: Optional[str] = None
    theme: str
    cluster_neighborhood: str
    morning: ActivitySlot
    lunch: ActivitySlot
    afternoon: ActivitySlot
    evening: ActivitySlot
    daily_transit_overview: Optional[str] = "All activities clustered within 2 km radius to eliminate transit fatigue."
    transit_fatigue_score: str = "Low"  # Low, Moderate, Elevated

    def get_all_slots(self) -> List[ActivitySlot]:
        return [self.morning, self.lunch, self.afternoon, self.evening]

    def get_daily_cost_usd(self) -> float:
        return sum(slot.estimated_cost_usd for slot in self.get_all_slots())


class Itinerary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str
    destination: str
    country: str = "International"
    days: List[DayPlan]
    total_cost_usd: float = 0.0
    preferences: TripPreferences
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))

    def calculate_total_cost(self) -> float:
        total = sum(day.get_daily_cost_usd() for day in self.days)
        self.total_cost_usd = round(total, 2)
        return self.total_cost_usd


class SavedTrip(BaseModel):
    id: str
    title: str
    destination: str
    country: str
    dates: str
    duration_days: int
    budget_level: str
    currency: str
    total_cost_usd: float
    created_at: str
    itinerary_data: Dict[str, Any]
