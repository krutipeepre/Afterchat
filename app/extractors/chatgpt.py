from bs4 import BeautifulSoup
from app.extractors.base import BaseExtractor
from app.models import Conversation, Message, Role

class ChatGPTAdapter(BaseExtractor):
    """
    Attempts to extract conversation data from a publicly shared ChatGPT link.
    """
    
    async def extract(self) -> Conversation:
        # 1. Fetch the raw HTML using the base class method
        html = await self.fetch_html()
        soup = BeautifulSoup(html, "html.parser")
        
        # 2. Extract Title
        title = "ChatGPT Conversation"
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            # ChatGPT titles often append " - ChatGPT" to the end
            title = title_tag.string.replace(" - ChatGPT", "").strip()

        messages = []
        
        # 3. Heuristic Extraction Strategy
        # We target elements with the 'data-message-author-role' attribute, 
        # which is currently common in their server-rendered HTML.
        message_nodes = soup.find_all(attrs={"data-message-author-role": True})
        
        if message_nodes:
            for node in message_nodes:
                role_attr = node.get("data-message-author-role")
                
                # Map to our strict Pydantic Enum
                if role_attr == "user":
                    role = Role.USER
                elif role_attr == "assistant":
                    role = Role.ASSISTANT
                else:
                    continue # Skip unknown roles
                
                # Extract the text content, using newlines for block elements
                content = node.get_text(separator="\n", strip=True)
                
                if content:
                    messages.append(Message(role=role, content=content))
                    
        # 4. Handle extraction failure (Anti-bot walls or DOM updates)
        if not messages:
            messages.append(Message(
                role=Role.SYSTEM, 
                content="Extraction failed. The platform either blocked the request via Cloudflare, or the page structure has changed. Please use the text-paste fallback method."
            ))

        return Conversation(
            title=title,
            source="ChatGPT",
            messages=messages
        )