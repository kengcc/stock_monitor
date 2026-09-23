"""Tests for optional watchlist review dates."""

import asyncio
import json
from datetime import date, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytz
import pytest

from src.chat.telegram_adapter import TelegramAdapter
from src.locale import load_locale
from src.locale.en import STRINGS as EN_STRINGS
from src.locale.zh import STRINGS as ZH_STRINGS
from src.stock_manager import StockManager, StockPersistenceError


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


@pytest.mark.parametrize(
    "value",
    ["tomorrow", "2026-02-30", "31-12-2026", "20260923", "2026-W39-3", ""],
)
def test_invalid_review_date_is_rejected_without_changes(tmp_path, value):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)
    manager.add_stock("AAPL")
    before = data_file.read_text()

    with pytest.raises(ValueError, match="Unsupported review date"):
        manager.update_review_date("AAPL", value)

    assert manager.get_stock("AAPL").review_date is None
    assert data_file.read_text() == before


@pytest.mark.parametrize("value", ["2026-02-30", "20260923", "2026-W39-3"])
def test_invalid_update_preserves_existing_review_date(tmp_path, value):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)
    manager.add_stock("AAPL")
    manager.update_review_date("AAPL", "2026-12-31")
    before = data_file.read_text()

    with pytest.raises(ValueError, match="Unsupported review date"):
        manager.update_review_date("AAPL", value)

    assert manager.get_stock("AAPL").review_date == "2026-12-31"
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

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "2027-01-15"]))
        assert manager.get_stock("AAPL").review_date == "2027-01-15"

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "CLEAR"]))
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

        await adapter.cmd_review(update, MagicMock(args=["MSFT", "tomorrow"]))
        assert "not found" in update.message.reply_text.await_args.args[0]

    asyncio.run(run())


def test_review_command_reports_save_failure_and_rolls_back(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        with patch.object(
            manager,
            "_save",
            side_effect=StockPersistenceError("denied"),
        ):
            await adapter.cmd_review(update, MagicMock(args=["AAPL", "2026-12-31"]))

        assert manager.get_stock("AAPL").review_date is None
        assert StockManager(tmp_path / "stocks.json").get_stock("AAPL").review_date is None
        assert "save" in update.message.reply_text.await_args.args[0].lower()

    asyncio.run(run())


def test_interrupted_save_preserves_original_json(tmp_path):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)
    manager.add_stock("AAPL")
    original = data_file.read_text()

    def partial_dump(data, handle, **kwargs):
        handle.write('{"partial":')
        raise OSError("interrupted")

    with patch("src.stock_manager.json.dump", side_effect=partial_dump):
        with pytest.raises(StockPersistenceError, match="Failed to save"):
            manager.update_review_date("AAPL", "2026-12-31")

    assert data_file.read_text() == original
    assert StockManager(data_file).get_stock("AAPL").review_date is None


@pytest.mark.parametrize(
    "records",
    [
        [
            ("BAD", {"ticker": "BAD", "review_date": "invalid"}),
            ("AAPL", {"ticker": "AAPL"}),
        ],
        [
            ("AAPL", {"ticker": "AAPL"}),
            ("BAD", {"ticker": "BAD", "review_date": "invalid"}),
            ("MSFT", {"ticker": "MSFT"}),
        ],
    ],
)
def test_malformed_saved_date_does_not_create_partial_load(tmp_path, records):
    data_file = tmp_path / "stocks.json"
    original = json.dumps(dict(records))
    data_file.write_text(original)

    manager = StockManager(data_file)

    expected = [ticker for ticker, data in records if data.get("review_date") != "invalid"]
    assert manager.get_all_tickers() == expected
    assert manager.get_stock("BAD") is None
    assert data_file.read_text() == original


@pytest.mark.parametrize("args", [[], ["AAPL"], ["AAPL", "2026-12-31", "extra"]])
def test_review_command_rejects_wrong_argument_count(tmp_path, args):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_review(update, MagicMock(args=args))

        assert manager.get_stock("AAPL").review_date is None
        assert "Usage" in update.message.reply_text.await_args.args[0]

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
            await adapter.cmd_list(update, MagicMock())

        message = update.message.reply_text.await_args.args[0]
        assert "⚠️ Review due: 2026-09-22" in message
        assert "Review: 2026-09-23" in message
        assert "Review: 2026-09-24" in message
        assert message.index("TODAY") < message.index("FUTURE") < message.index("PAST")

    asyncio.run(run())


def test_list_uses_configured_timezone_across_midnight(tmp_path):
    async def run():
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        manager.update_review_date("AAPL", "2026-09-23")
        timezone = pytz.timezone("America/New_York")
        adapter = TelegramAdapter(
            token="fake-token",
            stock_manager=manager,
            timezone=timezone,
        )
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        instant = datetime(2026, 9, 24, 0, 30, tzinfo=pytz.UTC)

        with patch("src.chat.telegram_adapter.datetime") as mock_datetime:
            mock_datetime.now.side_effect = lambda tz=None: instant.astimezone(tz)
            await adapter.cmd_list(update, MagicMock())

        message = update.message.reply_text.await_args.args[0]
        assert "Review: 2026-09-23" in message
        assert "Review due" not in message

    asyncio.run(run())


def test_review_commands_and_overdue_list_are_localized_in_chinese(tmp_path):
    async def run():
        load_locale("zh")
        manager = StockManager(tmp_path / "stocks.json")
        manager.add_stock("AAPL")
        adapter = TelegramAdapter(token="fake-token", stock_manager=manager, timezone=pytz.UTC)
        update = MagicMock()
        update.message.reply_text = AsyncMock()

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "2026-09-22"]))
        assert "复查日期已设为" in update.message.reply_text.await_args.args[0]

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "20260923"]))
        assert "必须使用" in update.message.reply_text.await_args.args[0]

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "clear"]))
        assert "已清除" in update.message.reply_text.await_args.args[0]

        await adapter.cmd_review(update, MagicMock(args=["AAPL", "2026-09-22"]))
        with patch("src.chat.telegram_adapter.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 9, 23, tzinfo=pytz.UTC)
            await adapter.cmd_list(update, MagicMock())
        assert "待复查: 2026-09-22" in update.message.reply_text.await_args.args[0]

    asyncio.run(run())


def test_review_date_calendar_boundaries(tmp_path):
    data_file = tmp_path / "stocks.json"
    manager = StockManager(data_file)
    manager.add_stock("AAPL")

    assert manager.update_review_date("AAPL", "2028-02-29") is True
    assert manager.get_stock("AAPL").is_review_overdue(date(2028, 2, 29)) is False
    assert manager.get_stock("AAPL").is_review_overdue(date(2028, 3, 1)) is True

    with pytest.raises(ValueError, match="Unsupported review date"):
        manager.update_review_date("AAPL", "2027-02-29")
    assert manager.get_stock("AAPL").review_date == "2028-02-29"

    assert manager.update_review_date("AAPL", "0001-01-01") is True
    assert manager.update_review_date("AAPL", "9999-12-31") is True


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


def test_review_strings_exist_in_both_locales():
    review_keys = {
        "cmd_review",
        "review_usage",
        "review_invalid",
        "review_ok",
        "review_cleared",
        "review_not_found",
        "review_save_failed",
        "list_review_date",
        "list_review_overdue",
    }

    assert review_keys <= EN_STRINGS.keys()
    assert review_keys <= ZH_STRINGS.keys()


def test_review_command_is_in_telegram_menu():
    async def run():
        adapter = TelegramAdapter(token="fake-token", stock_manager=MagicMock())
        adapter.app = MagicMock()
        adapter.app.initialize = AsyncMock()
        adapter.app.start = AsyncMock()
        adapter.app.bot.delete_my_commands = AsyncMock()
        adapter.app.bot.set_my_commands = AsyncMock()
        adapter.app.bot.set_chat_menu_button = AsyncMock()
        adapter.app.updater.start_polling = AsyncMock()

        await adapter.start()

        commands = adapter.app.bot.set_my_commands.await_args.args[0]
        assert "review" in [command.command for command in commands]

    asyncio.run(run())


def test_review_command_is_documented_in_start_script():
    start_script = Path(__file__).parents[1] / "start.sh"

    assert "/review" in start_script.read_text()
