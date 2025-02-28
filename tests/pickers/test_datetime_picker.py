import pytest
from whenever import Date
from whenever import LocalDateTime
from whenever import Time

from textual_timepiece.pickers import DateSelect
from textual_timepiece.pickers import DateTimePicker
from textual_timepiece.pickers import TimeSelect


@pytest.fixture
def datetime_app(create_app):
    return create_app(DateTimePicker)


@pytest.mark.unit
async def test_datetime_default(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.action_focus_next()
        datetime_app.widget.query_one("#target-default").focus()
        await pilot.press("enter")
        assert datetime_app.widget.datetime == freeze_time.at(Time())


@pytest.mark.snapshot
def test_datetime_dialog(datetime_app, snap_compare, freeze_time):
    async def run_before(pilot):
        datetime_app.action_focus_next()
        datetime_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(datetime_app, run_before=run_before)


@pytest.mark.snapshot
def test_mini_datetime_dialog(datetime_app, snap_compare, freeze_time):
    async def run_before(pilot):
        datetime_app.widget.add_class("mini")
        datetime_app.action_focus_next()
        datetime_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(datetime_app, run_before=run_before)


@pytest.mark.unit
async def test_datetime_dialog_messages(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.action_focus_next()
        datetime_app.widget.query_one("#target-default").focus()

        await pilot.press("shift+enter", "down", "down", "enter")
        assert datetime_app.widget.datetime.date() == Date(2025, 2, 3)

        datetime_app.widget.query_one(TimeSelect).action_focus_neighbor("up")
        await pilot.press("up", "enter")
        assert datetime_app.widget.datetime == Date(2025, 2, 3).at(Time(22))


@pytest.mark.unit
async def test_datetime_dialog_messages_reverse(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.action_focus_next()

        await pilot.press("shift+enter")
        datetime_app.widget.query_one(TimeSelect).action_focus_neighbor("up")
        await pilot.press("up", "enter")
        assert datetime_app.widget.datetime == freeze_time.at(Time(22))
        datetime_app.widget.query_one("#target-default").focus()

        datetime_app.widget.query_one(DateSelect).focus()
        await pilot.press("down", "down", "enter")
        assert datetime_app.widget.datetime == Date(2025, 2, 3).at(Time(22))


@pytest.mark.unit
async def test_dt_pick_spinbox(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.widget.query_one("#target-default").press()
        datetime_app.widget.input_widget.focus()

        await pilot.press("right", "right", "right", "up")
        assert datetime_app.widget.datetime == freeze_time.replace(
            year=2026
        ).at(Time())

        await pilot.press("right", "right", "down")
        assert datetime_app.widget.datetime == freeze_time.replace(
            year=2026, month=1
        ).at(Time())

        datetime_app.widget.input_widget.cursor_position = 0
        await pilot.press("3")
        assert datetime_app.widget.datetime == freeze_time.replace(
            year=3026, month=1
        ).at(Time())

        await pilot.press("shift+end", "left", "down")
        assert datetime_app.widget.datetime == freeze_time.replace(
            year=3026, month=1, day=5
        ).at(Time(23, 59, 59))


@pytest.mark.unit
async def test_dt_dialog_edge_cases(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.widget.focus()
        select = datetime_app.widget.overlay.date_select
        select.post_message(DateSelect.DateChanged(select, Date.MIN))
        await pilot.pause()
        assert datetime_app.widget.date == Date.MIN

        select.post_message(DateSelect.DateChanged(select, Date.MAX))
        await pilot.pause()
        assert datetime_app.widget.date == Date.MAX


@pytest.mark.unit
async def test_dt_input_edge_cases(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.widget.input_widget.focus()
        datetime_app.widget.datetime = LocalDateTime.MAX
        await pilot.press("up")

        datetime_app.widget.datetime = LocalDateTime.MIN
        await pilot.press("down")
