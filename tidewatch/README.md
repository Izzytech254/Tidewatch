# TideWatch 🌊

**Know your flood risk before the water knows your address.**

A real-time, personalized flood risk dashboard for Norfolk, VA residents and businesses. Combines NOAA tide data, NWS weather forecasts, and USGS elevation data into a single, actionable risk score.

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** React, Mapbox GL JS
- **APIs:** NOAA Tides & Currents, National Weather Service, USGS Elevation
- **Notifications:** Twilio (SMS alerts)

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env  # Add your Mapbox token
npm run dev
```

## Project Structure

```
tidewatch/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── config.py          # Settings & env vars
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # External API clients
│   │   ├── engine/            # Risk scoring engine
│   │   └── models/            # Pydantic models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API client
│   │   └── utils/             # Helpers
│   ├── package.json
│   └── .env.example
└── README.md
```

## License

MIT
