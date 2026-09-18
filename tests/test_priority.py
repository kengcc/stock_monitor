"""Tests for watchlist stock priorities."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.telegram_adapter import TelegramAdapter
from src.locale import load_locale
from src.stock_manager import Priority, StockManager


def setup_function():
    load_locale("en")


def test_add_stock_defaults_to_medium_and_persists(tmp_path):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)

    assert manager.add_stock("aapl") is True
    assert manager.get_stock("AAPL").priority is Priority.MEDIUM
    assert json.loads(data_file.read_text())["AAPL"]["priority"] == "MEDIUM"


def test_add_stock_with_explicit_case_insensitive_priority(tmp_path):
    manager = StockManager(tmp_path / "stocks.json")

    assert manager.add_stock("nvda", priority="high") is True
    assert manager.get_stock("NVDA").priority is Priority.HIGH


def test_invalid_priority_is_rejected_without_changes(tmp_path):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)

    with pytest.raises(ValueError, match="Unsupported priority"):
        manager.add_stock("AAPL", priority="urgent")

    assert manager.list_stocks() == []
    assert not data_file.exists()


def test_existing_stock_migrates_to_medium_and_is_persisted(tmp_path):
    data_file = tmp_path / "stocks.json"
    data_file.write_text(json.dumps({
        "AAPL": {
            "ticker": "AAPL",
            "name": "",
            "added_date": "2026-01-01T00:00:00",
            "keywords": [],
        }
    }))

    manager = StockManager(data_file)

    assert manager.get_stock("AAPL").priority is Priority.MEDIUM
    assert json.loads(data_file.read_text())["AAPL"]["priority"] == "MEDIUM"


def test_update_priority_preserves_background_order(tmp_path):
    manager = StockManager(tmp_path / "stocks.json")
    manager.add_stock("AAPL", priority="LOW")
    manager.add_stock("MSFT", priority="MEDIUM")

    assert manager.update_priority("AAPL", "critical") is True
    assert manager.get_stock("AAPL").priority is Priority.CRITICAL
    assert manager.get_all_tickers() == ["AAPL", "MSFT"]


def test_invalid_update_does_not_change_priority(tmp_path):
    manager = StockManager(tmp_path / "stocks.json")
    manager.add_stock("AAPL")

    with pytest.raises(ValueError, match="Unsupported priority"):
        manager.update_priority("AAPL", "urgent")

    assert manager.get_stock("AAPL").priority is Priority.MEDIUM


def test_priority_command_updates_stock(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock(args=["aapl", "critical"])

        await adapter.cmd_priority(update, context)

        assert manager.get_stock("AAPL").priority is Priority.CRITICAL
        assert "CRITICAL" in update.message.reply_text.await_args.args[0]

    asyncio.run(run())


@pytest.mark.parametrize(
    ("args", "expected"),
    [(["AAPL"], Priority.MEDIUM), (["AAPL", "high"], Priority.HIGH)],
)
def test_add_command_accepts_default_or_explicit_priority(tmp_path, args, expected):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_add(update, MagicMock(args=args))

        assert manager.get_stock("AAPL").priority is expected
        assert expected.value in update.message.reply_text.await_args_list[0].args[0]

    asyncio.run(run())


def test_priority_command_rejects_invalid_value(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        context = MagicMock(args=["AAPL", "urgent"])

        await adapter.cmd_priority(update, context)

        assert manager.get_stock("AAPL").priority is Priority.MEDIUM
        assert "LOW, MEDIUM, HIGH, or CRITICAL" in update.message.reply_text.await_args.args[0]

    asyncio.run(run())


def test_priority_handler_is_registered():
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

    assert "priority" in commands


def test_list_displays_stable_priority_order(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("LOW1", priority="LOW")
        manager.add_stock("HIGH1", priority="HIGH")
        manager.add_stock("CRIT1", priority="CRITICAL")
        manager.add_stock("HIGH2", priority="HIGH")
        manager.add_stock("MED1")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_list(update, MagicMock())

        message = update.message.reply_text.await_args.args[0]
        tickers = ["CRIT1", "HIGH1", "HIGH2", "MED1", "LOW1"]
        assert all(f"[{manager.get_stock(t).priority.value}] ${t}" in message for t in tickers)
        assert [message.index(ticker) for ticker in tickers] == sorted(
            message.index(ticker) for ticker in tickers
        )
        assert manager.get_all_tickers() == ["LOW1", "HIGH1", "CRIT1", "HIGH2", "MED1"]

    asyncio.run(run())
