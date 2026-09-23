"""
Stock Manager - Manages watched stock list
股票管理器 - 管理关注股票列表
"""

import json
import logging
import os
import re
from datetime import date
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def parse(cls, value) -> "Priority":
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).upper())
        except (TypeError, ValueError):
            raise ValueError(f"Unsupported priority: {value}") from None


PRIORITY_RANK = {
    Priority.CRITICAL: 0,
    Priority.HIGH: 1,
    Priority.MEDIUM: 2,
    Priority.LOW: 3,
}


class StockPersistenceError(RuntimeError):
    """Raised when the watchlist cannot be saved safely."""


@dataclass
class Stock:
    """Stock information"""
    ticker: str  # Stock ticker symbol (e.g., AAPL, TSLA)
    name: str = ""  # Company name
    added_date: str = ""
    keywords: List[str] = None  # Additional keywords to monitor
    priority: Priority = Priority.MEDIUM
    review_date: Optional[str] = None

    def __post_init__(self):
        self.ticker = self.ticker.upper()
        self.priority = Priority.parse(self.priority)
        self.review_date = parse_review_date(self.review_date)
        if self.keywords is None:
            self.keywords = []

    def is_review_overdue(self, on_date: date) -> bool:
        """Return whether the review date is before the supplied local date."""
        return (
            self.review_date is not None
            and date.fromisoformat(self.review_date) < on_date
        )


def parse_review_date(value) -> Optional[str]:
    """Validate and normalize an optional ISO review date."""
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)
    ):
        raise ValueError(f"Unsupported review date: {value}")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValueError(f"Unsupported review date: {value}") from None


class StockManager:
    """Manages the list of stocks to monitor"""

    def __init__(self, data_file: Path = Path("data/stocks.json")):
        self.data_file = data_file
        self.stocks: Dict[str, Stock] = {}
        self._load()

    def _load(self):
        """Load valid stocks, logging and skipping malformed records."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load stocks: {e}")
                return

            if not isinstance(data, dict):
                logger.error("Failed to load stocks: top-level JSON must be an object")
                return

            loaded_stocks = {}
            migrated = False
            skipped = False
            for ticker, stock_data in data.items():
                try:
                    if 'priority' not in stock_data:
                        stock_data = {**stock_data, 'priority': Priority.MEDIUM}
                        migrated = True
                    loaded_stocks[ticker] = Stock(**stock_data)
                except Exception as e:
                    skipped = True
                    logger.error(f"Skipped invalid saved stock {ticker}: {e}")

            self.stocks = loaded_stocks
            if migrated and not skipped:
                try:
                    self._save()
                    logger.info("Migrated existing stocks to MEDIUM priority")
                except StockPersistenceError:
                    logger.error("Could not persist stock priority migration")
            logger.info(f"Loaded {len(self.stocks)} stocks")
        else:
            logger.info("No existing stock list found, starting fresh")

    def _save(self):
        """Atomically save stocks, leaving the existing file intact on failure."""
        temp_path = None
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(
                'w',
                encoding='utf-8',
                dir=self.data_file.parent,
                prefix=f".{self.data_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as f:
                temp_path = Path(f.name)
                data = {ticker: asdict(stock) for ticker, stock in self.stocks.items()}
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, self.data_file)
            logger.info(f"Saved {len(self.stocks)} stocks")
        except Exception as e:
            if temp_path is not None:
                try:
                    temp_path.unlink(missing_ok=True)
                except OSError:
                    logger.warning(f"Failed to remove temporary stock file {temp_path}")
            logger.error(f"Failed to save stocks: {e}")
            raise StockPersistenceError("Failed to save stock data") from e

    def add_stock(self, ticker: str, name: str = "", keywords: List[str] = None,
                  priority: Priority = Priority.MEDIUM) -> bool:
        """Add a stock to monitor"""
        from datetime import datetime

        ticker = ticker.upper()
        priority = Priority.parse(priority)

        if ticker in self.stocks:
            logger.warning(f"Stock {ticker} already exists")
            return False

        self.stocks[ticker] = Stock(
            ticker=ticker,
            name=name,
            added_date=datetime.now().isoformat(),
            keywords=keywords or [],
            priority=priority,
        )
        try:
            self._save()
        except StockPersistenceError:
            del self.stocks[ticker]
            raise
        logger.info(f"Added stock: {ticker}")
        return True

    def remove_stock(self, ticker: str) -> bool:
        """Remove a stock from monitoring"""
        ticker = ticker.upper()

        if ticker not in self.stocks:
            logger.warning(f"Stock {ticker} not found")
            return False

        previous_stocks = self.stocks.copy()
        del self.stocks[ticker]
        try:
            self._save()
        except StockPersistenceError:
            self.stocks = previous_stocks
            raise
        logger.info(f"Removed stock: {ticker}")
        return True

    def get_stock(self, ticker: str) -> Optional[Stock]:
        """Get stock information"""
        return self.stocks.get(ticker.upper())

    def list_stocks(self) -> List[Stock]:
        """Get all stocks"""
        return list(self.stocks.values())

    def get_all_tickers(self) -> List[str]:
        """Get all ticker symbols"""
        return list(self.stocks.keys())

    def update_stock(self, ticker: str, **kwargs) -> bool:
        """Update stock information"""
        ticker = ticker.upper()

        if ticker not in self.stocks:
            return False

        stock = self.stocks[ticker]
        validated_values = {}
        for key, value in kwargs.items():
            if hasattr(stock, key):
                if key == 'priority':
                    value = Priority.parse(value)
                elif key == 'review_date':
                    value = parse_review_date(value)
                validated_values[key] = value

        previous_values = {
            key: getattr(stock, key)
            for key in validated_values
        }
        for key, value in validated_values.items():
            setattr(stock, key, value)

        try:
            self._save()
        except StockPersistenceError:
            for key, value in previous_values.items():
                setattr(stock, key, value)
            raise
        return True

    def update_priority(self, ticker: str, priority) -> bool:
        """Update a stock priority, rejecting unsupported values."""
        return self.update_stock(ticker, priority=Priority.parse(priority))

    def update_review_date(self, ticker: str, review_date: Optional[str]) -> bool:
        """Set or clear a stock review date, rejecting invalid dates."""
        if ticker.upper() not in self.stocks:
            return False
        return self.update_stock(ticker, review_date=review_date)
