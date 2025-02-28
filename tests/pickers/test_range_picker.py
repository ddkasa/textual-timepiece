from functools import partial

import pytest
from whenever import DateDelta
from whenever import Time
from whenever import TimeDelta
from whenever import days

from textual_timepiece._extra import LockButton
from textual_timepiece.pickers import DateRangePicker
from textual_timepiece.pickers import DateTimeDurationPicker
from textual_timepiece.pickers import DateTimeRangePicker


@pytest.fixture
def date_range_app(create_app):
    return create_app(DateRangePicker)


@pytest.fixture
def datetime_range_app(create_app):
    return create_app(DateTimeRangePicker)


@pytest.fixture
def datetime_dur_range_app(create_app):
    return create_app(DateTimeDurationPicker)


@pytest.fixture
def range_snap_compare(snap_compare):
    return partial(snap_compare, terminal_size=(85, 34))


@pytest.mark.snapshot
def test_date_range_dialog(date_range_app, range_snap_compare, freeze_time):
    async def run_before(pilot):
        date_range_app.action_focus_next()
        date_range_app.widget.query_one("#target-default-start").press()
        date_range_app.widget.query_one("#target-default-end").press()
        await pilot.press("shift+enter")

    assert range_snap_compare(date_range_app, run_before=run_before)


@pytest.mark.snapshot
def test_mini_date_range_dialog(
    date_range_app,
    range_snap_compare,
    freeze_time,
):
    async def run_before(pilot):
        date_range_app.widget.add_class("mini")
        date_range_app.action_focus_next()
        date_range_app.widget.query_one("#target-default-start").press()
        await pilot.press("shift+enter")

    assert range_snap_compare(date_range_app, run_before=run_before)


@pytest.mark.unit
async def test_date_range_lock(create_app, freeze_time):
    date_range_app = create_app(DateRangePicker(date_range=DateDelta(days=5)))

    async with date_range_app.run_test() as pilot:
        date_range_app.action_focus_next()
        date_range_app.widget.query_one("#target-default-start").press()
        await pilot.pause()
        assert date_range_app.widget.end_date == freeze_time + DateDelta(
            days=5
        )

        date_range_app.widget.end_date += days(5)
        await pilot.pause()
        assert date_range_app.widget.start_date == freeze_time + DateDelta(
            days=5
        )


@pytest.mark.unit
async def test_date_range_cap_disable(date_range_app, freeze_time):
    async with date_range_app.run_test():
        assert date_range_app.widget.start_input.disabled is False
        assert date_range_app.widget.end_input.disabled is False

        date_range_app.widget.disable_end()
        assert date_range_app.widget.start_input.disabled is False
        assert date_range_app.widget.end_input.disabled

        date_range_app.widget.disable_start()
        assert date_range_app.widget.start_input.disabled
        assert date_range_app.widget.end_input.disabled

        date_range_app.widget.disable_end(disable=False)
        assert date_range_app.widget.start_input.disabled
        assert date_range_app.widget.end_input.disabled is False


@pytest.mark.snapshot
def test_dt_range_dialog(datetime_range_app, range_snap_compare, freeze_time):
    async def run_before(pilot):
        datetime_range_app.action_focus_next()
        datetime_range_app.widget.query_one("#target-default-start").press()
        datetime_range_app.widget.query_one("#target-default-end").press()
        await pilot.pause()
        datetime_range_app.widget.end_dt = (
            datetime_range_app.widget.end_dt.add(weeks=2)
        )

        await pilot.press("shift+enter")

    assert range_snap_compare(datetime_range_app, run_before=run_before)


@pytest.mark.snapshot
def test_mini_dt_range_dialog(
    datetime_range_app, range_snap_compare, freeze_time
):
    async def run_before(pilot):
        datetime_range_app.add_class("mini")
        datetime_range_app.action_focus_next()
        datetime_range_app.widget.query_one("#target-default-start").press()

        await pilot.press("shift+enter")

    assert range_snap_compare(datetime_range_app, run_before=run_before)


@pytest.mark.snapshot
def test_dt_dur_range_dialog(
    datetime_dur_range_app, range_snap_compare, freeze_time
):
    async def run_before(pilot):
        datetime_dur_range_app.action_focus_next()
        datetime_dur_range_app.widget.query_one(
            "#target-default-start"
        ).press()
        datetime_dur_range_app.widget.query_one("#target-default-end").focus()
        await pilot.press("enter")
        datetime_dur_range_app.widget.end_dt = (
            datetime_dur_range_app.widget.end_dt.add(weeks=2)
        )
        await pilot.press("shift+enter")
        await pilot.pause()

    assert range_snap_compare(datetime_dur_range_app, run_before=run_before)


@pytest.mark.snapshot
def test_mini_dt_dur_range_dialog(
    datetime_dur_range_app, range_snap_compare, freeze_time
):
    async def run_before(pilot):
        datetime_dur_range_app.widget.add_class("mini")
        datetime_dur_range_app.action_focus_next()
        await pilot.pause()

    assert range_snap_compare(datetime_dur_range_app, run_before=run_before)


@pytest.mark.unit
async def test_dt_dur_range_lock(create_app, freeze_time):
    datetime_dur_range_app = create_app(
        DateTimeDurationPicker(time_range=TimeDelta(hours=48))
    )

    async with datetime_dur_range_app.run_test() as pilot:
        datetime_dur_range_app.action_focus_next()
        datetime_dur_range_app.widget.query_one(
            "#target-default-start"
        ).press()
        await pilot.pause()
        assert (
            datetime_dur_range_app.widget.end_date
            == freeze_time + DateDelta(days=2)
        )


@pytest.mark.unit
async def test_datetime_range_bindings(
    datetime_range_app, range_snap_compare, freeze_time
):
    async with datetime_range_app.run_test() as pilot:
        datetime_range_app.action_focus_next()

        await pilot.press("ctrl+t")
        assert datetime_range_app.widget.start_dt.date() == freeze_time

        await pilot.press("alt+ctrl+t")
        assert datetime_range_app.widget.end_dt.date() == freeze_time

        await pilot.press("ctrl+shift+d")
        assert datetime_range_app.widget.start_dt is None
        assert datetime_range_app.widget.end_dt is None


@pytest.mark.unit
async def test_dt_range_cap_disable(datetime_range_app, freeze_time):
    async with datetime_range_app.run_test():
        assert datetime_range_app.widget.start_input.disabled is False
        assert datetime_range_app.widget.end_input.disabled is False

        datetime_range_app.widget.disable_end()
        assert datetime_range_app.widget.start_input.disabled is False
        assert datetime_range_app.widget.end_input.disabled

        datetime_range_app.widget.disable_start()
        assert datetime_range_app.widget.start_input.disabled
        assert datetime_range_app.widget.end_input.disabled

        datetime_range_app.widget.disable_end(disable=False)
        assert datetime_range_app.widget.start_input.disabled
        assert datetime_range_app.widget.end_input.disabled is False


@pytest.mark.unit
async def test_datetime_range_lock(datetime_range_app, freeze_time):
    async with datetime_range_app.run_test() as pilot:
        datetime_range_app.action_focus_next()

        await pilot.press("ctrl+t")
        assert datetime_range_app.widget.start_dt.date() == freeze_time

        datetime_range_app.widget.end_dt = None
        button = datetime_range_app.widget.query_one(LockButton).press()
        await pilot.pause()
        assert button.locked is False

        datetime_range_app.widget.end_dt = freeze_time.at(Time()).add(
            days=5, ignore_dst=True
        )

        button.press()
        assert button.locked
        await pilot.pause()
        datetime_range_app.widget.end_dt = (
            datetime_range_app.widget.end_dt.add(days=5)
        )
        assert datetime_range_app.widget.start_dt.date() == freeze_time.add(
            days=5
        )
