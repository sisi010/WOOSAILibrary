# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import profiles, admin, chat, payment

app = FastAPI(
    title="WoosAI Cloud API",
    description="MongoDB-based cloud storage for WOOSAILibrary user profiles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    # Database connection is established lazily on first use via get_db()
    print("🚀 WoosAI Cloud API started!")


@app.on_event("shutdown")
async def shutdown():
    """Close database on shutdown"""
    from app.database import close_db
    close_db()
    print("👋 WoosAI Cloud API stopped")


@app.get("/")
async def root():
    """API root - health check"""
    return {
        "service": "WoosAI Cloud API",
        "version": "1.0.0",
        "status": "running",
        "database": "MongoDB Atlas",
        "domain": "woos-ai.com",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }


# Include routers
app.include_router(profiles.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(payment.router)