from bs4 import BeautifulSoup
from app.extractors.base import BaseExtractor
from app.models import Conversation, Message, Role

class GeminiAdapter(BaseExtractor):
    """
    Attempts to extract conversation data from a publicly shared Gemini link.
    """
    
    async def extract(self) -> Conversation:
        html = await self.fetch_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Extract Title
        title = "Gemini Conversation"
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            title = title_tag.string.strip()

        messages = []
        
        # 2. Heuristic Extraction Strategy
        # Gemini often uses complex, dynamically generated class names.
        # We look for common structural patterns or data attributes if available in the SSR payload.
        # Note: This is a best-effort heuristic. Google frequently changes this structure.
        
        # Look for elements that typically wrap user queries and model responses in the shared view.
        # We will look for generic paragraph containers as a fallback heuristic if specific roles aren't found.
        message_blocks = soup.find_all(["div", "p"], class_=lambda c: c and ("message" in c.lower() or "content" in c.lower() or "text" in c.lower()))
        
        if message_blocks:
            # Since role distinction in raw HTML for Gemini is very difficult without JS execution,
            # we alternate roles if we can't determine them, or default to ASSISTANT for block content.
            # A more robust implementation would parse the nested JSON state if it exists in a <script> tag.
            
            for idx, block in enumerate(message_blocks):
                content = block.get_text(separator="\n", strip=True)
                
                # Simple heuristic: filter out very short UI strings
                if content and len(content) > 10:
                    # Guessing role based on order (User usually asks first)
                    # This is imperfect and highlights why the text fallback is crucial.
                    guessed_role = Role.USER if idx % 2 == 0 else Role.ASSISTANT
                    messages.append(Message(role=guessed_role, content=content))

        # 3. Handle extraction failure
        if not messages:
            messages.append(Message(
                role=Role.SYSTEM, 
                content="Extraction failed. Gemini conversations often require JavaScript execution which is not supported by this server. Please use the text-paste fallback method."
            ))

        return Conversation(
            title=title,
            source="Google Gemini",
            messages=messages
        )