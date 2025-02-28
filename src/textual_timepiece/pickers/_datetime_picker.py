from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar
from typing import cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.reactive import var
from textual.widgets import Input
from whenever import Date
from whenever import LocalDateTime
from whenever import SystemDateTime
from whenever import Time

from textual_timepiece._extra import BaseMessage
from textual_timepiece._extra import TargetButton
from textual_timepiece._utility import DateScope
from textual_timepiece._utility import round_time

from ._base_picker import AbstractInput
from ._base_picker import BaseOverlay
from ._base_picker import BasePicker
from ._date_picker import DateSelect
from ._time_picker import DurationSelect
from ._time_picker import TimeSelect


class DateTimeOverlay(BaseOverlay):
    date = var[Date | None](None, init=False)

    DEFAULT_CSS: ClassVar[str] = """
    DateTimeOverlay {
        layout: horizontal;
        max-width: 76;
        height: auto;
        Vertical {
            width: auto;
            height: auto;
        }
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield DateSelect().data_bind(date=DateTimeOverlay.date)
        with Vertical():
            yield DurationSelect()
            yield TimeSelect()
            # TODO: This should be toggleable and slide out at the user behest.

    @cached_property
    def date_select(self) -> DateSelect:
        return cast(DateSelect, self.query_one(DateSelect))


class DateTimeInput(AbstractInput[LocalDateTime]):
    """Input that combines both date and time into one."""

    @dataclass
    class DateTimeChanged(BaseMessage):
        """Sent when the datetime is changed."""

        widget: DateTimeInput
        datetime: LocalDateTime | None

    PATTERN: ClassVar[str] = r"0009-B9-99 99:99:99"
    FORMAT: ClassVar[str] = r"%Y-%m-%d %H:%M:%S"
    ALIAS = "datetime"

    datetime = var[LocalDateTime | None](None, init=False)
    """Current datetime or none if nothing is set."""

    def __init__(
        self,
        value: LocalDateTime | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        tooltip: str | None = None,
        *,
        disabled: bool = False,
        select_on_focus: bool = True,
        spinbox_sensitivity: int = 1,
    ) -> None:
        super().__init__(
            value=value,
            name=name,
            id=id,
            classes=classes,
            tooltip=tooltip,
            disabled=disabled,
            select_on_focus=select_on_focus,
            spinbox_sensitivity=spinbox_sensitivity,
        )

    def watch_datetime(self, value: LocalDateTime | None) -> None:
        with self.prevent(Input.Changed):
            if value:
                self.value = value.py_datetime().strftime(self.FORMAT)
            else:
                self.value = ""

        self.post_message(self.DateTimeChanged(self, self.datetime))

    def _watch_value(self, value: str) -> None:
        if (dt := self.convert()) is not None:
            self.datetime = dt

    def convert(self) -> LocalDateTime | None:
        try:
            return LocalDateTime.strptime(self.value, self.FORMAT)
        except ValueError:
            return None

    def action_adjust_time(self, offset: int) -> None:
        """Adjust date with an offset depending on the text cursor position."""

        try:
            if self.datetime is None:
                self.datetime = SystemDateTime.now().local()
            elif self.cursor_position < 4:
                self.datetime = self.datetime.add(
                    years=offset,
                    ignore_dst=True,
                )
            elif 5 <= self.cursor_position < 7:
                self.datetime = self.datetime.add(
                    months=offset,
                    ignore_dst=True,
                )
            elif 8 <= self.cursor_position < 10:
                self.datetime = self.datetime.add(
                    days=offset,
                    ignore_dst=True,
                )
            elif 11 <= self.cursor_position < 13:
                self.datetime = self.datetime.add(
                    hours=offset,
                    ignore_dst=True,
                )
            elif 14 <= self.cursor_position < 16:
                self.datetime = self.datetime.add(
                    minutes=offset,
                    ignore_dst=True,
                )
            else:
                self.datetime = self.datetime.add(
                    seconds=offset,
                    ignore_dst=True,
                )
        except ValueError as err:
            self.log.debug(err)
            if not str(err).endswith("out of range"):
                raise

    def insert_text_at_cursor(self, text: str) -> None:
        if not text.isdigit():
            return

        # Extra Date Filtering
        if self.cursor_position == 6 and text not in "012":
            return

        if self.cursor_position == 5 and text not in "0123":
            return

        if (
            self.cursor_position == 6
            and self.value[5] == "3"
            and text not in "01"
        ):
            return

        # Extra Time Filtering
        if self.cursor_position == 11:
            if (
                text == "2"
                and len(self.value) >= 12
                and self.value[12] not in "0123"
            ):
                self.value = self.value[:12] + "3" + self.value[13:]
            elif text not in "012":
                return

        if (
            self.cursor_position == 12
            and self.value[11] == "2"
            and text not in "0123"
        ):
            return

        if self.cursor_position in {14, 17} and text not in "012345":
            return

        super().insert_text_at_cursor(text)


class DateTimePicker(
    BasePicker[DateTimeInput, LocalDateTime, DateTimeOverlay]
):
    """Datetime picker with a date and time in one input.


    Params:
        value: Initial datetime value for the widget.
        name: Name for the widget.
        id: DOM identifier for the widget.
        classes: CSS classes for the widget
        disabled: Whether to disable the widget.
        tooltip: Tooltip to show on hover.
    """

    @dataclass
    class DateTimeChanged(BaseMessage):
        """Message sent when the datetime is updated."""

        widget: DateTimePicker
        datetime: LocalDateTime | None

    INPUT = DateTimeInput
    ALIAS = "datetime"

    datetime = var[LocalDateTime | None](None, init=False)
    """The current set datetime. Bound of to all subwidgets."""
    date = var[Date | None](None, init=False)
    """Computed date based on the datetime for the overlay."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-control"):
            yield DateTimeInput().data_bind(DateTimePicker.datetime)
            yield TargetButton(
                id="target-default",
                tooltip="Set the datetime to now.",
            )
            yield self._compose_expand_button()

        yield (
            DateTimeOverlay().data_bind(
                date=DateTimePicker.date,
                show=DateTimePicker.expanded,
            )
        )

    def _compute_date(self) -> Date | None:
        if self.datetime:
            return self.datetime.date()
        return None

    def _watch_datetime(self, datetime: LocalDateTime | None) -> None:
        self.post_message(self.DateTimeChanged(self, datetime))

    def _on_date_select_date_changed(
        self,
        message: DateSelect.DateChanged,
    ) -> None:
        message.stop()
        if not message.date:
            return
        if self.datetime:
            self.datetime = self.datetime.time().on(message.date)
        else:
            self.datetime = message.date.at(Time())

    @on(DurationSelect.DurationRounded)
    def _round_time(self, message: DurationSelect.DurationRounded) -> None:
        message.stop()
        if self.datetime is None:
            return

        time = round_time(self.datetime.time(), message.value)
        self.datetime = self.datetime.replace_time(time)

    @on(DurationSelect.DurationAdjusted)
    def _adjust_time(self, message: DurationSelect.DurationAdjusted) -> None:
        message.stop()
        if self.datetime:
            self.datetime = self.datetime.add(message.delta, ignore_dst=True)
        else:
            self.datetime = SystemDateTime.now().local()

    @on(TimeSelect.TimeSelected)
    def _set_time(self, message: TimeSelect.TimeSelected) -> None:
        message.stop()
        if self.datetime is None:
            self.datetime = (
                SystemDateTime.now().local().replace_time(message.target)
            )
        else:
            self.datetime = self.datetime.replace_time(message.target)

    @on(DateTimeInput.DateTimeChanged)
    def _dt_input_changed(
        self, message: DateTimeInput.DateTimeChanged
    ) -> None:
        message.stop()
        with self.input_widget.prevent(DateTimeInput.DateTimeChanged):
            self.datetime = message.datetime

    def to_default(self) -> None:
        """Reset the picker datetime to the current time."""
        self.datetime = SystemDateTime.now().local()
        self.overlay.date_select.scope = DateScope.MONTH
