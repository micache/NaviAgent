# API Usage Guide

## Installation

Install FastAPI dependencies:
```bash
pip install -r requirements-api.txt
```

## Running the API

Start the server:
```bash
cd src
python main.py
```

Or with uvicorn directly:
```bash
cd src
uvicorn naviagent.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, access:
- Interactive API docs (Swagger): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Endpoints

### 1. Start a Session
```bash
POST /session/start?session_id=user123
```

Response:
```json
{
  "session_id": "user123",
  "message": "Hello! Welcome to NaviAgent Travel Service...",
  "state": "ask_destination"
}
```

### 2. Send Message
```bash
POST /message
Content-Type: application/json

{
  "session_id": "user123",
  "message": "I want a peaceful place with mountains",
  "image_url": null
}
```

Response:
```json
{
  "session_id": "user123",
  "response": "Based on your description, I recommend Da Lat, Vietnam...",
  "state": "confirm_destination",
  "travel_data": {
    "destination": "Da Lat, Vietnam",
    "departure_point": null,
    ...
  }
}
```

### 3. Send Image URL
```bash
POST /message
Content-Type: application/json

{
  "session_id": "user123",
  "message": "image provided",
  "image_url": "https://example.com/tower.jpg"
}
```

### 4. Get Session Status
```bash
GET /session/user123/status
```

Response:
```json
{
  "session_id": "user123",
  "state": "collect_travel_date",
  "travel_data": {
    "destination": "Da Lat, Vietnam",
    "departure_point": "Hanoi",
    "travel_date": null,
    ...
  },
  "is_completed": false
}
```

### 5. Reset Session
```bash
POST /session/reset?session_id=user123
```

### 6. End Session
```bash
DELETE /session/user123
```

### 7. List Active Sessions
```bash
GET /sessions
```

### 8. Health Check
```bash
GET /health
```

## Example Workflow

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"
session_id = "user_12345"

# 1. Start session
response = requests.post(f"{BASE_URL}/session/start?session_id={session_id}")
print(response.json())

# 2. Customer says they don't have a destination
response = requests.post(
    f"{BASE_URL}/message",
    json={
        "session_id": session_id,
        "message": "No, I need suggestions"
    }
)
print(response.json()["response"])

# 3. Customer describes their ideal trip
response = requests.post(
    f"{BASE_URL}/message",
    json={
        "session_id": session_id,
        "message": "I want mountains, cool weather, and pine trees"
    }
)
print(response.json()["response"])

# 4. Customer confirms destination
response = requests.post(
    f"{BASE_URL}/message",
    json={
        "session_id": session_id,
        "message": "yes"
    }
)
print(response.json()["response"])

# 5. Continue collecting information
responses = [
    "Hanoi",           # departure
    "December 25th",   # travel date
    "5 days",          # length of stay
    "2 people",        # guests
    "1000 USD",        # budget
    "independent",     # travel style
    "none"             # special notes
]

for msg in responses:
    response = requests.post(
        f"{BASE_URL}/message",
        json={
            "session_id": session_id,
            "message": msg
        }
    )
    print(response.json()["response"])

# 6. Confirm final details
response = requests.post(
    f"{BASE_URL}/message",
    json={
        "session_id": session_id,
        "message": "yes, looks perfect"
    }
)
print(response.json()["response"])

# 7. Get final travel data
response = requests.get(f"{BASE_URL}/session/{session_id}/status")
print(response.json()["travel_data"])

# 8. End session
requests.delete(f"{BASE_URL}/session/{session_id}")
```

### JavaScript/Fetch Example

```javascript
const BASE_URL = 'http://localhost:8000';
const sessionId = 'user_12345';

// Start session
async function startSession() {
  const response = await fetch(`${BASE_URL}/session/start?session_id=${sessionId}`, {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data.message);
}

// Send message
async function sendMessage(message, imageUrl = null) {
  const response = await fetch(`${BASE_URL}/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      image_url: imageUrl
    })
  });
  const data = await response.json();
  console.log(data.response);
  return data;
}

// Usage
await startSession();
await sendMessage("No, I need help");
await sendMessage("I want a beach with good food");
await sendMessage("yes");
// Continue conversation...
```

### cURL Examples

```bash
# Start session
curl -X POST "http://localhost:8000/session/start?session_id=user123"

# Send message
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "I want mountains and cool weather"
  }'

# Send image
curl -X POST "http://localhost:8000/message" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "image provided",
    "image_url": "https://example.com/tower.jpg"
  }'

# Get status
curl "http://localhost:8000/session/user123/status"

# List sessions
curl "http://localhost:8000/sessions"

# Health check
curl "http://localhost:8000/health"
```

## Guidebook Generation

### Generate Guidebook
```bash
POST /v1/generate_guidebook
Content-Type: application/json

{
  "travel_plan": {
    "version": "1.0",
    "request_summary": {
      "destination": "Tokyo, Japan",
      "duration": 7,
      "budget": 50000000,
      "travelers": 2
    },
    "itinerary": {...},
    "budget": {...},
    "advisory": {...}
  },
  "formats": ["pdf", "html", "markdown"],
  "language": "vi"
}
```

Response:
```json
{
  "guidebook_id": "uuid-string",
  "files": {
    "pdf": "guidebooks/guidebook_tokyo.pdf",
    "html": "guidebooks/guidebook_tokyo.html",
    "markdown": "guidebooks/guidebook_tokyo.md"
  },
  "generated_at": "2024-06-01T10:30:00+00:00",
  "language": "vi",
  "output_dir": "guidebooks"
}
```

### Get Guidebook Info
```bash
GET /v1/guidebook/{guidebook_id}
```

### Download Guidebook
```bash
GET /v1/guidebook/{guidebook_id}/download?format=pdf
```

Supported formats: `pdf`, `html`, `markdown`

### cURL Example
```bash
# Generate guidebook
curl -X POST "http://localhost:8000/v1/generate_guidebook" \
  -H "Content-Type: application/json" \
  -d '{"travel_plan": {...}, "formats": ["pdf"], "language": "vi"}'

# Download PDF
curl "http://localhost:8000/v1/guidebook/{id}/download?format=pdf" --output guidebook.pdf
```

For detailed guidebook documentation, see [docs/GUIDEBOOK_GUIDE.md](docs/GUIDEBOOK_GUIDE.md).

## Features

- **Session Management**: Multiple concurrent user sessions
- **State Tracking**: Automatic conversation state management
- **Image Support**: Send image URLs for destination identification
- **CORS Enabled**: Ready for frontend integration
- **Error Handling**: Proper HTTP error codes and messages
- **Interactive Docs**: Auto-generated API documentation
- **Guidebook Generation**: Generate PDF, HTML, and Markdown guidebooks

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (e.g., session already exists)
- `404`: Session not found
- `500`: Internal server error

## Production Deployment

For production, use a production ASGI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or with Gunicorn:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
