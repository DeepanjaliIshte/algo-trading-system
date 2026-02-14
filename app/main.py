import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

# Import all models BEFORE create_all
from app.models import user, strategy, order, trade

# Import routers
from app.routers import auth, strategies


# ----------------------------
# Logging Configuration
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ----------------------------
# Create Database Tables
# ----------------------------
Base.metadata.create_all(bind=engine)


# ----------------------------
# FastAPI App Instance
# ----------------------------
app = FastAPI(
    title="Algo Trading SaaS API",
    description="Production-style API for algorithmic trading platform",
    version="1.0.0",
)


# ----------------------------
# CORS Middleware
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Register Routers
# ----------------------------
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])


# ----------------------------
# Health Check Endpoint
# ----------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "Algo Trading SaaS API"}
