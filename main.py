from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import logging
import sys
from pathlib import Path

# Import routers
from routers import auth, dashboard, instances, messages, campaigns, finances, groups, webhooks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="WhatsApp Bot Management System",
    description="Complete WhatsApp bot management system with Baileys integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(instances.router)
app.include_router(messages.router)
app.include_router(campaigns.router)
app.include_router(finances.router)
app.include_router(groups.router)
app.include_router(webhooks.router)

# Static files and templates
templates = Jinja2Templates(directory="templates")

# Serve static files
static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main application"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "whatsapp-bot-api",
        "version": "1.0.0"
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("WhatsApp Bot Management System starting up...")
    logger.info("API Documentation available at: /api/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("WhatsApp Bot Management System shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )