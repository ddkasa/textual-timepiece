from __future__ import annotations

import math
from calendar import day_abbr
from calendar import month_name
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import NamedTuple
from typing import TypeAlias
from typing import cast

from rich.segment import Segment
from rich.style import Style
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.binding import BindingType
from textual.containers import Horizontal
from textual.events import Blur
from textual.events import Click
from textual.events import Focus
from textual.events import Leave
from textual.events import MouseMove
from textual.geometry import Offset
from textual.geometry import Size
from textual.reactive import reactive
from textual.reactive import var
from textual.strip import Strip
from textual.widgets import Button
from textual.widgets import Input
from whenever import Date
from whenever import DateDelta

from textual_timepiece._extra import BaseMessage
from textual_timepiece._extra import TargetButton
from textual_timepiece._types import Directions
from textual_timepiece._utility import DateScope
from textual_timepiece._utility import Scope
from textual_timepiece._utility import get_scope
from textual_timepiece.constants import LEFT_ARROW
from textual_timepiece.constants import RIGHT_ARROW
from textual_timepiece.constants import TARGET_ICON

from ._base_picker import AbstractInput
from ._base_picker import BaseOverlay
from ._base_picker import BaseOverlayWidget
from ._base_picker import BasePicker

if TYPE_CHECKING:
    pass


DisplayData: TypeAlias = Scope


# TODO: Month and year picker
# PERF: Region refreshing


class DateCursor(NamedTuple):
    """Cursor for keyboard navigation on the calendar dialog."""

    y: int = 0
    x: int = 0

    def confine(self, data: DisplayData) -> DateCursor:
        """Confines cursor to the current display data size."""
        y = min(len(data) + 1, self.y)
        x = min(len(data[y - 1]) - 1 if y else 3, max(self.x, 0))
        return DateCursor(y, x)

    def replace(self, **kwargs: int) -> DateCursor:
        """Create a new cursor with the supplied kwargs."""
        return self._replace(**kwargs)


class DateSelect(BaseOverlayWidget):
    """Date selection widget for selecting dates and date-ranges visually.

    Supports mouse and keyboard navigation with arrow keys.

    INFO:
        Control+Click/Enter will go back in scope with the top header.

    Params:
        start: Initial start date for the widget.
        end: Initial end date for the widget.
        name: Name of the widget.
        id: Unique dom id for the widget
        classes: Any CSS classes that should be added to the widget.
        is_range: Whether the selection is a range. Automatically true if an
            'end_date' or 'date_range' parameter is supplied.
        disabled: Whether to disable the widget.
        select_on_focus: Whether to place a keyboard cursor on widget focus.
        date_range: Whether to restrict the dates to a certain range.
            Will automatically convert to absolute values.
    """

    @dataclass
    class DateChanged(BaseMessage):
        """Message sent when the start date changed."""

        widget: DateSelect
        date: Date | None

    @dataclass
    class EndDateChanged(BaseMessage):
        """Message sent when the end date changed."""

        widget: DateSelect
        date: Date | None

    DEFAULT_CSS: ClassVar[str] = """
    DateSelect {
        background: $surface;
        width: auto;
        border: round $secondary;

        .dateselect--primary-date {
            color: $primary;
        }

        .dateselect--secondary-date {
            color: $secondary;
        }

        .dateselect--range-date {
            background: $panel-darken-3;
        }

        .dateselect--hovered-date {
            color: $accent;
            text-style: bold;
        }

        .dateselect--cursor-date {
            color: $accent;
            text-style: reverse bold;
        }

        .dateselect--start-date {
            color: $accent-lighten-3;
            text-style: italic;
        }

        .dateselect--end-date {
            color: $accent-lighten-3;
            text-style: italic;
        }
    }
    """
    """Default CSS for the `DateSelect` widget."""

    BINDING_GROUP_TITLE = "Date Select"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "up",
            "move_cursor('up')",
            tooltip="Move the cursor up.",
        ),
        Binding(
            "right",
            "move_cursor('right')",
            tooltip="Move cursor to the right.",
        ),
        Binding(
            "down",
            "move_cursor('down')",
            tooltip="Move the cursor down.",
        ),
        Binding(
            "left",
            "move_cursor('left')",
            tooltip="Move the cursor to the left.",
        ),
        Binding(
            "enter",
            "select_cursor",
            tooltip="Navigate or select to the hovered part.",
        ),
        Binding(
            "ctrl+enter",
            "select_cursor(True)",
            tooltip="Reverse Navigate or select to the hovered part.",
        ),
    ]
    """All bindings for DateSelect

    | Key(s) | Description |
    | :- | :- |
    | up | Move the cursor up. |
    | right | Move cursor to the right. |
    | down | Move the cursor down. |
    | left | Move the cursor to the left. |
    | enter | Navigate or select to the hovered part. |
    | ctrl+enter | Reverse Navigate or select to the hovered part. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "dateselect--start-date",
        "dateselect--end-date",
        "dateselect--cursor-date",
        "dateselect--hovered-date",  # NOTE: Only affects the foreground
        "dateselect--secondary-date",
        "dateselect--primary-date",
        "dateselect--range-date",  # NOTE: Only affects the background.
    }
    """All component classes for DateSelect.

    | Class | Description |
    | :- | :- |
    | `dateselect--cursor-date` | Color of label under the keyboard cursor. |
    | `dateselect--end-date` | Color of the selected end date if enabled. |
    | `dateselect--hovered-date` | Color of the mouse hovered date. |
    | `dateselect--primary-date` | Standard color of unselected dates. |
    | `dateselect--range-date` | Color of any dates if both end and start date\
            are selected |
    | `dateselect--secondary-date` | Color of weekdays labels in month view. |
    | `dateselect--start-date` | Color of selected start date. |
    """

    date = reactive[Date | None](None, init=False)
    """Start date. Bound to base dialog if using with a prebuilt picker."""

    date_range = var[DateDelta | None](None, init=False)
    """Constant date range in between the start and end dates."""

    end_date = reactive[Date | None](None, init=False)
    """End date for date ranges.

    Bound to base dialog if using with a prebuilt picker.
    """

    scope = var[DateScope](DateScope.MONTH)
    """Scope of the current date picker view."""

    loc = reactive[Date](Date.today_in_system_tz, init=False)
    """Current location of the date picker for navigation."""

    data = reactive[DisplayData](list, init=False, layout=True)
    """Data for displaying date info.

    Layout required as the size might differ between months.
    """

    header = reactive[str]("", init=False)
    """Navigation date header is computed dynamically."""

    cursor_offset = reactive[Offset | None](None, init=False)
    """Mouse cursor position for mouse navigation."""

    cursor = reactive[DateCursor | None](None, init=False)
    """Keyboard cursor position."""

    def __init__(
        self,
        start: Date | None = None,
        end: Date | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        is_range: bool = False,
        disabled: bool = False,
        select_on_focus: bool = True,
        date_range: DateDelta | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._is_range = is_range or bool(end) or bool(date_range)

        self._select_on_focus = select_on_focus

        self.set_reactive(DateSelect.date, start)
        self.set_reactive(DateSelect.end_date, end)
        self.set_reactive(DateSelect.date_range, date_range)

    def _compute_header(self) -> str:
        if self.scope == DateScope.YEAR:
            return str(self.loc.year)

        elif self.scope == DateScope.DECADE:
            start = math.floor(self.loc.year / 10) * 10
            return f"{start} <-> {start + 9}"

        elif self.scope == DateScope.CENTURY:
            start = math.floor(self.loc.year / 100) * 100
            return f"{start} <-> {start + 99}"

        return f"{month_name[self.loc.month]} {self.loc.year}"

    def _validate_date_range(
        self,
        date_range: DateDelta | None,
    ) -> DateDelta | None:
        if date_range is None:
            return None
        return abs(date_range)

    def _watch_date_range(self, new: DateDelta | None) -> None:
        if new is None:
            return
        self._is_range = True
        if self.date:
            self.end_date = self.date.add(new)
        elif self.end_date:
            self.date = self.end_date.subtract(new)

    def _watch_scope(self, scope: DateScope) -> None:
        self.data = get_scope(scope, self.loc)
        if self.cursor:
            self._find_move()

    def _watch_date(self, date: Date | None) -> None:
        self.scope = DateScope.MONTH
        if date:
            if self.date_range:
                self.end_date = date.add(self.date_range)

            self.loc = date

    def _watch_loc(self, loc: Date) -> None:
        self.data = get_scope(self.scope, loc)

        if self.cursor:
            self.cursor = self.cursor.confine(self.data)

    async def _on_mouse_move(self, event: MouseMove) -> None:
        self.cursor_offset = event.offset

    def _on_leave(self, event: Leave) -> None:
        self.cursor_offset = None

    def _on_blur(self, event: Blur) -> None:
        self.cursor = None

    def _on_focus(self, event: Focus) -> None:
        if self._select_on_focus:
            self.cursor = DateCursor()

    def _on_date_select_date_changed(
        self,
        message: DateSelect.DateChanged,
    ) -> None:
        self.date = message.date
        if self.date_range and message.date:
            self.end_date = message.date.add(self.date_range)

    def _on_date_select_end_date_changed(
        self,
        message: DateSelect.EndDateChanged,
    ) -> None:
        self.end_date = message.date
        if self.date_range and message.date:
            self.date = message.date.subtract(self.date_range)

    async def _on_click(self, event: Click) -> None:
        target = self.get_line_offset(event.offset)
        self._navigate_picker(target, ctrl=event.ctrl)

    def action_move_cursor(self, direction: Directions) -> None:
        """Move cursor to the next spot depending on direction."""
        if self.cursor is None:
            self.log.debug("Cursor does not exist. Placing default location.")
            self.cursor = DateCursor()
        elif direction == "up":
            self._find_move(y=-1)
        elif direction == "right":
            self._find_move(x=1)
        elif direction == "down":
            self._find_move(y=1)
        elif direction == "left":
            self._find_move(x=-1)

    def _find_move(self, *, y: int = 0, x: int = 0) -> None:
        cursor = cast(DateCursor, self.cursor)
        if (new_y := cursor.y + y) == 0:
            new_x = cursor.x + x
            if cursor.y != 0:
                # NOTE: Making sure different row lengths align.
                new_x = math.ceil(((cursor.x) / len(self.data[0])) * 3)

            self.cursor = cursor.replace(y=new_y, x=new_x).confine(self.data)

        elif y and 0 <= new_y <= len(self.data):
            new_x = cursor.x
            if cursor.y == 0:
                # NOTE: Making sure different row lengths align.
                new_x = math.ceil(((cursor.x) / 3) * len(self.data[0]))

            self.cursor = cursor.replace(y=new_y, x=new_x).confine(self.data)

        elif x and 0 <= (new_x := cursor.x + x) < len(self.data[cursor.y - 1]):
            self.cursor = cursor.replace(x=new_x).confine(self.data)

    def _set_date(self, target: str | int, *, ctrl: bool) -> None:
        try:
            value = int(target)
            date = min(Date.MAX, max(Date.MIN, self.loc.replace(day=value)))
        except ValueError:
            return
        if ctrl:
            self.post_message(self.EndDateChanged(self, date))
        else:
            self.post_message(self.DateChanged(self, date))

    def _set_month(self, target: str) -> None:
        try:
            month_no = list(month_name).index(target)
        except IndexError:
            return
        else:
            self.set_reactive(
                DateSelect.loc,
                Date(self.loc.year, month_no, self.loc.day),
            )
            self.scope = DateScope.MONTH

    def _set_years(self, target: str | int) -> None:
        if self.scope == DateScope.CENTURY and isinstance(target, str):
            target = target.split("-")[0]
        try:
            value = max(1, min(int(target), 9999))
        except ValueError:
            return
        else:
            self.set_reactive(DateSelect.loc, self.loc.replace(year=value))
            self.scope = DateScope(self.scope.value - 1)

    def _set_target(self, target: str | int, *, ctrl: bool = False) -> None:
        if self.scope == DateScope.MONTH:
            self._set_date(target, ctrl=ctrl)
        elif self.scope == DateScope.YEAR:
            self._set_month(cast(str, target))
        else:
            self._set_years(target)

    def check_action(
        self, action: str, parameters: tuple[object, ...]
    ) -> bool | None:
        if action == "select_cursor":
            return self.cursor is not None

        return True

    def action_select_cursor(self, ctrl: bool = False) -> None:
        """Triggers the functionality for what is below the keyboard cursor."""
        cursor = cast(DateCursor, self.cursor)
        if cursor.y == 0:
            nav = (
                LEFT_ARROW,
                self.header,
                TARGET_ICON,
                RIGHT_ARROW,
            )
            self._navigate_picker(nav[cursor.x], ctrl=ctrl)
        else:
            self._navigate_picker(self.data[cursor.y - 1][cursor.x], ctrl=ctrl)

    def _navigate_picker(self, target: str | int, *, ctrl: bool) -> None:
        if target == LEFT_ARROW:
            self._crement_scope(-1)
        elif target == TARGET_ICON:
            self._set_current_scope()
        elif target == RIGHT_ARROW:
            self._crement_scope(1)
        elif target == self.header:
            if ctrl:
                self.scope = DateScope(max(self.scope.value - 1, 1))
            else:
                self.scope = DateScope(min(self.scope.value + 1, 4))
        elif target or isinstance(target, int):
            self._set_target(target, ctrl=ctrl and self._is_range)

    def _set_current_scope(self) -> None:
        self.scope = DateScope.MONTH
        self.loc = self.date or self.end_date or Date.today_in_system_tz()

    def _crement_scope(self, value: int) -> None:
        with suppress(ValueError):  # NOTE: Preventing out of range values.
            if self.scope == DateScope.MONTH:
                self.loc = self.loc.add(months=value)
            elif self.scope == DateScope.YEAR:
                self.loc = self.loc.add(years=value)
            elif self.scope == DateScope.DECADE:
                self.loc = self.loc.add(years=10 * value)
            else:
                self.loc = self.loc.add(years=100 * value)

    def _filter_style(
        self,
        y: int,
        x: range,
        date: Date | None = None,
        log_idx: DateCursor | None = None,
    ) -> Style:
        """Filters a rich style based on location data.

        Args:
            y: Current row being rendered.
            x: Range of indexes to target.
            date: If a date is being filtered.
            log_idx: Logical index for rendering the keyboard cursor.

        Returns:
            Combined style with all the properties that matched.
        """
        styles = [self.get_component_rich_style("dateselect--primary-date")]

        if date:
            if date == self.date:
                styles.append(
                    self.get_component_rich_style("dateselect--start-date")
                )
            elif date == self.end_date:
                styles.append(
                    self.get_component_rich_style("dateselect--end-date")
                )

            if self.is_day_in_range(date):
                styles.append(
                    self.get_component_rich_style(
                        "dateselect--range-date"
                    ).background_style
                )

        if (
            self.cursor_offset
            and self.cursor_offset.y == y
            and self.cursor_offset.x in x
        ):
            style = self.get_component_rich_style("dateselect--hovered-date")
            styles.append(style.from_color(style.color))

        if self.cursor and self.cursor == log_idx:
            styles.append(
                self.get_component_rich_style("dateselect--cursor-date")
            )

        return Style.combine(styles)

    def is_day_in_range(self, day: Date) -> bool:
        """Checks if a given date is within selected the date range(inclusive).

        Args:
            day: Date to check against.

        Returns:
            True if in the range else false.
        """
        return bool(
            self._is_range
            and self.date
            and self.end_date
            and self.date <= day <= self.end_date
        )

    def _render_header(self, y: int) -> list[Segment]:
        header_len = len(self.header)
        rem = self.size.width - (header_len + 10)
        blank, blank_extra = divmod(rem, 2)
        header_start = 5 + blank + blank_extra
        header_end = header_start + header_len
        right_nav_start = header_end + (blank - blank_extra) + len(TARGET_ICON)

        y += self._top_border_offset()
        return [
            Segment("   ", self.rich_style),
            Segment(
                LEFT_ARROW,
                self._filter_style(
                    y,
                    range(4, 5),
                    log_idx=DateCursor(0, 0),
                ),
            ),
            Segment(" " * (blank), self.rich_style),
            Segment(
                self.header,
                style=self._filter_style(
                    y,
                    range(header_start, header_end),
                    log_idx=DateCursor(0, 1),
                ),
            ),
            Segment("   ", self.rich_style),
            Segment(
                TARGET_ICON,
                style=self._filter_style(
                    y,
                    range(header_end + 1, header_end + 3),
                    log_idx=DateCursor(0, 2),
                ),
            ),
            Segment(" " * (blank - (3 - blank_extra)), self.rich_style),
            Segment(
                RIGHT_ARROW,
                style=self._filter_style(
                    y,
                    range(right_nav_start, right_nav_start + 2),
                    log_idx=DateCursor(0, 3),
                ),
            ),
        ]

    def _render_weekdays(self) -> list[Segment]:
        day_style = self.get_component_rich_style("dateselect--secondary-date")
        empty = Segment("  ", style=self.rich_style)
        segs = [Segment(" ", style=self.rich_style)]
        for i in range(7):
            segs.append(empty)
            segs.append(Segment(day_abbr[i], day_style))
        return segs

    def _render_month(self, y: int) -> list[Segment]:
        border_offset = self._top_border_offset()
        y += border_offset
        if y == (3 + border_offset):
            return self._render_weekdays()

        month = (y - (4 + border_offset)) // 2
        # NOTE: Removing nav header + weekdays

        date = None
        segments = [Segment(" ", style=self.rich_style)]
        subtotal = int(self.styles.border_left[0] != "")
        for i in range(7):
            segments.append(
                Segment(
                    "  ",
                    self._filter_style(
                        y,
                        range(subtotal, subtotal + 3),
                        date=date,
                    ),
                )
            )
            subtotal += 2
            if not (day := self.data[month][i]):
                segments.append(
                    Segment(
                        "   ",
                        style=self._filter_style(
                            y,
                            range(subtotal, subtotal + 4),
                            date=date,
                            log_idx=DateCursor(month + 1, i),
                        ),
                    )
                )
                date = None
            else:
                date = self.loc.replace(day=cast(int, day))
                segments.append(
                    Segment(
                        str(day).rjust(3),
                        style=self._filter_style(
                            y,
                            range(subtotal, subtotal + 4),
                            date=date,
                            log_idx=DateCursor(month + 1, i),
                        ),
                    )
                )
            subtotal += 3

        return segments

    def _render_year(self, y: int) -> list[Segment]:
        if (row := (y - 2) // 2) > 3:
            return []

        y += self._top_border_offset()

        values = self.data[row]
        value_max_width = self.size.width // len(values)

        segs = list[Segment]()
        for i, value in enumerate(values):
            if self.scope == DateScope.CENTURY:
                value = f"{value}-{cast(int, value) + 9}"
            else:
                value = str(value)
            n = len(value)
            start = (i * value_max_width) + (abs(value_max_width - n) // 2)
            end = start + n + 1

            value = value.center(value_max_width)
            segs.append(
                Segment(
                    value,
                    self._filter_style(
                        y,
                        range(start, end),
                        log_idx=DateCursor(row + 1, i),
                    ),
                )
            )

        return segs

    def render_line(self, y: int) -> Strip:
        if (y % 2 == 0) or (len(self.data) + 2) * 2 < y or not self.data:
            return Strip.blank(self.size.width)

        if y == 1:
            line = self._render_header(y)
        elif self.scope == DateScope.MONTH:
            line = self._render_month(y)
        else:
            line = self._render_year(y)

        return Strip(line)

    def get_content_height(
        self,
        container: Size,
        viewport: Size,
        width: int,
    ) -> int:
        total = 3 + len(self.data) * 2

        if self.scope == DateScope.MONTH:
            return total + 2

        return total

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return 38


class EndDateSelect(DateSelect):
    """Date select widget that inverts the widgets controls to select end_date
    first.

    Params:
        start: Initial start date for the widget.
        end: Initial end date for the widget.
        name: Name of the widget.
        id: Unique dom id for the widget
        classes: Any dom classes that should be added to the widget.
        disabled: Whether to disable the widget.
        select_on_focus: Whether to place a keyboard cursor on widget focus.
        date_range: Whether to restrict the dates to a concrete range.
    """

    def __init__(
        self,
        start: Date | None = None,
        end: Date | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        select_on_focus: bool = True,
        date_range: DateDelta | None = None,
    ) -> None:
        super().__init__(
            start=start,
            end=end,
            name=name,
            id=id,
            classes=classes,
            is_range=True,
            disabled=disabled,
            select_on_focus=select_on_focus,
            date_range=date_range,
        )

    def _watch_end_date(self, date: Date | None) -> None:
        if date:
            self.scope = DateScope.MONTH
            self.loc = date
            if self.date_range:
                self.date = date - self.date_range

    def _set_date(self, target: str | int, *, ctrl: bool) -> None:
        try:
            value = int(target)
        except ValueError:
            return
        else:
            date = min(Date.MAX, max(Date.MIN, self.loc.replace(day=value)))
            if not ctrl:
                self.post_message(self.EndDateChanged(self, date))
            else:
                self.post_message(self.DateChanged(self, date))

    def _set_current_scope(self) -> None:
        self.set_reactive(DateSelect.scope, DateScope.MONTH)
        if self.end_date:
            self.loc = self.end_date
        elif self.date:
            self.loc = self.date


class DateOverlay(BaseOverlay):
    date = var[Date | None](None, init=False)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        date_range: DateDelta | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._date_range = date_range

    def compose(self) -> ComposeResult:
        yield DateSelect(date_range=self._date_range).data_bind(
            date=DateOverlay.date
        )

    @cached_property
    def date_select(self) -> DateSelect:
        return cast(DateSelect, self.query_one(DateSelect))


class EndDateOverlay(DateOverlay):
    date = var[Date | None](None, init=False)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
    ) -> None:
        super().__init__(name, id, classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield EndDateSelect().data_bind(end_date=EndDateOverlay.date)


# TODO: Support for End Date in same input "YYYY/MM/DD - YYYY/MM/DD"


class DateInput(AbstractInput[Date]):
    """Date picker for full dates.

    Params:
        day: Initial value to set.
        name: Name of the widget.
        id: Unique dom identifier value.
        classes: Any dom classes to add.
        tooltip: Tooltip to show when hovering the widget.
        disabled: Whether to disable the widget.
        select_on_focus: Whether to place the cursor on focus.
        spinbox_sensitivity: Sensitivity setting for spinbox functionality.
    """

    @dataclass
    class DateChanged(BaseMessage):
        """Message sent when the date changed."""

        widget: DateInput
        date: Date | None

    PATTERN: ClassVar[str] = "0009-B9-99"
    DATE_FORMAT: ClassVar[str] = "%Y-%m-%d"
    ALIAS = "date"
    date = var[Date | None](None, init=False)
    """Date that is set. Bound if using within a picker."""

    def __init__(
        self,
        day: Date | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        tooltip: str | None = "YYYY-MM-DD Format.",
        *,
        disabled: bool = False,
        select_on_focus: bool = True,
        spinbox_sensitivity: int = 1,
    ) -> None:
        super().__init__(
            value=day,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
            select_on_focus=select_on_focus,
            spinbox_sensitivity=spinbox_sensitivity,
        )

    def watch_date(self, new: Date | None) -> None:
        # FIX: probably should prevent date changes
        with self.prevent(Input.Changed):
            self.value = (
                new.py_date().strftime(self.DATE_FORMAT) if new else ""
            )
        self.post_message(self.DateChanged(self, new))

    def _watch_value(self, value: str) -> None:
        if date := self.convert():
            self.date = date

    def action_adjust_time(self, offset: int) -> None:
        """Adjust date with an offset depending on the text cursor position."""

        try:
            if self.date is None:
                self.date = Date.today_in_system_tz()
            elif self._is_year_pos():
                self.date = self.date.add(years=offset)
            elif self._is_month_pos():
                self.date = self.date.add(months=offset)
            else:
                self.date = self.date.add(days=offset)
        except ValueError as err:
            self.log.debug(err)
            if not str(err).endswith("out of range"):
                raise

    def _is_year_pos(self) -> bool:
        return self.cursor_position < 4

    def _is_month_pos(self) -> bool:
        return 5 <= self.cursor_position < 7

    def _is_day_pos(self) -> bool:
        return 8 <= self.cursor_position

    def convert(self) -> Date | None:
        # NOTE: Pydate instead as I want to keep it open to standard formats.
        try:
            return Date.from_py_date(
                datetime.strptime(self.value, self.DATE_FORMAT).date()
            )
        except ValueError:
            return None

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

        super().insert_text_at_cursor(text)


class DatePicker(BasePicker[DateInput, Date, DateOverlay]):
    """Single date picker with an input and overlay.

    Params:
        date: Initial date for the picker.
        name: Name for the widget.
        id: DOM identifier for widget.
        classes: Classes to add the widget.
        date_range: Date range to lock the widget to.
        disabled: Disable the widget.
        validator: A callable that will validate and adjust the date if needed.
        tooltip: A tooltip to show when hovering the widget.

    Examples:
        >>> def limit_dates(date: Date | None) -> Date | None:
        >>>     if date is None:
        >>>         return None
        >>>     return min(Date(2025, 2, 20), max(Date(2025, 2, 6), date))
        >>> yield DatePicker(validator=limit_dates)

        >>> yield DatePicker(
        >>>     Date.today_in_system_tz(),
        >>>     date_range=DateDelta(days=5),
        >>> )
    """

    @dataclass
    class DateChanged(BaseMessage):
        """Message sent when the date changed."""

        widget: DatePicker
        date: Date | None

    BINDING_GROUP_TITLE = "Date Picker"
    ALIAS = "date"

    DateValidator: TypeAlias = Callable[[Date | None], Date | None]
    """Callable type for validating date types."""

    date = var[Date | None](None, init=False)
    """Current date for the picker. This is bound to every other subwidget."""

    def __init__(
        self,
        date: Date | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        date_range: DateDelta | None = None,
        disabled: bool = False,
        validator: DateValidator | None = None,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(
            value=date,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
        )
        self._date_range = date_range
        self.validator = validator

    def _validate_date(self, date: Date | None) -> Date | None:
        if self.validator is None:
            return date

        return self.validator(date)

    def check_action(
        self, action: str, parameters: tuple[object, ...]
    ) -> bool | None:
        if action == "target_today":
            return self.date != Date.today_in_system_tz()
        return True

    def compose(self) -> ComposeResult:
        with Horizontal(id="input-control"):
            yield DateInput(id="date-input").data_bind(date=DatePicker.date)

            yield TargetButton(
                id="target-default",
                disabled=self.date == Date.today_in_system_tz(),
                tooltip="Set the date to today.",
            )
            yield self._compose_expand_button()

        yield (
            DateOverlay(date_range=self._date_range).data_bind(
                date=DatePicker.date, show=DatePicker.expanded
            )
        )

    def _on_date_select_date_changed(
        self,
        message: DateSelect.DateChanged,
    ) -> None:
        message.stop()
        self.date = message.date

    def _watch_date(self, new: Date) -> None:
        self.query_exactly_one("#target-default", Button).disabled = (
            new == Date.today_in_system_tz()
        )
        self.post_message(self.DateChanged(self, new))

    @on(DateInput.DateChanged)
    def _input_updated(self, message: DateInput.DateChanged) -> None:
        message.stop()
        with message.widget.prevent(DateInput.DateChanged):
            self.date = message.date

    def action_clear(self) -> None:
        """Clear the date."""
        self.date = None

    def to_default(self) -> None:
        """Reset the date to today."""
        self.overlay.date_select.scope = DateScope.MONTH
        self.date = Date.today_in_system_tz()
