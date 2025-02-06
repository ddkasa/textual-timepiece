import asyncio

import pytest
from textual.pilot import Pilot
from whenever import Date
from whenever import DateDelta

from textual_timepiece import DatePicker


@pytest.fixture
def date_app(create_app):
    return create_app(DatePicker)


@pytest.mark.unit
async def test_picker_dialog(date_app):
    async with date_app.run_test() as pilot:
        date_app.action_focus_next()

        await pilot.press("shift+enter")
        assert date_app.query_one(DatePicker).expanded

        await pilot.press("shift+enter")
        assert not date_app.query_one(DatePicker).expanded


@pytest.mark.snapshot
def test_date_dialog(date_app, snap_compare, freeze_time):
    async def run_before(pilot: Pilot):
        date_app.action_focus_next()
        date_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(date_app, run_before=run_before)


@pytest.mark.snapshot
def test_date_dialog_range(create_app, snap_compare, freeze_time):
    date_app = create_app(
        DatePicker(freeze_time, date_range=DateDelta(weeks=2))
    )

    async def run_before(pilot: Pilot):
        date_app.action_focus_next()
        await pilot.press("shift+enter")

    assert snap_compare(date_app, run_before=run_before)


@pytest.mark.unit
async def test_target_today(date_app, freeze_time) -> None:
    async with date_app.run_test():
        date_app.widget.query_one("#target-default").press()
        await asyncio.sleep(0.1)
        assert date_app.widget.date == freeze_time


@pytest.mark.unit
async def test_keyboard_dialog_navigaton(date_app, freeze_time) -> None:
    async with date_app.run_test() as pilot:
        date_app.widget.focus().query_one("#target-default").press()
        await pilot.press(
            "shift+enter",
            "right",
            "enter",
            "enter",
            "right",
            "right",
            "enter",
            "down",
            "enter",
            "enter",
            "enter",
        )

        assert date_app.widget.date == Date(2032, 3, 3)


@pytest.mark.unit
async def test_spinbox_features(date_app, freeze_time) -> None:
    async with date_app.run_test() as pilot:
        date_app.widget.query_one("#target-default").focus()

        await pilot.press("enter", "left", "left", "up")
        assert date_app.widget.date == Date(2025, 2, 7)

        await pilot.press("enter", "left", "left", "up")
        assert date_app.widget.date == Date(2025, 3, 7)

        await pilot.press("enter", "left", "left", "down")
        assert date_app.widget.date == Date(2024, 3, 7)


@pytest.mark.unit
async def test_clear_action(date_app) -> None:
    async with date_app.run_test() as pilot:
        date_app.widget.query_one("#target-default").focus()
        await pilot.press("enter", "ctrl+shift+d")
        assert date_app.widget.value is None


@pytest.mark.unit
async def test_date_range(date_app, freeze_time) -> None:
    async with date_app.run_test() as pilot:
        date_app.widget.query_one("#target-default").focus()
        select = date_app.widget.date_dialog.date_select
        await pilot.press("enter")
        select.date_range = DateDelta(days=5)
        assert date_app.widget.date == freeze_time
        assert select.end_date == Date(2025, 2, 11)
