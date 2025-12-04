# Guidebook Generation Guide

This guide explains how to use the NaviAgent Guidebook Generation module to create professional, printable travel guidebooks from travel plan data.

## Overview

The Guidebook Generator transforms travel plan JSON data (from `travel_plan_output.json`) into professional guidebooks in multiple formats:

- **PDF**: Print-ready documents with table of contents, page numbers, and professional typography
- **HTML**: Responsive web pages with interactive elements and print support
- **Markdown**: Clean, readable markdown with GitHub-flavored formatting

## Quick Start

### Using Python

```python
from travel_planner.guidebook import GuidebookGenerator

# From a JSON file
generator = GuidebookGenerator.from_file("travel_plan_output.json")
files = generator.generate_all_formats()
print(files)
# {'pdf': 'guidebooks/guidebook_tokyo.pdf', 
#  'html': 'guidebooks/guidebook_tokyo.html', 
#  'markdown': 'guidebooks/guidebook_tokyo.md'}

# From a TravelPlan object
from schemas.response import TravelPlan
travel_plan = TravelPlan(...)
generator = GuidebookGenerator(travel_plan.model_dump())
pdf_path = generator.generate_pdf()
```

### Using the API

```bash
# Generate guidebook from travel plan
curl -X POST "http://localhost:8000/v1/generate_guidebook" \
  -H "Content-Type: application/json" \
  -d '{
    "travel_plan": {...},
    "formats": ["pdf", "html", "markdown"],
    "language": "vi"
  }'

# Response
{
  "guidebook_id": "uuid",
  "files": {
    "pdf": "guidebooks/guidebook_tokyo.pdf",
    "html": "guidebooks/guidebook_tokyo.html",
    "markdown": "guidebooks/guidebook_tokyo.md"
  },
  "generated_at": "2024-06-01T10:30:00"
}

# Download a specific format
curl "http://localhost:8000/v1/guidebook/{guidebook_id}/download?format=pdf" \
  --output guidebook.pdf
```

## Guidebook Contents

Each guidebook includes the following sections:

### 1. Cover Page
- Destination name
- Trip dates and duration
- Number of travelers
- Budget

### 2. Executive Summary
- Trip overview
- Key highlights
- Budget summary

### 3. Detailed Itinerary
- Day-by-day schedule
- Activities with times
- Locations with addresses
- Cost estimates
- Tips and notes

### 4. Flight Information
- Selected flight details
- Alternative options
- Booking tips
- Visa requirements

### 5. Accommodation
- Selected hotel details
- Alternative recommendations
- Best areas to stay
- Booking tips

### 6. Budget Breakdown
- Cost by category (flights, accommodation, food, activities)
- Visual breakdown
- Total vs budget comparison
- Saving recommendations

### 7. Advisory & Warnings
- Important warnings
- Location descriptions
- Visa information
- Weather forecast
- Safety tips
- Recommended SIM cards and apps

### 8. Souvenir Suggestions
- Recommended items
- Estimated prices
- Where to buy

### 9. Appendix
- Packing list checklist
- Emergency contacts

## Configuration Options

### Language Support

The guidebook supports Vietnamese (`vi`) and English (`en`):

```python
# Vietnamese (default)
generator = GuidebookGenerator(data, language="vi")

# English
generator = GuidebookGenerator(data, language="en")
```

### Output Directory

Specify a custom output directory:

```python
generator = GuidebookGenerator(
    travel_plan_data=data,
    output_dir="my_guidebooks"
)
```

### Specific Formats

Generate only specific formats:

```python
# Only PDF and HTML
files = generator.generate_all_formats(formats=["pdf", "html"])

# Only Markdown
md_path = generator.generate_markdown()
```

## API Reference

### GuidebookGenerator Class

```python
class GuidebookGenerator:
    def __init__(
        self,
        travel_plan_data: Dict[str, Any],
        output_dir: str = "guidebooks",
        language: str = "vi"
    ):
        """
        Initialize the GuidebookGenerator.
        
        Args:
            travel_plan_data: Dictionary containing travel plan data
            output_dir: Directory to save generated guidebooks
            language: Language for content ("vi" or "en")
        """
        
    @classmethod
    def from_file(cls, file_path: str, output_dir: str = "guidebooks", language: str = "vi"):
        """Create generator from a JSON file."""
        
    def generate_all_formats(self, formats: List[str] = None) -> Dict[str, str]:
        """Generate guidebooks in all specified formats."""
        
    def generate_pdf(self, output_path: str = None) -> str:
        """Generate PDF guidebook."""
        
    def generate_html(self, output_path: str = None) -> str:
        """Generate HTML guidebook."""
        
    def generate_markdown(self, output_path: str = None) -> str:
        """Generate Markdown guidebook."""
        
    def get_guidebook_response(self) -> Dict[str, Any]:
        """Get structured response with guidebook information."""
```

### API Endpoints

#### POST /v1/generate_guidebook

Generate a travel guidebook from a travel plan.

**Request Body:**
```json
{
  "travel_plan": {
    "version": "1.0",
    "request_summary": {...},
    "itinerary": {...},
    "budget": {...},
    "advisory": {...},
    "souvenirs": [...],
    "logistics": {...},
    "accommodation": {...}
  },
  "formats": ["pdf", "html", "markdown"],
  "language": "vi"
}
```

**Response:**
```json
{
  "guidebook_id": "uuid-string",
  "files": {
    "pdf": "guidebooks/guidebook_destination.pdf",
    "html": "guidebooks/guidebook_destination.html",
    "markdown": "guidebooks/guidebook_destination.md"
  },
  "generated_at": "2024-06-01T10:30:00+00:00",
  "language": "vi",
  "output_dir": "guidebooks"
}
```

#### GET /v1/guidebook/{guidebook_id}

Get information about a previously generated guidebook.

#### GET /v1/guidebook/{guidebook_id}/download?format=pdf

Download a specific guidebook file. Supported formats: `pdf`, `html`, `markdown`

## Travel Plan Data Structure

The guidebook generator expects data in the following structure:

```json
{
  "version": "1.0",
  "request_summary": {
    "destination": "Tokyo, Japan",
    "duration": 7,
    "budget": 50000000,
    "travelers": 2
  },
  "itinerary": {
    "daily_schedules": [
      {
        "day_number": 1,
        "date": "2024-06-01",
        "title": "Day Title",
        "activities": [
          {
            "time": "08:00 - 10:00",
            "location_name": "Location",
            "address": "Full address",
            "activity_type": "sightseeing",
            "description": "Description",
            "estimated_cost": 1000,
            "notes": "Tips"
          }
        ]
      }
    ],
    "location_list": ["Location 1", "Location 2"],
    "summary": "Trip summary",
    "selected_flight": {...},
    "selected_accommodation": {...}
  },
  "budget": {
    "categories": [...],
    "total_estimated_cost": 49000000,
    "budget_status": "Within budget",
    "recommendations": [...]
  },
  "advisory": {
    "warnings_and_tips": [...],
    "location_descriptions": [...],
    "visa_info": "...",
    "weather_info": "...",
    "sim_and_apps": [...],
    "safety_tips": [...]
  },
  "souvenirs": [...],
  "logistics": {...},
  "accommodation": {...}
}
```

## PDF Format Details

The PDF guidebook features:
- **A4 page size** - Standard print format
- **Professional typography** - Clean, readable fonts
- **Color-coded sections** - Easy navigation
- **Headers and footers** - Destination name and page numbers
- **Print-ready** - Optimized for printing

## HTML Format Details

The HTML guidebook features:
- **Responsive design** - Works on desktop and mobile
- **Modern styling** - Clean, professional appearance
- **Interactive elements** - Collapsible sections
- **Print support** - CSS media queries for printing
- **Print button** - One-click printing

## Markdown Format Details

The Markdown guidebook features:
- **GitHub-flavored markdown** - Tables, checkboxes, emojis
- **Clean formatting** - Easy to read and edit
- **Copy-paste friendly** - Use in documents, emails
- **Table of contents** - Anchor links to sections

## Error Handling

The generator validates input data and provides clear error messages:

```python
# Empty data
GuidebookGenerator({})
# ValueError: Travel plan must contain at least one section of data

# Invalid type
GuidebookGenerator("not a dict")
# ValueError: Travel plan data must be a dictionary

# File not found
GuidebookGenerator.from_file("missing.json")
# FileNotFoundError: Travel plan file not found: missing.json
```

## Performance

- **Generation time**: < 5 seconds for typical guidebooks
- **Memory usage**: < 500MB for PDF generation
- **File sizes**: 
  - PDF: ~100KB-1MB depending on content
  - HTML: ~20-50KB
  - Markdown: ~10-30KB

## Testing

Run the guidebook tests:

```bash
cd /path/to/NaviAgent
uv run pytest tests/test_guidebook.py -v
```

## Troubleshooting

### PDF not generating
- Ensure `reportlab` is installed: `pip install reportlab>=4.0.0`
- Check for sufficient disk space
- Verify write permissions in output directory

### Unicode/Vietnamese text issues
- Ensure files are saved with UTF-8 encoding
- Use proper locale settings

### HTML not styling correctly
- Clear browser cache
- Check if CSS file is in the correct location
- Verify template path configuration

## Future Enhancements

Planned features for future releases:
- Custom template support
- Map integration (Google Maps Static API)
- QR codes for booking links
- Multi-language auto-translation
- Image inclusion
- Custom branding/logo support
