"""
Markdown formatter for guidebook generation.

This module generates clean, readable Markdown guidebooks with
GitHub-flavored markdown support, table formatting, and emoji icons.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from travel_planner.guidebook.formatters.base import BaseFormatter
from travel_planner.guidebook.utils.formatting_helpers import (
    format_currency,
    format_date,
    get_activity_icon,
    sanitize_text,
)

logger = logging.getLogger(__name__)


class MarkdownFormatter(BaseFormatter):
    """
    Formatter for generating Markdown guidebooks.

    Generates clean, readable markdown with:
    - GitHub-flavored markdown support
    - Table formatting for schedules
    - Emoji support for visual appeal
    """

    def get_default_filename(self) -> str:
        """Get the default filename for markdown output."""
        destination_slug = (
            self.destination.lower().replace(" ", "_").replace(",", "")[:30]
            if self.destination
            else "travel"
        )
        return f"guidebook_{destination_slug}.md"

    def generate(self, output_path: Optional[str] = None) -> str:
        """
        Generate the Markdown guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated file.
        """
        logger.info("Generating Markdown guidebook...")

        output_file = self.get_output_path(output_path)
        labels = self.get_labels()

        # Build markdown content
        content_parts = [
            self._generate_cover_page(labels),
            self._generate_toc(labels),
            self._generate_executive_summary(labels),
            self._generate_itinerary_section(labels),
            self._generate_flights_section(labels),
            self._generate_accommodation_section(labels),
            self._generate_budget_section(labels),
            self._generate_advisory_section(labels),
            self._generate_souvenirs_section(labels),
            self._generate_appendix(labels),
        ]

        content = "\n\n---\n\n".join(filter(None, content_parts))

        # Write to file
        output_file.write_text(content, encoding="utf-8")
        logger.info(f"Markdown guidebook generated: {output_file}")

        return str(output_file)

    def _generate_cover_page(self, labels: Dict[str, str]) -> str:
        """Generate the cover page section."""
        lines = [
            f"# 🗺️ {labels['title']}",
            "",
            f"## {self.destination or 'Your Destination'}",
            "",
        ]

        if self.request_summary:
            lines.extend(
                [
                    "| 📋 | |",
                    "|---|---|",
                    f"| **{labels['destination']}** | {self.destination} |",
                    f"| **{labels['duration']}** | {self.trip_duration} "
                    + f"{'ngày' if self.language == 'vi' else 'days'} |",
                    f"| **{labels['travelers']}** | {self.num_travelers} |",
                    f"| **{labels['budget_label']}** | {format_currency(self.budget_amount)} |",
                    "",
                ]
            )

        if self.generated_at:
            lines.append(f"*{labels['generated_at']}: {format_date(self.generated_at[:10])}*")

        return "\n".join(lines)

    def _generate_toc(self, labels: Dict[str, str]) -> str:
        """Generate table of contents."""
        toc_items = [
            ("executive-summary", labels["executive_summary"], "📊"),
            ("itinerary", labels["itinerary"], "📅"),
            ("flights", labels["flights"], "✈️"),
            ("accommodation", labels["accommodation"], "🏨"),
            ("budget", labels["budget"], "💰"),
            ("advisory", labels["advisory"], "⚠️"),
            ("souvenirs", labels["souvenirs"], "🎁"),
            ("appendix", labels["appendix"], "📎"),
        ]

        lines = [f"## 📑 {labels['table_of_contents']}", ""]
        for anchor, title, icon in toc_items:
            lines.append(f"- [{icon} {title}](#{anchor})")

        return "\n".join(lines)

    def _generate_executive_summary(self, labels: Dict[str, str]) -> str:
        """Generate executive summary section."""
        lines = [f"## 📊 {labels['executive_summary']}", ""]

        # Trip overview
        if self.itinerary:
            summary = self.itinerary.get("summary")
            if summary:
                lines.extend([sanitize_text(summary), ""])

            # Location highlights
            location_list = self.itinerary.get("location_list", [])
            if location_list:
                lines.append("### 📍 Highlights")
                for loc in location_list[:5]:
                    lines.append(f"- {loc}")
                lines.append("")

        # Quick budget overview
        if self.budget:
            lines.extend(
                [
                    "### 💵 Budget Overview",
                    f"- **{labels['total_cost']}:** "
                    + f"{format_currency(self.budget.get('total_estimated_cost', 0))}",
                    f"- **{labels['status']}:** {self.budget.get('budget_status', 'N/A')}",
                    "",
                ]
            )

        return "\n".join(lines)

    def _generate_itinerary_section(self, labels: Dict[str, str]) -> str:
        """Generate the detailed itinerary section."""
        if not self.itinerary:
            return ""

        lines = [f"## 📅 {labels['itinerary']}", ""]

        # Selected flight info
        selected_flight = self.itinerary.get("selected_flight")
        if selected_flight:
            lines.extend(
                [
                    f"### ✈️ {labels['selected_flight']}",
                    f"- **Airline:** {selected_flight.get('airline', 'N/A')}",
                    f"- **Outbound:** {selected_flight.get('outbound_flight', 'N/A')}",
                    f"- **Return:** {selected_flight.get('return_flight', 'N/A')}",
                    f"- **Cost:** {format_currency(selected_flight.get('total_cost', 0))}",
                    "",
                ]
            )

        # Selected accommodation info
        selected_hotel = self.itinerary.get("selected_accommodation")
        if selected_hotel:
            lines.extend(
                [
                    f"### 🏨 {labels['selected_hotel']}",
                    f"- **Name:** {selected_hotel.get('name', 'N/A')}",
                    f"- **Area:** {selected_hotel.get('area', 'N/A')}",
                    f"- **Check-in:** {selected_hotel.get('check_in', 'N/A')}",
                    f"- **Check-out:** {selected_hotel.get('check_out', 'N/A')}",
                    f"- **Cost:** {format_currency(selected_hotel.get('total_cost', 0))}",
                    "",
                ]
            )

        # Daily schedules
        daily_schedules = self.itinerary.get("daily_schedules", [])
        for day in daily_schedules:
            day_num = day.get("day_number", 0)
            title = day.get("title", "")
            date_str = day.get("date", "")

            header = f"### {labels['day']} {day_num}"
            if title:
                header += f": {title}"
            if date_str:
                header += f" ({format_date(date_str)})"

            lines.extend([header, ""])

            # Activity table
            activities = day.get("activities", [])
            if activities:
                lines.extend(
                    [
                        f"| {labels['time']} | {labels['activity']} | "
                        + f"{labels['location']} | {labels['cost']} |",
                        "|---|---|---|---|",
                    ]
                )

                for activity in activities:
                    icon = get_activity_icon(activity.get("activity_type", ""))
                    time = activity.get("time", "")
                    description = sanitize_text(activity.get("description", ""), max_length=50)
                    location = activity.get("location_name", "")
                    cost = activity.get("estimated_cost")
                    cost_str = format_currency(cost) if cost else "-"

                    lines.append(f"| {time} | {icon} {description} | {location} | {cost_str} |")

                lines.append("")

                # Notes for activities with notes
                for activity in activities:
                    notes = activity.get("notes")
                    if notes:
                        lines.append(f"> 💡 **{activity.get('location_name')}:** {notes}")

                lines.append("")

        return "\n".join(lines)

    def _generate_flights_section(self, labels: Dict[str, str]) -> str:
        """Generate flight information section."""
        if not self.logistics:
            return ""

        lines = [f"## ✈️ {labels['flights']}", ""]

        # Flight options
        flight_options = self.logistics.get("flight_options", [])
        if flight_options:
            lines.append(f"### {labels['flight_options']}")
            lines.append("")

            for i, flight in enumerate(flight_options, 1):
                rec_marker = "⭐ " if i == 1 else ""
                lines.extend(
                    [
                        f"#### {rec_marker}{flight.get('airline', 'Unknown')}",
                        f"- **Type:** {flight.get('flight_type', 'N/A')}",
                        f"- **Departure:** {flight.get('departure_time', 'N/A')}",
                        f"- **Duration:** {flight.get('duration', 'N/A')}",
                        f"- **Price:** {format_currency(flight.get('price_per_person', 0))}/person",
                        f"- **Class:** {flight.get('cabin_class', 'N/A')}",
                    ]
                )

                benefits = flight.get("benefits", [])
                if benefits:
                    lines.append(f"- **Benefits:** {', '.join(benefits)}")

                lines.append("")

        # Booking tips
        booking_tips = self.logistics.get("booking_tips", [])
        if booking_tips:
            lines.extend([f"### 💡 {labels['booking_tips']}", ""])
            for tip in booking_tips:
                lines.append(f"- {tip}")
            lines.append("")

        return "\n".join(lines)

    def _generate_accommodation_section(self, labels: Dict[str, str]) -> str:
        """Generate accommodation section."""
        if not self.accommodation:
            return ""

        lines = [f"## 🏨 {labels['accommodation']}", ""]

        # Best areas
        best_areas = self.accommodation.get("best_areas", [])
        if best_areas:
            lines.extend(
                [
                    "### 📍 Best Areas",
                    "",
                    ", ".join(best_areas),
                    "",
                ]
            )

        # Accommodation options
        recommendations = self.accommodation.get("recommendations", [])
        if recommendations:
            for hotel in recommendations:
                name = hotel.get("name", "Unknown")
                hotel_type = hotel.get("type", "")
                area = hotel.get("area", "")
                price = hotel.get("price_per_night", 0)
                rating = hotel.get("rating")
                amenities = hotel.get("amenities", [])

                lines.extend(
                    [
                        f"#### 🏨 {name}",
                        f"- **Type:** {hotel_type}",
                        f"- **Area:** {area}",
                        f"- **Price:** {format_currency(price)} {labels['per_night']}",
                    ]
                )

                if rating:
                    lines.append(f"- **Rating:** {'⭐' * int(rating)} ({rating})")

                if amenities:
                    lines.append(f"- **{labels['amenities']}:** {', '.join(amenities)}")

                lines.append("")

        # Booking tips
        booking_tips = self.accommodation.get("booking_tips", [])
        if booking_tips:
            lines.extend([f"### 💡 {labels['booking_tips']}", ""])
            for tip in booking_tips:
                lines.append(f"- {tip}")
            lines.append("")

        return "\n".join(lines)

    def _generate_budget_section(self, labels: Dict[str, str]) -> str:
        """Generate budget breakdown section."""
        if not self.budget:
            return ""

        lines = [f"## 💰 {labels['budget']}", ""]

        # Categories table
        categories = self.budget.get("categories", [])
        if categories:
            lines.extend(
                [
                    f"| {labels['category']} | {labels['estimated']} | {labels['notes']} |",
                    "|---|---:|---|",
                ]
            )

            for cat in categories:
                name = cat.get("category_name", "")
                cost = format_currency(cat.get("estimated_cost", 0))
                notes = sanitize_text(cat.get("notes", ""), max_length=30) or "-"
                lines.append(f"| {name} | {cost} | {notes} |")

            lines.extend(
                [
                    "",
                    f"**{labels['total_cost']}:** "
                    + f"{format_currency(self.budget.get('total_estimated_cost', 0))}",
                    "",
                    f"**{labels['status']}:** {self.budget.get('budget_status', 'N/A')}",
                    "",
                ]
            )

        # Recommendations
        recommendations = self.budget.get("recommendations", [])
        if recommendations:
            lines.extend([f"### 💡 {labels['recommendations']}", ""])
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)

    def _generate_advisory_section(self, labels: Dict[str, str]) -> str:
        """Generate advisory and warnings section."""
        if not self.advisory:
            return ""

        lines = [f"## ⚠️ {labels['advisory']}", ""]

        # Warnings and tips
        warnings = self.advisory.get("warnings_and_tips", [])
        if warnings:
            lines.extend([f"### 📢 {labels['warnings']}", ""])
            for warning in warnings:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")

        # Location descriptions
        location_descriptions = self.advisory.get("location_descriptions", [])
        if location_descriptions:
            lines.append("### 📍 Location Guide")
            lines.append("")
            for loc in location_descriptions:
                name = loc.get("location_name", "")
                desc = loc.get("description", "")
                highlights = loc.get("highlights", [])

                lines.extend([f"#### {name}", desc, ""])

                if highlights:
                    for highlight in highlights:
                        lines.append(f"- ✨ {highlight}")
                    lines.append("")

        # Visa info
        visa_info = self.advisory.get("visa_info")
        if visa_info:
            lines.extend([f"### 🛂 {labels['visa_info']}", visa_info, ""])

        # Weather info
        weather_info = self.advisory.get("weather_info")
        if weather_info:
            lines.extend([f"### 🌤️ {labels['weather_info']}", weather_info, ""])

        # Safety tips
        safety_tips = self.advisory.get("safety_tips", [])
        if safety_tips:
            lines.extend([f"### 🛡️ {labels['safety_tips']}", ""])
            for tip in safety_tips:
                lines.append(f"- {tip}")
            lines.append("")

        # SIM and apps
        sim_apps = self.advisory.get("sim_and_apps", [])
        if sim_apps:
            lines.extend([f"### 📱 {labels['sim_apps']}", ""])
            for item in sim_apps:
                lines.append(f"- {item}")
            lines.append("")

        return "\n".join(lines)

    def _generate_souvenirs_section(self, labels: Dict[str, str]) -> str:
        """Generate souvenir suggestions section."""
        if not self.souvenirs:
            return ""

        lines = [f"## 🎁 {labels['souvenirs']}", ""]

        for souvenir in self.souvenirs:
            name = souvenir.get("item_name", "")
            description = souvenir.get("description", "")
            price = souvenir.get("estimated_price", "")
            where = souvenir.get("where_to_buy", "")

            lines.extend([f"### 🛍️ {name}", description, ""])

            if price:
                lines.append(f"- **{labels['price']}:** {price}")
            if where:
                lines.append(f"- **{labels['where_to_buy']}:** {where}")

            lines.append("")

        return "\n".join(lines)

    def _generate_appendix(self, labels: Dict[str, str]) -> str:
        """Generate appendix section."""
        lines = [f"## 📎 {labels['appendix']}", ""]

        # Packing list suggestions
        lines.extend(
            [
                f"### 🧳 {labels['packing_list']}",
                "",
                "- [ ] Passport & travel documents",
                "- [ ] Travel insurance",
                "- [ ] Credit/debit cards",
                "- [ ] Cash (local currency)",
                "- [ ] Phone charger & adapter",
                "- [ ] Medications",
                "- [ ] Comfortable walking shoes",
                "- [ ] Weather-appropriate clothing",
                "- [ ] Toiletries",
                "- [ ] Camera",
                "",
            ]
        )

        # Emergency contacts
        lines.extend(
            [
                f"### 📞 {labels['emergency_contacts']}",
                "",
                "| Service | Number |",
                "|---|---|",
                "| Police | 113 |",
                "| Ambulance | 115 |",
                "| Fire | 114 |",
                "| Embassy | (Check local) |",
                "",
            ]
        )

        return "\n".join(lines)
