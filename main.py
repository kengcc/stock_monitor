#!/usr/bin/env python3
"""
Stock Monitor - AI-powered stock news and social media monitoring

Flow:
- Every hour: fetch news → AI analyze → cache results → check breaking news
- 07:30 daily: fetch+analyze+cache → auto-push summary to chat
- /summary command: instantly return cached results (no re-fetch)
"""

import os
import sys
import signal
import logging
import asyncio
import schedule
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import pytz

sys.path.insert(0, str(Path(__file__).parent))

from src.stock_manager import StockManager
from src.news_fetcher import NewsFetcher
from src.social_fetcher import SocialFetcher
from src.ai_analyzer import AIAnalyzer
from src.chat import create_adapter
from src.locale import load_locale, t

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/stock_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class StockMonitor:
    """Main stock monitoring service"""

    def __init__(self):
        load_dotenv()

        # Load locale
        lang = os.getenv('LANGUAGE', 'zh')
        load_locale(lang)
        logger.info(f"Locale loaded: {lang}")

        # Initialize components
        self.stock_manager = StockManager(Path("data/stocks.json"))

        self.news_fetcher = NewsFetcher(
            newsapi_key=os.getenv('NEWSAPI_KEY'),
            finnhub_key=os.getenv('FINNHUB_API_KEY'),
            alphavantage_key=os.getenv('ALPHAVANTAGE_API_KEY')
        )

        self.social_fetcher = SocialFetcher(
            reddit_client_id=os.getenv('REDDIT_CLIENT_ID'),
            reddit_client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            reddit_user_agent=os.getenv('REDDIT_USER_AGENT'),
            twitter_bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
        )

        self.analyzer = AIAnalyzer(
            api_key=os.getenv('AI_API_KEY'),
            base_url=os.getenv('AI_BASE_URL') or None,
            model=os.getenv('AI_MODEL', 'gpt-4o-mini')
        )

        # Create chat adapter
        platform = os.getenv('CHAT_PLATFORM', 'telegram')
        self.chat = create_adapter(
            platform=platform,
            token=os.getenv('TELEGRAM_BOT_TOKEN'),
            stock_manager=self.stock_manager,
        )

        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))

        # Cache: stores latest summaries per ticker
        self.cached_summaries = {}
        self.last_fetch_time = None
        self.last_checked_news = {}  # Track last checked news per ticker
        self.last_activity = datetime.now(self.timezone)  # Watchdog tracking
        self._shutdown = False

    async def periodic_fetch_with_timeout(self):
        """Timeout-protected wrapper around periodic_fetch."""
        timeout_secs = 600  # 10 minutes max for a full fetch cycle
        try:
            await asyncio.wait_for(self.periodic_fetch(), timeout=timeout_secs)
        except asyncio.TimeoutError:
            logger.error(f"periodic_fetch timed out after {timeout_secs}s, skipping this cycle")
        except Exception as e:
            logger.error(f"periodic_fetch error: {e}", exc_info=True)

    async def periodic_fetch(self):
        """Fetch news + AI analyze + cache for all tickers + check breaking news"""
        logger.info("Starting periodic fetch and analysis...")

        tickers = self.stock_manager.get_all_tickers()
        if not tickers:
            logger.info("No stocks in watchlist, skipping fetch")
            return

        self.cached_summaries['timestamp'] = datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M %Z')

        for ticker in tickers:
            try:
                stock = self.stock_manager.get_stock(ticker)
                company_name = stock.name if stock else ""

                # Fetch news (one fetch, reuse for both summary and breaking news)
                news = self.news_fetcher.fetch_all(ticker, company_name)
                social = self.social_fetcher.fetch_all(ticker)

                # AI analyze and cache (returns {'brief': ..., 'detail': ...})
                result = await self.analyzer.analyze_ticker(ticker, news, social)
                self.cached_summaries[ticker] = {
                    'brief': result['brief'],
                    'detail': result['detail'],
                    'news_count': len(news),
                    'social_count': len(social)
                }
                logger.info(f"Cached summary for {ticker}: {result['brief']}")

                # Check breaking news (reuse fetched news, no extra API call)
                if news:
                    latest_news = news[0]
                    last_checked = self.last_checked_news.get(ticker)

                    if not last_checked or latest_news.url != last_checked:
                        breaking = await self.analyzer.analyze_breaking_news(ticker, latest_news)

                        if breaking['urgent'] and breaking['impact'] in ['high', 'medium']:
                            await self.chat.send_breaking_news(
                                chat_id=self.chat_id,
                                ticker=ticker,
                                news_title=latest_news.title,
                                news_url=latest_news.url,
                                analysis=breaking
                            )
                            logger.info(f"Sent breaking news alert for {ticker}")

                        self.last_checked_news[ticker] = latest_news.url

            except Exception as e:
                logger.error(f"Periodic fetch failed for {ticker}: {e}")
                if ticker not in self.cached_summaries:
                    self.cached_summaries[ticker] = {
                        'brief': t("fetch_fail_brief"),
                        'detail': t("fetch_fail_detail", error=str(e)),
                        'news_count': 0,
                        'social_count': 0
                    }

        self.last_fetch_time = datetime.now(self.timezone)
        self.last_activity = datetime.now(self.timezone)
        logger.info(f"Periodic fetch complete. Cached {len(tickers)} tickers.")

    async def fetch_single_ticker(self, ticker: str):
        """Fetch and cache a single newly added ticker"""
        logger.info(f"Fetching data for new ticker {ticker}...")
        try:
            stock = self.stock_manager.get_stock(ticker)
            company_name = stock.name if stock else ""

            news = self.news_fetcher.fetch_all(ticker, company_name)
            social = self.social_fetcher.fetch_all(ticker)

            result = await self.analyzer.analyze_ticker(ticker, news, social)
            self.cached_summaries[ticker] = {
                'brief': result['brief'],
                'detail': result['detail'],
                'news_count': len(news),
                'social_count': len(social)
            }
            self.cached_summaries['timestamp'] = datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M %Z')
            logger.info(f"Cached new ticker {ticker}: {result['brief']}")
            return True
        except Exception as e:
            logger.error(f"Failed to fetch new ticker {ticker}: {e}")
            self.cached_summaries[ticker] = {
                'brief': t("fetch_fail_brief"),
                'detail': t("fetch_fail_detail", error=str(e)),
                'news_count': 0,
                'social_count': 0
            }
            return False

    async def push_daily_summary(self):
        """Fetch fresh data + push summary to chat (called at 07:30)"""
        logger.info("Daily summary: fetching fresh data...")
        await self.periodic_fetch_with_timeout()
        await self.send_cached_summary()

    async def send_cached_summary(self):
        """Send cached summaries to chat (called by /summary command)"""
        if not self.cached_summaries or len(self.cached_summaries) <= 1:
            # Only timestamp or empty — no data yet
            await self.chat.send_message(self.chat_id, t("summary_no_cache"))
            await self.periodic_fetch()

        await self.chat.send_daily_summary(self.chat_id, self.cached_summaries)

        fetch_time = self.cached_summaries.get('timestamp', 'N/A')
        logger.info(f"Sent cached summary (data from {fetch_time})")

    def get_health_status(self) -> dict:
        """Return cheap, in-memory health info for /health (no network/AI calls)."""
        now = datetime.now(self.timezone)
        last_fetch = None
        if self.last_fetch_time is not None:
            last_fetch = self.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S %Z')

        if self._shutdown:
            status = 'shutting down'
        elif self.last_fetch_time is None:
            status = 'starting'
        else:
            status = 'ok'

        return {
            'status': status,
            'timestamp': now.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'last_fetch': last_fetch,
            'watchlist_count': len(self.stock_manager.get_all_tickers()),
        }

    async def run_scheduled_tasks(self):
        """Run scheduled tasks in async context"""
        while not self._shutdown:
            schedule.run_pending()
            await asyncio.sleep(30)

    async def watchdog(self):
        """Monitor bot health - restart Telegram polling if stale."""
        watchdog_interval = 300  # Check every 5 minutes
        stale_threshold = 900   # 15 minutes with no activity = stale
        while not self._shutdown:
            await asyncio.sleep(watchdog_interval)
            try:
                elapsed = (datetime.now(self.timezone) - self.last_activity).total_seconds()
                # Update activity on each watchdog tick (proves event loop is alive)
                self.last_activity = datetime.now(self.timezone)

                # Check if Telegram polling is still running
                if hasattr(self.chat, 'app') and self.chat.app and self.chat.app.updater:
                    if not self.chat.app.updater.running:
                        logger.warning("Watchdog: Telegram polling stopped, restarting...")
                        await self.chat.restart_polling()
                        logger.info("Watchdog: Telegram polling restarted")

                logger.debug(f"Watchdog OK: event loop alive, last_activity {elapsed:.0f}s ago")
            except Exception as e:
                logger.error(f"Watchdog error: {e}")

    async def graceful_shutdown(self):
        """Gracefully shutdown all components."""
        logger.info("Initiating graceful shutdown...")
        self._shutdown = True
        try:
            await self.chat.stop()
        except Exception as e:
            logger.error(f"Error stopping chat: {e}")
        logger.info("Stock Monitor stopped.")

    async def start(self):
        """Start the monitoring service"""
        logger.info("Starting Stock Monitor...")

        # Validate config
        if not self.chat_id:
            logger.error("TELEGRAM_CHAT_ID not set. Please update .env file.")
            return

        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.graceful_shutdown()))

        # Validate AI connection
        if not await self.analyzer.validate_connection():
            logger.warning("AI API connection test failed, continuing anyway...")

        # Setup chat adapter
        self.chat.setup()

        # Connect chat adapter to callbacks
        self.chat.set_callbacks(
            summary_cb=self.send_cached_summary,
            fetch_ticker_cb=self.fetch_single_ticker,
            cached_ref=self.cached_summaries,
            health_cb=self.get_health_status,
        )

        # Schedule daily summary (07:30 AM ET = 2h before market open)
        summary_time = os.getenv('DAILY_SUMMARY_TIME', '07:30')
        schedule.every().day.at(summary_time).do(
            lambda: asyncio.create_task(self.push_daily_summary())
        )
        logger.info(f"Scheduled daily summary at {summary_time} {self.timezone}")

        # Schedule periodic fetch every hour
        check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', '60'))
        schedule.every(check_interval).minutes.do(
            lambda: asyncio.create_task(self.periodic_fetch_with_timeout())
        )
        logger.info(f"Scheduled periodic fetch every {check_interval} minutes")

        # Start chat adapter
        await self.chat.start()

        # Send startup message
        await self.chat.send_message(self.chat_id, t("startup"))

        # Run initial fetch to populate cache
        logger.info("Running initial fetch to populate cache...")
        await self.periodic_fetch_with_timeout()

        stock_count = len(self.stock_manager.get_all_tickers())
        await self.chat.send_message(
            self.chat_id,
            t("startup_done", count=stock_count, interval=check_interval)
        )

        # Start scheduled task loop + watchdog concurrently
        logger.info("Stock Monitor is running. Press Ctrl+C to stop.")
        try:
            await asyncio.gather(
                self.run_scheduled_tasks(),
                self.watchdog(),
            )
        except asyncio.CancelledError:
            logger.info("Tasks cancelled, shutting down...")
        finally:
            if not self._shutdown:
                await self.graceful_shutdown()


def main():
    """Main entry point"""
    monitor = StockMonitor()

    try:
        asyncio.run(monitor.start())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down Stock Monitor...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
