# Flask Web Interface — Project Risk Assessment Agent

This document describes the **Flask web interface** for the Project Risk Assessment Agent.
For the Streamlit interface, see `streamlit_app.py`.

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Flask app

```bash
python app.py
```

### 3. Open in browser

Navigate to **http://localhost:5000**

---

## Features

| Feature | Details |
|---------|---------|
| **Home page** | Introduction, feature overview, and "Start Assessment" button |
| **Interview form** | Four-section form — background, risk focus, decision style, time pressure |
| **Risk report** | Full HTML report with sortable risk table, frameworks, checklists |
| **PDF export** | Download the report as a professionally formatted PDF |
| **Progress indicator** | Live progress bar as you fill in the form |
| **Pre-fill support** | Navigating back to the form pre-fills previous answers |
| **Responsive design** | Works on desktop, tablet, and mobile |

---

## User Flow

```
http://localhost:5000           ← Home page
        ↓ "Start Assessment"
/interview                      ← Fill in the four-section form
        ↓ "Generate Report"
/generate-report (POST)         ← Validates and stores form data
        ↓ redirect
/report                         ← Beautiful HTML report
        ↓ "Download PDF"
/download-pdf                   ← PDF file download
```

---

## Routes

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/` | Home page |
| `GET` | `/interview` | Interview form (pre-filled from session if available) |
| `POST` | `/generate-report` | Process form data → redirect to `/report` |
| `GET` | `/report` | Display the assessment report |
| `GET` | `/download-pdf` | Download report as PDF (requires `reportlab`) |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `risk-assessment-dev-key-change-in-production` | Flask session secret key — **change for production** |

Set it in your shell:

```bash
export SECRET_KEY="your-secure-random-key-here"
python app.py
```

---

## PDF Export

PDF generation requires the `reportlab` package (included in `requirements.txt`).

If `reportlab` is not installed, the `/download-pdf` route falls back to a plain `.txt` download.

---

## Running Both Interfaces

You can run both the Flask and Streamlit interfaces simultaneously:

```bash
# Terminal 1 — Flask (port 5000)
python app.py

# Terminal 2 — Streamlit (port 8501)
streamlit run streamlit_app.py
```

---

## CLI Interface

The command-line interface is unaffected:

```bash
# Interactive CLI
python main.py

# Demo mode (no input required)
python main.py --demo
```

---

## No Breaking Changes

- `agent/` folder is completely untouched
- CLI (`main.py`) still works as before
- Streamlit interface moved to `streamlit_app.py`
- Flask interface added as `app.py`
