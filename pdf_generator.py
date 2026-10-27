"""
Production-grade Offline PDF Itinerary Guide Generator using ReportLab.
Skill Wallet Capstone Project 4.
"""

import io
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from models import Itinerary
from config import EMERGENCY_DATA, OFFLINE_EMERGENCY_CHECKLIST, CURRENCIES
from budget_tracker import format_currency


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and display 'Page X of Y'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Footer text
        footer_text = f"Personalized Travel Itinerary Planner • Capstone Project 4 • Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 36, 25, footer_text)

        # Bottom rule
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 38, A4[0] - 36, 38)
        self.restoreState()


def generate_itinerary_pdf(itinerary: Itinerary, currency: str = "USD") -> bytes:
    """
    Generate a complete, styled offline PDF travel guide.
    Returns: PDF content bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=46,
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E293B"),
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#E05A47"),
        spaceBefore=10,
        spaceAfter=4,
    )

    day_heading = ParagraphStyle(
        "DayHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
    )

    bold_body = ParagraphStyle(
        "BoldBodyDark",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B"),
    )

    tip_style = ParagraphStyle(
        "TipText",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0369A1"),
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph(itinerary.title, title_style))
    meta_line = (
        f"<b>Destination:</b> {itinerary.destination}, {itinerary.country} &nbsp;|&nbsp; "
        f"<b>Dates:</b> {itinerary.preferences.start_date} to {itinerary.preferences.end_date} ({itinerary.preferences.duration_days} Days) &nbsp;|&nbsp; "
        f"<b>Pace:</b> {itinerary.preferences.pace} &nbsp;|&nbsp; <b>Party:</b> {itinerary.preferences.travel_party}"
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph(meta_line, subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#E05A47"), spaceBefore=2, spaceAfter=8))

    # 2. Executive Summary & Budget Overview Table
    story.append(Paragraph("TRIP SNAPSHOT & ESTIMATED BUDGET", section_heading))

    total_cost_formatted = format_currency(itinerary.total_cost_usd, currency)
    daily_avg_formatted = format_currency(itinerary.total_cost_usd / max(1, len(itinerary.days)), currency)

    summary_data = [
        [
            Paragraph("<b>Target Tier</b>", bold_body),
            Paragraph(itinerary.preferences.budget_level, body_style),
            Paragraph("<b>Total Projected Spend</b>", bold_body),
            Paragraph(f"<b>{total_cost_formatted}</b> (${itinerary.total_cost_usd:.2f} USD)", bold_body),
        ],
        [
            Paragraph("<b>Travel Mood</b>", bold_body),
            Paragraph(itinerary.preferences.vibe, body_style),
            Paragraph("<b>Average Daily Spend</b>", bold_body),
            Paragraph(daily_avg_formatted, body_style),
        ],
        [
            Paragraph("<b>Dietary Focus</b>", bold_body),
            Paragraph(itinerary.preferences.dietary, body_style),
            Paragraph("<b>Key Interests</b>", bold_body),
            Paragraph(", ".join(itinerary.preferences.interests[:3]), body_style),
        ],
    ]

    summary_table = Table(summary_data, colWidths=[110, 150, 120, 140])
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 10))

    # 3. Destination Emergency Checklist
    country_key = itinerary.country if itinerary.country in EMERGENCY_DATA else "Default"
    emergency_info = EMERGENCY_DATA.get(country_key, EMERGENCY_DATA["Default"])

    story.append(Paragraph("OFFLINE EMERGENCY CONTACTS & SAFETY CHECKLIST", section_heading))

    emerg_rows = [
        [
            Paragraph("<b>Police:</b> " + emergency_info["police"], bold_body),
            Paragraph("<b>Ambulance:</b> " + emergency_info["ambulance"], bold_body),
            Paragraph("<b>Fire:</b> " + emergency_info["fire"], bold_body),
            Paragraph("<b>General Emergency:</b> " + emergency_info["general"], bold_body),
        ],
        [
            Paragraph("<b>Embassy / Diplomatic Line:</b> " + emergency_info["embassy_info"], body_style),
            "",
            "",
            "",
        ],
    ]

    emerg_table = Table(emerg_rows, colWidths=[125, 125, 125, 145])
    emerg_table.setStyle(
        TableStyle([
            ("SPAN", (0, 1), (3, 1)),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#F87171")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FECACA")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(emerg_table)
    story.append(Spacer(1, 6))

    # Checklist bullet points in 2 columns
    chk_items = OFFLINE_EMERGENCY_CHECKLIST[:6]
    chk_half = len(chk_items) // 2
    chk_col1 = "<br/>".join([f"• [ ] {item}" for item in chk_items[:chk_half]])
    chk_col2 = "<br/>".join([f"• [ ] {item}" for item in chk_items[chk_half:]])

    chk_table = Table(
        [[Paragraph(chk_col1, body_style), Paragraph(chk_col2, body_style)]],
        colWidths=[260, 260],
    )
    chk_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(chk_table)
    story.append(Spacer(1, 14))

    # 4. Day-by-Day Optimized Itinerary Plan
    story.append(Paragraph("DAY-BY-DAY GEOGRAPHICALLY CLUSTERED ITINERARY", section_heading))

    for day in itinerary.days:
        day_elements = []

        day_title = f"<b>Day {day.day_number}:</b> {day.theme} &nbsp;[<i>Cluster: {day.cluster_neighborhood} • Fatigue: {day.transit_fatigue_score}</i>]"
        day_elements.append(Paragraph(day_title, day_heading))
        if day.daily_transit_overview:
            day_elements.append(Paragraph(f"Transit: {day.daily_transit_overview}", subtitle_style))
        day_elements.append(Spacer(1, 4))

        # Build table for 4 slots
        slot_rows = [
            [
                Paragraph("<b>Time / Slot</b>", bold_body),
                Paragraph("<b>Activity & Neighborhood</b>", bold_body),
                Paragraph("<b>Experience, Transit & Tip</b>", bold_body),
                Paragraph("<b>Cost</b>", bold_body),
            ]
        ]

        for slot in day.get_all_slots():
            cost_str = format_currency(slot.estimated_cost_usd, currency)
            desc_text = slot.description
            if slot.transit_from_previous:
                desc_text += f"<br/><font color='#D97706'>Transit: {slot.transit_from_previous}</font>"
            if slot.dietary_options:
                desc_text += f"<br/><font color='#059669'>Dietary: {slot.dietary_options}</font>"
            if slot.insider_tip:
                desc_text += f"<br/><font color='#0284C7'>Tip: {slot.insider_tip}</font>"

            slot_badge = slot.slot_type
            if slot.customized:
                slot_badge += " (Customized)"

            slot_rows.append([
                Paragraph(f"<b>{slot.time}</b><br/>{slot_badge}", body_style),
                Paragraph(f"<b>{slot.title}</b><br/><font color='#64748B'>{slot.neighborhood}</font>", body_style),
                Paragraph(desc_text, body_style),
                Paragraph(f"<b>{cost_str}</b>", bold_body),
            ])

        day_table = Table(slot_rows, colWidths=[90, 130, 240, 60])
        day_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        day_elements.append(day_table)
        day_elements.append(Spacer(1, 10))

        story.append(KeepTogether(day_elements))

    # Build the document with dynamic numbered canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
