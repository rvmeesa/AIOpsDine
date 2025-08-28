# AIOpsDine 🍽️

## Overview
Welcome to **AIOpsDine**, an innovative AI-powered restaurant management system. This project harnesses a multi-agent architecture with NLP, Computer Vision, and ML to streamline table management, order processing, and customer recommendations, featuring a user-friendly Streamlit frontend.

## Features
- **Multi-Agent System**: Agents for FAQ, Vision, Order Management, Recommendations, and Analytics.
- **Real-Time Operations**: Detect empty tables, assign seats, and suggest upsells dynamically.
- **NLP Integration**: Answer queries and parse orders using LangChain and OpenAI.
- **Computer Vision**: Monitor table status and cleanliness with OpenCV/YOLO.
- **Streamlit Frontend**: Interactive UI for real-time management and visualization.
- **Scalable Architecture**: Built with FastAPI, SQLite/Postgres, and asyncio.

## Architecture
### System Diagram

           [Clients: Streamlit UI / Web App]
                      ↓
           [FastAPI Backend (REST API)]
                      ↓
           [Orchestrator <--> Message Bus]
                      ↓
           [Agents: FAQ, Vision, Order, Reco, Analytics]
                      ↓
           [Data: SQL DB, Object Storage, Models]

- **Orchestrator**: Coordinates agent workflows (e.g., table assignment).
- **Agents**: Handle specialized tasks with clear I/O contracts.
- **Data**: Stores orders, reservations, and analytics in a modular database.
- **Frontend**: Streamlit UI for interactive control and monitoring.

## Setup
1. Clone the repo: `git clone <repository-URL>`
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables (e.g., `OPENAI_API_KEY`) in a `.env` file.
4. Initialize the DB: `python db/seed.py`
5. Run the backend: `uvicorn app.main:app --reload`
6. Run the frontend: `streamlit run frontend/app.py`

## Usage
- **API Endpoints**: Access via `/api/faq/query`, `/api/vision/ingest`, etc. (see `/docs`).
- **Streamlit UI**: Launch `frontend/app.py` to manage tables, orders, and analytics interactively.
- **Simulation**: Use `simulations/` scripts to test vision and order flows.

## Tech Stack
- **Backend**: FastAPI, Python asyncio
- **NLP**: LangChain, OpenAI
- **Vision**: OpenCV, YOLOv8
- **ML**: scikit-learn
- **Database**: SQLite (MVP), Postgres (prod)
- **Frontend**: Streamlit
- **UI Styling**: Streamlit components
