from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar
from typing import Self
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.reactive import var
from textual.widgets import Button
from textual.widgets import Static
from whenever import Date
from whenever import DateDelta
from whenever import SystemDateTime
from whenever import Time
from whenever import TimeDelta

from textual_timepiece._extra import BaseMessage
from textual_timepiece._extra import LockButton
from textual_timepiece._extra import TargetButton
from textual_timepiece._utility import round_time

from ._base_picker import AbstractDialog
from ._base_picker import AbstractPicker
from ._date_picker import DateInput
from ._date_picker import DateSelect
from ._date_picker import EndDateSelect
from ._datetime_picker import DateTimeInput
from ._time_picker import DurationInput
from ._time_picker import DurationSelect

# TODO: Set a maximum and minimum range that is required.
# TODO: Limit or validate to min/max dates


class DateRangeDialog(AbstractDialog):
    """Simple date range dialog with to date selects combined."""

    DEFAULT_CSS = """
    DateRangeDialog {
        layout: horizontal;

        Static#spacer {
            width: 1;
            height: 100%;
            hatch: ">" $primary 50%;
        }
    }
    """
    start = var[Date | None](None, init=False)
    stop = var[Date | None](None, init=False)

    def compose(self) -> ComposeResult:
        yield DateSelect(is_range=True, id="start-date-select").data_bind(
            date=DateRangeDialog.start, end_date=DateRangeDialog.stop
        )
        yield Static(id="spacer")
        yield EndDateSelect(id="end-date-select").data_bind(
            date=DateRangeDialog.start, end_date=DateRangeDialog.stop
        )


class DateRangePicker(AbstractPicker):
    """Date range picker for picking inclusive date ranges.

    Params:
        start: Initial start date for the picker.
        end: Initial end date for the picker.
        name: Name for the widget.
        id: DOM identifier for the widget.
        classes: CSS classes for the widget
        date_range: Date range to restrict the date to. If provided the picker
            lock will be permanently on for the widgets lifetime or when
            re-enabled programmatically.
        disabled: Whether to disable the widget
        tooltip: Tooltip to show on hover.
    """

    @dataclass
    class DateRangeChanged(BaseMessage):
        widget: DateRangePicker
        start: Date | None
        end: Date | None

    BINDING_GROUP_TITLE = "Date Range Picker"

    BINDINGS: ClassVar = [
        Binding("ctrl+shift+d", "clear", "Clear Dates"),
        Binding(
            "ctrl+t",
            "target_default_start",
            "Start To Today",
            tooltip="Set the start date to todays date.",
        ),
        Binding(
            "alt+ctrl+t",
            "target_default_end",
            "End To Today",
            tooltip="Set the end date to today or the start date.",
        ),
    ]

    start_date = var[Date | None](None, init=False)
    """Picker start date. Bound to sub widgets"""
    end_date = var[Date | None](None, init=False)
    """Picker end date. Bound to sub widgets"""

    def __init__(
        self,
        start: Date | None = None,
        end: Date | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        date_range: DateDelta | None = None,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(name, id, classes, disabled=disabled, tooltip=tooltip)
        self.set_reactive(DateRangePicker.start_date, start)
        self.set_reactive(DateRangePicker.end_date, end)
        self._date_range = date_range

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-control"):
            yield DateInput(id="start-date-input").data_bind(
                date=DateRangePicker.start_date,
            )

            yield TargetButton(
                id="target-default-start",
                tooltip="Set the start date to today.",
            )
            yield LockButton(
                is_locked=self._date_range is not None,
                id="lock-button",
                tooltip="Lock the range inbetween the dates.",
                disabled=self._date_range is not None,
            )

            yield DateInput(id="stop-date-input").data_bind(
                date=DateRangePicker.end_date,
            )
            yield TargetButton(
                id="target-default-end",
                tooltip="Set the end date to today or the start date.",
            )
            yield self._compose_expand_button()

        yield DateRangeDialog().data_bind(
            show=DateRangePicker.expanded,
            start=DateRangePicker.start_date,
            stop=DateRangePicker.end_date,
        )

    def _watch_start_date(self, date: Date | None) -> None:
        if date and self._date_range:
            with self.prevent(self.DateRangeChanged):
                self.end_date = date + self._date_range
        self.post_message(self.DateRangeChanged(self, date, self.end_date))

    def _watch_end_date(self, date: Date | None) -> None:
        if date and self._date_range:
            with self.prevent(self.DateRangeChanged):
                self.start_date = date - self._date_range
        self.post_message(self.DateRangeChanged(self, self.start_date, date))

    @on(DateSelect.DateChanged)
    @on(DateSelect.EndDateChanged)
    def _dialog_date_changed(
        self,
        message: DateSelect.DateChanged | DateSelect.EndDateChanged,
    ) -> None:
        """Handles changes in dates including, keeping dates the same span."""
        message.stop()
        if isinstance(message, DateSelect.DateChanged):
            self.start_date = message.date
        else:
            self.end_date = message.date

    @on(DateInput.DateChanged, "#start-date-input")
    @on(DateInput.DateChanged, "#stop-date-input")
    def _date_input_change(self, message: DateInput.DateChanged) -> None:
        message.stop()
        with message.control.prevent(DateInput.DateChanged):
            if message.control.id == "start-date-input":
                self.start_date = message.date
            else:
                self.end_date = message.date

    @on(Button.Pressed, "#target-default-start")
    def _action_target_default_start(
        self,
        message: Button.Pressed | None = None,
    ) -> None:
        if message:
            message.stop()
        new_date = Date.today_in_system_tz()
        if not self.end_date or new_date <= self.end_date:
            self.start_date = new_date
        else:
            self.start_date = self.end_date

    @on(Button.Pressed, "#target-default-end")
    def _action_target_default_end(
        self,
        message: Button.Pressed | None = None,
    ) -> None:
        if message:
            message.stop()
        if (
            self.start_date
            and (new_date := Date.today_in_system_tz()) >= self.start_date
        ):
            self.end_date = new_date
        else:
            self.end_date = self.start_date

    @on(Button.Pressed, "#lock-button")
    def _lock_delta(self, message: Button.Pressed) -> None:
        message.stop()

        if (
            self.end_date
            and self.start_date
            and cast(LockButton, message.control).locked
        ):
            self._date_range = self.end_date - self.start_date
        else:
            self._date_range = None
            cast(LockButton, message.control).locked = False

    def action_clear(self) -> None:
        """Clear the start and end dates."""
        self.start_date = None
        self.end_date = None

    def disable_start(self, *, disable: bool = True) -> Self:
        """Utility method to disable start input widgets."""
        self.start_input.disabled = disable
        self.dialog.query_one(
            "#start-date-select", DateSelect
        ).disabled = disable
        self.query_one("#target-default-start", Button).disabled = disable
        return self

    def disable_end(self, *, disable: bool = True) -> Self:
        """Utility method to disable end input widgets."""
        self.end_input.disabled = disable
        self.dialog.query_one(
            "#end-date-select", EndDateSelect
        ).disabled = disable
        self.query_one("#target-default-end", Button).disabled = disable
        return self

    @cached_property
    def dialog(self) -> DateRangeDialog:
        return self.query_exactly_one(DateRangeDialog)

    @cached_property
    def start_input(self) -> DateInput:
        return self.query_exactly_one("#start-input", DateInput)

    @cached_property
    def end_input(self) -> DateInput:
        return self.query_exactly_one("#end-input", DateInput)

    @cached_property
    def lock_button(self) -> LockButton:
        return cast(LockButton, self.query_exactly_one(LockButton))


class DateTimeRangeDialog(AbstractDialog):
    DEFAULT_CSS = """
    DateTimeRangeDialog {
        layout: horizontal !important;
        width: auto;
        Vertical {
            width: auto;
            height: auto;
        }
        Static {
            width: 1;
            height: 100%;
            hatch: "⟩" $primary 50%;
        }
    }
    """

    start = var[Date | None](None, init=False)
    stop = var[Date | None](None, init=False)

    def compose(self) -> ComposeResult:
        with Vertical(id="start-column"):
            yield DurationSelect(id="start-time-select")
            yield DateSelect(is_range=True, id="start-date-select").data_bind(
                date=DateTimeRangeDialog.start,
                end_date=DateTimeRangeDialog.stop,
            )
        yield Static(id="spacer", expand=True)
        with Vertical(id="end-column"):
            yield DurationSelect(id="end-time-select")
            yield EndDateSelect(id="end-date-select").data_bind(
                date=DateTimeRangeDialog.start,
                end_date=DateTimeRangeDialog.stop,
            )


class DateTimeRangePicker(AbstractPicker):
    """Datetime range picker with two datetime inputs.

    Params:
        start: Initial start datetime for the picker.
        end: Initial end datetime for the picker.
        name: Name for the widget.
        id: DOM identifier for the widget.
        classes: CSS classes for the widget
        time_range: Time range to restrict the datetimes to. If provided the
            picker lock will be permanently on for the widgets lifetime or
            re-enabled programmatically.
        disabled: Whether to disable the widget
        tooltip: Tooltip to show on hover.
    """

    @dataclass
    class DTRangeChanged(BaseMessage):
        widget: DateTimeRangePicker
        start: SystemDateTime | None
        end: SystemDateTime | None

    BINDING_GROUP_TITLE = "Datetime Range Picker"

    BINDINGS: ClassVar = [
        Binding(
            "ctrl+shift+d",
            "clear",
            "Clear",
            tooltip="Clear end and start datetime.",
        ),
        Binding(
            "ctrl+t",
            "target_default_start",
            "Start To Today",
            tooltip="Set the start date to todays date.",
        ),
        Binding(
            "alt+ctrl+t",
            "target_default_end",
            "End To Today",
            tooltip="Set the end date to today or the start date.",
        ),
    ]

    start_dt = var[SystemDateTime | None](None, init=False)
    """Picker start datetime. Bound to all the parent widgets."""
    end_dt = var[SystemDateTime | None](None, init=False)
    """Picker end datetime. Bound to all the parent widgets."""

    start_date = var[Date | None](None, init=False)
    """Start date dynamically computed depending on start datetime."""
    end_date = var[Date | None](None, init=False)
    """End date dynamically computed depending on the end datetime."""

    def __init__(
        self,
        start: SystemDateTime | None = None,
        end: SystemDateTime | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        time_range: TimeDelta | None = None,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
        )
        self.set_reactive(DateTimeRangePicker.start_dt, start)
        self.set_reactive(DateTimeRangePicker.end_dt, end)

        self._time_range = time_range

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-control"):
            yield DateTimeInput(id="start-input").data_bind(
                datetime=DateTimeRangePicker.start_dt,
            )

            yield TargetButton(
                id="target-default-start",
                tooltip="Set the start time to now.",
            )
            yield LockButton(
                is_locked=self._time_range is not None,
                id="lock-button",
                tooltip="Lock the time range.",
                disabled=self._time_range is not None,
            )

            yield DateTimeInput(id="end-input").data_bind(
                datetime=DateTimeRangePicker.end_dt,
            )
            yield TargetButton(
                id="target-default-end",
                tooltip="Set the end time to now or the start time.",
            )
            yield self._compose_expand_button()

        yield DateTimeRangeDialog().data_bind(
            show=DateTimeDurationPicker.expanded,
            start=DateTimeDurationPicker.start_date,
            stop=DateTimeDurationPicker.end_date,
        )

    def _compute_start_date(self) -> Date | None:
        if self.start_dt is None:
            return None
        return self.start_dt.date()

    def _compute_end_date(self) -> Date | None:
        if self.end_dt is None:
            return None

        return self.end_dt.date()

    def _watch_start_dt(self, new: SystemDateTime | None) -> None:
        if new and self._time_range:
            with self.prevent(self.DTRangeChanged):
                self.end_dt = new + self._time_range
        self.post_message(self.DTRangeChanged(self, new, self.end_dt))

    def _watch_end_dt(self, new: SystemDateTime | None) -> None:
        if new and self._time_range:
            with self.prevent(self.DTRangeChanged):
                self.start_dt = new - self._time_range
        self.post_message(self.DTRangeChanged(self, self.start_dt, new))

    @on(Button.Pressed, "#lock-button")
    def _lock_delta(self, message: Button.Pressed) -> None:
        message.stop()

        if (
            cast(LockButton, message.control).locked
            and self.end_dt
            and self.start_dt
        ):
            self._time_range = self.end_dt - self.start_dt
        else:
            self._time_range = None
            cast(LockButton, message.control).locked = False

    @on(DateSelect.DateChanged)
    @on(DateSelect.EndDateChanged)
    def _dialog_date_changed(self, message: DateSelect.DateChanged) -> None:
        message.stop()
        if isinstance(message, DateSelect.DateChanged):
            self.adjust_start_date(message.date)
        else:
            self.adjust_end_date(message.date)

    def adjust_start_date(self, date: Date | None) -> None:
        """Set or clear the current start date depending on the input."""
        if self.start_dt and date:
            self.start_dt = self.start_dt.replace_date(date)
        elif date:
            self.start_dt = date.at(Time()).assume_system_tz(
                disambiguate="compatible"
            )
        else:
            self.start_dt = date

    def adjust_end_date(self, date: Date | None) -> None:
        """Set or clear the current end date depending on the input."""
        if self.end_dt and date:
            self.end_dt = self.end_dt.replace_date(date)
        elif date:
            self.end_dt = date.at(Time()).assume_system_tz(
                disambiguate="compatible"
            )
        else:
            self.end_dt = date

    def action_clear(self) -> None:
        """Clear the start and end datetimes."""
        self.start_dt = None
        self.end_dt = None

    @on(DurationSelect.DurationRounded)
    def _round_duration(self, message: DurationSelect.DurationRounded) -> None:
        message.stop()
        if message.widget.id == "start-time-select":
            if self.start_dt is None:
                return
            time = round_time(self.start_dt.time(), message.value)
            self.start_dt = self.start_dt.replace_time(time)

        elif self.end_dt:
            time = round_time(self.end_dt.time(), message.value)
            self.end_dt = self.end_dt.replace_time(time)

    @on(DurationSelect.DurationAdjusted)
    def _adjust_duration(
        self, message: DurationSelect.DurationAdjusted
    ) -> None:
        message.stop()
        if message.widget.id == "start-time-select":
            if self.start_dt is None:
                return
            self.start_dt += message.delta
        elif self.end_dt:
            self.end_dt += message.delta
        elif self.start_dt:
            self.end_dt = self.start_dt + message.delta

    @on(DateTimeInput.DateTimeChanged, "#start-input")
    def _start_dt_input_changed(
        self,
        message: DateTimeInput.DateTimeChanged,
    ) -> None:
        message.stop()
        with message.control.prevent(DateTimeInput.DateTimeChanged):
            self.start_dt = message.datetime

    @on(DateTimeInput.DateTimeChanged, "#end-input")
    def _end_dt_input_changed(
        self, message: DateTimeInput.DateTimeChanged
    ) -> None:
        message.stop()
        with message.control.prevent(DateTimeInput.DateTimeChanged):
            self.end_dt = message.datetime

    def disable_start(self, *, disable: bool = True) -> Self:
        """Utility method to disable start input widgets."""
        self.start_input.disabled = disable
        self.dialog.query_one("#start-column", Vertical).disabled = disable
        self.query_one("#target-default-start", Button).disabled = disable
        return self

    def disable_end(self, *, disable: bool = True) -> Self:
        """Utility method to disable end input widgets."""
        self.end_input.disabled = disable
        self.dialog.query_one("#end-column", Vertical).disabled = disable
        self.query_one("#target-default-end", Button).disabled = disable
        return self

    @on(Button.Pressed, "#target-default-start")
    def _action_target_default_start(
        self,
        message: Button.Pressed | None = None,
    ) -> None:
        if message:
            message.stop()
        self.start_dt = SystemDateTime.now()

    @on(Button.Pressed, "#target-default-end")
    def _action_target_default_end(
        self,
        message: Button.Pressed | None = None,
    ) -> None:
        if message:
            message.stop()
        now = SystemDateTime.now()
        if not self.start_dt or now >= self.start_dt:
            self.end_dt = now
        else:
            self.end_dt = self.start_dt

    @cached_property
    def dialog(self) -> DateTimeRangeDialog:
        return self.query_exactly_one(DateTimeRangeDialog)

    @cached_property
    def start_input(self) -> DateTimeInput:
        return self.query_exactly_one("#start-input", DateTimeInput)

    @cached_property
    def end_input(self) -> DateTimeInput:
        return self.query_exactly_one("#end-input", DateTimeInput)

    @cached_property
    def lock_button(self) -> LockButton:
        return cast(LockButton, self.query_exactly_one(LockButton))


class DateTimeDurationPicker(DateTimeRangePicker):
    """Datetime range with a duration input in the middle.

    Duration display up to 99:99:99. Use the DateTimeRangePicker picker if a
    longer duration is required.

    Params:
        start: Initial start datetime for the picker.
        end: Initial end datetime for the picker.
        name: Name for the widget.
        id: DOM identifier for the widget.
        classes: CSS classes for the widget
        time_range: Time range to restrict the datetimes to. If provided the
            picker lock will be permanently on for the widgets lifetime or
            re-enabled programmatically.
        disabled: Whether to disable the widget
        tooltip: Tooltip to show on hover.
    """

    duration = var[TimeDelta | None](None, init=False)
    """Duration between start and end datetimes. Computed dynamically."""

    async def on_mount(self) -> None:
        """Overrides the compose method in order to a duration input."""
        await self.query_exactly_one("#input-control", Horizontal).mount(
            DurationInput(self.duration, id="duration-input").data_bind(
                DateTimeDurationPicker.duration
            ),
            after=1,
        )

    def _compute_duration(self) -> TimeDelta:
        if self.start_dt is None or self.end_dt is None:
            return TimeDelta()
        return self.end_dt - self.start_dt

    @on(DurationInput.DurationChanged)
    def _new_duration(self, message: DurationInput.DurationChanged) -> None:
        message.stop()
        with message.control.prevent(DurationInput.DurationChanged):
            if message.duration is None:
                self.end_dt = None
            elif self.start_dt:
                self.end_dt = self.start_dt + message.duration
            elif self.end_dt:
                self.start_dt = self.end_dt - message.duration

    @on(Button.Pressed, "#lock-button")
    def _lock_duration(self, message: Button.Pressed) -> None:
        message.stop()
        if self.start_date:
            self.duration_input.disabled = cast(
                LockButton, message.button
            ).locked

    @cached_property
    def duration_input(self) -> DurationInput:
        return cast(DurationInput, self.query_exactly_one(DurationInput))
