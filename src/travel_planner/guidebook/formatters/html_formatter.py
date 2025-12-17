"""
Enhanced HTML formatter for guidebook generation with improved styling and images.

This module generates responsive, visually appealing HTML guidebooks with:
- Beautiful hero images and location photos
- Highlighted schedules with clear time indicators
- Professional table styling with borders
- Modern gradient designs
- Print-friendly layouts
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
    Enhanced formatter for generating beautiful HTML guidebooks.

    Generates responsive HTML with:
    - Hero images and location photos
    - Modern CSS styling with gradients
    - Highlighted schedule items
    - Professional table designs
    - Print-friendly media queries
    - Interactive collapsible sections
    - Mobile-friendly responsive design
    """

    def __init__(
        self,
        travel_plan: Dict[str, Any],
        output_dir: str = "guidebooks",
        language: str = "vi",
        image_fetcher=None,
        search_function=None,
    ):
        """
        Initialize the Enhanced HTML formatter.

        Args:
            travel_plan: Dictionary containing travel plan data.
            output_dir: Directory to save output files.
            language: Language for content (vi or en).
            image_fetcher: Optional ImageFetcher instance
            search_function: Optional function for web search
        """
        super().__init__(travel_plan, output_dir, language)
        self.image_fetcher = image_fetcher
        self.search_function = search_function

        # Setup Jinja2 environment
        try:
            self.env = Environment(
                loader=PackageLoader("travel_planner.guidebook", "templates"),
                autoescape=select_autoescape(["html", "xml"]),
            )
        except Exception:
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
        Generate the Enhanced HTML guidebook.

        Args:
            output_path: Optional custom output path.

        Returns:
            Path to the generated file.
        """
        logger.info("Generating Enhanced HTML guidebook...")

        output_file = self.get_output_path(output_path)
        labels = self.get_labels()

        # Build HTML content
        html_content = self._build_html(labels)

        # Write to file
        output_file.write_text(html_content, encoding="utf-8")
        logger.info(f"Enhanced HTML guidebook generated: {output_file}")

        return str(output_file)

    def _build_html(self, labels: Dict[str, str]) -> str:
        """Build the complete HTML document."""
        # Generate inline HTML with enhanced styling
        return self._generate_enhanced_html(labels)

    def _get_hero_image(self) -> Optional[str]:
        """Get hero image for destination."""
        if not self.image_fetcher or not self.destination:
            return None

        try:
            image_data = self.image_fetcher.get_destination_hero(
                self.destination,
                search_func=self.search_function,
            )
            return self.image_fetcher.get_data_uri(image_data)
        except Exception as e:
            logger.warning(f"Failed to get hero image: {e}")
            return None

    def _get_location_image(self, location: str) -> Optional[str]:
        """Get image for a specific location."""
        if not self.image_fetcher:
            return None

        try:
            image_data = self.image_fetcher.get_location_image(
                location,
                destination=self.destination,
                search_func=self.search_function,
            )
            return self.image_fetcher.get_data_uri(image_data)
        except Exception as e:
            logger.debug(f"Failed to get location image for {location}: {e}")
            return None

    def _generate_enhanced_html(self, labels: Dict[str, str]) -> str:
        """Generate HTML using enhanced inline template with better styling."""
        css = self._get_enhanced_css()
        body_content = self._generate_enhanced_body_content(labels)

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
                if (content) {{
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                }}
            }});
        }});

        // Print button
        const printBtn = document.getElementById('printBtn');
        if (printBtn) {{
            printBtn.addEventListener('click', function(e) {{
                e.preventDefault();
                window.print();
            }});
            printBtn.style.cursor = 'pointer';
        }}

        // Smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
    </script>
</body>
</html>"""

    def _get_enhanced_css(self) -> str:
        """Get the enhanced CSS stylesheet with modern styling."""
        return """
/* Enhanced Guidebook Styles - Production Ready */

:root {
    --primary-color: #2563eb;
    --primary-dark: #1d4ed8;
    --primary-light: #3b82f6;
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
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
    color: var(--text-color);
    line-height: 1.6;
    padding: 20px 0;
}

.guidebook {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* ============================================
   COVER PAGE WITH HERO IMAGE
   ============================================ */
.cover-page {
    position: relative;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    padding: 0;
    border-radius: 20px;
    margin-bottom: 30px;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
    min-height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.cover-hero-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.3;
}

.cover-content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 60px 40px;
    background: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    margin: 20px;
}

.cover-page h1 {
    font-size: 3.5em;
    margin-bottom: 15px;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    animation: fadeInDown 1s ease-out;
}

.cover-page .destination {
    font-size: 2.2em;
    margin-bottom: 40px;
    opacity: 0.95;
    font-weight: 600;
    animation: fadeInUp 1s ease-out 0.2s both;
}

.trip-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 25px;
    margin-top: 40px;
    animation: fadeIn 1s ease-out 0.4s both;
}

.trip-info-item {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    transition: transform 0.3s ease, background 0.3s ease;
}

.trip-info-item:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.25);
}

.trip-info-item .label {
    font-size: 0.9em;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.trip-info-item .value {
    font-size: 1.5em;
    font-weight: 700;
}

/* Animations */
@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

/* ============================================
   SECTIONS WITH MODERN CARDS
   ============================================ */
.section {
    background: var(--card-background);
    border-radius: 16px;
    padding: 35px;
    margin-bottom: 25px;
    box-shadow: var(--shadow-md);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.section:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 1.8em;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 25px;
    padding-bottom: 15px;
    border-bottom: 3px solid var(--primary-color);
    cursor: pointer;
    user-select: none;
    transition: color 0.3s ease;
}

.section-header:hover {
    color: var(--primary-dark);
}

.section-header.collapsed::after {
    content: '▼';
    margin-left: auto;
    font-size: 0.6em;
    transition: transform 0.3s ease;
}

.section-header:not(.collapsed)::after {
    content: '▲';
    margin-left: auto;
    font-size: 0.6em;
    transition: transform 0.3s ease;
}

.section-icon {
    font-size: 1.3em;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    border-radius: 12px;
    color: white;
}

/* ============================================
   DAY SCHEDULE - HIGHLIGHTED & ENHANCED
   ============================================ */
.day-schedule {
    border: 2px solid var(--border-color);
    border-radius: 16px;
    margin-bottom: 30px;
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.day-schedule:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}

.day-header {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    padding: 20px 25px;
    font-weight: 700;
    font-size: 1.3em;
    display: flex;
    align-items: center;
    gap: 15px;
}

.day-number {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2em;
    font-weight: 700;
    border: 2px solid white;
}

.day-content {
    padding: 25px;
    background: linear-gradient(to bottom, #ffffff, #f8fafc);
}

/* ============================================
   ACTIVITY CARDS - HIGHLIGHTED TIMES
   ============================================ */
.activity {
    display: grid;
    grid-template-columns: 120px 60px 1fr auto;
    gap: 20px;
    align-items: start;
    padding: 20px;
    margin-bottom: 15px;
    border-radius: 12px;
    background: white;
    border: 2px solid var(--border-color);
    transition: all 0.3s ease;
}

.activity:hover {
    border-color: var(--primary-color);
    transform: translateX(5px);
    box-shadow: var(--shadow-md);
}

.activity:last-child {
    margin-bottom: 0;
}

/* HIGHLIGHTED TIME */
.activity-time {
    font-weight: 700;
    font-size: 1.1em;
    color: white;
    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
    padding: 12px 15px;
    border-radius: 10px;
    text-align: center;
    box-shadow: var(--shadow);
    min-width: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.activity-icon {
    font-size: 2em;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border-radius: 50%;
    box-shadow: var(--shadow);
}

.activity-details {
    flex: 1;
}

.activity-name {
    font-weight: 700;
    font-size: 1.1em;
    margin-bottom: 8px;
    color: var(--text-color);
}

.activity-location {
    color: var(--text-muted);
    font-size: 0.95em;
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 10px;
}

.activity-cost {
    color: var(--success-color);
    font-weight: 700;
    font-size: 1.1em;
    background: #f0fdf4;
    padding: 10px 15px;
    border-radius: 8px;
    border: 2px solid #86efac;
    white-space: nowrap;
}

.activity-notes {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    padding: 12px 15px;
    border-radius: 8px;
    margin-top: 12px;
    font-size: 0.95em;
    border-left: 4px solid var(--accent-color);
    display: flex;
    align-items: start;
    gap: 8px;
}

.location-image-container {
    margin-top: 15px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow-md);
}

.location-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.location-image:hover {
    transform: scale(1.05);
}

/* ============================================
   TABLES WITH CLEAR BORDERS
   ============================================ */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 20px 0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow);
}

th, td {
    padding: 15px 20px;
    text-align: left;
    border: 2px solid var(--border-color);
    word-wrap: break-word;
    word-break: break-word;
    overflow-wrap: break-word;
    white-space: normal;
}

th {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
    font-weight: 700;
    font-size: 1.05em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

td {
    background: white;
}

tr:nth-child(even) td {
    background: #f8fafc;
}

tr:hover td {
    background: #e0f2fe;
    transition: background 0.3s ease;
}

tbody tr:first-child td {
    border-top: none;
}

tbody tr:last-child td:first-child {
    border-bottom-left-radius: 12px;
}

tbody tr:last-child td:last-child {
    border-bottom-right-radius: 12px;
}

/* ============================================
   CARDS WITH IMAGES
   ============================================ */
.card {
    border: 2px solid var(--border-color);
    border-radius: 12px;
    padding: 0;
    margin-bottom: 20px;
    overflow: hidden;
    box-shadow: var(--shadow);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    background: white;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}

.card-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}

.card-content {
    padding: 20px;
}

.card-header {
    font-weight: 700;
    font-size: 1.3em;
    margin-bottom: 12px;
    color: var(--primary-color);
}

.card-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent-color), #f97316);
    color: white;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    margin-left: 10px;
    font-weight: 600;
    box-shadow: var(--shadow-sm);
}

/* ============================================
   LISTS
   ============================================ */
.tip-list, .warning-list {
    list-style: none;
    padding: 0;
}

.tip-list li, .warning-list li {
    padding: 15px 15px 15px 50px;
    position: relative;
    border-bottom: 2px solid var(--border-color);
    background: white;
    margin-bottom: 10px;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.tip-list li:hover, .warning-list li:hover {
    background: #f0fdf4;
    transform: translateX(5px);
}

.tip-list li::before {
    content: '💡';
    position: absolute;
    left: 15px;
    font-size: 1.5em;
}

.warning-list li::before {
    content: '⚠️';
    position: absolute;
    left: 15px;
    font-size: 1.5em;
}

/* ============================================
   BUDGET VISUALIZATION
   ============================================ */
.budget-chart {
    margin: 25px 0;
}

.budget-bar {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    gap: 15px;
}

.budget-bar-label {
    min-width: 180px;
    font-weight: 600;
    color: var(--text-color);
}

.budget-bar-track {
    flex: 1;
    height: 30px;
    background: var(--border-color);
    border-radius: 15px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.budget-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary-light), var(--primary-color));
    border-radius: 15px;
    transition: width 0.6s ease;
    box-shadow: 0 0 10px rgba(37, 99, 235, 0.5);
}

.budget-bar-value {
    min-width: 140px;
    text-align: right;
    font-weight: 700;
    color: var(--primary-color);
    font-size: 1.1em;
}

.budget-total {
    font-size: 1.5em;
    font-weight: 700;
    text-align: right;
    padding: 25px;
    margin-top: 20px;
    border-top: 3px solid var(--primary-color);
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
    border-radius: 12px;
}

/* ============================================
   FOOTER
   ============================================ */
.footer {
    text-align: center;
    padding: 40px;
    color: white;
    font-size: 0.95em;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 12px;
    margin-top: 30px;
}

/* ============================================
   ACTIONS BAR
   ============================================ */
.actions {
    display: flex;
    gap: 15px;
    justify-content: center;
    margin: 25px 0;
    flex-wrap: wrap;
}

.btn {
    padding: 14px 28px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1.05em;
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
    color: white;
}

.btn-primary:hover {
    background: linear-gradient(135deg, var(--primary-dark), #1e40af);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-secondary {
    background: linear-gradient(135deg, var(--secondary-color), #475569);
    color: white;
}

.btn-secondary:hover {
    background: linear-gradient(135deg, #475569, #334155);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

/* ============================================
   HIGHLIGHTS AND BADGES
   ============================================ */
.highlight-box {
    background: linear-gradient(135deg, #dbeafe, #bfdbfe);
    border-left: 4px solid var(--primary-color);
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}

.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.85em;
    font-weight: 600;
    margin-right: 5px;
}

.badge-primary {
    color: white;
}

.badge-success {
    background: var(--success-color);
    color: white;
}

.badge-warning {
    background: var(--warning-color);
    color: white;
}

/* ============================================
   PRINT STYLES
   ============================================ */
@media print {
    body {
        background: white;
        padding: 0;
    }

    .guidebook {
        max-width: none;
        padding: 0;
    }

    .cover-page {
        page-break-after: always;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }

    .section {
        page-break-inside: avoid;
        box-shadow: none;
        border: 2px solid #ddd;
    }

    .actions, .btn {
        display: none !important;
    }

    .section-header::after {
        display: none;
    }

    .day-schedule {
        page-break-inside: avoid;
    }

    .activity {
        page-break-inside: avoid;
    }
}

/* ============================================
   MOBILE RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
    .cover-page h1 {
        font-size: 2em;
    }

    .cover-page .destination {
        font-size: 1.5em;
    }

    .trip-info {
        grid-template-columns: repeat(2, 1fr);
    }

    .activity {
        grid-template-columns: 1fr;
        gap: 15px;
    }

    .activity-time {
        justify-self: start;
    }

    table {
        display: block;
        overflow-x: auto;
    }

    .budget-bar {
        flex-direction: column;
        align-items: stretch;
    }

    .budget-bar-label,
    .budget-bar-value {
        min-width: auto;
        text-align: left;
    }
}

@media (max-width: 480px) {
    .guidebook {
        padding: 0 10px;
    }

    .section {
        padding: 20px 15px;
    }

    .trip-info {
        grid-template-columns: 1fr;
    }

    .section-header {
        font-size: 1.4em;
    }
}
"""

    def _generate_enhanced_body_content(self, labels: Dict[str, str]) -> str:
        """Generate the enhanced body content with images and styling."""
        sections = [
            self._generate_enhanced_cover_page(labels),
            self._generate_actions_html(),
            self._generate_enhanced_summary_section(labels),
            self._generate_enhanced_itinerary_section(labels),
            self._generate_enhanced_flights_section(labels),
            self._generate_enhanced_accommodation_section(labels),
            self._generate_enhanced_budget_section(labels),
            self._generate_enhanced_advisory_section(labels),
            self._generate_enhanced_souvenirs_section(labels),
            self._generate_footer_html(labels),
        ]

        return "\n".join(filter(None, sections))

    def _generate_enhanced_cover_page(self, labels: Dict[str, str]) -> str:
        """Generate enhanced cover page with hero image."""
        days_label = "ngày" if self.language == "vi" else "days"
        travelers_label = "người" if self.language == "vi" else "travelers"

        # Get hero image
        hero_image = self._get_hero_image()
        hero_image_html = ""
        if hero_image:
            hero_image_html = f'<img src="{hero_image}" alt="{sanitize_text(self.destination)}" class="cover-hero-image">'

        return f"""
        <div class="cover-page">
            {hero_image_html}
            <div class="cover-content">
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
            </div>
        </div>"""

    def _generate_actions_html(self) -> str:
        """Generate actions bar HTML."""
        return """
        <div class="actions">
            <button class="btn btn-primary" id="printBtn">🖨️ In Guidebook</button>
        </div>"""

    def _generate_enhanced_summary_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced executive summary section."""
        summary = self.itinerary.get("summary", "") if self.itinerary else ""
        location_list = self.itinerary.get("location_list", []) if self.itinerary else []

        locations_html = ""
        if location_list:
            locations_items = "".join(
                f'<li><span class="badge badge-primary">📍</span> {sanitize_text(loc)}</li>'
                for loc in location_list[:5]
            )
            locations_html = f"""
            <h3 style="color: var(--primary-color); margin-top: 25px; margin-bottom: 15px;">📍 Highlights</h3>
            <ul style="list-style: none; padding: 0;">{locations_items}</ul>"""

        budget_info = ""
        if self.budget:
            total = format_currency(self.budget.get("total_estimated_cost", 0))
            status = self.budget.get("budget_status", "N/A")
            budget_info = f"""
            <div class="highlight-box" style="margin-top: 25px;">
                <h3 style="color: var(--primary-color); margin-bottom: 10px;">💵 Tóm Tắt Ngân Sách</h3>
                <p style="font-size: 1.1em; margin: 8px 0;"><strong>{labels['total_cost']}:</strong> {total}</p>
                <p style="font-size: 1.1em; margin: 8px 0;"><strong>{labels['status']}:</strong> 
                    <span class="badge badge-success">{status}</span>
                </p>
            </div>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">📊</span>
                {labels['executive_summary']}
            </h2>
            <div class="section-content">
                <p style="font-size: 1.1em; line-height: 1.8; margin-bottom: 20px;">{sanitize_text(summary)}</p>
                {locations_html}
                {budget_info}
            </div>
        </div>"""

    def _generate_enhanced_itinerary_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced itinerary section with highlighted schedules."""
        if not self.itinerary:
            return ""

        daily_schedules = self.itinerary.get("daily_schedules", [])
        days_html = ""

        for day in daily_schedules:
            day_num = day.get("day_number", 0)
            title = day.get("title", "")
            date_str = day.get("date", "")

            header_text = f"{labels['day']} {day_num}"
            if title:
                header_text += f": {sanitize_text(title)}"

            date_badge = ""
            if date_str:
                date_badge = f'<span class="badge badge-warning">📅 {format_date(date_str)}</span>'

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

                cost_html = ""
                if cost_str:
                    cost_html = f'<div class="activity-cost">{cost_str}</div>'

                # Get location image
                location_image_html = ""
                if self.image_fetcher and location:
                    image_url = self._get_location_image(location)
                    if image_url:
                        location_image_html = f"""
                        <div class="location-image-container">
                            <img src="{image_url}" alt="{location}" class="location-image">
                        </div>"""

                activities_html += f"""
                <div class="activity">
                    <div class="activity-time">{time}</div>
                    <div class="activity-icon">{icon}</div>
                    <div class="activity-details">
                        <div class="activity-name">{name}</div>
                        <div class="activity-location">📍 {location}</div>
                        {notes_html}
                        {location_image_html}
                    </div>
                    {cost_html}
                </div>"""

            days_html += f"""
            <div class="day-schedule">
                <div class="day-header">
                    <div class="day-number">{day_num}</div>
                    <div style="flex: 1;">
                        <div>{header_text}</div>
                        {date_badge}
                    </div>
                </div>
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

    def _generate_enhanced_flights_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced flights section with images."""
        if not self.logistics:
            return ""

        flight_options = self.logistics.get("flight_options", [])
        if not flight_options:
            return ""

        flights_html = ""
        for i, flight in enumerate(flight_options):
            badge = '<span class="card-badge">⭐ Recommended</span>' if i == 0 else ""
            airline = sanitize_text(flight.get("airline", "Unknown"))
            flight_type = flight.get("flight_type", "")
            departure = flight.get("departure_time", "")
            duration = flight.get("duration", "")
            price = format_currency(flight.get("price_per_person", 0))
            cabin = flight.get("cabin_class", "")
            benefits = flight.get("benefits", [])

            benefits_html = ""
            if benefits:
                benefits_items = "".join(
                    f'<span class="badge badge-success">{sanitize_text(b)}</span> '
                    for b in benefits
                )
                benefits_html = f"<p style='margin-top: 12px;'><strong>Benefits:</strong> {benefits_items}</p>"

            flights_html += f"""
            <div class="card">
                <div class="card-content">
                    <div class="card-header">✈️ {airline} {badge}</div>
                    <table style="box-shadow: none; margin: 15px 0;">
                        <tr>
                            <th>Type</th>
                            <th>Departure</th>
                            <th>Duration</th>
                            <th>Price</th>
                            <th>Class</th>
                        </tr>
                        <tr>
                            <td>{flight_type}</td>
                            <td>{departure}</td>
                            <td>{duration}</td>
                            <td><strong>{price}</strong>/person</td>
                            <td>{cabin}</td>
                        </tr>
                    </table>
                    {benefits_html}
                </div>
            </div>"""

        # Booking tips
        tips = self.logistics.get("booking_tips", [])
        tips_html = ""
        if tips:
            tips_items = "".join(f"<li>{sanitize_text(tip)}</li>" for tip in tips)
            tips_html = f"""
            <h3 style="color: var(--primary-color); margin-top: 30px; margin-bottom: 15px;">💡 {labels['booking_tips']}</h3>
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

    def _generate_enhanced_accommodation_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced accommodation section."""
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
                amenities_badges = "".join(
                    f'<span class="badge badge-primary">{sanitize_text(a)}</span> '
                    for a in amenities
                )
                amenities_html = f"<p style='margin-top: 10px;'><strong>{labels['amenities']}:</strong><br>{amenities_badges}</p>"

            hotels_html += f"""
            <div class="card">
                <div class="card-content">
                    <div class="card-header">🏨 {name}</div>
                    <table style="box-shadow: none; margin: 15px 0;">
                        <tr>
                            <th>Type</th>
                            <th>Area</th>
                            <th>Price</th>
                        </tr>
                        <tr>
                            <td>{hotel_type}</td>
                            <td>{area}</td>
                            <td><strong>{price}</strong> {labels['per_night']}</td>
                        </tr>
                    </table>
                    {rating_html}
                    {amenities_html}
                </div>
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

    def _generate_enhanced_budget_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced budget section with visualizations."""
        if not self.budget:
            return ""

        categories = self.budget.get("categories", [])
        total = self.budget.get("total_estimated_cost", 0)
        status = self.budget.get("budget_status", "N/A")

        # Create table
        table_html = ""
        if categories:
            table_rows = ""
            for cat in categories:
                name = sanitize_text(cat.get("category_name", ""))
                cost = format_currency(cat.get("estimated_cost", 0))
                notes = sanitize_text(cat.get("notes", "")) or "-"
                table_rows += f"""
                <tr>
                    <td><strong>{name}</strong></td>
                    <td style="text-align: right;"><strong>{cost}</strong></td>
                    <td>{notes}</td>
                </tr>"""

            table_html = f"""
            <table>
                <thead>
                    <tr>
                        <th>{labels['category']}</th>
                        <th style="text-align: right;">{labels['estimated']}</th>
                        <th>{labels['notes']}</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>"""

        # Budget bars visualization
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
            <h3 style="color: var(--primary-color); margin-top: 30px; margin-bottom: 15px;">💡 {labels['recommendations']}</h3>
            <ul class="tip-list">{items}</ul>"""

        return f"""
        <div class="section">
            <h2 class="section-header">
                <span class="section-icon">💰</span>
                {labels['budget']}
            </h2>
            <div class="section-content">
                {table_html}
                <div class="budget-chart">
                    <h3 style="color: var(--primary-color); margin: 25px 0 20px;">📊 Budget Visualization</h3>
                    {budget_bars_html}
                </div>
                <div class="budget-total">
                    {labels['total_cost']}: {format_currency(total)}<br>
                    <span style="font-size: 0.7em; color: var(--text-muted);">
                        {labels['status']}: <span class="badge badge-success">{status}</span>
                    </span>
                </div>
                {recommendations_html}
            </div>
        </div>"""

    def _generate_enhanced_advisory_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced advisory section."""
        if not self.advisory:
            return ""

        warnings = self.advisory.get("warnings_and_tips", [])
        warnings_html = ""
        if warnings:
            items = "".join(f"<li>{sanitize_text(w)}</li>" for w in warnings)
            warnings_html = f"""
            <h3 style="color: var(--danger-color); margin-bottom: 15px;">📢 {labels['warnings']}</h3>
            <ul class="warning-list">{items}</ul>"""

        visa_info = self.advisory.get("visa_info", "")
        visa_html = ""
        if visa_info:
            visa_html = f"""
            <div class="highlight-box" style="margin-top: 25px;">
                <h3 style="color: var(--primary-color); margin-bottom: 10px;">🛂 {labels['visa_info']}</h3>
                <p style="line-height: 1.8;">{sanitize_text(visa_info)}</p>
            </div>"""

        weather_info = self.advisory.get("weather_info", "")
        weather_html = ""
        if weather_info:
            weather_html = f"""
            <div class="highlight-box" style="margin-top: 25px; background: linear-gradient(135deg, #dbeafe, #bfdbfe);">
                <h3 style="color: var(--primary-color); margin-bottom: 10px;">🌤️ {labels['weather_info']}</h3>
                <p style="line-height: 1.8;">{sanitize_text(weather_info)}</p>
            </div>"""

        safety_tips = self.advisory.get("safety_tips", [])
        safety_html = ""
        if safety_tips:
            items = "".join(f"<li>{sanitize_text(t)}</li>" for t in safety_tips)
            safety_html = f"""
            <h3 style="color: var(--success-color); margin-top: 25px; margin-bottom: 15px;">🛡️ {labels['safety_tips']}</h3>
            <ul class="tip-list">{items}</ul>"""

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

    def _generate_enhanced_souvenirs_section(self, labels: Dict[str, str]) -> str:
        """Generate enhanced souvenirs section."""
        if not self.souvenirs:
            return ""

        souvenirs_html = ""
        for souvenir in self.souvenirs:
            name = sanitize_text(souvenir.get("item_name", ""))
            description = sanitize_text(souvenir.get("description", ""))
            price = souvenir.get("estimated_price", "")
            where = souvenir.get("where_to_buy", "")

            price_html = (
                f"<p style='margin: 10px 0;'><strong>{labels['price']}:</strong> "
                f"<span class='badge badge-success'>{price}</span></p>"
                if price
                else ""
            )
            where_html = (
                f"<p style='margin: 10px 0;'><strong>{labels['where_to_buy']}:</strong> {sanitize_text(where)}</p>"
                if where
                else ""
            )

            souvenirs_html += f"""
            <div class="card">
                <div class="card-content">
                    <div class="card-header">🛍️ {name}</div>
                    <p style="line-height: 1.8; margin-bottom: 15px;">{description}</p>
                    {price_html}
                    {where_html}
                </div>
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
            <p style="margin-bottom: 10px; font-size: 1.1em;">✨ {labels['generated_at']}: {generated_date}</p>
            <p style="opacity: 0.8;">NaviAgent Travel Guidebook v{self.version}</p>
            <p style="margin-top: 15px; opacity: 0.7;">Made with ❤️ for your perfect journey</p>
        </div>"""