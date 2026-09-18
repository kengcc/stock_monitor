"""Tests for the /health Telegram command."""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytz

from src.locale import load_locale
from src.chat.telegram_adapter import TelegramAdapter, build_health_reply


def setup_function():
    load_locale("en")


def test_build_health_reply_includes_status_and_timestamp():
    msg = build_health_reply({
        "status": "ok",
        "timestamp": "2026-09-18 13:00:00 UTC",
        "watchlist_count": 3,
        "last_fetch": "2026-09-18 12:00:00 UTC",
    })

    assert "ok" in msg
    assert "2026-09-18 13:00:00 UTC" in msg
    assert "3" in msg
    assert "2026-09-18 12:00:00 UTC" in msg


def test_build_health_reply_when_never_fetched():
    msg = build_health_reply({
        "status": "ok",
        "timestamp": "2026-09-18 13:00:00 UTC",
        "watchlist_count": 0,
        "last_fetch": None,
    })

    assert "never" in msg
    assert "0" in msg


def test_cmd_health_replies_with_callback_data():
    async def _run():
        adapter = TelegramAdapter(token="fake-token", stock_manager=MagicMock())
        adapter.health_callback = lambda: {
            "status": "ok",
            "timestamp": "2026-09-18 13:00:00 UTC",
            "watchlist_count": 2,
            "last_fetch": None,
        }

        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_health(update, MagicMock())

        update.message.reply_text.assert_awaited_once()
        args, kwargs = update.message.reply_text.await_args
        assert "ok" in args[0]
        assert "2026-09-18 13:00:00 UTC" in args[0]
        assert kwargs.get("parse_mode") == "Markdown"

    asyncio.run(_run())


def test_cmd_health_without_callback():
    async def _run():
        adapter = TelegramAdapter(token="fake-token", stock_manager=MagicMock())
        adapter.health_callback = None

        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_health(update, MagicMock())

        update.message.reply_text.assert_awaited_once()
        assert "unavailable" in update.message.reply_text.await_args.args[0].lower()

    asyncio.run(_run())


def test_get_health_status_shape():
    from main import StockMonitor

    monitor = object.__new__(StockMonitor)
    monitor.timezone = pytz.UTC
    monitor._shutdown = False
    monitor.last_fetch_time = datetime(2026, 9, 18, 12, 0, tzinfo=pytz.UTC)
    monitor.stock_manager = MagicMock()
    monitor.stock_manager.get_all_tickers.return_value = ["AAPL", "MSFT"]

    health = StockMonitor.get_health_status(monitor)

    assert health["status"] == "ok"
    assert health["watchlist_count"] == 2
    assert health["last_fetch"] is not None
    assert "timestamp" in health


def test_health_handler_registered_in_setup():
    """setup() should register the health CommandHandler."""
    adapter = TelegramAdapter(token="fake-token", stock_manager=MagicMock())

    fake_app = MagicMock()
    fake_builder = MagicMock()
    fake_builder.token.return_value = fake_builder
    fake_builder.read_timeout.return_value = fake_builder
    fake_builder.write_timeout.return_value = fake_builder
    fake_builder.connect_timeout.return_value = fake_builder
    fake_builder.pool_timeout.return_value = fake_builder
    fake_builder.build.return_value = fake_app

    with patch("telegram.ext.Application.builder", return_value=fake_builder):
        adapter.setup()

    registered_commands = []
    for call in fake_app.add_handler.call_args_list:
        handler = call.args[0]
        if hasattr(handler, "commands"):
            registered_commands.extend(handler.commands)

    assert "health" in registered_commands
