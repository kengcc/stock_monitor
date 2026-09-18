"""
ChatAdapter - Abstract base class for chat platform adapters.

To add a new platform (e.g., Discord):
1. Create src/chat/discord_adapter.py
2. Implement DiscordAdapter(ChatAdapter)
3. Register in src/chat/__init__.py create_adapter()
"""

from abc import ABC, abstractmethod
from src.stock_manager import StockManager


class ChatAdapter(ABC):
    """Abstract chat platform adapter."""

    def __init__(self, stock_manager: StockManager, **kwargs):
        self.stock_manager = stock_manager
        self.summary_callback = None
        self.fetch_ticker_callback = None
        self.cached_summaries_ref = None
        self.health_callback = None

    def set_callbacks(self, summary_cb, fetch_ticker_cb, cached_ref, health_cb=None):
        """Inject callbacks from main monitor."""
        self.summary_callback = summary_cb
        self.fetch_ticker_callback = fetch_ticker_cb
        self.cached_summaries_ref = cached_ref
        self.health_callback = health_cb

    @abstractmethod
    def setup(self):
        """Initialize handlers / listeners."""
        ...

    @abstractmethod
    async def start(self):
        """Start the adapter (connect, begin polling/listening)."""
        ...

    @abstractmethod
    async def stop(self):
        """Stop the adapter gracefully."""
        ...

    @abstractmethod
    async def send_message(self, chat_id: str, text: str, **kwargs):
        """Send a text message."""
        ...

    @abstractmethod
    async def send_daily_summary(self, chat_id: str, summaries: dict):
        """Send compact summary list with detail interaction."""
        ...

    @abstractmethod
    async def send_breaking_news(self, chat_id: str, ticker: str,
                                  news_title: str, news_url: str, analysis: dict):
        """Send breaking news alert."""
        ...
