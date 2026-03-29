# LeadForge AI Scraper Platform

An automated lead generation and scraping engine built with FastAPI and React.

## Features
- **Discovery Engine:** Automatically find businesses based on keyword and location.
- **Deep Scraper:** Extracts emails, phone numbers, and social links from company websites.
- **AI Analytics:** Uses Google Gemini AI to analyze business models and generate sales pitches.
- **Data Vault:** Manage and export leads in CSV/JSON format.

## Tech Stack
- **Frontend:** React, Vite, Tailwind CSS, Framer Motion
- **Backend:** Python FastAPI, SQLAlchemy (SQLite)
- **AI:** Google Gemini API
- **Scraper:** Custom HTML Parser with RegEx extraction

## Local Setup

### Prerequisites
- Python 3.9+
- Node.js & npm

### Backend Configuration
1. Navigate to `/backend`
2. Create a `.env` file:
   ```env
   GEMINI_API_KEY=your_key_here
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8880 --reload
   ```

### Frontend Configuration
1. Navigate to `/frontend`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run development server:
   ```bash
   npm run dev
   ```

## License
MIT
