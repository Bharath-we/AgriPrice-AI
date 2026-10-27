"""
AgriPrice AI: FastAPI Application Entrypoint
Tamil Nadu Agricultural Commodity Price Prediction Engine
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, APP_VERSION, API_PREFIX, CORS_ORIGINS
from app.api.router import api_router
from app.ml.predictor import AgriPricePredictor

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event: initialize the Scikit-learn model and dataset cache on startup.
    """
    print(f"Starting {APP_NAME} v{APP_VERSION}...")
    try:
        predictor = AgriPricePredictor()
        print(f"[Startup] ML Model ready. Algorithm: {predictor.metrics.get('algorithm')}")
    except Exception as e:
        print(f"[Startup Warning] ML model initialization will complete on first request: {e}")
    yield
    print(f"Shutting down {APP_NAME}...")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Intermediate Full-Stack AI System for Agricultural Commodity Price Prediction in Tamil Nadu, India.",
    lifespan=lifespan,
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount central API routes
app.include_router(api_router, prefix=API_PREFIX)

@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "region": "Tamil Nadu, India",
        "docs_url": "/docs",
        "health_check": f"{API_PREFIX}/health",
    }

@app.get(f"{API_PREFIX}/health")
def health_check():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
    }
