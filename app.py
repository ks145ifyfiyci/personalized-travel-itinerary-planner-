"""
Personalized Travel Itinerary Planner (Skill Wallet Capstone Project 4)
Production-Ready Full-Stack Travel SaaS Architecture in Streamlit.
"""

import os
import json
from datetime import datetime, date, timedelta
import streamlit as st
from streamlit_folium import st_folium

# Internal Modules
from config import (
    APP_NAME,
    APP_SUBTITLE,
    PROJECT_BADGE,
    CURRENCIES,
    BUDGET_LEVELS,
    TRAVEL_VIBES,
    TRAVEL_PARTIES,
    TRAVEL_PACES,
    INTEREST_OPTIONS,
    DIETARY_PREFERENCES,
    TIME_SLOTS,
)
from models import TripPreferences, Itinerary, DayPlan, ActivitySlot
from ai_service import AIService
import mock_data
from clustering import create_folium_itinerary_map, evaluate_transit_efficiency
from budget_tracker import (
    calculate_budget_analytics,
    create_cumulative_budget_chart,
    create_category_pie_chart,
    format_currency,
)
from pdf_generator import generate_itinerary_pdf
import storage


# Page Configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "static", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()


# Session State Initialization
if "preferences" not in st.session_state:
    st.session_state.preferences = TripPreferences(
        destination="Paris",
        vibe="Cultural & Heritage Discovery 🏛️",
        duration_days=3,
        start_date=date.today().strftime("%Y-%m-%d"),
        end_date=(date.today() + timedelta(days=3)).strftime("%Y-%m-%d"),
        budget_level="Moderate",
        currency="USD",
        travel_party="Couple",
        pace="Moderate",
        interests=["Art, Museums & Architecture", "Food & Culinary Gems", "History & Ancient Heritage"],
        dietary="No Restrictions",
    )

if "current_itinerary" not in st.session_state:
    # Pre-load an initial sample itinerary so the user immediately sees a populated UI
    st.session_state.current_itinerary = mock_data.generate_mock_itinerary(st.session_state.preferences)

if "recommendations" not in st.session_state:
    st.session_state.recommendations = mock_data.get_mock_recommendations("Cultural & Heritage Discovery 🏛️", "Moderate")

if "api_provider" not in st.session_state:
    st.session_state.api_provider = "demo"

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "status_message" not in st.session_state:
    st.session_state.status_message = "Ready. Demo mode loaded with sample 3-day Paris itinerary."


# Helper to instantiate AIService
def get_ai_service() -> AIService:
    provider = st.session_state.api_provider
    api_key = st.session_state.api_key.strip()
    return AIService(provider=provider, api_key=api_key)


# ==========================================
# SIDEBAR: CONFIGURATION & USER PREFERENCES (Epic 3)
# ==========================================
with st.sidebar:
    st.markdown(f"<span class='hero-badge'>{PROJECT_BADGE}</span>", unsafe_allow_html=True)
    st.title("⚙️ Travel Engine")

    st.markdown("### 1. Engine & AI Configuration")
    provider_choice = st.selectbox(
        "AI Engine Mode",
        options=["Demo Mode (Zero Setup / Instant)", "Google Gemini", "Groq (Llama-3)"],
        index=0 if st.session_state.api_provider == "demo" else (1 if st.session_state.api_provider == "gemini" else 2),
        help="Select Demo Mode to test without any API keys, or connect your Gemini / Groq key.",
    )

    if "Demo" in provider_choice:
        st.session_state.api_provider = "demo"
        st.success("🟢 Demo Mode Active: High-fidelity realistic generator enabled.")
    elif "Gemini" in provider_choice:
        st.session_state.api_provider = "gemini"
        key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.api_key if st.session_state.api_provider == "gemini" else os.getenv("GEMINI_API_KEY", ""),
            placeholder="AIzaSy...",
            help="Your API key remains local in your browser session.",
        )
        st.session_state.api_key = key_input
        if key_input:
            st.success("🟢 Gemini Key Connected")
        else:
            st.warning("⚠️ Enter key above or switch to Demo Mode.")
    else:
        st.session_state.api_provider = "groq"
        key_input = st.text_input(
            "Groq API Key",
            type="password",
            value=st.session_state.api_key if st.session_state.api_provider == "groq" else os.getenv("GROQ_API_KEY", ""),
            placeholder="gsk_...",
            help="Groq API key for ultra-fast Llama-3.3 inference.",
        )
        st.session_state.api_key = key_input
        if key_input:
            st.success("🟢 Groq Key Connected")
        else:
            st.warning("⚠️ Enter key above or switch to Demo Mode.")

    st.markdown("---")
    st.markdown("### 2. Base Currency & Pricing")
    currency_keys = list(CURRENCIES.keys())
    selected_currency = st.selectbox(
        "Display Currency",
        options=currency_keys,
        index=currency_keys.index(st.session_state.preferences.currency) if st.session_state.preferences.currency in currency_keys else 0,
        format_func=lambda c: f"{c} ({CURRENCIES[c]['symbol']}) - {CURRENCIES[c]['name']}",
    )
    st.session_state.preferences.currency = selected_currency

    st.markdown("---")
    st.markdown("### 3. Trip Preferences Form")

    dest_input = st.text_input(
        "Destination City / Region",
        value=st.session_state.preferences.destination,
        placeholder="e.g. Paris, Tokyo, Bali, Rome, Jaipur, New York",
        help="Leave blank or use Tab 1 if you are looking for mood-based recommendations.",
    )
    st.session_state.preferences.destination = dest_input

    vibe_selection = st.selectbox(
        "Travel Vibe / Mood",
        options=TRAVEL_VIBES,
        index=TRAVEL_VIBES.index(st.session_state.preferences.vibe) if st.session_state.preferences.vibe in TRAVEL_VIBES else 2,
    )
    st.session_state.preferences.vibe = vibe_selection

    duration = st.slider(
        "Trip Duration (Days)",
        min_value=1,
        max_value=10,
        value=st.session_state.preferences.duration_days,
        help="Optimized multi-day plans with zero geographic backtracking.",
    )
    st.session_state.preferences.duration_days = duration

    # Dates
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        s_date = st.date_input("Start Date", value=datetime.strptime(st.session_state.preferences.start_date, "%Y-%m-%d").date())
    with col_d2:
        e_date = st.date_input("End Date", value=s_date + timedelta(days=duration))
    
    st.session_state.preferences.start_date = s_date.strftime("%Y-%m-%d")
    st.session_state.preferences.end_date = e_date.strftime("%Y-%m-%d")

    budget_level = st.select_slider(
        "Budget Tier",
        options=list(BUDGET_LEVELS.keys()),
        value=st.session_state.preferences.budget_level,
        format_func=lambda b: f"{BUDGET_LEVELS[b]['icon']} {b}",
    )
    st.session_state.preferences.budget_level = budget_level
    st.caption(f"{BUDGET_LEVELS[budget_level]['description']} (~${BUDGET_LEVELS[budget_level]['daily_target_usd']}/day target)")

    party = st.selectbox(
        "Travel Party",
        options=[p["value"] for p in TRAVEL_PARTIES],
        format_func=lambda x: next(p["label"] for p in TRAVEL_PARTIES if p["value"] == x),
        index=[p["value"] for p in TRAVEL_PARTIES].index(st.session_state.preferences.travel_party),
    )
    st.session_state.preferences.travel_party = party

    pace = st.selectbox(
        "Travel Pace",
        options=[p["value"] for p in TRAVEL_PACES],
        format_func=lambda x: next(p["label"] for p in TRAVEL_PACES if p["value"] == x),
        index=[p["value"] for p in TRAVEL_PACES].index(st.session_state.preferences.pace),
    )
    st.session_state.preferences.pace = pace

    interests = st.multiselect(
        "Core Interests & Themes",
        options=INTEREST_OPTIONS,
        default=st.session_state.preferences.interests,
    )
    st.session_state.preferences.interests = interests

    dietary = st.selectbox(
        "Dietary Preference",
        options=DIETARY_PREFERENCES,
        index=DIETARY_PREFERENCES.index(st.session_state.preferences.dietary) if st.session_state.preferences.dietary in DIETARY_PREFERENCES else 0,
    )
    st.session_state.preferences.dietary = dietary

    notes = st.text_input(
        "Accessibility & Special Notes",
        value=st.session_state.preferences.accessibility_notes or "",
        placeholder="e.g. wheelchair accessible, stroller-friendly, senior-friendly",
    )
    st.session_state.preferences.accessibility_notes = notes

    st.markdown("---")
    generate_btn = st.button("🚀 Generate Optimized Itinerary", type="primary", use_container_width=True)


# ==========================================
# MAIN APPLICATION INTERFACE
# ==========================================

# Hero Banner
st.markdown(
    f"""
    <div class="hero-header">
        <span class="hero-badge">{PROJECT_BADGE}</span>
        <h1 class="hero-title">{APP_NAME}</h1>
        <p class="hero-subtitle">{APP_SUBTITLE}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Notification banner
if st.session_state.status_message:
    st.info(f"ℹ️ {st.session_state.status_message}")

# Handle primary generation button
if generate_btn:
    with st.spinner(f"Architecting optimized itinerary for {st.session_state.preferences.destination or 'selected destination'}..."):
        ai_svc = get_ai_service()
        # If destination is empty, use the first recommended destination
        if not st.session_state.preferences.destination.strip():
            if st.session_state.recommendations:
                st.session_state.preferences.destination = st.session_state.recommendations[0].city
            else:
                st.session_state.preferences.destination = "Paris"

        itin, status_msg = ai_svc.generate_itinerary(st.session_state.preferences)
        st.session_state.current_itinerary = itin
        st.session_state.status_message = status_msg
        # Auto-save to persistence
        storage.save_itinerary_to_db(itin)
        st.rerun()


# Four Primary Tabs Matching Epics 3, 4, and 5
tab_recommender, tab_itinerary, tab_customization, tab_management = st.tabs([
    "🧭 Tab 1: Smart Destination Recommender",
    "📅 Tab 2: Day-by-Day Optimized Itinerary",
    "⚡ Tab 3: Vibe Customization & Slot Swap",
    "📂 Tab 4: Trip Management & PDF Export",
])


# ==============================================================================
# TAB 1: SMART DESTINATION RECOMMENDER (Epic 3)
# ==============================================================================
with tab_recommender:
    st.subheader("Smart Destination Recommender")
    st.markdown(
        "Discover ideal destinations tailored to your **travel mood, budget tier, and travel party**. "
        "Select any match to instantly load it into the Day-by-Day Itinerary Planner."
    )

    col_rec_ctrl1, col_rec_ctrl2 = st.columns([3, 1])
    with col_rec_ctrl1:
        st.write(f"Current Vibe: **{st.session_state.preferences.vibe}** &nbsp;|&nbsp; Budget Tier: **{st.session_state.preferences.budget_level}** &nbsp;|&nbsp; Party: **{st.session_state.preferences.travel_party}**")
    with col_rec_ctrl2:
        refresh_recs = st.button("🔄 Refresh Recommendations", use_container_width=True)

    if refresh_recs:
        with st.spinner("Analyzing global travel matches..."):
            ai_svc = get_ai_service()
            recs, msg = ai_svc.recommend_destinations(
                vibe=st.session_state.preferences.vibe,
                budget_level=st.session_state.preferences.budget_level,
                duration_days=st.session_state.preferences.duration_days,
                travel_party=st.session_state.preferences.travel_party,
                interests=st.session_state.preferences.interests,
            )
            st.session_state.recommendations = recs
            st.session_state.status_message = msg
            st.rerun()

    # Render top 3 destination cards
    recs = st.session_state.recommendations
    if recs:
        cols = st.columns(len(recs))
        for idx, rec in enumerate(recs):
            with cols[idx]:
                daily_cost_curr = format_currency(rec.estimated_daily_usd, selected_currency)
                tags_html = "".join([f"<span class='vibe-tag'>{tag}</span>" for tag in rec.vibe_tags])
                highlights_html = "".join([f"<li>{h}</li>" for h in rec.highlights])

                st.markdown(
                    f"""
                    <div class="dest-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span class="match-score-pill">🎯 {rec.match_score}% Match</span>
                            <span style="font-weight:700; color:#0F172A; font-size:13px;">~{daily_cost_curr}/day</span>
                        </div>
                        <h3 style="margin:4px 0 2px 0; font-size:20px; color:#0F172A;">{rec.city}, {rec.country}</h3>
                        <div style="color:#64748B; font-size:12px; margin-bottom:8px;">🌤️ {rec.weather_season}</div>
                        <div style="margin-bottom:10px;">{tags_html}</div>
                        <p style="font-size:12.5px; color:#334155; line-height:1.45; margin-bottom:10px;">{rec.why_matched}</p>
                        <div style="font-size:12px; font-weight:700; color:#1E293B; margin-bottom:4px;">Signature Highlights:</div>
                        <ul style="font-size:12px; color:#475569; padding-left:18px; margin-bottom:12px;">{highlights_html}</ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(f"✈️ Select {rec.city} & Build Itinerary", key=f"sel_dest_{idx}", use_container_width=True, type="primary"):
                    st.session_state.preferences.destination = rec.city
                    with st.spinner(f"Generating optimized itinerary for {rec.city}..."):
                        ai_svc = get_ai_service()
                        itin, status_msg = ai_svc.generate_itinerary(st.session_state.preferences)
                        st.session_state.current_itinerary = itin
                        st.session_state.status_message = f"Selected {rec.city}! {status_msg}"
                        storage.save_itinerary_to_db(itin)
                        st.rerun()


# ==============================================================================
# TAB 2: DAY-BY-DAY OPTIMIZED ITINERARY GENERATOR (Epic 4)
# ==============================================================================
with tab_itinerary:
    itin = st.session_state.current_itinerary

    if itin:
        # Calculate budget analytics and metrics
        analytics = calculate_budget_analytics(itin, selected_currency)

        # Header metrics row
        st.markdown(f"## {itin.title}")
        st.caption(f"📍 {itin.destination}, {itin.country} • {itin.preferences.duration_days} Days ({itin.preferences.start_date} to {itin.preferences.end_date}) • Pace: {itin.preferences.pace}")

        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        with m_col1:
            st.metric("Total Duration", f"{len(itin.days)} Days", delta=f"{itin.preferences.travel_party}")
        with m_col2:
            st.metric("Projected Spend", format_currency(analytics["total_spend_usd"], selected_currency), delta=f"${analytics['total_spend_usd']:.0f} USD")
        with m_col3:
            st.metric("Average Daily Spend", format_currency(analytics["total_spend_usd"] / max(1, len(itin.days)), selected_currency))
        with m_col4:
            st.metric("Benchmark Target", format_currency(analytics["target_budget_usd"], selected_currency), delta=analytics["budget_health"], delta_color="normal" if analytics["variance_usd"] >= 0 else "inverse")
        with m_col5:
            st.metric("Geographic Clustering", "Zero Backtracking", delta="Low Fatigue Score")

        st.markdown("---")

        # Interactive Geographic Route Map Section
        st.subheader("🗺️ Geographic Clustering & Route Visualization")
        st.markdown(
            "Every day is concentrated within a dedicated district to **minimize travel transit fatigue**. "
            "Lines connect the daily sequential slots: Morning ➡️ Lunch ➡️ Afternoon ➡️ Evening."
        )

        map_filter_col1, map_filter_col2 = st.columns([3, 1])
        with map_filter_col2:
            day_filter_opts = ["All Days Combined"] + [f"Day {d.day_number}: {d.cluster_neighborhood}" for d in itin.days]
            selected_map_day_str = st.selectbox("Filter Map View", options=day_filter_opts)
            selected_day_num = None if "All" in selected_map_day_str else int(selected_map_day_str.split(":")[0].replace("Day", "").strip())

        with map_filter_col1:
            # Render Folium Leaflet Map
            folium_map = create_folium_itinerary_map(itin, selected_day=selected_day_num)
            st_folium(folium_map, width="100%", height=380, returned_objects=[])

        st.markdown("---")

        # Day-by-Day Sequential Slots Accordion
        st.subheader("📅 Structured Day-wise Plans")

        for day in itin.days:
            transit_eval = evaluate_transit_efficiency(day)
            fatigue_badge_html = f"<span class='fatigue-pill' style='background:{transit_eval['badge_color']}20; color:{transit_eval['badge_color']}; border:1px solid {transit_eval['badge_color']}60;'>Transit: {transit_eval['fatigue_score']} Fatigue ({transit_eval['total_distance_km']} km)</span>"
            day_cost_str = format_currency(day.get_daily_cost_usd(), selected_currency)

            expander_title = f"Day {day.day_number}: {day.theme} • 📍 {day.cluster_neighborhood} ({day_cost_str})"

            with st.expander(expander_title, expanded=(day.day_number == 1)):
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <div>
                            <span style="font-weight:700; color:#1E293B; font-size:14px;">District Cluster: {day.cluster_neighborhood}</span>
                            <div style="font-size:12px; color:#64748B;">{day.daily_transit_overview}</div>
                        </div>
                        <div>{fatigue_badge_html}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Render the 4 sequential time slots
                slots = [
                    ("morning", day.morning, "Morning Sightseeing", "09:00 - 12:30", "morning"),
                    ("lunch", day.lunch, "Lunch Recommendation", "12:30 - 14:00", "lunch"),
                    ("afternoon", day.afternoon, "Afternoon Leisure & Culture", "14:30 - 17:30", "afternoon"),
                    ("evening", day.evening, "Evening Dining & Entertainment", "18:30 - 22:00", "evening"),
                ]

                for slot_id, slot, default_type, default_time, style_class in slots:
                    cost_str = format_currency(slot.estimated_cost_usd, selected_currency)
                    customized_class = "customized-glow" if slot.customized else ""
                    custom_tag = "⚡ Customized Slot &nbsp;|&nbsp; " if slot.customized else ""

                    footer_items = []
                    if slot.transit_from_previous:
                        footer_items.append(f"<span class='tag-transit'>🚶 {slot.transit_from_previous}</span>")
                    if slot.dietary_options:
                        footer_items.append(f"<span class='tag-dietary'>🥗 {slot.dietary_options}</span>")
                    if slot.insider_tip:
                        footer_items.append(f"<span class='tag-tip'>💡 Tip: {slot.insider_tip}</span>")

                    footer_html = f"<div class='slot-footer'>{''.join(footer_items)}</div>" if footer_items else ""

                    st.markdown(
                        f"""
                        <div class="slot-card {style_class} {customized_class}">
                            <div class="slot-header">
                                <span class="slot-badge {style_class}">{slot.slot_type} ({slot.time})</span>
                                <span class="cost-pill">{custom_tag}Est. {cost_str} (${slot.estimated_cost_usd:.1f} USD)</span>
                            </div>
                            <div class="slot-title">{slot.title}</div>
                            <div class="slot-neighborhood">📍 {slot.neighborhood} &nbsp;•&nbsp; <span style="color:#64748B;">{slot.category}</span></div>
                            <div class="slot-desc">{slot.description}</div>
                            {footer_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("---")

        # Running Cumulative Budget Tracker Section
        st.subheader("💰 Running Cumulative Budget Tracker & Financials")
        st.markdown(
            f"Monitoring itemized spend against standard **{itin.preferences.budget_level}** benchmarks. "
            f"Status: **<font color='{analytics['health_color']}'>{analytics['budget_health']}</font>** ({analytics['variance_msg']})"
        )

        b_col1, b_col2 = st.columns([3, 2])
        with b_col1:
            fig_bar = create_cumulative_budget_chart(analytics["df_daily"], selected_currency)
            st.plotly_chart(fig_bar, use_container_width=True)

        with b_col2:
            fig_pie = create_category_pie_chart(analytics["category_totals_usd"], selected_currency)
            st.plotly_chart(fig_pie, use_container_width=True)

        with st.expander("📊 View Itemized Daily Financial Ledger", expanded=False):
            st.dataframe(analytics["df_daily"], use_container_width=True, hide_index=True)

    else:
        st.info("No itinerary generated yet. Configure preferences in the sidebar and click 'Generate Optimized Itinerary'.")


# ==============================================================================
# TAB 3: VIBE CUSTOMIZATION & DYNAMIC ACTIVITY SWAP (Epic 4)
# ==============================================================================
with tab_customization:
    st.subheader("⚡ Vibe Customization & Dynamic Activity Swap")
    st.markdown(
        "Need a change of vibe? **Swap or regenerate single slots** without wiping the rest of the plan. "
        "The AI respects the day's neighborhood cluster to preserve zero-fatigue geographic routing."
    )

    itin = st.session_state.current_itinerary
    if itin and itin.days:
        day_options = {f"Day {d.day_number}: {d.theme} ({d.cluster_neighborhood})": d.day_number for d in itin.days}
        selected_day_label = st.selectbox("1. Select Day to Modify", options=list(day_options.keys()))
        target_day_num = day_options[selected_day_label]
        target_day = next(d for d in itin.days if d.day_number == target_day_num)

        slot_options = {
            "Morning Sightseeing (09:00 - 12:30)": "morning",
            "Lunch Recommendation (12:30 - 14:00)": "lunch",
            "Afternoon Leisure & Culture (14:30 - 17:30)": "afternoon",
            "Evening Dining & Entertainment (18:30 - 22:00)": "evening",
        }
        selected_slot_label = st.selectbox("2. Select Time Slot to Modify", options=list(slot_options.keys()))
        target_slot_id = slot_options[selected_slot_label]
        current_slot: ActivitySlot = getattr(target_day, target_slot_id)

        # Show Current Slot Snapshot
        st.markdown(
            f"""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:10px; padding:14px; margin:12px 0;">
                <div style="font-weight:700; color:#475569; font-size:12px; text-transform:uppercase;">Current Activity In This Slot:</div>
                <div style="font-size:16px; font-weight:700; color:#0F172A; margin:4px 0;">{current_slot.title}</div>
                <div style="font-size:13px; color:#334155;">{current_slot.description}</div>
                <div style="font-size:12px; color:#64748B; margin-top:6px;">📍 {current_slot.neighborhood} • Est. Cost: {format_currency(current_slot.estimated_cost_usd, selected_currency)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 3. Choose Customization Direction")
        swap_mode = st.radio(
            "Customization Method",
            options=["Quick Preset Vibe Swaps", "Custom Tailored Request"],
            horizontal=True,
        )

        if swap_mode == "Quick Preset Vibe Swaps":
            preset_options = [
                "Swap for Outdoor Market & Scenic Public Park",
                "Find Authentic Vegetarian / Vegan Dining Gem",
                "Switch to High-Adrenaline Adventure / Outdoor Thrill",
                "Change to Free / Budget-Friendly Hidden Gem",
                "Romantic Sunset Overlook & Wine Bar",
                "Kid & Family-Friendly Interactive Activity",
                "Artisan Coffee & Indie Bookshop Haven",
            ]
            customization_text = st.selectbox("Select Preset Transformation", options=preset_options)
        else:
            customization_text = st.text_area(
                "Enter Your Custom Request",
                placeholder="e.g. 'Swap lunch for a rooftop cafe with view of the river and plant-based options' or 'Change afternoon to contemporary sculpture gallery'",
            )

        if st.button("⚡ Swap This Slot Now", type="primary"):
            if not customization_text.strip():
                st.warning("Please enter or select a customization request.")
            else:
                with st.spinner(f"Swapping {current_slot.slot_type} on Day {target_day_num}..."):
                    ai_svc = get_ai_service()
                    updated_slot, swap_msg = ai_svc.customize_slot(
                        day_plan=target_day,
                        slot_id=target_slot_id,
                        customization_prompt=customization_text,
                        prefs=itin.preferences,
                    )
                    # Update in place
                    setattr(target_day, target_slot_id, updated_slot)
                    itin.calculate_total_cost()
                    st.session_state.current_itinerary = itin
                    storage.save_itinerary_to_db(itin)
                    st.session_state.status_message = swap_msg
                    st.success(f"Slot swapped successfully! {swap_msg}")
                    st.rerun()

    else:
        st.info("Please generate an itinerary first in Tab 2 to use the dynamic slot customizer.")


# ==============================================================================
# TAB 4: TRIP MANAGEMENT & OFFLINE PDF EXPORT (Epic 5)
# ==============================================================================
with tab_management:
    st.subheader("📂 Trip Management & Offline PDF Export")
    st.markdown(
        "Persist multiple trip plans in the zero-dependency local database, browse trip history, "
        "and generate a **publication-ready offline PDF travel guide** with emergency contact checklists."
    )

    pdf_col, db_col = st.columns([1, 1])

    # 1. 1-Click PDF Export
    with pdf_col:
        st.markdown("### 📥 1-Click Offline PDF Travel Guide")
        st.markdown(
            "Export a beautifully formatted, print-ready PDF containing:\n"
            "- Complete day-by-day sequential itineraries with times & costs\n"
            "- Geographic cluster notes and transit fatigue recommendations\n"
            "- **Destination-specific emergency hotline directory** (Police, Ambulance, Fire, Embassies)\n"
            "- Offline travel survival & medical safety checklist\n"
            "- Itemized budget ledger and currency conversions"
        )

        current_itin = st.session_state.current_itinerary
        if current_itin:
            with st.spinner("Compiling publication-ready PDF..."):
                pdf_data = generate_itinerary_pdf(current_itin, selected_currency)

            filename = f"{current_itin.destination.replace(' ', '_')}_{current_itin.preferences.duration_days}Day_Itinerary.pdf"
            st.download_button(
                label=f"📄 Download Offline PDF Guide ({current_itin.destination})",
                data=pdf_data,
                file_name=filename,
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
            st.caption("✨ Pure Python PDF generation via ReportLab. Works seamlessly offline.")
        else:
            st.warning("Generate an itinerary first to export a PDF.")

    # 2. Database Persistence & Trip History Viewer
    with db_col:
        st.markdown("### 💾 Saved Trips Persistence")
        if current_itin:
            if st.button("💾 Save Active Trip to Persistence DB", use_container_width=True):
                saved = storage.save_itinerary_to_db(current_itin)
                st.success(f"Saved '{saved.title}' to persistent database!")
                st.rerun()

        # Database export/backup
        all_trips = storage.get_all_trips()
        st.markdown(f"**Trip History ({len(all_trips)} saved trips):**")

        if all_trips:
            for trip in all_trips:
                cost_str = format_currency(trip.total_cost_usd, selected_currency)
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:700; color:#0F172A; font-size:14px;">{trip.title}</span>
                                <span style="font-weight:700; color:#E05A47; font-size:12px;">{cost_str}</span>
                            </div>
                            <div style="font-size:12px; color:#64748B;">📍 {trip.destination}, {trip.country} • {trip.dates} ({trip.duration_days} Days) • {trip.budget_level} Tier</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    t_btn_col1, t_btn_col2 = st.columns([3, 1])
                    with t_btn_col1:
                        if st.button(f"📂 Load Trip", key=f"load_{trip.id}", use_container_width=True):
                            loaded_itin = storage.itinerary_from_saved_trip(trip)
                            st.session_state.current_itinerary = loaded_itin
                            st.session_state.preferences = loaded_itin.preferences
                            st.session_state.status_message = f"Loaded saved trip '{trip.title}'."
                            st.rerun()
                    with t_btn_col2:
                        if st.button("🗑️", key=f"del_{trip.id}", use_container_width=True, help="Delete trip"):
                            storage.delete_trip_by_id(trip.id)
                            st.rerun()
        else:
            st.info("No saved trips in database yet.")


# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center; color:#94A3B8; font-size:12px; padding:12px 0;">
        <b>{APP_NAME}</b> • {PROJECT_BADGE} • Senior Full-Stack Travel SaaS Architecture • Streamlit Community Cloud Ready
    </div>
    """,
    unsafe_allow_html=True,
)
