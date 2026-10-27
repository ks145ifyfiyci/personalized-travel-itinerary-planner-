import sys
import os
sys.path.append(os.path.dirname(__file__))

from models import TripPreferences
from ai_service import AIService
import storage
from clustering import evaluate_transit_efficiency, create_folium_itinerary_map
from budget_tracker import calculate_budget_analytics, create_cumulative_budget_chart, create_category_pie_chart, format_currency
from pdf_generator import generate_itinerary_pdf

print("1. Testing AI Service (Demo Mode)...")
svc = AIService(provider="demo")
recs, msg = svc.recommend_destinations("Cultural & Heritage Discovery 🏛️", "Moderate")
print(f"   Recommended {len(recs)} destinations: {[r.city for r in recs]}")

prefs = TripPreferences(destination="Tokyo", duration_days=3, budget_level="Moderate", currency="INR")
itin, msg = svc.generate_itinerary(prefs)
print(f"   Generated itinerary: {itin.title} ({len(itin.days)} days, ${itin.total_cost_usd} USD)")

print("2. Testing Geographic Clustering & Route...")
for day in itin.days:
    eval_res = evaluate_transit_efficiency(day)
    print(f"   Day {day.day_number} ({day.cluster_neighborhood}): {eval_res['total_distance_km']} km, Fatigue: {eval_res['fatigue_score']}")

folium_map = create_folium_itinerary_map(itin)
print("   Folium map created successfully.")

print("3. Testing Budget Analytics & Charts...")
analytics = calculate_budget_analytics(itin, "INR")
print(f"   Total Spend INR: {format_currency(analytics['total_spend_usd'], 'INR')}, Status: {analytics['budget_health']}")
fig_bar = create_cumulative_budget_chart(analytics['df_daily'], "INR")
fig_pie = create_category_pie_chart(analytics['category_totals_usd'], "INR")
print("   Plotly charts generated successfully.")

print("4. Testing Vibe Customization & Slot Swap...")
target_day = itin.days[0]
old_title = target_day.lunch.title
new_slot, swap_msg = svc.customize_slot(target_day, "lunch", "Find authentic vegetarian matcha ramen cafe", prefs)
print(f"   Old lunch: {old_title}")
print(f"   New lunch: {new_slot.title} (Cost: ${new_slot.estimated_cost_usd}, Customized: {new_slot.customized})")

print("5. Testing Persistence Storage...")
saved = storage.save_itinerary_to_db(itin)
print(f"   Saved trip ID: {saved.id}, Title: {saved.title}")
all_trips = storage.get_all_trips()
print(f"   Total trips in database: {len(all_trips)}")
retrieved = storage.get_trip_by_id(saved.id)
assert retrieved is not None
reconstructed = storage.itinerary_from_saved_trip(retrieved)
print(f"   Reconstructed trip from DB: {reconstructed.title}")

print("6. Testing Offline PDF Generation...")
pdf_bytes = generate_itinerary_pdf(itin, "INR")
print(f"   Generated offline PDF successfully: {len(pdf_bytes)} bytes.")

print("\n🎉 ALL TESTS PASSED WITH 100% SUCCESS!")
