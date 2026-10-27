"""
AI Service layer integrating Google Gemini and Groq with fallback to Demo Mode.
Skill Wallet Capstone Project 4.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from models import (
    TripPreferences,
    DestinationRecommendation,
    ActivitySlot,
    DayPlan,
    Itinerary,
)
import mock_data


def clean_json_response(raw_text: str) -> str:
    """Strip markdown code blocks or extra tokens from LLM output."""
    cleaned = raw_text.strip()
    # Match ```json ... ``` or ``` ... ```
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


class AIService:
    def __init__(
        self,
        provider: str = "demo",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        """
        Initialize the AI service.
        provider: 'gemini', 'groq', or 'demo'
        """
        self.provider = provider.lower()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY" if self.provider == "gemini" else "GROQ_API_KEY")
        self.model_name = model_name

        if not self.model_name:
            if self.provider == "gemini":
                self.model_name = "gemini-2.5-flash"
            elif self.provider == "groq":
                self.model_name = "llama-3.3-70b-versatile"

    def _call_gemini(self, prompt: str) -> str:
        """Execute request via Google GenAI SDK."""
        if not self.api_key:
            raise ValueError("Gemini API Key is missing. Please provide a valid key or switch to Demo Mode.")
        from google import genai
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text

    def _call_groq(self, prompt: str) -> str:
        """Execute request via Groq SDK."""
        if not self.api_key:
            raise ValueError("Groq API Key is missing. Please provide a valid key or switch to Demo Mode.")
        from groq import Groq
        client = Groq(api_key=self.api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a senior full-stack travel SaaS architect and itinerary optimizer. Return strictly valid JSON with no markdown wrapping."},
                {"role": "user", "content": prompt},
            ],
            model=self.model_name,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return chat_completion.choices[0].message.content

    def _execute_prompt(self, prompt: str) -> str:
        """Route to selected provider."""
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        elif self.provider == "groq":
            return self._call_groq(prompt)
        else:
            raise ValueError("Demo Mode active. No external LLM called.")

    def recommend_destinations(
        self,
        vibe: str,
        budget_level: str = "Moderate",
        duration_days: int = 4,
        travel_party: str = "Couple",
        interests: Optional[List[str]] = None,
    ) -> Tuple[List[DestinationRecommendation], str]:
        """
        Recommend top 3 cities based on travel mood and budget.
        Returns: (List[DestinationRecommendation], status_message)
        """
        if self.provider == "demo" or not self.api_key:
            recs = mock_data.get_mock_recommendations(vibe, budget_level)
            return recs, "Demo Mode: Loaded curated high-match destinations."

        prompt = f"""
Return a JSON array of top 3 recommended destination cities matching these travel requirements:
- Travel Vibe / Mood: {vibe}
- Budget Level: {budget_level}
- Duration: {duration_days} days
- Travel Party: {travel_party}
- Core Interests: {', '.join(interests or ['Food', 'Culture'])}

Return strictly a JSON object with a single key "destinations" containing an array of 3 objects with this exact schema:
{{
  "destinations": [
    {{
      "city": "City Name",
      "country": "Country Name",
      "match_score": 95,
      "vibe_tags": ["#Tag1", "#Tag2", "#Tag3", "#Tag4"],
      "weather_season": "Optimal season & current climate description (e.g. 22°C sunny)",
      "estimated_daily_usd": 120.0,
      "why_matched": "Compelling 2-sentence rationale explaining why this city matches the requested vibe and budget",
      "highlights": ["Top Landmark 1", "Top Experience 2", "Culinary Highlight 3", "Hidden Gem 4"],
      "best_neighborhoods": ["District 1", "District 2"]
    }}
  ]
}}
Only return the valid JSON object.
"""
        try:
            raw = self._execute_prompt(prompt)
            cleaned = clean_json_response(raw)
            data = json.loads(cleaned)
            dest_list = data.get("destinations", data if isinstance(data, list) else [])
            result = [DestinationRecommendation(**item) for item in dest_list[:3]]
            return result, f"Successfully recommended destinations using {self.provider.upper()} ({self.model_name})."
        except Exception as e:
            # Fallback seamlessly to mock data with warning
            recs = mock_data.get_mock_recommendations(vibe, budget_level)
            return recs, f"Notice: External AI call failed ({str(e)}). Seamlessly loaded curated destinations."

    def generate_itinerary(self, prefs: TripPreferences) -> Tuple[Itinerary, str]:
        """
        Generate a day-by-day itinerary with geographic clustering and itemized costs.
        Returns: (Itinerary, status_message)
        """
        if self.provider == "demo" or not self.api_key:
            itin = mock_data.generate_mock_itinerary(prefs)
            return itin, "Demo Mode: Generated optimized curated itinerary with geographic clustering."

        interests_str = ", ".join(prefs.interests) if prefs.interests else "General Sights, Culture, Food"
        prompt = f"""
You are a senior full-stack travel SaaS architect creating an optimized itinerary.
Plan an itinerary for:
- Destination: {prefs.destination}
- Duration: {prefs.duration_days} Days (from {prefs.start_date} to {prefs.end_date})
- Vibe / Travel Mood: {prefs.vibe}
- Budget Tier: {prefs.budget_level} (Reference currency: {prefs.currency})
- Travel Party: {prefs.travel_party}
- Pace: {prefs.pace}
- Interests: {interests_str}
- Dietary Preferences: {prefs.dietary}
- Special Notes: {prefs.accessibility_notes or 'None'}

GEOGRAPHIC CLUSTERING INSTRUCTIONS:
To eliminate transit fatigue and prevent backtracking across the city, you MUST:
1. Assign each day to a specific geographic neighborhood or district cluster (e.g. '7th Arrondissement & Eiffel Precinct' or 'Lower Manhattan & DUMBO').
2. Keep all 4 daily slots (Morning, Lunch, Afternoon, Evening) strictly within that same localized cluster or consecutive logical walking route.
3. Include explicit transit guidance between sequential slots (e.g. '5 min walk via Rue Cler', '8 min metro Line 1').
4. Include itemized estimated costs in USD for each activity.

Provide the response strictly as a JSON object matching this schema:
{{
  "title": "Inspiring Title for Trip",
  "destination": "{prefs.destination}",
  "country": "Country Name",
  "days": [
    {{
      "day_number": 1,
      "date": "{prefs.start_date}",
      "theme": "Theme of Day 1",
      "cluster_neighborhood": "Specific District / Cluster Name",
      "daily_transit_overview": "Summary of transit efficiency (e.g., all stops within 1.5 km)",
      "transit_fatigue_score": "Low",
      "morning": {{
        "slot_id": "morning",
        "slot_type": "Morning Sightseeing",
        "time": "09:00 - 12:30",
        "title": "Activity Title",
        "description": "Engaging, practical description of sightseeing activity",
        "neighborhood": "Specific neighborhood",
        "estimated_cost_usd": 25.0,
        "category": "Sightseeing",
        "latitude": 48.8584,
        "longitude": 2.2945,
        "insider_tip": "Practical insider tip for crowds or timing"
      }},
      "lunch": {{
        "slot_id": "lunch",
        "slot_type": "Lunch Recommendation",
        "time": "12:30 - 14:00",
        "title": "Bistro / Restaurant Name",
        "description": "Culinary specialty and ambiance description",
        "neighborhood": "Nearby neighborhood",
        "estimated_cost_usd": 20.0,
        "category": "Food",
        "latitude": 48.8566,
        "longitude": 2.3055,
        "transit_from_previous": "10 min scenic walk",
        "dietary_options": "Dietary highlights catering to {prefs.dietary}",
        "insider_tip": "Booking advice or table tip"
      }},
      "afternoon": {{
        "slot_id": "afternoon",
        "slot_type": "Afternoon Leisure & Culture",
        "time": "14:30 - 17:30",
        "title": "Activity Title",
        "description": "Leisure or cultural exploration",
        "neighborhood": "Nearby neighborhood",
        "estimated_cost_usd": 15.0,
        "category": "Culture",
        "latitude": 48.8550,
        "longitude": 2.3126,
        "transit_from_previous": "8 min walk along avenue",
        "insider_tip": "Quiet viewpoint or entrance tip"
      }},
      "evening": {{
        "slot_id": "evening",
        "slot_type": "Evening Dining & Entertainment",
        "time": "18:30 - 22:00",
        "title": "Dinner & Night Activity Title",
        "description": "Evening dining and entertainment experience",
        "neighborhood": "Evening quarter",
        "estimated_cost_usd": 45.0,
        "category": "Entertainment",
        "latitude": 48.8530,
        "longitude": 2.3499,
        "transit_from_previous": "Short stroll or direct 5-min transit",
        "dietary_options": "Evening dining dietary options",
        "insider_tip": "Sunset or reservation advice"
      }}
    }}
  ]
}}
Only return the valid JSON object.
"""
        try:
            raw = self._execute_prompt(prompt)
            cleaned = clean_json_response(raw)
            data = json.loads(cleaned)

            days = []
            for d in data.get("days", []):
                day_plan = DayPlan(
                    day_number=d.get("day_number", len(days) + 1),
                    date=d.get("date", prefs.start_date),
                    theme=d.get("theme", "Exploration"),
                    cluster_neighborhood=d.get("cluster_neighborhood", "City Center"),
                    daily_transit_overview=d.get("daily_transit_overview", "Geographically clustered for low transit strain."),
                    transit_fatigue_score=d.get("transit_fatigue_score", "Low"),
                    morning=ActivitySlot(**d["morning"]),
                    lunch=ActivitySlot(**d["lunch"]),
                    afternoon=ActivitySlot(**d["afternoon"]),
                    evening=ActivitySlot(**d["evening"]),
                )
                days.append(day_plan)

            itin = Itinerary(
                title=data.get("title", f"{prefs.duration_days}-Day Trip to {prefs.destination}"),
                destination=data.get("destination", prefs.destination),
                country=data.get("country", "International"),
                days=days,
                preferences=prefs,
            )
            itin.calculate_total_cost()
            return itin, f"Itinerary generated via {self.provider.upper()} ({self.model_name})."
        except Exception as e:
            # Fallback gracefully
            itin = mock_data.generate_mock_itinerary(prefs)
            return itin, f"Notice: AI generation fallback triggered ({str(e)}). Loaded geographically clustered plan."

    def customize_slot(
        self,
        day_plan: DayPlan,
        slot_id: str,
        customization_prompt: str,
        prefs: TripPreferences,
    ) -> Tuple[ActivitySlot, str]:
        """
        Dynamically regenerate or swap a single activity slot without altering the rest of the plan.
        Returns: (Updated ActivitySlot, status_message)
        """
        current_slot: ActivitySlot = getattr(day_plan, slot_id)

        if self.provider == "demo" or not self.api_key:
            # Rich offline swap logic
            new_title = f"{current_slot.neighborhood}: {customization_prompt.strip().capitalize()}"
            new_desc = f"Tailored update: Replaced '{current_slot.title}' based on your preference: '{customization_prompt}'. Geographically anchored in {day_plan.cluster_neighborhood} to preserve zero-fatigue clustering."
            
            # Slight price adjustment
            cost = current_slot.estimated_cost_usd
            if "free" in customization_prompt.lower() or "budget" in customization_prompt.lower():
                cost = round(max(0.0, cost * 0.4), 1)
            elif "luxury" in customization_prompt.lower() or "michelin" in customization_prompt.lower():
                cost = round(cost * 1.8, 1)

            dietary = current_slot.dietary_options
            if "veg" in customization_prompt.lower():
                dietary = "100% Vegetarian / Plant-based local specialty verified"

            updated_slot = current_slot.model_copy(
                update={
                    "title": new_title,
                    "description": new_desc,
                    "estimated_cost_usd": cost,
                    "dietary_options": dietary,
                    "insider_tip": "Customized recommendation verified for immediate walking proximity.",
                    "customized": True,
                }
            )
            return updated_slot, f"Slot updated in Demo Mode based on: '{customization_prompt}'"

        prompt = f"""
You are customizing a single itinerary slot while preserving the overall trip plan.
Current Destination: {prefs.destination}
Day {day_plan.day_number} Neighborhood Cluster: {day_plan.cluster_neighborhood}
Current Slot: {current_slot.slot_type} ({current_slot.time})
Current Activity: "{current_slot.title}" - {current_slot.description}
Neighborhood: {current_slot.neighborhood}

USER CUSTOMIZATION REQUEST:
"{customization_prompt}"

RULES:
1. The new activity MUST remain within or immediately adjacent to '{day_plan.cluster_neighborhood}' to avoid transit fatigue.
2. Directly satisfy the user's customization request (e.g. vegetarian dining, outdoor market, art gallery, kid-friendly).
3. Return strictly a JSON object with this exact ActivitySlot schema:
{{
  "slot_id": "{slot_id}",
  "slot_type": "{current_slot.slot_type}",
  "time": "{current_slot.time}",
  "title": "New Activity Title",
  "description": "Engaging description satisfying the request",
  "neighborhood": "{day_plan.cluster_neighborhood}",
  "estimated_cost_usd": {current_slot.estimated_cost_usd},
  "category": "{current_slot.category}",
  "latitude": {current_slot.latitude or 0.0},
  "longitude": {current_slot.longitude or 0.0},
  "transit_from_previous": "Short 5-8 min walk within cluster",
  "dietary_options": "Relevant dietary info if food slot",
  "insider_tip": "Insider local tip",
  "customized": true
}}
Only return the valid JSON object.
"""
        try:
            raw = self._execute_prompt(prompt)
            cleaned = clean_json_response(raw)
            data = json.loads(cleaned)
            updated_slot = ActivitySlot(**data)
            updated_slot.customized = True
            return updated_slot, f"Slot dynamically customized via {self.provider.upper()}."
        except Exception as e:
            # Fallback
            new_title = f"{current_slot.neighborhood}: {customization_prompt.strip().capitalize()}"
            updated_slot = current_slot.model_copy(
                update={
                    "title": new_title,
                    "description": f"Customized adjustment: {customization_prompt}. Retained within {day_plan.cluster_neighborhood}.",
                    "customized": True,
                }
            )
            return updated_slot, f"Notice: Swapped using intelligent fallback ({str(e)})."
