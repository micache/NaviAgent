"""
HTML formatter for guidebook generation.

This module generates responsive HTML guidebooks with modern CSS styling,
print-friendly media queries, and interactive elements.
"""

import logging
from typing import Any, Dict, Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from travel_planner.guidebook.formatters.base import BaseFormatter
from travel_planner.guidebook.utils.formatting_helpers import (
    format_currency,
    format_date,
    get_activity_icon,
    sanitize_text,
)

logger = logging.getLogger(__name__)


class HTMLFormatter(BaseFormatter):
    """
    Formatter for generating HTML guidebooks.

    Generates responsive HTML with:
    - Modern CSS styling
    - Print-friendly media queries
    - Interactive collapsible sections
    - Mobile-friendly responsive design
    """

    def __init__(
        self,
        travel_plan: Dict[str, Any],
        output_dir: str = "guidebooks",
        language: str = "vi",
    ):
        """
        Initialize the HTML formatter.

        Args:
            travel_plan: Dictionary containing travel plan data.
            output_dir: Directory to save output files.
            language: Language for content (vi or en).
        """
        super().__init__(travel_plan, output_dir, language)

        # Setup Jinja2 environment with fallback to inline template
        try:
            self.env = Environment(
                loader=PackageLoader("travel_planner.guidebook", "templates"),
                autoescape=select_autoescape(["html", "xml"]),
            )
        except Exception:
            # Fallback to inline template if package loader fails
            self.env = None
            logger.debug("Using inline HTML template")

    def get_default_filename(self) -> str:
        """Get the default filename for HTML output."""
        destination_slug = (
            self.destination.lower().replace(" ", "_").replace(",", "")[:30]
            if self.destination
            else "travel"
        )
        return f"guidebook_{destination_slug}.html"

    def generate(self, output_path: Optional[str] = None) -> str:
        """
        Generate the HTML guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated file.
        """
        logger.info("Generating HTML guidebook...")

        output_file = self.get_output_path(output_path)
        labels = self.get_labels()

        # Build HTML content
        html_content = self._build_html(labels)

        # Write to file
        output_file.write_text(html_content, encoding="utf-8")
        logger.info(f"HTML guidebook generated: {output_file}")

        return str(output_file)

    def _build_html(self, labels: Dict[str, str]) -> str:
        """Build the complete HTML document."""
        # Use template if available, otherwise use inline HTML
        if self.env:
            try:
                template = self.env.get_template("guidebook.html")
                return template.render(
                    travel_plan=self.travel_plan,
                    labels=labels,
                    language=self.language,
                    format_currency=format_currency,
                    format_date=format_date,
                    get_activity_icon=get_activity_icon,
                    sanitize_text=sanitize_text,
                )
            except Exception as e:
                logger.debug(f"Template rendering failed: {e}, using inline HTML")

        # Inline HTML template
        return self._generate_inline_html(labels)

    def _generate_inline_html(self, labels: Dict[str, str]) -> str:
        """Generate HTML using inline template."""
        css = self._get_css()
        body_content = self._generate_body_content(labels)

        return f"""<!DOCTYPE html>
<html lang="{self.language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{labels['title']} - {self.destination}</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="guidebook">
{body_content}
    </div>
    <script>
        // Collapsible sections
        document.querySelectorAll('.section-header').forEach(header => {{
            header.addEventListener('click', () => {{
                header.classList.toggle('collapsed');
                const content = header.nextElementSibling;
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            }});
        }});

        // Print button
        document.getElementById('printBtn')?.addEventListener('click', () => window.print());
    </script>
</body>
</html>"""

    def _get_css(self) -> str:
        """Get the CSS stylesheet."""
        return """
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --accent-color: #f59e0b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --background-color: #f8fafc;
    --card-background: #ffffff;
    --text-color: #1e293b;
    --text-muted: #64748b;
    --border-color: #e2e8f0;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
}

.guidebook {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

/* Cover Page */
.cover-page {
    background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
    color: white;
    padding: 60px 40px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 30px;
}

.cover-page h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

.cover-page .destination {
    font-size: 1.8em;
    margin-bottom: 30px;
    opacity: 0.95;
}

.trip-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 20px;
    margin-top: 30px;
}

.trip-info-item {
    background: rgba(255, 255, 255, 0.15);
    padding: 15px;
    border-radius: 8px;
}

.trip-info-item .label {
    font-size: 0.85em;
    opacity: 0.9;
}

.trip-info-item .value {
    font-size: 1.3em;
    font-weight: 600;
}

/* Sections */
.section {
    background: var(--card-background);
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.4em;
    font-weight: 600;
    color: var(--primary-color);
    margin-bottom: 20px;
    cursor: pointer;
    user-select: none;
}

.section-header:hover {
    opacity: 0.8;
}

.section-header.collapsed::after {
    content: '▼';
    margin-left: auto;
    font-size: 0.7em;
}

.section-header:not(.collapsed)::after {
    content: '▲';
    margin-left: auto;
    font-size: 0.7em;
}

.section-icon {
    font-size: 1.2em;
}

/* Day Schedule */
.day-schedule {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    margin-bottom: 20px;
    overflow: hidden;
}

.day-header {
    background: var(--primary-color);
    color: white;
    padding: 15px 20px;
    font-weight: 600;
}

.day-content {
    padding: 20px;
}

/* Activity */
.activity {
    display: flex;
    gap: 15px;
    padding: 15px 0;
    border-bottom: 1px solid var(--border-color);
}

.activity:last-child {
    border-bottom: none;
}

.activity-time {
    min-width: 100px;
    font-weight: 500;
    color: var(--primary-color);
}

.activity-icon {
    font-size: 1.3em;
}

.activity-details {
    flex: 1;
}

.activity-name {
    font-weight: 600;
    margin-bottom: 5px;
}

.activity-location {
    color: var(--text-muted);
    font-size: 0.9em;
}

.activity-cost {
    color: var(--success-color);
    font-weight: 500;
}

.activity-notes {
    background: #fef3c7;
    padding: 10px;
    border-radius: 6px;
    margin-top: 10px;
    font-size: 0.9em;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
}

th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

th {
    background: var(--background-color);
    font-weight: 600;
    color: var(--text-muted);
}

/* Cards */
.card {
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
}

.card-header {
    font-weight: 600;
    font-size: 1.1em;
    margin-bottom: 10px;
}

.card-badge {
    display: inline-block;
    background: var(--accent-color);
    color: white;
    padding: 3px 10px;
    border-radius: 15px;
    font-size: 0.8em;
    margin-left: 10px;
}

/* Lists */
.tip-list, .warning-list {
    list-style: none;
    padding: 0;
}

.tip-list li, .warning-list li {
    padding: 10px 0 10px 30px;
    position: relative;
    border-bottom: 1px solid var(--border-color);
}

.tip-list li::before {
    content: '💡';
    position: absolute;
    left: 0;
}

.warning-list li::before {
    content: '⚠️';
    position: absolute;
    left: 0;
}

/* Budget */
.budget-chart {
    margin: 20px 0;
}

.budget-bar {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.budget-bar-label {
    min-width: 150px;
    font-weight: 500;
}

.budget-bar-track {
    flex: 1;
    height: 20px;
    background: var(--border-color);
    border-radius: 10px;
    overflow: hidden;
}

.budget-bar-fill {
    height: 100%;
    background: var(--primary-color);
    border-radius: 10px;
}

.budget-bar-value {
    min-width: 100px;
    text-align: right;
    font-weight: 500;
}

.budget-total {
    font-size: 1.3em;
    font-weight: 600;
    text-align: right;
    padding-top: 15px;
    border-top: 2px solid var(--primary-color);
}

/* Footer */
.footer {
    text-align: center;
    padding: 30px;
    color: var(--text-muted);
    font-size: 0.9em;
}

/* Actions */
.actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: #1d4ed8;
}

/* Print styles */
@media print {
    body {
        background: white;
    }

    .guidebook {
        max-width: none;
        padding: 0;
    }

    .cover-page {
        page-break-after: always;
    }

    .section {
        page-break-inside: avoid;
        box-shadow: none;
        border: 1px solid #ddd;
    }

    .actions, .btn {
        display: none;
    }

    .section-header::after {
        display: none;
    }
}

/* Mobile responsive */
@media (max-width: 768px) {
    .cover-page {
        padding: 40px 20px;
    }

    .cover-page h1 {
        font-size: 1.8em;
    }

    .trip-info {
        grid-template-columns: repeat(2, 1fr);
    }

    .activity {
        flex-direction: column;
        gap: 10px;
    }

    .activity-time {
        min-width: auto;
    }

    table {
        display: block;
        overflow-x: auto;
    }
}"""

    def _generate_body_content(self, labels: Dict[str, str]) -> str:
        """Generate the body content."""
        sections = [
            self._generate_cover_page_html(labels),
            self._generate_actions_html(),
            self._generate_summary_section_html(labels),
            self._generate_itinerary_section_html(labels),
            self._generate_flights_section_html(labels),
            self._generate_accommodation_section_html(labels),
            self._generate_budget_section_html(labels),
            self._generate_advisory_section_html(labels),
            self._generate_souvenirs_section_html(labels),
            self._generate_footer_html(labels),
        ]

        return "\n".join(filter(None, sections))

    def _generate_cover_page_html(self, labels: Dict[str, str]) -> str:
        """Generate cover page HTML."""
        days_label = "ngày" if self.language == "vi" else "days"
        travelers_label = "người" if self.language == "vi" else "travelers"

        return f"""
        <div class="cover-page">
            <h1>🗺️ {labels['title']}</h1>
            <div class="destination">{sanitize_text(self.destination)}</div>

            <div class="trip-info">
                <div class="trip-info-item">
                    <div class="label">{labels['duration']}</div>
                    <div class="value">{self.trip_duration} {days_label}</div>
                </div>
                <div class="trip-info-item">
                    <div class="label">{labels['travelers']}</div>
                    <div class="value">{self.num_travelers} {travelers_label}</div>
                </div>
                <div class="trip-info-item">
                    <div class="label">{labels['budget_label']}</div>
                    <div class="value">{format_currency(self.budget_amount)}</div>
                </div>
            </div>
        </div>"""

    def _generate_actions_html(self) -> str:
        """Generate actions bar HTML."""
        return """
        <div class="actions">
            <button class="btn btn-primary" id="printBtn">🖨️ Print</button>
        </div>"""

    def _generate_summary_section_html(self, labels: Dict[str, str]) -> str:
        """Generate executive summary section HTML."""
        summary = self.itinerary.get("summary", "") if self.itinerary else ""
        location_list = self.itinerary.get("location_list", []) if self.itinerary else []

        locations_html = ""
        if location_list:
            locations_items = "".join(f"<li>{sanitize_text(loc)}</li>" for loc in location_list[:5])
            locations_html = f"<ul>{locations_items}</ul>"

        budget_info = ""
        if self.budget:
            total = format_currency(self.budget.get("total_estimated_cost", 0))
            status = self.budget.get("budget_status", "N/A")
            budget_info = f"""
            <div style="margin-top: 20px;">
                <strong>{labels['total_cost']}:</strong> {total}<br>
                <strong>{labels['status']}:</strong> {status}
            </div>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">📊</span>
                {labels['executive_summary']}
            </h2>
            <div class="section-content">
                <p>{sanitize_text(summary)}</p>
                {locations_html}
                {budget_info}
            </div>
        </div>"""

    def _generate_itinerary_section_html(self, labels: Dict[str, str]) -> str:
        """Generate itinerary section HTML."""
        if not self.itinerary:
            return ""

        daily_schedules = self.itinerary.get("daily_schedules", [])
        days_html = ""

        for day in daily_schedules:
            day_num = day.get("day_number", 0)
            title = day.get("title", "")
            date_str = day.get("date", "")

            header = f"{labels['day']} {day_num}"
            if title:
                header += f": {sanitize_text(title)}"
            if date_str:
                header += f" ({format_date(date_str)})"

            activities_html = ""
            for activity in day.get("activities", []):
                icon = get_activity_icon(activity.get("activity_type", ""))
                time = activity.get("time", "")
                name = sanitize_text(activity.get("description", ""))
                location = sanitize_text(activity.get("location_name", ""))
                cost = activity.get("estimated_cost")
                cost_str = format_currency(cost) if cost else ""
                notes = activity.get("notes", "")

                notes_html = ""
                if notes:
                    notes_html = f'<div class="activity-notes">💡 {sanitize_text(notes)}</div>'

                activities_html += f"""
                <div class="activity">
                    <div class="activity-time">{time}</div>
                    <div class="activity-icon">{icon}</div>
                    <div class="activity-details">
                        <div class="activity-name">{name}</div>
                        <div class="activity-location">📍 {location}</div>
                        {notes_html}
                    </div>
                    <div class="activity-cost">{cost_str}</div>
                </div>"""

            days_html += f"""
            <div class="day-schedule">
                <div class="day-header">{header}</div>
                <div class="day-content">{activities_html}</div>
            </div>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">📅</span>
                {labels['itinerary']}
            </h2>
            <div class="section-content">
                {days_html}
            </div>
        </div>"""

    def _generate_flights_section_html(self, labels: Dict[str, str]) -> str:
        """Generate flights section HTML."""
        if not self.logistics:
            return ""

        flight_options = self.logistics.get("flight_options", [])
        if not flight_options:
            return ""

        flights_html = ""
        for i, flight in enumerate(flight_options):
            badge = '<span class="card-badge">Recommended</span>' if i == 0 else ""
            airline = sanitize_text(flight.get("airline", "Unknown"))
            flight_type = flight.get("flight_type", "")
            departure = flight.get("departure_time", "")
            duration = flight.get("duration", "")
            price = format_currency(flight.get("price_per_person", 0))
            cabin = flight.get("cabin_class", "")
            benefits = flight.get("benefits", [])

            benefits_html = ""
            if benefits:
                benefits_items = ", ".join(sanitize_text(b) for b in benefits)
                benefits_html = f"<p><strong>Benefits:</strong> {benefits_items}</p>"

            flights_html += f"""
            <div class="card">
                <div class="card-header">{airline} {badge}</div>
                <p><strong>Type:</strong> {flight_type}</p>
                <p><strong>Departure:</strong> {departure}</p>
                <p><strong>Duration:</strong> {duration}</p>
                <p><strong>Price:</strong> {price}/person</p>
                <p><strong>Class:</strong> {cabin}</p>
                {benefits_html}
            </div>"""

        # Booking tips
        tips = self.logistics.get("booking_tips", [])
        tips_html = ""
        if tips:
            tips_items = "".join(f"<li>{sanitize_text(tip)}</li>" for tip in tips)
            tips_html = f"""
            <h3 style="margin-top: 20px;">💡 {labels['booking_tips']}</h3>
            <ul class="tip-list">{tips_items}</ul>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">✈️</span>
                {labels['flights']}
            </h2>
            <div class="section-content">
                {flights_html}
                {tips_html}
            </div>
        </div>"""

    def _generate_accommodation_section_html(self, labels: Dict[str, str]) -> str:
        """Generate accommodation section HTML."""
        if not self.accommodation:
            return ""

        recommendations = self.accommodation.get("recommendations", [])
        if not recommendations:
            return ""

        hotels_html = ""
        for hotel in recommendations:
            name = sanitize_text(hotel.get("name", "Unknown"))
            hotel_type = hotel.get("type", "")
            area = hotel.get("area", "")
            price = format_currency(hotel.get("price_per_night", 0))
            rating = hotel.get("rating")
            amenities = hotel.get("amenities", [])

            rating_html = ""
            if rating:
                stars = "⭐" * int(rating)
                rating_html = f"<p><strong>Rating:</strong> {stars} ({rating})</p>"

            amenities_html = ""
            if amenities:
                amenities_str = ", ".join(sanitize_text(a) for a in amenities)
                amenities_html = f"<p><strong>{labels['amenities']}:</strong> {amenities_str}</p>"

            hotels_html += f"""
            <div class="card">
                <div class="card-header">🏨 {name}</div>
                <p><strong>Type:</strong> {hotel_type}</p>
                <p><strong>Area:</strong> {area}</p>
                <p><strong>Price:</strong> {price} {labels['per_night']}</p>
                {rating_html}
                {amenities_html}
            </div>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">🏨</span>
                {labels['accommodation']}
            </h2>
            <div class="section-content">
                {hotels_html}
            </div>
        </div>"""

    def _generate_budget_section_html(self, labels: Dict[str, str]) -> str:
        """Generate budget section HTML."""
        if not self.budget:
            return ""

        categories = self.budget.get("categories", [])
        total = self.budget.get("total_estimated_cost", 0)
        status = self.budget.get("budget_status", "N/A")

        budget_bars_html = ""
        if categories and total > 0:
            for cat in categories:
                name = sanitize_text(cat.get("category_name", ""))
                cost = cat.get("estimated_cost", 0)
                percentage = (cost / total * 100) if total else 0
                cost_str = format_currency(cost)

                budget_bars_html += f"""
                <div class="budget-bar">
                    <div class="budget-bar-label">{name}</div>
                    <div class="budget-bar-track">
                        <div class="budget-bar-fill" style="width: {percentage}%;"></div>
                    </div>
                    <div class="budget-bar-value">{cost_str}</div>
                </div>"""

        recommendations = self.budget.get("recommendations", [])
        recommendations_html = ""
        if recommendations:
            items = "".join(f"<li>{sanitize_text(r)}</li>" for r in recommendations)
            recommendations_html = f"""
            <h3 style="margin-top: 20px;">💡 {labels['recommendations']}</h3>
            <ul class="tip-list">{items}</ul>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">💰</span>
                {labels['budget']}
            </h2>
            <div class="section-content">
                <div class="budget-chart">
                    {budget_bars_html}
                </div>
                <div class="budget-total">
                    {labels['total_cost']}: {format_currency(total)}<br>
                    <span style="font-size: 0.8em; color: var(--text-muted);">
                        {labels['status']}: {status}
                    </span>
                </div>
                {recommendations_html}
            </div>
        </div>"""

    def _generate_advisory_section_html(self, labels: Dict[str, str]) -> str:
        """Generate advisory section HTML."""
        if not self.advisory:
            return ""

        warnings = self.advisory.get("warnings_and_tips", [])
        warnings_html = ""
        if warnings:
            items = "".join(f"<li>{sanitize_text(w)}</li>" for w in warnings)
            warnings_html = f"""
            <h3>📢 {labels['warnings']}</h3>
            <ul class="warning-list">{items}</ul>"""

        visa_info = self.advisory.get("visa_info", "")
        visa_html = ""
        if visa_info:
            visa_html = f"""
            <h3>🛂 {labels['visa_info']}</h3>
            <p>{sanitize_text(visa_info)}</p>"""

        weather_info = self.advisory.get("weather_info", "")
        weather_html = ""
        if weather_info:
            weather_html = f"""
            <h3>🌤️ {labels['weather_info']}</h3>
            <p>{sanitize_text(weather_info)}</p>"""

        safety_tips = self.advisory.get("safety_tips", [])
        safety_html = ""
        if safety_tips:
            items = "".join(f"<li>{sanitize_text(t)}</li>" for t in safety_tips)
            safety_html = f"""
            <h3>🛡️ {labels['safety_tips']}</h3>
            <ul>{items}</ul>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">⚠️</span>
                {labels['advisory']}
            </h2>
            <div class="section-content">
                {warnings_html}
                {visa_html}
                {weather_html}
                {safety_html}
            </div>
        </div>"""

    def _generate_souvenirs_section_html(self, labels: Dict[str, str]) -> str:
        """Generate souvenirs section HTML."""
        if not self.souvenirs:
            return ""

        souvenirs_html = ""
        for souvenir in self.souvenirs:
            name = sanitize_text(souvenir.get("item_name", ""))
            description = sanitize_text(souvenir.get("description", ""))
            price = souvenir.get("estimated_price", "")
            where = souvenir.get("where_to_buy", "")

            price_html = f"<p><strong>{labels['price']}:</strong> {price}</p>" if price else ""
            where_html = (
                f"<p><strong>{labels['where_to_buy']}:</strong> {sanitize_text(where)}</p>"
                if where
                else ""
            )

            souvenirs_html += f"""
            <div class="card">
                <div class="card-header">🛍️ {name}</div>
                <p>{description}</p>
                {price_html}
                {where_html}
            </div>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">🎁</span>
                {labels['souvenirs']}
            </h2>
            <div class="section-content">
                {souvenirs_html}
            </div>
        </div>"""

    def _generate_footer_html(self, labels: Dict[str, str]) -> str:
        """Generate footer HTML."""
        generated_date = format_date(self.generated_at[:10]) if self.generated_at else ""

        return f"""
        <div class="footer">
            <p>{labels['generated_at']}: {generated_date}</p>
            <p>NaviAgent Travel Guidebook v{self.version}</p>
        </div>"""
