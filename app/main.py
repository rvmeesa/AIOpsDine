from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routers import health, faq, vision, orders, reco, analytics ,tables
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Restaurant Manager API", description="SaaS backend for restaurant operations", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health, prefix="/api", tags=["Health"])
app.include_router(faq, prefix="/api/faq", tags=["FAQ"])
app.include_router(vision, prefix="/api", tags=["Vision"])
app.include_router(orders, prefix="/api", tags=["Orders"])
app.include_router(reco, tags=["Recommendations"])
app.include_router(analytics, prefix="/api", tags=["Analytics"])
app.include_router(tables.router, prefix="/api/tables")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Restaurant Manager API...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AI Restaurant Manager API...")