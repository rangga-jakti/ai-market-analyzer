# AI Market Trend Analyzer

Aplikasi web untuk menganalisis peluang bisnis berdasarkan data Google Trends.

## Tech Stack

- **Backend**: Django 6 + Python 3.12
- **Database**: PostgreSQL
- **Data**: pytrends (Google Trends API)
- **Frontend**: Django Templates + CSS (Dark UI)
- **Charts**: Chart.js

## Fitur

- Analisis tren pasar berdasarkan keyword
- Trend Score algoritma multi-faktor (0–100)
- Grafik tren interaktif 3 bulan terakhir
- AI Business Insight otomatis
- Dashboard riwayat analisis
- UI premium dengan animasi

## Cara Install

### 1. Clone repository
git clone https://github.com/username/ai-market-analyzer.git
cd ai-market-analyzer

### 2. Buat virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Setup database PostgreSQL
psql -U postgres
CREATE DATABASE market_analyzer_db;
CREATE USER market_analyzer_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE market_analyzer_db TO market_analyzer_user;
\q

### 5. Konfigurasi environment
cp .env.example .env
# Edit .env dengan kredensial database kamu

### 6. Jalankan migrasi
python manage.py migrate

### 7. Buat superuser
python manage.py createsuperuser

### 8. Jalankan server
python manage.py runserver

Buka http://127.0.0.1:8000

## Struktur Project

ai-market-analyzer/
├── apps/analyzer/      # Django app utama
├── services/           # Business logic layer
│   ├── trend_service.py
│   ├── scoring_service.py
│   ├── ai_service.py
│   └── analysis_service.py
├── templates/          # HTML templates
├── static/css/         # Stylesheet
├── config/             # Django settings
└── requirements.txt