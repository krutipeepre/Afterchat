import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

# Import our custom models and PDF engine
from app.models import ConversionRequest, Conversation, Message, Role
from app.pdf.generator import generate_pdf

# Initialize the application
app = FastAPI(
    title="afterchat.", 
    description="Privacy-First AI Conversation-to-PDF Web Application"
)

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# ---------------------------------------------------------
# API Routes
# ---------------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Simple endpoint to verify the server is running."""
    return {"status": "ok", "message": "Afterchat backend is online."}

@app.post("/api/convert")
async def convert_conversation(request: ConversionRequest):
    """
    Main conversion endpoint. 
    Accepts either a URL or raw text, extracts the data, and returns a PDF.
    """
    if request.method == "text":
        # 1. Handle the Text-Paste Fallback
        if not request.data.strip():
            raise HTTPException(status_code=400, detail="Provided text is empty.")
            
        # Treat the entire pasted block as a single raw import for now
        conversation = Conversation(
            title="Raw Text Import",
            source="Text Fallback",
            messages=[
                Message(role=Role.USER, content=request.data.strip())
            ]
        )
        
    elif request.method == "url":
        # 2. Placeholder for URL Extraction (Next Milestone)
        # We will plug in the extractors here shortly.
        raise HTTPException(
            status_code=501, 
            detail="URL extraction is not yet implemented. Please use the text fallback."
        )
        
    else:
        raise HTTPException(status_code=400, detail="Invalid method specified.")

    # 3. Generate and stream the PDF
    try:
        pdf_buffer = generate_pdf(conversation)
        
        # Return the buffer as a streaming response
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=afterchat-conversation.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

# ---------------------------------------------------------
# Frontend Routing
# ---------------------------------------------------------

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the main HTML page on the root URL."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Frontend not found."}