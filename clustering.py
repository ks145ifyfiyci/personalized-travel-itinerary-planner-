"""
Geographic Clustering and Route Optimization Module.
Groups nearby attractions to minimize transit fatigue and prevent backtracking.
Skill Wallet Capstone Project 4.
"""

import math
from typing import List, Dict, Any, Tuple, Optional
import folium
from folium import plugins
from models import DayPlan, Itinerary, ActivitySlot

# Distinct vibrant colors for consecutive days
DAY_COLORS = [
    "#2563EB",  # Day 1: Royal Blue
    "#059669",  # Day 2: Emerald Green
    "#D97706",  # Day 3: Sunset Amber
    "#7C3AED",  # Day 4: Deep Violet
    "#DC2626",  # Day 5: Crimson Red
    "#0D9488",  # Day 6: Teal
    "#EA580C",  # Day 7: Orange Flame
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two geographic points in kilometers."""
    r = 6371.0  # Earth's radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def evaluate_transit_efficiency(day_plan: DayPlan) -> Dict[str, Any]:
    """
    Compute daily walking distance and transit fatigue score across the 4 sequential slots.
    """
    slots = day_plan.get_all_slots()
    valid_coords = [(s.latitude, s.longitude) for s in slots if s.latitude and s.longitude]

    total_km = 0.0
    legs = []

    for i in range(len(valid_coords) - 1):
        lat1, lon1 = valid_coords[i]
        lat2, lon2 = valid_coords[i + 1]
        dist = haversine_distance_km(lat1, lon1, lat2, lon2)
        total_km += dist
        legs.append(round(dist, 2))

    total_km = round(total_km, 2)

    # Fatigue rating
    if total_km <= 3.5:
        fatigue_score = "Low"
        badge_color = "#10B981"  # green
        desc = "Optimal Walking Cluster: All activities within leisurely walking range (< 3.5 km total transit)."
    elif total_km <= 7.0:
        fatigue_score = "Moderate"
        badge_color = "#F59E0B"  # amber
        desc = "Balanced Transit: Short 5-10 min public transit or rideshare connects sub-districts."
    else:
        fatigue_score = "Elevated"
        badge_color = "#EF4444"  # red
        desc = "Cross-District: Distinct morning & evening quarters. Consider metro or rideshare."

    return {
        "total_distance_km": total_km,
        "fatigue_score": fatigue_score,
        "badge_color": badge_color,
        "description": desc,
        "legs": legs,
    }


def create_folium_itinerary_map(itinerary: Itinerary, selected_day: Optional[int] = None) -> folium.Map:
    """
    Generate an interactive Leaflet map rendering all days or a single selected day.
    Draws markers with custom icons and sequential polyline paths connecting the daily slots.
    """
    all_slots = []
    days_to_render = (
        [d for d in itinerary.days if d.day_number == selected_day]
        if selected_day
        else itinerary.days
    )

    for day in days_to_render:
        for slot in day.get_all_slots():
            if slot.latitude and slot.longitude:
                all_slots.append((day.day_number, slot))

    # Center map on average coordinate, or default to world center
    if all_slots:
        avg_lat = sum(s[1].latitude for s in all_slots) / len(all_slots)
        avg_lon = sum(s[1].longitude for s in all_slots) / len(all_slots)
        start_zoom = 13 if len(all_slots) > 1 else 12
    else:
        avg_lat, avg_lon = 48.8566, 2.3522  # Paris default
        start_zoom = 12

    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=start_zoom,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Render each day with its own color and path
    for day in days_to_render:
        color = DAY_COLORS[(day.day_number - 1) % len(DAY_COLORS)]
        day_coords = []

        day_feature_group = folium.FeatureGroup(name=f"Day {day.day_number}: {day.cluster_neighborhood}")

        for slot in day.get_all_slots():
            if not (slot.latitude and slot.longitude):
                continue

            day_coords.append((slot.latitude, slot.longitude))

            # HTML Popup Content
            popup_html = f"""
            <div style="font-family: system-ui, sans-serif; font-size: 13px; min-width: 200px; color: #1E293B;">
                <div style="font-weight: 700; font-size: 14px; color: {color}; margin-bottom: 4px;">
                    Day {day.day_number} • {slot.slot_type}
                </div>
                <div style="font-weight: 600; margin-bottom: 2px;">{slot.title}</div>
                <div style="color: #64748B; font-size: 11px; margin-bottom: 6px;">📍 {slot.neighborhood} ({slot.time})</div>
                <p style="margin: 4px 0 8px 0; line-height: 1.4;">{slot.description[:130]}...</p>
                <div style="display: flex; justify-content: space-between; border-top: 1px solid #E2E8F0; padding-top: 6px; font-size: 11px;">
                    <span style="font-weight: 600; color: #0F172A;">Est. Cost: ${slot.estimated_cost_usd}</span>
                    <span style="background-color: #F1F5F9; padding: 2px 6px; border-radius: 4px;">{slot.category}</span>
                </div>
            </div>
            """

            folium.CircleMarker(
                location=[slot.latitude, slot.longitude],
                radius=8,
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.85,
                tooltip=f"Day {day.day_number} - {slot.slot_type}: {slot.title}",
                popup=folium.Popup(popup_html, max_width=300),
            ).add_to(day_feature_group)

        # Draw sequential transit route polyline
        if len(day_coords) > 1:
            folium.PolyLine(
                locations=day_coords,
                color=color,
                weight=3,
                opacity=0.7,
                dash_array="6, 6",
                tooltip=f"Day {day.day_number} Cluster Path",
            ).add_to(day_feature_group)

        day_feature_group.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m
