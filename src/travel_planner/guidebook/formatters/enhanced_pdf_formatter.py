import logging
from typing import Any, Dict, Optional

# --- ReportLab Imports (Required for the logic in your file) ---
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# --- Local Project Imports ---
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
    Formatter for generating PDF guidebooks using ReportLab.

    Generates clean, printable PDFs with:
    - Cover page with trip overview
    - Table of contents
    - Day-by-day itinerary
    - Budget breakdown
    - Travel advisory
    - Souvenirs section
    - Vietnamese character support
    """

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
        self._setup_fonts()
        self._setup_styles()

    # ... The rest of your code (_setup_fonts, _setup_styles, etc.) goes here ...

    def _setup_fonts(self) -> None:
        """Set up fonts for Vietnamese character support."""
        # Use built-in fonts that support Vietnamese
        # ReportLab's built-in fonts will work for basic Latin characters
        # For full Vietnamese support, we'd need to register a Unicode font
        # but we'll use Helvetica as fallback which works for most characters
        try:
            # Try to use DejaVu fonts if available (good Unicode support)
            import os

            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/DejaVuSans.ttf",
                "C:/Windows/Fonts/DejaVuSans.ttf",
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                    pdfmetrics.registerFont(
                        TTFont(
                            "DejaVuSans-Bold",
                            font_path.replace(".ttf", "-Bold.ttf"),
                        )
                    )
                    self.font_name = "DejaVuSans"
                    self.font_name_bold = "DejaVuSans-Bold"
                    logger.debug("Using DejaVu Sans font for Vietnamese support")
                    return
        except Exception as e:
            logger.debug(f"Could not load DejaVu font: {e}")

        # Fallback to Helvetica
        self.font_name = "Helvetica"
        self.font_name_bold = "Helvetica-Bold"
        logger.debug("Using Helvetica font")

    def _setup_styles(self) -> None:
        """Set up paragraph styles for the document."""
        self.styles = getSampleStyleSheet()

        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CoverTitle",
                parent=self.styles["Heading1"],
                fontSize=28,
                fontName=self.font_name_bold,
                textColor=colors.HexColor("#2563eb"),
                alignment=1,  # Center
                spaceAfter=20,
            )
        )

        # Subtitle/destination style
        self.styles.add(
            ParagraphStyle(
                name="CoverSubtitle",
                parent=self.styles["Heading2"],
                fontSize=22,
                fontName=self.font_name_bold,
                textColor=colors.HexColor("#1e293b"),
                alignment=1,  # Center
                spaceAfter=30,
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=16,
                fontName=self.font_name_bold,
                textColor=colors.HexColor("#2563eb"),
                spaceBefore=20,
                spaceAfter=12,
            )
        )

        # Day header style
        self.styles.add(
            ParagraphStyle(
                name="DayHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                fontName=self.font_name_bold,
                textColor=colors.HexColor("#1d4ed8"),
                spaceBefore=15,
                spaceAfter=8,
            )
        )

        # Normal text style
        self.styles.add(
            ParagraphStyle(
                name="NormalText",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName=self.font_name,
                textColor=colors.HexColor("#1e293b"),
                leading=14,
            )
        )

        # Small text style
        self.styles.add(
            ParagraphStyle(
                name="SmallText",
                parent=self.styles["Normal"],
                fontSize=9,
                fontName=self.font_name,
                textColor=colors.HexColor("#64748b"),
                leading=12,
            )
        )

        # Info label style
        self.styles.add(
            ParagraphStyle(
                name="InfoLabel",
                parent=self.styles["Normal"],
                fontSize=10,
                fontName=self.font_name_bold,
                textColor=colors.HexColor("#64748b"),
            )
        )

        # TOC entry style
        self.styles.add(
            ParagraphStyle(
                name="TOCEntry",
                parent=self.styles["Normal"],
                fontSize=11,
                fontName=self.font_name,
                leftIndent=20,
                spaceBefore=5,
            )
        )

    def get_default_filename(self) -> str:
        """Get the default filename for PDF output."""
        destination_slug = (
            self.destination.lower().replace(" ", "_").replace(",", "")[:30]
            if self.destination
            else "travel"
        )
        return f"guidebook_{destination_slug}.pdf"

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

        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        # Build story (content)
        story = []

        # Cover page
        self._add_cover_page(story, labels)

        # Table of contents
        self._add_toc(story, labels)

        # Executive summary
        self._add_summary_section(story, labels)

        # Itinerary
        self._add_itinerary_section(story, labels)

        # Flights
        self._add_flights_section(story, labels)

        # Accommodation
        self._add_accommodation_section(story, labels)

        # Budget
        self._add_budget_section(story, labels)

        # Advisory
        self._add_advisory_section(story, labels)

        # Souvenirs
        self._add_souvenirs_section(story, labels)

        # Footer info
        self._add_footer(story, labels)

        # Build PDF
        doc.build(story)
        logger.info(f"PDF guidebook generated: {output_file}")

        return str(output_file)

    def _add_cover_page(self, story: list, labels: Dict[str, str]) -> None:
        """Add cover page to the document."""
        story.append(Spacer(1, 3 * cm))

        # Title
        title_text = f"🗺️ {labels['title']}"
        story.append(Paragraph(title_text, self.styles["CoverTitle"]))

        # Destination
        destination_text = sanitize_text(self.destination) or "Your Destination"
        story.append(Paragraph(destination_text, self.styles["CoverSubtitle"]))

        story.append(Spacer(1, 2 * cm))

        # Trip info table
        days_label = "ngày" if self.language == "vi" else "days"
        travelers_label = "người" if self.language == "vi" else "travelers"

        trip_data = [
            [labels["duration"], f"{self.trip_duration} {days_label}"],
            [labels["travelers"], f"{self.num_travelers} {travelers_label}"],
            [labels["budget_label"], format_currency(self.budget_amount)],
        ]

        table = Table(trip_data, colWidths=[6 * cm, 8 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), self.font_name_bold),
                    ("FONTNAME", (1, 0), (1, -1), self.font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#64748b")),
                    ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#1e293b")),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(table)

        story.append(Spacer(1, 3 * cm))

        # Generated date
        if self.generated_at:
            date_text = f"{labels['generated_at']}: {format_date(self.generated_at[:10])}"
            story.append(
                Paragraph(date_text, self.styles["SmallText"])
            )

        story.append(PageBreak())

    def _add_toc(self, story: list, labels: Dict[str, str]) -> None:
        """Add table of contents."""
        story.append(
            Paragraph(f"📑 {labels['table_of_contents']}", self.styles["SectionHeader"])
        )
        story.append(Spacer(1, 10))

        toc_items = [
            f"📊 {labels['executive_summary']}",
            f"📅 {labels['itinerary']}",
            f"✈️ {labels['flights']}",
            f"🏨 {labels['accommodation']}",
            f"💰 {labels['budget']}",
            f"⚠️ {labels['advisory']}",
            f"🎁 {labels['souvenirs']}",
        ]

        for item in toc_items:
            story.append(Paragraph(item, self.styles["TOCEntry"]))

        story.append(PageBreak())

    def _add_summary_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add executive summary section."""
        story.append(
            Paragraph(f"📊 {labels['executive_summary']}", self.styles["SectionHeader"])
        )

        # Trip overview
        if self.itinerary:
            summary = self.itinerary.get("summary", "")
            if summary:
                story.append(
                    Paragraph(sanitize_text(summary), self.styles["NormalText"])
                )
                story.append(Spacer(1, 10))

            # Location highlights
            location_list = self.itinerary.get("location_list", [])
            if location_list:
                story.append(
                    Paragraph("📍 Highlights:", self.styles["InfoLabel"])
                )
                for loc in location_list[:5]:
                    story.append(
                        Paragraph(f"  • {sanitize_text(loc)}", self.styles["NormalText"])
                    )
                story.append(Spacer(1, 10))

        # Budget overview
        if self.budget:
            total = self.budget.get("total_estimated_cost", 0)
            status = self.budget.get("budget_status", "N/A")

            story.append(
                Paragraph("💵 Budget Overview:", self.styles["InfoLabel"])
            )
            story.append(
                Paragraph(
                    f"  • {labels['total_cost']}: {format_currency(total)}",
                    self.styles["NormalText"],
                )
            )
            story.append(
                Paragraph(
                    f"  • {labels['status']}: {status}",
                    self.styles["NormalText"],
                )
            )

        story.append(Spacer(1, 20))

    def _add_itinerary_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add itinerary section."""
        if not self.itinerary:
            return

        story.append(
            Paragraph(f"📅 {labels['itinerary']}", self.styles["SectionHeader"])
        )

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

            story.append(Paragraph(header, self.styles["DayHeader"]))

            # Activity table
            activities = day.get("activities", [])
            if activities:
                table_data = [
                    [labels["time"], labels["activity"], labels["location"], labels["cost"]]
                ]

                for activity in activities:
                    icon = get_activity_icon(activity.get("activity_type", ""))
                    time = activity.get("time", "")
                    description = sanitize_text(
                        activity.get("description", ""), max_length=40
                    )
                    location = sanitize_text(
                        activity.get("location_name", ""), max_length=25
                    )
                    cost = activity.get("estimated_cost")
                    cost_str = format_currency(cost) if cost else "-"

                    table_data.append([time, f"{icon} {description}", location, cost_str])

                table = Table(
                    table_data,
                    colWidths=[2.5 * cm, 7 * cm, 4 * cm, 2.5 * cm],
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("FONTNAME", (0, 0), (-1, 0), self.font_name_bold),
                            ("FONTNAME", (0, 1), (-1, -1), self.font_name),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#64748b")),
                            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 10))

        story.append(Spacer(1, 10))

    def _add_flights_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add flight information section."""
        if not self.logistics:
            return

        flight_options = self.logistics.get("flight_options", [])
        if not flight_options:
            return

        story.append(
            Paragraph(f"✈️ {labels['flights']}", self.styles["SectionHeader"])
        )

        for i, flight in enumerate(flight_options[:3]):  # Limit to 3 flights
            airline = sanitize_text(flight.get("airline", "Unknown"))
            rec_marker = " ⭐ Recommended" if i == 0 else ""

            story.append(
                Paragraph(f"{airline}{rec_marker}", self.styles["DayHeader"])
            )

            flight_info = [
                f"  • Type: {flight.get('flight_type', 'N/A')}",
                f"  • Departure: {flight.get('departure_time', 'N/A')}",
                f"  • Duration: {flight.get('duration', 'N/A')}",
                f"  • Price: {format_currency(flight.get('price_per_person', 0))}/person",
                f"  • Class: {flight.get('cabin_class', 'N/A')}",
            ]

            for info in flight_info:
                story.append(Paragraph(info, self.styles["NormalText"]))

            story.append(Spacer(1, 10))

        # Booking tips
        booking_tips = self.logistics.get("booking_tips", [])
        if booking_tips:
            story.append(
                Paragraph(f"💡 {labels['booking_tips']}:", self.styles["InfoLabel"])
            )
            for tip in booking_tips[:3]:
                story.append(
                    Paragraph(f"  • {sanitize_text(tip)}", self.styles["NormalText"])
                )

        story.append(Spacer(1, 10))

    def _add_accommodation_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add accommodation section."""
        if not self.accommodation:
            return

        recommendations = self.accommodation.get("recommendations", [])
        if not recommendations:
            return

        story.append(
            Paragraph(f"🏨 {labels['accommodation']}", self.styles["SectionHeader"])
        )

        for hotel in recommendations[:3]:  # Limit to 3 hotels
            name = sanitize_text(hotel.get("name", "Unknown"))
            story.append(Paragraph(f"🏨 {name}", self.styles["DayHeader"]))

            price_text = format_currency(hotel.get("price_per_night", 0))
            hotel_info = [
                f"  • Type: {hotel.get('type', 'N/A')}",
                f"  • Area: {hotel.get('area', 'N/A')}",
                f"  • Price: {price_text} {labels['per_night']}",
            ]

            rating = hotel.get("rating")
            if rating:
                stars = "⭐" * int(rating)
                hotel_info.append(f"  • Rating: {stars} ({rating})")

            amenities = hotel.get("amenities", [])
            if amenities:
                hotel_info.append(
                    f"  • {labels['amenities']}: {', '.join(str(a) for a in amenities[:5])}"
                )

            for info in hotel_info:
                story.append(Paragraph(info, self.styles["NormalText"]))

            story.append(Spacer(1, 10))

    def _add_budget_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add budget breakdown section."""
        if not self.budget:
            return

        story.append(
            Paragraph(f"💰 {labels['budget']}", self.styles["SectionHeader"])
        )

        categories = self.budget.get("categories", [])
        total = self.budget.get("total_estimated_cost", 0)

        if categories:
            table_data = [[labels["category"], labels["estimated"], labels["notes"]]]

            for cat in categories:
                name = sanitize_text(cat.get("category_name", ""))
                cost = format_currency(cat.get("estimated_cost", 0))
                notes = sanitize_text(cat.get("notes", ""), max_length=25) or "-"
                table_data.append([name, cost, notes])

            table = Table(table_data, colWidths=[5 * cm, 5 * cm, 6 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, 0), self.font_name_bold),
                        ("FONTNAME", (0, 1), (-1, -1), self.font_name),
                        ("FONTSIZE", (0, 0), (-1, -1), 10),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 10))

        # Total
        story.append(
            Paragraph(
                f"{labels['total_cost']}: {format_currency(total)}",
                self.styles["DayHeader"],
            )
        )
        story.append(
            Paragraph(
                f"{labels['status']}: {self.budget.get('budget_status', 'N/A')}",
                self.styles["SmallText"],
            )
        )

        # Recommendations
        recommendations = self.budget.get("recommendations", [])
        if recommendations:
            story.append(Spacer(1, 10))
            story.append(
                Paragraph(f"💡 {labels['recommendations']}:", self.styles["InfoLabel"])
            )
            for rec in recommendations[:3]:
                story.append(
                    Paragraph(f"  • {sanitize_text(rec)}", self.styles["NormalText"])
                )

        story.append(Spacer(1, 10))

    def _add_advisory_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add advisory section."""
        if not self.advisory:
            return

        story.append(
            Paragraph(f"⚠️ {labels['advisory']}", self.styles["SectionHeader"])
        )

        # Warnings
        warnings = self.advisory.get("warnings_and_tips", [])
        if warnings:
            story.append(
                Paragraph(f"📢 {labels['warnings']}:", self.styles["InfoLabel"])
            )
            for warning in warnings[:5]:
                story.append(
                    Paragraph(
                        f"  ⚠️ {sanitize_text(warning)}", self.styles["NormalText"]
                    )
                )
            story.append(Spacer(1, 10))

        # Visa info
        visa_info = self.advisory.get("visa_info", "")
        if visa_info:
            story.append(
                Paragraph(f"🛂 {labels['visa_info']}:", self.styles["InfoLabel"])
            )
            story.append(
                Paragraph(f"  {sanitize_text(visa_info)}", self.styles["NormalText"])
            )
            story.append(Spacer(1, 8))

        # Weather info
        weather_info = self.advisory.get("weather_info", "")
        if weather_info:
            story.append(
                Paragraph(f"🌤️ {labels['weather_info']}:", self.styles["InfoLabel"])
            )
            story.append(
                Paragraph(f"  {sanitize_text(weather_info)}", self.styles["NormalText"])
            )
            story.append(Spacer(1, 8))

        # Safety tips
        safety_tips = self.advisory.get("safety_tips", [])
        if safety_tips:
            story.append(
                Paragraph(f"🛡️ {labels['safety_tips']}:", self.styles["InfoLabel"])
            )
            for tip in safety_tips[:5]:
                story.append(
                    Paragraph(f"  • {sanitize_text(tip)}", self.styles["NormalText"])
                )

        story.append(Spacer(1, 10))

    def _add_souvenirs_section(self, story: list, labels: Dict[str, str]) -> None:
        """Add souvenirs section."""
        if not self.souvenirs:
            return

        story.append(
            Paragraph(f"🎁 {labels['souvenirs']}", self.styles["SectionHeader"])
        )

        for souvenir in self.souvenirs[:5]:  # Limit to 5 souvenirs
            name = sanitize_text(souvenir.get("item_name", ""))
            story.append(Paragraph(f"🛍️ {name}", self.styles["DayHeader"]))

            description = souvenir.get("description", "")
            if description:
                story.append(
                    Paragraph(sanitize_text(description), self.styles["NormalText"])
                )

            price = souvenir.get("estimated_price", "")
            where = souvenir.get("where_to_buy", "")

            if price:
                story.append(
                    Paragraph(
                        f"  • {labels['price']}: {price}", self.styles["NormalText"]
                    )
                )
            if where:
                story.append(
                    Paragraph(
                        f"  • {labels['where_to_buy']}: {sanitize_text(where)}",
                        self.styles["NormalText"],
                    )
                )

            story.append(Spacer(1, 8))

    def _add_footer(self, story: list, labels: Dict[str, str]) -> None:
        """Add footer with generation info."""
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(
                "---",
                ParagraphStyle(
                    name="FooterLine",
                    alignment=1,
                    textColor=colors.HexColor("#e2e8f0"),
                ),
            )
        )
        story.append(Spacer(1, 10))

        footer_text = f"NaviAgent Travel Guidebook v{self.version}"
        story.append(
            Paragraph(
                footer_text,
                ParagraphStyle(
                    name="Footer",
                    alignment=1,
                    fontSize=9,
                    textColor=colors.HexColor("#64748b"),
                ),
            )
        )
