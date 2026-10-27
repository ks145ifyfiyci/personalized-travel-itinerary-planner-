"""
Simulated JSON-based Database Persistence for Trip Management.
Zero external database dependencies. Compatible with Streamlit Community Cloud.
Skill Wallet Capstone Project 4.
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import Itinerary, SavedTrip, TripPreferences, DayPlan, ActivitySlot


STORAGE_DIR = os.path.join(os.path.dirname(__file__), "data")
STORAGE_FILE = os.path.join(STORAGE_DIR, "trips.json")


def _ensure_storage_dir():
    """Ensure data storage directory exists."""
    os.makedirs(STORAGE_DIR, exist_ok=True)


def _seed_initial_trip_if_empty():
    """Seed sample trip if database is brand new."""
    if not os.path.exists(STORAGE_FILE) or os.path.getsize(STORAGE_FILE) == 0:
        import mock_data
        prefs = TripPreferences(
            destination="Paris",
            vibe="Cultural & Heritage Discovery 🏛️",
            duration_days=3,
            start_date="2026-05-15",
            end_date="2026-05-17",
            budget_level="Moderate",
            currency="USD",
            travel_party="Couple",
            pace="Moderate",
            interests=["Art, Museums & Architecture", "Food & Culinary Gems", "History & Ancient Heritage"],
            dietary="Vegetarian",
        )
        sample_itin = mock_data.generate_mock_itinerary(prefs)
        sample_trip = SavedTrip(
            id=sample_itin.id,
            title=sample_itin.title,
            destination=sample_itin.destination,
            country=sample_itin.country,
            dates=f"{prefs.start_date} to {prefs.end_date}",
            duration_days=prefs.duration_days,
            budget_level=prefs.budget_level,
            currency=prefs.currency,
            total_cost_usd=sample_itin.total_cost_usd,
            created_at=sample_itin.created_at,
            itinerary_data=sample_itin.model_dump(),
        )
        _write_raw_trips([sample_trip.model_dump()])


def _read_raw_trips() -> List[Dict[str, Any]]:
    """Read raw records from JSON file."""
    _ensure_storage_dir()
    _seed_initial_trip_if_empty()
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _write_raw_trips(trips: List[Dict[str, Any]]) -> None:
    """Write raw records to JSON file."""
    _ensure_storage_dir()
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(trips, f, indent=2, ensure_ascii=False)


def get_all_trips() -> List[SavedTrip]:
    """Retrieve all saved trips sorted by creation date."""
    records = _read_raw_trips()
    trips = []
    for r in records:
        try:
            trips.append(SavedTrip(**r))
        except Exception:
            continue
    # Most recent first
    return sorted(trips, key=lambda x: x.created_at, reverse=True)


def get_trip_by_id(trip_id: str) -> Optional[SavedTrip]:
    """Retrieve single trip by ID."""
    all_trips = get_all_trips()
    for t in all_trips:
        if t.id == trip_id:
            return t
    return None


def save_itinerary_to_db(itinerary: Itinerary) -> SavedTrip:
    """Save or update an itinerary in local JSON persistence."""
    records = _read_raw_trips()

    saved_obj = SavedTrip(
        id=itinerary.id,
        title=itinerary.title,
        destination=itinerary.destination,
        country=itinerary.country,
        dates=f"{itinerary.preferences.start_date} to {itinerary.preferences.end_date}",
        duration_days=itinerary.preferences.duration_days,
        budget_level=itinerary.preferences.budget_level,
        currency=itinerary.preferences.currency,
        total_cost_usd=itinerary.total_cost_usd,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        itinerary_data=itinerary.model_dump(),
    )

    # Check if existing id
    updated = False
    for i, r in enumerate(records):
        if r.get("id") == itinerary.id:
            records[i] = saved_obj.model_dump()
            updated = True
            break

    if not updated:
        records.append(saved_obj.model_dump())

    _write_raw_trips(records)
    return saved_obj


def delete_trip_by_id(trip_id: str) -> bool:
    """Delete a trip from persistence."""
    records = _read_raw_trips()
    new_records = [r for r in records if r.get("id") != trip_id]
    if len(new_records) != len(records):
        _write_raw_trips(new_records)
        return True
    return False


def itinerary_from_saved_trip(saved: SavedTrip) -> Itinerary:
    """Reconstruct an Itinerary Pydantic model from a SavedTrip."""
    raw = saved.itinerary_data
    prefs = TripPreferences(**raw["preferences"])

    days = []
    for d in raw.get("days", []):
        day = DayPlan(
            day_number=d["day_number"],
            date=d.get("date"),
            theme=d["theme"],
            cluster_neighborhood=d["cluster_neighborhood"],
            daily_transit_overview=d.get("daily_transit_overview"),
            transit_fatigue_score=d.get("transit_fatigue_score", "Low"),
            morning=ActivitySlot(**d["morning"]),
            lunch=ActivitySlot(**d["lunch"]),
            afternoon=ActivitySlot(**d["afternoon"]),
            evening=ActivitySlot(**d["evening"]),
        )
        days.append(day)

    itin = Itinerary(
        id=saved.id,
        title=saved.title,
        destination=saved.destination,
        country=saved.country,
        days=days,
        total_cost_usd=saved.total_cost_usd,
        preferences=prefs,
        created_at=saved.created_at,
    )
    itin.calculate_total_cost()
    return itin
