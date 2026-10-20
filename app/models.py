from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Role(str, Enum):
    """Identifies the speaker of a message."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"  # For platform notes or extraction errors

class Message(BaseModel):
    """Represents a single turn in the conversation."""
    role: Role
    content: str = Field(..., description="The raw text or extracted content of the message")

class Conversation(BaseModel):
    """The normalized structure of an extracted AI conversation."""
    title: Optional[str] = Field(default="AI Conversation", description="The title of the chat")
    source: str = Field(default="Unknown", description="e.g., ChatGPT, Gemini, Text Fallback")
    messages: List[Message] = Field(default_factory=list, description="Chronological list of messages")

class ConversionRequest(BaseModel):
    """The payload structure expected from the frontend JavaScript."""
    method: str = Field(..., description="Must be 'url' or 'text'")
    data: str = Field(..., description="The actual URL string or the pasted raw text")