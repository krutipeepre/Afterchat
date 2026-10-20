import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Initialize the application
app = FastAPI(
    title="afterchat.", 
    description="Privacy-First AI Conversation-to-PDF Web Application"
)

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure static directory exists to prevent startup errors during development
os.makedirs(STATIC_DIR, exist_ok=True)

# ---------------------------------------------------------
# API Routes
# ---------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Simple endpoint to verify the server is running."""
    return {"status": "ok", "message": "Afterchat backend is online."}

@app.post("/api/convert")
async def convert_conversation():
    """
    Placeholder for the main conversion logic.
    We will update this to accept data and return a PDF once our extractors and PDF engine are built.
    """
    return {"status": "pending", "message": "Extraction and PDF generation coming soon."}

# ---------------------------------------------------------
# Frontend Routing
# ---------------------------------------------------------

# Mount the static directory so the browser can access style.css and script.js
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the main HTML page on the root URL."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found. We need to build index.html next!"}