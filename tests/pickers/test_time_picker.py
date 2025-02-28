import pytest
from whenever import Time
from whenever import TimeDelta

from textual_timepiece.pickers import DurationPicker
from textual_timepiece.pickers import TimePicker
from textual_timepiece.pickers import TimeSelect


@pytest.fixture
def duration_app(create_app):
    return create_app(DurationPicker)


@pytest.fixture
def time_app(create_app):
    return create_app(TimePicker)


@pytest.mark.snapshot
def test_duration_dialog(duration_app, snap_compare, freeze_time):
    async def run_before(pilot):
        duration_app.action_focus_next()
        duration_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(duration_app, run_before=run_before)


@pytest.mark.snapshot
def test_mini_duration_dialog(duration_app, snap_compare, freeze_time):
    async def run_before(pilot):
        duration_app.widget.add_class("mini")
        duration_app.action_focus_next()
        duration_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(duration_app, run_before=run_before)


@pytest.mark.unit
async def test_duration_dialog_messages(duration_app, freeze_time):
    async with duration_app.run_test() as pilot:
        duration_app.action_focus_next()
        await pilot.press("shift+enter", "tab", "enter", "tab", "enter")
        assert duration_app.widget.duration.in_minutes() == 60


@pytest.mark.unit
async def test_duration_pick_spinbox(duration_app, freeze_time):
    async with duration_app.run_test() as pilot:
        duration_app.widget.query_one("#target-default").press()

        await pilot.press("up", "up")
        assert duration_app.widget.duration.in_seconds() == 1

        await pilot.press("left", "left", "left", "up")
        assert duration_app.widget.duration.in_seconds() == 61

        await pilot.press("left", "left", "down")
        assert duration_app.widget.duration == TimeDelta()


@pytest.mark.snapshot
def test_time_dialog(time_app, snap_compare, freeze_time):
    async def run_before(pilot):
        time_app.action_focus_next()
        time_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(time_app, run_before=run_before)


@pytest.mark.snapshot
def test_mini_time_dialog(time_app, snap_compare, freeze_time):
    async def run_before(pilot):
        time_app.widget.add_class("mini")
        time_app.action_focus_next()
        time_app.widget.query_one("#target-default").press()
        await pilot.press("shift+enter")

    assert snap_compare(time_app, run_before=run_before)


@pytest.mark.unit
async def test_time_dialog_messages(time_app, freeze_time):
    async with time_app.run_test() as pilot:
        time_app.action_focus_next()
        await pilot.press("shift+enter", "tab", "enter", "tab", "enter")
        assert time_app.widget.time == Time(1)

        time_app.widget.query_one(TimeSelect).action_focus_neighbor("up")
        await pilot.press("up", "enter")

        assert time_app.widget.time == Time(22)


@pytest.mark.unit
async def test_time_pick_spinbox(time_app, freeze_time):
    async with time_app.run_test() as pilot:
        time_app.widget.query_one("#target-default").press()
        time_app.widget.input_widget.focus()

        await pilot.press("left", "left", "left", "up")

        assert time_app.widget.time == Time(minute=1)

        await pilot.press("right", "right", "down")
        assert time_app.widget.time == Time(second=59)
