import httpx
from abc import ABC, abstractmethod
from app.models import Conversation

class BaseExtractor(ABC):
    """
    Abstract base class for all platform extractors.
    Ensures a consistent interface for the main application.
    """
    
    def __init__(self, url: str):
        self.url = url
        # Configure a standard HTTP client with strict timeouts (critical for Koyeb/serverless)
        # and browser-like headers to avoid immediate 403 blocks from basic WAFs.
        self.client = httpx.AsyncClient(
            timeout=10.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            follow_redirects=True
        )

    async def fetch_html(self) -> str:
        """Fetches the raw HTML content of the URL."""
        try:
            response = await self.client.get(self.url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            # We will catch this in the main router to show a clean error to the user
            raise ValueError(f"Platform returned an HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise ValueError(f"Network error while reaching the platform: {str(e)}")
        finally:
            # Always close the client to prevent connection leaks
            await self.client.aclose()

    @abstractmethod
    async def extract(self) -> Conversation:
        """
        Must be implemented by subclasses.
        Parses the HTML and returns a normalized Conversation object.
        """
        pass