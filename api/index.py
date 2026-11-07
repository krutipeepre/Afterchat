from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from app.models import ConversionRequest, Conversation, Message, Role
from app.pdf.generator import generate_pdf
from app.utils.security import is_valid_url
from app.extractors.chatgpt import ChatGPTAdapter
from app.extractors.gemini import GeminiAdapter

app = FastAPI(title="afterchat.")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Afterchat Vercel backend is online."}

@app.post("/api/convert")
async def convert_conversation(request: ConversionRequest):
    if request.method == "text":
        if not request.data.strip():
            raise HTTPException(status_code=400, detail="Provided text is empty.")
        conversation = Conversation(
            title="Raw Text Import",
            source="Text Fallback",
            messages=[Message(role=Role.USER, content=request.data.strip())]
        )
    elif request.method == "url":
        url = request.data.strip()
        is_safe, error_message = is_valid_url(url)
        if not is_safe:
            raise HTTPException(status_code=400, detail=error_message)
            
        try:
            if "chatgpt.com" in url or "chat.openai.com" in url:
                adapter = ChatGPTAdapter(url)
            elif "g.co" in url or "gemini.google.com" in url:
                adapter = GeminiAdapter(url)
            else:
                raise HTTPException(status_code=400, detail="Domain not supported.")
            conversation = await adapter.extract()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Invalid method specified.")

    try:
        pdf_buffer = generate_pdf(conversation)
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=afterchat-conversation.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")