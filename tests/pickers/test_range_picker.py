from functools import partial

import pytest
from whenever import DateDelta
from whenever import days
from whenever import weeks

from textual_timepiece import DateRangePicker
from textual_timepiece import DateTimeDurationPicker
from textual_timepiece import DateTimeRangePicker


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


@pytest.mark.snapshot
def test_dt_range_dialog(datetime_range_app, range_snap_compare, freeze_time):
    async def run_before(pilot):
        datetime_range_app.action_focus_next()
        datetime_range_app.widget.query_one("#target-default-start").press()
        datetime_range_app.widget.query_one("#target-default-end").press()
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
        datetime_dur_range_app.widget.query_one("#target-default-end").press()
        await pilot.pause()
        datetime_dur_range_app.widget.end_dt += weeks(2)
        await pilot.press("shift+enter")

    assert range_snap_compare(datetime_dur_range_app, run_before=run_before)


@pytest.mark.unit
async def test_dt_dur_range_lock(create_app, freeze_time):
    datetime_dur_range_app = create_app(
        DateTimeDurationPicker(time_range=DateDelta(days=5))
    )

    async with datetime_dur_range_app.run_test() as pilot:
        datetime_dur_range_app.action_focus_next()
        datetime_dur_range_app.widget.query_one(
            "#target-default-start"
        ).press()
        await pilot.pause()
        assert (
            datetime_dur_range_app.widget.end_date
            == freeze_time + DateDelta(days=5)
        )
