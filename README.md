# afterchat.

A privacy-first web application that converts shared AI conversation links (ChatGPT and Google Gemini) into clean, downloadable PDFs.

## Local Setup

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`
6. Open `http://127.0.0.1:8000` in your browser.

## Deployment

Designed for server-container platforms like Koyeb or Render using the included `Procfile`.