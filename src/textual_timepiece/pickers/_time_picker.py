from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from string import digits
from typing import ClassVar
from typing import Final
from typing import Literal
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.binding import BindingType
from textual.containers import Grid
from textual.containers import Horizontal
from textual.events import Mount
from textual.reactive import var
from textual.validation import Failure
from textual.validation import ValidationResult
from textual.validation import Validator
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Rule
from whenever import SystemDateTime
from whenever import Time
from whenever import TimeDelta
from whenever import hours
from whenever import minutes
from whenever import seconds

from textual_timepiece._extra import BaseMessage
from textual_timepiece._extra import TargetButton
from textual_timepiece._types import Directions
from textual_timepiece._utility import add_time
from textual_timepiece._utility import format_seconds
from textual_timepiece._utility import round_time

from ._base_picker import AbstractInput
from ._base_picker import BaseOverlay
from ._base_picker import BaseOverlayWidget
from ._base_picker import BasePicker


class DurationSelect(BaseOverlayWidget):
    """Duration picker with various buttons in order to set time.

    Params:
        name: Name of the widget.
        id: Unique dom id for the widget
        classes: Any CSS classes that should be added to the widget.
        disabled: Whether to disable the widget.
    """

    @dataclass
    class DurationAdjusted(BaseMessage):
        """Message sent when duration is added or subtracted."""

        widget: DurationSelect
        delta: TimeDelta

    @dataclass
    class DurationRounded(BaseMessage):
        """Sent when one of the headers are clicked in order to round the
        value.
        """

        widget: DurationSelect
        value: int
        """Value used as a rounding factor."""
        scope: Literal["hours", "minutes", "seconds"]
        """Which subunit to round the duration to."""

    DEFAULT_CSS: ClassVar[str] = """
    DurationSelect {
        height: 3;
        layout: horizontal;
        width: 38;

        Grid {
            height: 3;
            grid-size: 2 3;
            grid-gutter: 0;
            grid-rows: 1;

            & > Button:first-of-type {
                column-span: 2;
                text-style: bold;
                background-tint: $background 50%;
            }

            & > Button {
                border: none;
                min-width: 5;
                width: 100%;
                text-style: italic;
                &:hover {
                    border: none;
                }
            }

        }
    }
    """
    """Default CSS for the `DurationSelect` widget."""

    GRID_TEMPLATE: ClassVar[dict[str, tuple[str, ...]]] = {
        "hour-grid": ("Hours", "+1", "+4", "-1", "-4"),
        "minute-grid": ("Minutes", "+15", "+30", "-15", "-30"),
        "second-grid": ("Seconds", "+15", "+30", "-15", "-30"),
    }

    def compose(self) -> ComposeResult:
        for grid, buttons in DurationSelect.GRID_TEMPLATE.items():
            with Grid(id=grid):
                for button in buttons:
                    yield Button(button, classes=grid)

    def _on_button_pressed(self, message: Button.Pressed) -> None:
        message.stop()
        label = str(message.button.label)
        try:
            value = int(label[1:])
            if label.startswith("-"):
                value *= -1
        except ValueError:
            value = None

        if message.button.has_class("hour-grid"):
            if value:
                self.post_message(
                    self.DurationAdjusted(self, TimeDelta(hours=value))
                )
            else:
                self.post_message(self.DurationRounded(self, 21600, "hours"))

        elif message.button.has_class("minute-grid"):
            if value:
                self.post_message(
                    self.DurationAdjusted(self, TimeDelta(minutes=value))
                )
            else:
                self.post_message(self.DurationRounded(self, 3600, "minutes"))
        elif message.button.has_class("second-grid"):
            if value:
                self.post_message(
                    self.DurationAdjusted(self, TimeDelta(seconds=value))
                )
            else:
                self.post_message(self.DurationRounded(self, 60, "seconds"))


class TimeSelect(BaseOverlayWidget):
    """Time selection interface.

    Params:
        name: Name of the widget.
        id: Unique dom id for the widget
        classes: Any CSS classes that should be added to the widget.
        disabled: Whether to disable the widget.
    """

    @dataclass
    class TimeSelected(BaseMessage):
        """Message sent when a value is picked out of the time grid."""

        widget: TimeSelect
        target: Time

    DEFAULT_CSS: ClassVar[str] = """
    TimeSelect {
        layout: grid !important;
        grid-size: 4;
        grid-gutter: 0;
        grid-rows: 1;
        & > Button {
            border: none;
            min-width: 5;
            width: 100%;
            text-style: italic;
            &.dual-hour {
                background: $panel;
            }
            &:focus {
                text-style: bold;
                color: $primary;
            }
            &:hover {
                border: none;
            }
        }
    }
    """
    """Default CSS for the `TimeSelect` widget."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "up",
            "focus_neighbor('up')",
            "Go Up",
            tooltip="Focus the neighbor above.",
            show=False,
        ),
        Binding(
            "right",
            "focus_neighbor('right')",
            "Go Right",
            tooltip="Focus the neighbor to the right.",
            show=False,
        ),
        Binding(
            "down",
            "focus_neighbor('down')",
            "Go Down",
            tooltip="Focus the neighbor below.",
            show=False,
        ),
        Binding(
            "left",
            "focus_neighbor('left')",
            "Go Left",
            tooltip="Focus the neighbor to the left.",
            show=False,
        ),
    ]
    """All bindings for TimeSelect

    | Key(s) | Description |
    | :- | :- |
    | up | Focus the neighbor above. |
    | right | Focus the neighbor to the right. |
    | down | Focus the neighbor below. |
    | left | Focus the neighbor to the left. |
    """

    def compose(self) -> ComposeResult:
        start = Time()
        interval = minutes(30)
        for time in range(48):
            yield Button(
                start.format_common_iso().removesuffix(":00"),
                id=f"time-{time}",
                classes="time icon",
            ).set_class(bool(time % 2), "dual-hour", update=False)
            start = add_time(start, interval)

    def _on_button_pressed(self, message: Button.Pressed) -> None:
        message.stop()
        time = Time.parse_common_iso(f"{message.button.label}:00")
        self.post_message(self.TimeSelected(self, time))

    def action_focus_neighbor(self, direction: Directions) -> None:
        """Focus a nearby member. It will mirror back if going past an edge."""
        if not self.has_focus_within:
            widget = self.query_one("#time-0", Button)
        else:
            # FIX: Subclass a button with a required id.
            focused_id = int(
                cast(str, cast(Button, self.app.focused).id).split("-")[-1]
            )

            row, col = divmod(focused_id, 4)
            if direction == "up":
                if row - 1 >= 0:
                    id = focused_id - 4
                else:
                    id = 43 + (col + 1)

            elif direction == "right":
                if col + 1 <= 3:
                    id = focused_id + 1
                else:
                    id = focused_id - col

            elif direction == "down":
                if row + 1 < 12:
                    id = focused_id + 4
                else:
                    id = col

            else:
                if col - 1 >= 0:
                    id = focused_id - 1
                else:
                    id = focused_id + (3 - col)

            widget = self.query_one(f"#time-{id}", Button)

        self.app.set_focus(widget)


class DurationOverlay(BaseOverlay):
    """Basic dialog widget for editing durations."""

    def compose(self) -> ComposeResult:
        yield DurationSelect()


class TimeOverlay(BaseOverlay):
    """Time dialog which include a time matrix as well."""

    DEFAULT_CSS: ClassVar[str] = """
    TimeOverlay {
        max-width: 40;

        Rule#divider {
            margin: 0;
            padding: 0;
        }
    }
    """

    def compose(self) -> ComposeResult:
        yield DurationSelect()
        yield Rule.horizontal(id="divider")
        yield TimeSelect()


class DurationInput(AbstractInput[TimeDelta]):
    """Duration input for time deltas."""

    @dataclass
    class DurationChanged(BaseMessage):
        """Message sent when the duration changes through input or spinbox."""

        widget: DurationInput
        duration: TimeDelta | None

    ALIAS = "duration"
    MIN: Final[TimeDelta] = TimeDelta()
    MAX: Final[TimeDelta] = TimeDelta(hours=99, minutes=59, seconds=59)

    PATTERN = "99:99:99"

    duration = var[TimeDelta | None](None, init=False)
    """Current duration in a `TimeDelta` or None if empty.

    This value is capped at 99 hours, 59 minutes and 59 seconds.
    """

    def _validate_duration(
        self,
        duration: TimeDelta | None,
    ) -> TimeDelta | None:
        if duration is None:
            return None

        return max(self.MIN, min(self.MAX, duration))

    def _watch_duration(self, duration: TimeDelta | None) -> None:
        with self.prevent(Input.Changed), suppress(ValueError):
            if isinstance(duration, TimeDelta):
                self.value = format_seconds(int(duration.in_seconds()))
            else:
                self.value = ""

        self.post_message(self.DurationChanged(self, self.duration))

    def _watch_value(self, value: str) -> None:
        if dur := self.convert():
            self.duration = dur
        super()._watch_value(value)

    def convert(self) -> TimeDelta | None:
        try:
            hours, minutes, seconds = tuple(map(int, self.value.split(":")))
        except ValueError:
            return None
        if hours + minutes + seconds == 0:
            return TimeDelta()
        return TimeDelta(seconds=seconds, minutes=minutes, hours=hours)

    def action_adjust_time(self, offset: int) -> None:
        """Adjust time with an offset depending on the text cursor position."""
        if self.duration is None:
            self.duration = TimeDelta()
        elif 0 <= self.cursor_position < 2:
            self.duration += hours(offset)
        elif 3 <= self.cursor_position < 5:
            self.duration += minutes(offset)
        elif 6 <= self.cursor_position:
            self.duration += seconds(offset)


# TODO: Find a better way to show larger durations.


class DurationPicker(BasePicker[DurationInput, TimeDelta, DurationOverlay]):
    """Picker widget for picking durations.

    Duration is limited 99 hours, 59 minutes and 59 seconds.

    Params:
        value: Initial duration value for the widget.
        name: Name for the widget.
        id: DOM identifier for the widget.
        classes: CSS classes for the widget
        disabled: Whether to disable the widget.
        tooltip: Tooltip to show on hover.
    """

    @dataclass
    class DurationChanged(BaseMessage):
        """Message sent when the duration changes."""

        widget: DurationPicker
        duration: TimeDelta | None

    INPUT = DurationInput
    ALIAS = "duration"

    duration = var[TimeDelta | None](None, init=False)
    """Current duration. Bound to all the child widgets."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-control"):
            yield (
                DurationInput(id="data-input").data_bind(
                    duration=DurationPicker.duration
                )
            )
            yield TargetButton(
                id="target-default",
                tooltip="Set the duration to zero.",
            )
            yield self._compose_expand_button()

        yield DurationOverlay().data_bind(show=DurationPicker.expanded)

    def _on_mount(self, event: Mount) -> None:
        self.query_exactly_one("#target-default", Button).disabled = (
            self.duration is None or self.duration.in_seconds() == 0
        )

    def _watch_duration(self, delta: TimeDelta) -> None:
        self.query_exactly_one("#target-default", Button).disabled = (
            delta is None or delta.in_seconds() == 0
        )
        self.post_message(self.DurationChanged(self, delta))

    @on(DurationSelect.DurationRounded)
    def _round_duration(self, message: DurationSelect.DurationRounded) -> None:
        message.stop()
        if self.duration is None:
            return
        seconds = (
            round(self.duration.in_seconds() / message.value) * message.value
        )
        self.duration = TimeDelta(seconds=seconds)

    @on(DurationSelect.DurationAdjusted)
    def _adjust_duration(
        self,
        message: DurationSelect.DurationAdjusted,
    ) -> None:
        message.stop()
        if message.delta is None:
            self.duration = None
        elif self.duration is None:
            self.duration = message.delta
        else:
            self.duration += message.delta

    @on(DurationInput.DurationChanged)
    def _set_duration(self, message: DurationInput.DurationChanged) -> None:
        message.stop()
        with message.control.prevent(DurationInput.DurationChanged):
            self.duration = message.duration

    def to_default(self) -> None:
        """Reset the duration to 00:00:00."""
        self.duration = TimeDelta()


class TimeValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            Time.parse_common_iso(value.strip())
        except ValueError:
            return ValidationResult(
                [
                    Failure(
                        self,
                        "Parsing Failure!",
                        "Value is not adhering to ISO time!",
                    )
                ]
            )

        return self.success()


class TimeInput(AbstractInput[Time]):
    """Time input for a HH:MM:SS format"""

    @dataclass
    class TimeChanged(BaseMessage):
        """Message sent when the time is updated."""

        widget: TimeInput
        new_time: Time | None

    PATTERN = "00:00:00"
    ALIAS = "time"

    time = var[Time | None](None, init=False)
    """Currently set time or none if its empty."""

    def _watch_time(self, time: Time | None) -> None:
        with self.prevent(Input.Changed), suppress(ValueError):
            if time:
                self.value = time.format_common_iso()
            else:
                self.value = ""

        self.post_message(self.TimeChanged(self, self.time))

    def _watch_value(self, value: str) -> None:
        if (ts := self.convert()) is not None and ts != self.time:
            self.time = ts
        super()._watch_value(value)

    def convert(self) -> Time | None:
        try:
            return Time.parse_common_iso(self.value)
        except ValueError:
            return None

    def insert_text_at_cursor(self, text: str) -> None:
        if self.cursor_position > 7:
            return

        if text not in digits:
            self.cursor_position += 1
            return

        if self.cursor_position == 0:
            self.value = text + self.value[1:]
        elif self.cursor_position == 7:
            self.value = self.value[:-1] + text
            return
        elif self.cursor_position in {4, 1} or (
            self.value[self.cursor_position] != ":" and text in "543210"
        ):
            self.value = (
                self.value[: self.cursor_position]
                + text
                + self.value[self.cursor_position + 1 :]
            )

        self.cursor_position += 1

    def action_delete_right(self) -> None:
        return

    def action_delete_left(self) -> None:
        if self.cursor_position < 0:
            return

        elif self.cursor_position == 8:
            self.value = self.value[:-1] + "0"

        elif self.cursor_position not in {2, 5}:
            self.value = (
                self.value[: self.cursor_position]
                + "0"
                + self.value[self.cursor_position + 1 :]
            )

        if self.cursor_position > 0:
            self.cursor_position -= 1

    def action_adjust_time(self, offset: int) -> None:
        """Adjust time with an offset depending on the text cursor position."""
        if 0 <= self.cursor_position < 2:
            self.time = add_time(self.time or Time(), hours(offset))
        elif 3 <= self.cursor_position < 5:
            self.time = add_time(self.time or Time(), minutes(offset))
        elif 6 <= self.cursor_position:
            self.time = add_time(self.time or Time(), seconds(offset))


class TimePicker(BasePicker[TimeInput, Time, TimeOverlay]):
    """Time picker for a 24 hour clock.

    Params:
        value: Initial time for the widget.
        name: Name for the widget.
        id: DOM identifier for the widget.
        classes: CSS classes for the widget
        disabled: Whether to disable the widget.
        tooltip: Tooltip to show on hover.
    """

    @dataclass
    class TimeChanged(BaseMessage):
        """Sent when the time is changed with the overlay or other means."""

        widget: TimePicker
        new_time: Time

    INPUT = TimeInput
    ALIAS = "time"

    time = var[Time | None](None, init=False)
    """Currently set time that is bound to the subwidgets. None if empty."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-control"):
            yield TimeInput(id="data-input").data_bind(time=TimePicker.time)
            yield TargetButton(id="target-default", tooltip="Set time to now.")
            yield self._compose_expand_button()

        yield TimeOverlay().data_bind(show=TimePicker.expanded)

    @on(DurationSelect.DurationRounded)
    def _round_duration(self, message: DurationSelect.DurationRounded) -> None:
        message.stop()
        if self.time is None:
            return
        self.time = round_time(self.time, message.value)

    @on(DurationSelect.DurationAdjusted)
    def _adjust_duration(
        self, message: DurationSelect.DurationAdjusted
    ) -> None:
        message.stop()
        self.time = add_time(self.time or Time(), message.delta)

    @on(TimeSelect.TimeSelected)
    def _select_time(self, message: TimeSelect.TimeSelected) -> None:
        message.stop()
        self.time = message.target

    @on(TimeInput.TimeChanged)
    def _change_time(self, message: TimeInput.TimeChanged) -> None:
        message.stop()
        with message.control.prevent(TimeInput.TimeChanged):
            self.time = message.new_time

    def to_default(self) -> None:
        """Reset time to the local current time."""
        self.time = SystemDateTime.now().time()
