# 🚌 Buszerk

Smart Bus Management System for efficient route tracking, scheduling, and real-time passenger updates.
<!-- BADGES ROW 1 — Tech -->
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

<br/>

<!-- BADGES ROW 2 — Repo stats (auto-updating) -->
![GitHub last commit](https://img.shields.io/github/last-commit/Kumar070204/BUSZerk?style=flat-square&color=e94560)
![GitHub repo size](https://img.shields.io/github/repo-size/Kumar070204/BUSZerk?style=flat-square&color=0f3460)
![GitHub stars](https://img.shields.io/github/stars/Kumar070204/BUSZerk?style=flat-square&color=e94560)
![License](https://img.shields.io/github/license/Kumar070204/BUSZerk?style=flat-square&color=0f3460)

<br/>

> **Built for Chennai's MTC network** · Real-time crowd prediction · SOS alerts · Fake call escape · AI chatbot

</div>

---

## What is BUSZerk?

BUSZerk is a **women's safety + smart transit app** built specifically for Chennai's government bus system (MTC). It solves two problems that Chennai women face daily: not knowing if a bus is dangerously overcrowded before boarding, and having no quick safety escape when needed.

The core intelligence is an **XGBoost model trained on real MTC ticketing data** that predicts passenger load at each stop in real time. Layered on top are an SOS SMS system, a fake incoming call trigger, live bus tracking, and a Gemini-powered chatbot — all in one Flask + Firebase app, containerized with Docker.

---


## Features

| Feature | What it does |
|---|---|
| 🚌 **Smart Bus Feed** | Shows upcoming buses on your route with ETAs |
| 📊 **Crowd Prediction** | XGBoost model predicts passenger load stop-by-stop using real MTC data |
| 🆘 **SOS Alert** | One tap sends your GPS coordinates via SMS to an emergency contact (Fast2SMS API) |
| 📞 **Fake Call** | Schedules a fake incoming call in 5 seconds — instant exit from unsafe situations |
| 🗺️ **Bus Tracking** | Live tracking view tied to your Firebase profile |
| 🤖 **AI Chatbot** | Gemini-powered assistant for route queries and safety guidance |
| 🔐 **Auth** | Firebase Authentication + Firestore user profiles |

---

## How the ML model works

```mermaid
graph TD
    A[MTC Ticket Dataset\nBoarding stop · Destination · Time · Weather] --> B[Feature Engineering\nOne-hot encode stops & routes]
    B --> C[XGBoost Regressor\nTrained on historical passenger flow]
    C --> D[Predicted waiting passengers\nat each upcoming stop]
    D --> E[Real-time seat availability\ncalculated per stop]
    E --> F[Displayed in Bus Detail view\nbefore you board]
```

The model is loaded from `xgb_model.pkl` at startup and runs inference on each stop when a user views bus details. Random simulation for boarding/alighting is layered on top to reflect real bus dynamics.

---

## Architecture

```mermaid
graph LR
    subgraph Frontend
        A[Jinja2 Templates\nHTML · CSS · JS]
    end

    subgraph Backend
        B[Flask App\napp.py]
        C[XGBoost Model\nxgb_model.pkl]
        D[SOS SMS\nFast2SMS API]
        E[Fake Call\nThreading Timer]
    end

    subgraph Cloud
        F[Firebase Auth]
        G[Firestore DB\nUser profiles]
        H[Google Gemini\nChatbot]
    end

    A -->|HTTP| B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    B --> H
```

---

## Project structure

```
BUSZerk/
├── app.py                  # Flask routes + ML inference + SOS logic
├── BUSZERK1_.ipynb         # Model training notebook (XGBoost on MTC data)
├── MTC_TICKET_MON1.csv     # Real MTC ticketing dataset
├── xgb_model.pkl           # Trained XGBoost model
├── feature_columns.pkl     # Saved feature schema for inference
├── Dockerfile              # Multi-stage Docker build
├── templates/
│   ├── home.html           # Bus feed + route search
│   ├── bus_details.html    # Stop-by-stop crowd prediction
│   ├── sos.html            # SOS trigger page
│   ├── fake_call.html      # Fake call interface
│   ├── bus_tracking.html   # Live tracking
│   ├── chatbot.html        # Gemini chatbot
│   ├── login.html
│   └── signup.html
└── node_modules/
    └── @google/generative-ai   # Gemini SDK
```

---

## Getting started

### Prerequisites
- Python 3.9+
- Docker (optional but recommended)
- Firebase project with Authentication + Firestore enabled
- Fast2SMS API key
- Google Gemini API key

### Run locally

```bash
# Clone the repo
git clone https://github.com/Kumar070204/BUSZerk.git
cd BUSZerk/Buszerk-main

# Install dependencies
pip install -r requirements.txt

# Add your Firebase service account key
# → Drop buszerk-a24ab-firebase-adminsdk-*.json into the project root

# Run
python app.py
```

App runs at `http://localhost:5000`

### Run with Docker

```bash
docker build -t buszerk .
docker run -p 5000:5000 buszerk
```

---

## Dataset

Training data is sourced from **MTC (Metropolitan Transport Corporation) Chennai** ticket logs — `MTC_TICKET_MON1.csv`. Fields include:

| Column | Description |
|---|---|
| `Bus_ID` | MTC bus identifier |
| `Route_ID` | Route number |
| `Boarding_Stop` | Passenger origin stop |
| `Destination_Stop` | Passenger destination |
| `Day_of_Week` | Monday–Sunday |
| `Time` | Departure time slot |
| `Weather` | Weather condition at time of journey |

The XGBoost model is trained in `BUSZERK1_.ipynb` — see the notebook for preprocessing steps, feature engineering, and evaluation metrics.

---

## API reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET/POST | Home — bus feed, route search |
| `/bus/<id>` | GET | Stop-by-stop crowd prediction for a bus |
| `/send_sos` | POST | Trigger SOS SMS with lat/lng |
| `/trigger_call` | POST | Schedule fake incoming call |
| `/check_call` | GET | Poll call status |
| `/chatbot` | GET | Gemini AI chatbot interface |
| `/bus_tracking` | GET | Live bus tracking view |
| `/login` `/signup` `/logout` | GET/POST | Auth flows |

---

## Built by

**Kumaraswamy G** — ML & GenAI Developer, VIT Chennai

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/kumaraswamy-g-872b81277/)
[![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:kumaraswamy2004@gmail.com)

---

