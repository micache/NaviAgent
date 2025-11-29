"""
PDF formatter for guidebook generation.

This module generates professional PDF guidebooks using ReportLab,
with support for table of contents, page numbers, headers/footers,
and professional typography.
"""

import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from travel_planner.guidebook.formatters.base import BaseFormatter
from travel_planner.guidebook.utils.formatting_helpers import (
    format_currency,
    format_date,
    get_activity_icon,
    sanitize_text,
)

logger = logging.getLogger(__name__)


class PDFFormatter(BaseFormatter):
    """
    Formatter for generating professional PDF guidebooks.

    Uses ReportLab to create high-quality PDF documents with:
    - Table of contents with page numbers
    - Headers and footers
    - Professional typography
    - Color-coded sections
    - Print-friendly A4 format
    - Bookmarks for navigation
    """

    # Color scheme
    PRIMARY_COLOR = colors.HexColor("#2563eb")
    SECONDARY_COLOR = colors.HexColor("#64748b")
    ACCENT_COLOR = colors.HexColor("#f59e0b")
    SUCCESS_COLOR = colors.HexColor("#10b981")
    BACKGROUND_COLOR = colors.HexColor("#f8fafc")
    TEXT_COLOR = colors.HexColor("#1e293b")
    BORDER_COLOR = colors.HexColor("#e2e8f0")

    def __init__(
        self,
        travel_plan: Dict[str, Any],
        output_dir: str = "guidebooks",
        language: str = "vi",
    ):
        """
        Initialize the PDF formatter.

        Args:
            travel_plan: Dictionary containing travel plan data.
            output_dir: Directory to save output files.
            language: Language for content (vi or en).
        """
        super().__init__(travel_plan, output_dir, language)
        self._setup_styles()

    def get_default_filename(self) -> str:
        """Get the default filename for PDF output."""
        destination_slug = (
            self.destination.lower().replace(" ", "_").replace(",", "")[:30]
            if self.destination
            else "travel"
        )
        return f"guidebook_{destination_slug}.pdf"

    def _setup_styles(self) -> None:
        """Setup paragraph and table styles."""
        self.styles = getSampleStyleSheet()

        # Custom styles - using unique names to avoid conflicts
        self.styles.add(
            ParagraphStyle(
                "CoverTitle",
                parent=self.styles["Heading1"],
                fontSize=28,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=12,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "CoverSubtitle",
                parent=self.styles["Normal"],
                fontSize=18,
                textColor=colors.white,
                alignment=TA_CENTER,
                spaceAfter=30,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "SectionTitle",
                parent=self.styles["Heading1"],
                fontSize=16,
                textColor=self.PRIMARY_COLOR,
                spaceBefore=20,
                spaceAfter=12,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "SubsectionTitle",
                parent=self.styles["Heading2"],
                fontSize=13,
                textColor=self.TEXT_COLOR,
                spaceBefore=15,
                spaceAfter=8,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "GuidebookBody",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=self.TEXT_COLOR,
                leading=14,
                spaceAfter=8,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "SmallText",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=self.SECONDARY_COLOR,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "TipText",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=self.ACCENT_COLOR,
                leftIndent=15,
            )
        )

        self.styles.add(
            ParagraphStyle(
                "TOCEntry",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=self.TEXT_COLOR,
                spaceAfter=8,
            )
        )

    def generate(self, output_path: Optional[str] = None) -> str:
        """
        Generate the PDF guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated file.
        """
        logger.info("Generating PDF guidebook...")

        output_file = self.get_output_path(output_path)
        labels = self.get_labels()

        # Create document
        doc = BaseDocTemplate(
            str(output_file),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2 * cm,
        )

        # Setup page templates
        self._setup_page_templates(doc)

        # Build story (content)
        story = self._build_story(labels)

        # Build PDF
        doc.build(story)

        logger.info(f"PDF guidebook generated: {output_file}")
        return str(output_file)

    def _setup_page_templates(self, doc: BaseDocTemplate) -> None:
        """Setup page templates with headers and footers."""
        page_width, page_height = A4

        # Frame for content
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            page_width - doc.leftMargin - doc.rightMargin,
            page_height - doc.topMargin - doc.bottomMargin,
            id="normal",
        )

        # Cover page template (no header/footer)
        cover_template = PageTemplate(
            id="cover",
            frames=[frame],
            onPage=self._cover_page_callback,
        )

        # Normal page template with header/footer
        normal_template = PageTemplate(
            id="normal",
            frames=[frame],
            onPage=self._normal_page_callback,
        )

        doc.addPageTemplates([cover_template, normal_template])

    def _cover_page_callback(self, canvas, doc) -> None:
        """Callback for cover page (no header/footer)."""
        pass

    def _normal_page_callback(self, canvas, doc) -> None:
        """Callback to add header and footer to normal pages."""
        canvas.saveState()

        page_width, page_height = A4

        # Header
        canvas.setStrokeColor(self.PRIMARY_COLOR)
        canvas.setLineWidth(1)
        canvas.line(2 * cm, page_height - 1.5 * cm, page_width - 2 * cm, page_height - 1.5 * cm)

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(self.SECONDARY_COLOR)
        canvas.drawString(2 * cm, page_height - 1.3 * cm, f"{self.destination}")

        # Footer
        canvas.line(2 * cm, 1.5 * cm, page_width - 2 * cm, 1.5 * cm)
        canvas.drawString(2 * cm, 1 * cm, "NaviAgent Travel Guidebook")
        canvas.drawRightString(page_width - 2 * cm, 1 * cm, f"Page {doc.page}")

        canvas.restoreState()

    def _build_story(self, labels: Dict[str, str]) -> List:
        """Build the document story (content)."""
        story = []

        # Cover page
        story.extend(self._build_cover_page(labels))
        story.append(NextPageTemplate("normal"))
        story.append(PageBreak())

        # Table of contents
        story.extend(self._build_toc(labels))
        story.append(PageBreak())

        # Executive summary
        story.extend(self._build_summary_section(labels))
        story.append(PageBreak())

        # Itinerary
        if self.itinerary:
            story.extend(self._build_itinerary_section(labels))
            story.append(PageBreak())

        # Flights
        if self.logistics:
            story.extend(self._build_flights_section(labels))
            story.append(PageBreak())

        # Accommodation
        if self.accommodation:
            story.extend(self._build_accommodation_section(labels))
            story.append(PageBreak())

        # Budget
        if self.budget:
            story.extend(self._build_budget_section(labels))
            story.append(PageBreak())

        # Advisory
        if self.advisory:
            story.extend(self._build_advisory_section(labels))
            story.append(PageBreak())

        # Souvenirs
        if self.souvenirs:
            story.extend(self._build_souvenirs_section(labels))

        return story

    def _build_cover_page(self, labels: Dict[str, str]) -> List:
        """Build cover page content."""
        story = []

        # Background rectangle for cover
        story.append(Spacer(1, 5 * cm))

        # Title
        story.append(
            Paragraph(f"🗺️ {labels['title']}", self.styles["CoverTitle"]),
        )

        # Destination
        story.append(
            Paragraph(
                sanitize_text(self.destination),
                self.styles["CoverSubtitle"],
            )
        )

        story.append(Spacer(1, 2 * cm))

        # Trip info table
        days_label = "ngày" if self.language == "vi" else "days"
        travelers_label = "người" if self.language == "vi" else "travelers"

        info_data = [
            [labels["duration"], f"{self.trip_duration} {days_label}"],
            [labels["travelers"], f"{self.num_travelers} {travelers_label}"],
            [labels["budget_label"], format_currency(self.budget_amount)],
        ]

        info_table = Table(info_data, colWidths=[6 * cm, 6 * cm])
        info_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("TEXTCOLOR", (0, 0), (0, -1), self.SECONDARY_COLOR),
                    ("TEXTCOLOR", (1, 0), (1, -1), self.TEXT_COLOR),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                ]
            )
        )
        story.append(info_table)

        story.append(Spacer(1, 4 * cm))

        # Generated date
        if self.generated_at:
            story.append(
                Paragraph(
                    f"{labels['generated_at']}: {format_date(self.generated_at[:10])}",
                    self.styles["SmallText"],
                )
            )

        return story

    def _build_toc(self, labels: Dict[str, str]) -> List:
        """Build table of contents."""
        story = []

        story.append(Paragraph(f"📑 {labels['table_of_contents']}", self.styles["SectionTitle"]))
        story.append(Spacer(1, 0.5 * cm))

        toc_items = [
            (f"📊 {labels['executive_summary']}", "3"),
            (f"📅 {labels['itinerary']}", "4"),
            (f"✈️ {labels['flights']}", "-"),
            (f"🏨 {labels['accommodation']}", "-"),
            (f"💰 {labels['budget']}", "-"),
            (f"⚠️ {labels['advisory']}", "-"),
            (f"🎁 {labels['souvenirs']}", "-"),
        ]

        for title, page in toc_items:
            story.append(
                Paragraph(
                    f"{title} {'.' * 50} {page}",
                    self.styles["TOCEntry"],
                )
            )

        return story

    def _build_summary_section(self, labels: Dict[str, str]) -> List:
        """Build executive summary section."""
        story = []

        story.append(Paragraph(f"📊 {labels['executive_summary']}", self.styles["SectionTitle"]))

        # Summary text
        if self.itinerary:
            summary = self.itinerary.get("summary", "")
            if summary:
                story.append(Paragraph(sanitize_text(summary), self.styles["GuidebookBody"]))

            # Locations
            locations = self.itinerary.get("location_list", [])
            if locations:
                story.append(Spacer(1, 0.3 * cm))
                story.append(Paragraph("📍 Highlights", self.styles["SubsectionTitle"]))
                for loc in locations[:5]:
                    story.append(Paragraph(f"• {sanitize_text(loc)}", self.styles["GuidebookBody"]))

        # Budget overview
        if self.budget:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("💵 Budget Overview", self.styles["SubsectionTitle"]))
            total = format_currency(self.budget.get("total_estimated_cost", 0))
            status = self.budget.get("budget_status", "N/A")
            story.append(
                Paragraph(
                    f"<b>{labels['total_cost']}:</b> {total}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>{labels['status']}:</b> {status}",
                    self.styles["GuidebookBody"],
                )
            )

        return story

    def _build_itinerary_section(self, labels: Dict[str, str]) -> List:
        """Build itinerary section."""
        story = []

        story.append(Paragraph(f"📅 {labels['itinerary']}", self.styles["SectionTitle"]))

        # Selected flight info
        selected_flight = self.itinerary.get("selected_flight")
        if selected_flight:
            story.append(
                Paragraph(f"✈️ {labels['selected_flight']}", self.styles["SubsectionTitle"])
            )
            story.append(
                Paragraph(
                    f"<b>Airline:</b> {selected_flight.get('airline', 'N/A')}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Outbound:</b> {selected_flight.get('outbound_flight', 'N/A')} | "
                    f"<b>Return:</b> {selected_flight.get('return_flight', 'N/A')}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Cost:</b> {format_currency(selected_flight.get('total_cost', 0))}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(Spacer(1, 0.3 * cm))

        # Selected accommodation
        selected_hotel = self.itinerary.get("selected_accommodation")
        if selected_hotel:
            story.append(
                Paragraph(f"🏨 {labels['selected_hotel']}", self.styles["SubsectionTitle"])
            )
            story.append(
                Paragraph(
                    f"<b>Hotel:</b> {selected_hotel.get('name', 'N/A')} "
                    f"({selected_hotel.get('area', '')})",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Check-in:</b> {selected_hotel.get('check_in', 'N/A')} | "
                    f"<b>Check-out:</b> {selected_hotel.get('check_out', 'N/A')}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Cost:</b> {format_currency(selected_hotel.get('total_cost', 0))}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(Spacer(1, 0.5 * cm))

        # Daily schedules
        daily_schedules = self.itinerary.get("daily_schedules", [])
        for day in daily_schedules:
            day_num = day.get("day_number", 0)
            title = day.get("title", "")
            date_str = day.get("date", "")

            header = f"{labels['day']} {day_num}"
            if title:
                header += f": {sanitize_text(title)}"
            if date_str:
                header += f" ({format_date(date_str)})"

            story.append(Paragraph(header, self.styles["SubsectionTitle"]))

            # Activities table
            activities = day.get("activities", [])
            if activities:
                table_data = [
                    [labels["time"], labels["activity"], labels["location"], labels["cost"]]
                ]

                for activity in activities:
                    icon = get_activity_icon(activity.get("activity_type", ""))
                    time = activity.get("time", "")
                    desc = sanitize_text(activity.get("description", ""), max_length=40)
                    loc = sanitize_text(activity.get("location_name", ""), max_length=25)
                    cost = activity.get("estimated_cost")
                    cost_str = format_currency(cost) if cost else "-"

                    table_data.append([time, f"{icon} {desc}", loc, cost_str])

                table = Table(
                    table_data,
                    colWidths=[2.5 * cm, 7 * cm, 4 * cm, 2.5 * cm],
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), self.PRIMARY_COLOR),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("GRID", (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            (
                                "ROWBACKGROUNDS",
                                (0, 1),
                                (-1, -1),
                                [colors.white, self.BACKGROUND_COLOR],
                            ),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 0.5 * cm))

        return story

    def _build_flights_section(self, labels: Dict[str, str]) -> List:
        """Build flights section."""
        story = []

        story.append(Paragraph(f"✈️ {labels['flights']}", self.styles["SectionTitle"]))

        flight_options = self.logistics.get("flight_options", [])
        for i, flight in enumerate(flight_options):
            rec_marker = "⭐ " if i == 0 else ""
            airline = sanitize_text(flight.get("airline", "Unknown"))

            story.append(
                Paragraph(
                    f"{rec_marker}{airline}",
                    self.styles["SubsectionTitle"],
                )
            )

            story.append(
                Paragraph(
                    f"<b>Type:</b> {flight.get('flight_type', 'N/A')} | "
                    f"<b>Duration:</b> {flight.get('duration', 'N/A')} | "
                    f"<b>Class:</b> {flight.get('cabin_class', 'N/A')}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Price:</b> {format_currency(flight.get('price_per_person', 0))}/person",
                    self.styles["GuidebookBody"],
                )
            )

            benefits = flight.get("benefits", [])
            if benefits:
                story.append(
                    Paragraph(
                        f"<b>Benefits:</b> {', '.join(benefits)}",
                        self.styles["GuidebookBody"],
                    )
                )
            story.append(Spacer(1, 0.3 * cm))

        # Booking tips
        booking_tips = self.logistics.get("booking_tips", [])
        if booking_tips:
            story.append(Paragraph(f"💡 {labels['booking_tips']}", self.styles["SubsectionTitle"]))
            for tip in booking_tips:
                story.append(Paragraph(f"• {sanitize_text(tip)}", self.styles["TipText"]))

        return story

    def _build_accommodation_section(self, labels: Dict[str, str]) -> List:
        """Build accommodation section."""
        story = []

        story.append(Paragraph(f"🏨 {labels['accommodation']}", self.styles["SectionTitle"]))

        # Best areas
        best_areas = self.accommodation.get("best_areas", [])
        if best_areas:
            story.append(Paragraph("📍 Best Areas", self.styles["SubsectionTitle"]))
            story.append(Paragraph(", ".join(best_areas), self.styles["GuidebookBody"]))
            story.append(Spacer(1, 0.3 * cm))

        # Recommendations
        recommendations = self.accommodation.get("recommendations", [])
        for hotel in recommendations:
            name = sanitize_text(hotel.get("name", "Unknown"))
            hotel_type = hotel.get("type", "")
            area = hotel.get("area", "")
            price = format_currency(hotel.get("price_per_night", 0))
            rating = hotel.get("rating")

            story.append(Paragraph(f"🏨 {name}", self.styles["SubsectionTitle"]))
            story.append(
                Paragraph(
                    f"<b>Type:</b> {hotel_type} | <b>Area:</b> {area}",
                    self.styles["GuidebookBody"],
                )
            )
            story.append(
                Paragraph(
                    f"<b>Price:</b> {price} {labels['per_night']}",
                    self.styles["GuidebookBody"],
                )
            )
            if rating:
                stars = "⭐" * int(rating)
                story.append(
                    Paragraph(
                        f"<b>Rating:</b> {stars} ({rating})",
                        self.styles["GuidebookBody"],
                    )
                )

            amenities = hotel.get("amenities", [])
            if amenities:
                story.append(
                    Paragraph(
                        f"<b>{labels['amenities']}:</b> {', '.join(amenities)}",
                        self.styles["GuidebookBody"],
                    )
                )
            story.append(Spacer(1, 0.3 * cm))

        return story

    def _build_budget_section(self, labels: Dict[str, str]) -> List:
        """Build budget section."""
        story = []

        story.append(Paragraph(f"💰 {labels['budget']}", self.styles["SectionTitle"]))

        # Categories table
        categories = self.budget.get("categories", [])
        if categories:
            table_data = [[labels["category"], labels["estimated"], labels["notes"]]]

            for cat in categories:
                name = sanitize_text(cat.get("category_name", ""))
                cost = format_currency(cat.get("estimated_cost", 0))
                notes = sanitize_text(cat.get("notes", ""), max_length=30) or "-"
                table_data.append([name, cost, notes])

            # Total row
            total = format_currency(self.budget.get("total_estimated_cost", 0))
            table_data.append([f"<b>{labels['total_cost']}</b>", f"<b>{total}</b>", ""])

            # Create paragraphs for cells to support markup
            formatted_data = []
            for row in table_data:
                formatted_row = []
                for cell in row:
                    formatted_row.append(Paragraph(str(cell), self.styles["GuidebookBody"]))
                formatted_data.append(formatted_row)

            table = Table(formatted_data, colWidths=[5 * cm, 4 * cm, 7 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), self.PRIMARY_COLOR),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BACKGROUND", (0, -1), (-1, -1), self.BACKGROUND_COLOR),
                    ]
                )
            )
            story.append(table)

        # Status
        status = self.budget.get("budget_status", "N/A")
        story.append(Spacer(1, 0.3 * cm))
        story.append(
            Paragraph(
                f"<b>{labels['status']}:</b> {status}",
                self.styles["GuidebookBody"],
            )
        )

        # Recommendations
        recommendations = self.budget.get("recommendations", [])
        if recommendations:
            story.append(Spacer(1, 0.3 * cm))
            story.append(
                Paragraph(f"💡 {labels['recommendations']}", self.styles["SubsectionTitle"])
            )
            for rec in recommendations:
                story.append(Paragraph(f"• {sanitize_text(rec)}", self.styles["TipText"]))

        return story

    def _build_advisory_section(self, labels: Dict[str, str]) -> List:
        """Build advisory section."""
        story = []

        story.append(Paragraph(f"⚠️ {labels['advisory']}", self.styles["SectionTitle"]))

        # Warnings
        warnings = self.advisory.get("warnings_and_tips", [])
        if warnings:
            story.append(Paragraph(f"📢 {labels['warnings']}", self.styles["SubsectionTitle"]))
            for warning in warnings:
                story.append(Paragraph(f"⚠️ {sanitize_text(warning)}", self.styles["GuidebookBody"]))
            story.append(Spacer(1, 0.3 * cm))

        # Visa info
        visa_info = self.advisory.get("visa_info")
        if visa_info:
            story.append(Paragraph(f"🛂 {labels['visa_info']}", self.styles["SubsectionTitle"]))
            story.append(Paragraph(sanitize_text(visa_info), self.styles["GuidebookBody"]))
            story.append(Spacer(1, 0.3 * cm))

        # Weather info
        weather_info = self.advisory.get("weather_info")
        if weather_info:
            story.append(Paragraph(f"🌤️ {labels['weather_info']}", self.styles["SubsectionTitle"]))
            story.append(Paragraph(sanitize_text(weather_info), self.styles["GuidebookBody"]))
            story.append(Spacer(1, 0.3 * cm))

        # Safety tips
        safety_tips = self.advisory.get("safety_tips", [])
        if safety_tips:
            story.append(Paragraph(f"🛡️ {labels['safety_tips']}", self.styles["SubsectionTitle"]))
            for tip in safety_tips:
                story.append(Paragraph(f"• {sanitize_text(tip)}", self.styles["GuidebookBody"]))

        return story

    def _build_souvenirs_section(self, labels: Dict[str, str]) -> List:
        """Build souvenirs section."""
        story = []

        story.append(Paragraph(f"🎁 {labels['souvenirs']}", self.styles["SectionTitle"]))

        for souvenir in self.souvenirs:
            name = sanitize_text(souvenir.get("item_name", ""))
            description = sanitize_text(souvenir.get("description", ""))
            price = souvenir.get("estimated_price", "")
            where = souvenir.get("where_to_buy", "")

            story.append(Paragraph(f"🛍️ {name}", self.styles["SubsectionTitle"]))
            story.append(Paragraph(description, self.styles["GuidebookBody"]))
            if price:
                story.append(
                    Paragraph(
                        f"<b>{labels['price']}:</b> {price}",
                        self.styles["GuidebookBody"],
                    )
                )
            if where:
                story.append(
                    Paragraph(
                        f"<b>{labels['where_to_buy']}:</b> {sanitize_text(where)}",
                        self.styles["GuidebookBody"],
                    )
                )
            story.append(Spacer(1, 0.3 * cm))

        return story
