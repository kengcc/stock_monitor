"""Tests for optional watchlist review dates."""

import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytz
import pytest

from src.chat.telegram_adapter import TelegramAdapter
from src.locale import load_locale
from src.stock_manager import StockManager


def setup_function():
    load_locale("en")


def test_existing_stock_without_review_date_loads_unchanged(tmp_path):
    data_file = tmp_path / "stocks.json"
    original = {
        "AAPL": {
            "ticker": "AAPL",
            "name": "",
            "added_date": "2026-01-01T00:00:00",
            "keywords": [],
            "priority": "HIGH",
        }
    }
    data_file.write_text(json.dumps(original))

    manager = StockManager(data_file)

    assert manager.get_stock("AAPL").review_date is None
    assert json.loads(data_file.read_text()) == original


def test_review_date_can_be_set_updated_cleared_and_reloaded(tmp_path):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)
    manager.add_stock("AAPL")

    assert manager.update_review_date("AAPL", "2026-12-31") is True
    assert manager.update_review_date("AAPL", "2027-01-15") is True
    assert StockManager(data_file).get_stock("AAPL").review_date == "2027-01-15"
    assert manager.update_review_date("AAPL", None) is True
    assert StockManager(data_file).get_stock("AAPL").review_date is None


@pytest.mark.parametrize("value", ["tomorrow", "2026-02-30", "31-12-2026", ""])
def test_invalid_review_date_is_rejected_without_changes(tmp_path, value):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)
    manager.add_stock("AAPL")
    before = data_file.read_text()

    with pytest.raises(ValueError, match="Unsupported review date"):
        manager.update_review_date("AAPL", value)

    assert manager.get_stock("AAPL").review_date is None
    assert data_file.read_text() == before


def test_review_command_sets_and_clears_date(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_review(update, MagicMock(args=["aapl", "2026-12-31"]))
        assert manager.get_stock("AAPL").review_date == "2026-12-31"
        assert "2026-12-31" in update.message.reply_text.await_args.args[0]

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "clear"]))
        assert manager.get_stock("AAPL").review_date is None
        assert "cleared" in update.message.reply_text.await_args.args[0]

    asyncio.run(run())


def test_review_command_rejects_invalid_date_and_unknown_stock(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "tomorrow"]))
        assert manager.get_stock("AAPL").review_date is None
        assert "YYYY-MM-DD" in update.message.reply_text.await_args.args[0]

        await adapter.cmd_review(update, MagicMock(args=["MSFT", "2026-12-31"]))
        assert "not found" in update.message.reply_text.await_args.args[0]

    asyncio.run(run())


def test_list_marks_only_dates_before_today_as_overdue(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("PAST", priority="LOW")
        manager.add_stock("TODAY", priority="HIGH")
        manager.add_stock("FUTURE", priority="MEDIUM")
        manager.update_review_date("PAST", "2026-09-22")
        manager.update_review_date("TODAY", "2026-09-23")
        manager.update_review_date("FUTURE", "2026-09-24")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager, timezone=pytz.UTC)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        with patch("src.chat.telegram_adapter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 23, 12, tzinfo=pytz.UTC)
            mock_datetime.fromisoformat.side_effect = datetime.fromisoformat
            await adapter.cmd_list(update, MagicMock())

        message = update.message.reply_text.await_args.args[0]
        assert "⚠️ Review due: 2026-09-22" in message
        assert "Review: 2026-09-23" in message
        assert "Review: 2026-09-24" in message
        assert message.index("TODAY") < message.index("FUTURE") < message.index("PAST")

    asyncio.run(run())


def test_review_handler_is_registered():
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

    commands = []
    for call in fake_app.add_handler.call_args_list:
        handler = call.args[0]
        if hasattr(handler, "commands"):
            commands.extend(handler.commands)

    assert "review" in commands
