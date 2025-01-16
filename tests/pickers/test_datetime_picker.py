import pytest
from whenever import Date
from whenever import Time

from textual_timepiece import DateTimePicker
from textual_timepiece.pickers._time_picker import TimeSelect


@pytest.fixture
def datetime_app(create_app):
    return create_app(DateTimePicker)


@pytest.mark.unit
async def test_datetime_default(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.action_focus_next()
        datetime_app.widget.query_one("#target-default").focus()
        await pilot.press("enter")
        assert (
            datetime_app.widget.datetime
            == freeze_time.at(Time()).assume_system_tz()
        )


@pytest.mark.snapshot
def test_datetime_dialog(datetime_app, snap_compare, freeze_time):
    async def run_before(pilot):
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
        assert (
            datetime_app.widget.datetime
            == Date(2025, 2, 3).at(Time(22)).assume_system_tz()
        )


@pytest.mark.unit
async def test_dt_pick_spinbox(datetime_app, freeze_time):
    async with datetime_app.run_test() as pilot:
        datetime_app.widget.query_one("#target-default").press()
        datetime_app.widget.input_widget.focus()

        await pilot.press("right", "right", "right", "up")

        assert (
            datetime_app.widget.datetime
            == freeze_time.replace(year=2026).at(Time()).assume_system_tz()
        )

        await pilot.press("right", "right", "down")
        assert (
            datetime_app.widget.datetime
            == freeze_time.replace(year=2026, month=1)
            .at(Time())
            .assume_system_tz()
        )
        await pilot.press("shift+end", "left", "down")
        assert (
            datetime_app.widget.datetime
            == freeze_time.replace(year=2026, month=1, day=5)
            .at(Time(23, 59, 59))
            .assume_system_tz()
        )
