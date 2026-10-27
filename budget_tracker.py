"""
Budget Tracking and Currency Conversion Engine.
Calculates itemized costs, cumulative spend, category distributions, and budget variances.
Skill Wallet Capstone Project 4.
"""

from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import CURRENCIES, BUDGET_LEVELS
from models import Itinerary, ActivitySlot, DayPlan


def convert_currency(amount_usd: float, target_currency: str = "USD") -> float:
    """Convert amount in USD to selected target currency."""
    currency_meta = CURRENCIES.get(target_currency, CURRENCIES["USD"])
    rate = currency_meta["rate"]
    return round(amount_usd * rate, 2)


def format_currency(amount_usd: float, target_currency: str = "USD") -> str:
    """Format amount in USD into formatted string with currency symbol."""
    currency_meta = CURRENCIES.get(target_currency, CURRENCIES["USD"])
    symbol = currency_meta["symbol"]
    converted = convert_currency(amount_usd, target_currency)
    if target_currency in ["INR", "JPY"]:
        return f"{symbol}{converted:,.0f}"
    return f"{symbol}{converted:,.2f}"


def calculate_budget_analytics(itinerary: Itinerary, target_currency: str = "USD") -> Dict[str, Any]:
    """
    Generate comprehensive budget breakdown: daily itemized table, cumulative tracking,
    category splits, and benchmark variance.
    """
    days_data = []
    category_totals_usd: Dict[str, float] = {
        "Sightseeing": 0.0,
        "Food": 0.0,
        "Culture": 0.0,
        "Entertainment": 0.0,
        "Other": 0.0,
    }

    cumulative_usd = 0.0

    for day in itinerary.days:
        day_total_usd = 0.0
        slots = day.get_all_slots()

        morning_cost = slots[0].estimated_cost_usd
        lunch_cost = slots[1].estimated_cost_usd
        afternoon_cost = slots[2].estimated_cost_usd
        evening_cost = slots[3].estimated_cost_usd

        for slot in slots:
            cost = slot.estimated_cost_usd
            day_total_usd += cost
            cat = slot.category if slot.category in category_totals_usd else "Other"
            category_totals_usd[cat] += cost

        cumulative_usd += day_total_usd

        days_data.append({
            "Day": f"Day {day.day_number}",
            "Neighborhood": day.cluster_neighborhood,
            "Morning (USD)": morning_cost,
            "Lunch (USD)": lunch_cost,
            "Afternoon (USD)": afternoon_cost,
            "Evening (USD)": evening_cost,
            "Daily Total (USD)": round(day_total_usd, 2),
            "Cumulative (USD)": round(cumulative_usd, 2),
            f"Daily Total ({target_currency})": convert_currency(day_total_usd, target_currency),
            f"Cumulative ({target_currency})": convert_currency(cumulative_usd, target_currency),
        })

    total_spend_usd = round(cumulative_usd, 2)

    # Benchmark calculation
    budget_level = itinerary.preferences.budget_level
    bench_daily = BUDGET_LEVELS.get(budget_level, BUDGET_LEVELS["Moderate"])["daily_target_usd"]
    target_budget_usd = round(bench_daily * len(itinerary.days), 2)
    variance_usd = round(target_budget_usd - total_spend_usd, 2)

    if variance_usd >= 0:
        budget_health = "Under Budget"
        health_color = "#10B981"
        variance_msg = f"{format_currency(abs(variance_usd), target_currency)} under expected {budget_level} benchmark."
    elif abs(variance_usd) <= (target_budget_usd * 0.1):
        budget_health = "On Track"
        health_color = "#3B82F6"
        variance_msg = f"Within 10% tolerance of {budget_level} benchmark."
    else:
        budget_health = "Over Benchmark"
        health_color = "#EF4444"
        variance_msg = f"{format_currency(abs(variance_usd), target_currency)} above standard {budget_level} benchmark."

    return {
        "df_daily": pd.DataFrame(days_data),
        "total_spend_usd": total_spend_usd,
        "total_spend_target": convert_currency(total_spend_usd, target_currency),
        "target_budget_usd": target_budget_usd,
        "target_budget_target": convert_currency(target_budget_usd, target_currency),
        "variance_usd": variance_usd,
        "budget_health": budget_health,
        "health_color": health_color,
        "variance_msg": variance_msg,
        "category_totals_usd": category_totals_usd,
    }


def create_cumulative_budget_chart(df_daily: pd.DataFrame, target_currency: str = "USD") -> go.Figure:
    """Create a dual-axis chart: daily spend bar chart + cumulative progression line."""
    daily_col = f"Daily Total ({target_currency})"
    cum_col = f"Cumulative ({target_currency})"

    fig = go.Figure()

    # Daily Bar Chart
    fig.add_trace(
        go.Bar(
            x=df_daily["Day"],
            y=df_daily[daily_col],
            name="Daily Total",
            marker_color="#E05A47",
            opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Daily Spend: %{y}<extra></extra>",
        )
    )

    # Cumulative Line Chart
    fig.add_trace(
        go.Scatter(
            x=df_daily["Day"],
            y=df_daily[cum_col],
            name="Cumulative Spend",
            mode="lines+markers",
            line=dict(color="#1E293B", width=3),
            marker=dict(size=8, color="#1E293B"),
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Running Total: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        title=f"Daily Spend & Cumulative Budget Progression ({target_currency})",
        xaxis=dict(title="Trip Day"),
        yaxis=dict(title=f"Daily Spend ({target_currency})"),
        yaxis2=dict(
            title=f"Cumulative Spend ({target_currency})",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=50, b=40),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=320,
    )
    return fig


def create_category_pie_chart(category_totals_usd: Dict[str, float], target_currency: str = "USD") -> go.Figure:
    """Create category distribution donut chart."""
    categories = list(category_totals_usd.keys())
    values = [convert_currency(v, target_currency) for v in category_totals_usd.values()]

    colors = ["#E05A47", "#F59E0B", "#3B82F6", "#8B5CF6", "#10B981"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=values,
                hole=0.45,
                marker=dict(colors=colors),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Amount: %{value}<br>%{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=f"Spending Allocation by Category ({target_currency})",
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=320,
        showlegend=False,
    )
    return fig
