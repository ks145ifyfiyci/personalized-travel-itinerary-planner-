"""
Configuration module for the Personalized Travel Itinerary Planner SaaS app.
Skill Wallet Capstone Project 4.
"""

APP_NAME = "Personalized Travel Itinerary Planner"
APP_SUBTITLE = "AI-Powered Smart Travel SaaS • Curated Days, Geographic Optimization & Offline Export"
PROJECT_BADGE = "Skill Wallet Capstone Project 4"

# Currency Support with exchange rates relative to USD (1 USD = X Currency)
CURRENCIES = {
    "USD": {"symbol": "$", "rate": 1.0, "name": "US Dollar"},
    "INR": {"symbol": "₹", "rate": 83.5, "name": "Indian Rupee"},
    "EUR": {"symbol": "€", "rate": 0.92, "name": "Euro"},
    "GBP": {"symbol": "£", "rate": 0.79, "name": "British Pound"},
    "JPY": {"symbol": "¥", "rate": 155.0, "name": "Japanese Yen"},
    "AUD": {"symbol": "A$", "rate": 1.52, "name": "Australian Dollar"},
    "CAD": {"symbol": "C$", "rate": 1.37, "name": "Canadian Dollar"},
}

# Budget levels and typical daily spending benchmarks (USD)
BUDGET_LEVELS = {
    "Budget": {
        "icon": "🎒",
        "description": "Hostels/budget hotels, street food, public transit, free & affordable sights.",
        "daily_target_usd": 65,
    },
    "Moderate": {
        "icon": "✨",
        "description": "3-4 star boutique stays, sit-down local bistros, guided tours, occasional rideshare.",
        "daily_target_usd": 180,
    },
    "Luxury": {
        "icon": "💎",
        "description": "5-star luxury hotels, Michelin-starred/fine dining, private transfers & VIP experiences.",
        "daily_target_usd": 450,
    },
}

# Travel Vibe / Mood Options
TRAVEL_VIBES = [
    "Beach & Coastal Escapes 🏖️",
    "Mountains & Nature Trekking 🏔️",
    "Cultural & Heritage Discovery 🏛️",
    "Urban Exploration & Skyline 🏙️",
    "Romantic & Scenic Getaway 🌅",
    "Culinary & Foodie Tour 🍜",
    "Wellness, Yoga & Spa Retreat 🧘",
    "Adrenaline & Thrill Adventures 🏄",
]

# Travel Party Types
TRAVEL_PARTIES = [
    {"label": "Solo Explorer 🧭", "value": "Solo"},
    {"label": "Couple / Duo 💑", "value": "Couple"},
    {"label": "Family with Kids 👨‍👩‍👧‍👦", "value": "Family"},
    {"label": "Friend Group 🎉", "value": "Friends"},
]

# Travel Paces
TRAVEL_PACES = [
    {"label": "Relaxed (1-2 main activities, leisurely meals, ample downtime)", "value": "Relaxed"},
    {"label": "Moderate (Balanced sights, comfortable transit, good pacing)", "value": "Moderate"},
    {"label": "Fast-Paced (Maximum sightseeing, energetic, pack the day)", "value": "Fast-Paced"},
]

# Core Interests
INTEREST_OPTIONS = [
    "Food & Culinary Gems",
    "Adventure & Thrills",
    "History & Ancient Heritage",
    "Nightlife & Social Spots",
    "Art, Museums & Architecture",
    "Nature & Scenic Outdoors",
    "Local Markets & Shopping",
    "Relaxation, Spas & Cafes",
    "Photography & Viewpoints",
]

# Dietary and accessibility preferences
DIETARY_PREFERENCES = [
    "No Restrictions",
    "Vegetarian",
    "Vegan",
    "Halal",
    "Kosher",
    "Gluten-Free",
    "Pescatarian",
    "Jain Vegetarian",
]

# Time Slots for Itinerary
TIME_SLOTS = [
    {"id": "morning", "title": "Morning Sightseeing", "time": "09:00 - 12:30", "icon": "🌅"},
    {"id": "lunch", "title": "Lunch Recommendation", "time": "12:30 - 14:00", "icon": "🍽️"},
    {"id": "afternoon", "title": "Afternoon Leisure & Culture", "time": "14:30 - 17:30", "icon": "🏛️"},
    {"id": "evening", "title": "Evening Dining & Entertainment", "time": "18:30 - 22:00", "icon": "🌙"},
]

# Destination Emergency Database
EMERGENCY_DATA = {
    "France": {"police": "17", "ambulance": "15", "fire": "18", "general": "112", "embassy_info": "US: +33 1 43 12 22 22 / India: +33 1 40 50 70 70"},
    "Japan": {"police": "110", "ambulance": "119", "fire": "119", "general": "110 / 119", "embassy_info": "US: +81 3 3224 5000 / India: +81 3 3262 2391"},
    "USA": {"police": "911", "ambulance": "911", "fire": "911", "general": "911", "embassy_info": "Dial 911 for all immediate emergencies nationwide."},
    "Italy": {"police": "113", "ambulance": "118", "fire": "115", "general": "112", "embassy_info": "US: +39 06 46741 / India: +39 06 4884 642"},
    "Spain": {"police": "091", "ambulance": "061", "fire": "080", "general": "112", "embassy_info": "US: +34 91 587 2200 / India: +34 91 309 8882"},
    "India": {"police": "100", "ambulance": "102", "fire": "101", "general": "112", "embassy_info": "National Emergency Helpline: 112"},
    "Indonesia": {"police": "110", "ambulance": "118", "fire": "113", "general": "112", "embassy_info": "US: +62 21 5083 1000 / India: +62 21 520 4150"},
    "United Arab Emirates": {"police": "999", "ambulance": "998", "fire": "997", "general": "999", "embassy_info": "US: +971 2 414 2200 / India: +971 2 449 2700"},
    "Default": {"police": "112", "ambulance": "112", "fire": "112", "general": "112", "embassy_info": "Check local hotel reception and contact nearest home embassy hotline."},
}

# Standard offline emergency checklist
OFFLINE_EMERGENCY_CHECKLIST = [
    "Photocopy / Digital offline copies of Passport, Visa, and ID saved on device",
    "Active Travel Insurance policy number & international assistance phone line",
    "Offline Google Maps / Maps.me area downloaded for the destination",
    "Local physical cash currency reserves (minimum $100 equivalent for emergencies)",
    "Hotel address & room card in native local script/language for taxi drivers",
    "Portable power bank fully charged & universal wall plug adapter",
    "Prescription medications in original packaging with medical doctor prescription",
    "Emergency contacts ICE (In Case of Emergency) saved on phone lock screen",
]
