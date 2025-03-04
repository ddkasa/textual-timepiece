from __future__ import annotations

from calendar import Calendar
from calendar import day_abbr
from calendar import month_abbr
from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from functools import cached_property
from itertools import chain
from typing import ClassVar
from typing import NamedTuple
from typing import Self
from typing import TypeAlias
from typing import cast

from rich.color import Color as RColor
from rich.segment import Segment
from rich.style import Style as RStyle
from textual import on
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.binding import BindingType
from textual.color import Color
from textual.containers import Center
from textual.containers import Horizontal
from textual.events import Blur
from textual.events import Click
from textual.events import DescendantBlur
from textual.events import Focus
from textual.events import Leave
from textual.events import MouseMove
from textual.geometry import Offset
from textual.geometry import Size
from textual.reactive import reactive
from textual.reactive import var
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.validation import Integer
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import MaskedInput
from whenever import Date
from whenever import days

from textual_timepiece._extra import BaseMessage
from textual_timepiece._types import Directions

from ._extra import BaseWidget
from ._extra import TargetButton
from ._utility import flat_to_shape
from ._utility import format_seconds
from ._utility import iterate_timespan
from ._utility import normalize_values


class HeatmapCursor(NamedTuple):
    """Cursor for navigating a heatmap with the keyboard or mouse."""

    week: int
    day: int
    month: int | None = None

    def to_date(self, year: int) -> Date | None:
        if self.is_month:
            return Date(year, cast(int, self.month), 1)

        if (week := self.week) == 53:
            week = 1
            year += 1

        try:
            return Date.from_py_date(
                date.fromisocalendar(
                    year, week, 1 if self.is_week else self.day
                )
            )
        except ValueError:  # NOTE: Deals with far reach edge cases.
            return None

    def move(
        self,
        year: int,
        day_delta: int = 0,
        week_delta: int = 0,
    ) -> HeatmapCursor | Self:
        month = None
        week = self.week + week_delta
        day = self.day + day_delta
        if day == 9:
            if self.is_month:
                if (cursor_date := self.to_date(year)) is None:
                    return self
                iso = cursor_date.py_date()
            else:
                iso = date.fromisocalendar(year, min(week + 1, 52), 1)

            month = min(12, max(1, iso.month + week_delta))
            week = iso.replace(day=1, month=month).isocalendar().week

        return HeatmapCursor(week, day, month)

    @property
    def is_day(self) -> bool:
        return not self.is_week and self.month is None

    @property
    def is_week(self) -> bool:
        return self.day == 8

    @property
    def is_month(self) -> bool:
        return self.month is not None


# TODO: Dirty region tracking.


class ActivityHeatmap(ScrollView, BaseWidget):
    """Base renderable widget for an activity heatmap.

    Params:
        year: Year for verifying dates.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        select_on_focus: Whether to setup a keyboard cursor on focus.
        disabled: Whether the widget is disabled or not.

    Examples:
        >>> def compose(self) -> ComposeResult:
        >>>     yield ActivityHeatmap(2025)

        >>> def on_mount(self) -> None:
        >>>     activity = generate_activity()
        >>>     self.query_one(ActivityHeatmap).process_data(activity)
    """

    @dataclass
    class DateSelected(BaseMessage):
        """Message sent when a day is selected."""

        widget: ActivityHeatmap
        day: Date

    @dataclass
    class WeekSelected(BaseMessage):
        """Message sent when a week number is selected."""

        widget: ActivityHeatmap
        week: Date

    @dataclass
    class MonthSelected(BaseMessage):
        """Message sent when a month label is selected."""

        widget: ActivityHeatmap
        month: Date

    can_focus = True

    ActivityData: TypeAlias = list[list[float | None]]
    """Final data type that the heatmap uses."""

    BORDER_TITLE = "Activity Heatmap"
    BINDING_GROUP_TITLE = "Activity Heatmap"

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "right",
            "move_cursor('right')",
            "Move Right",
            tooltip="Move the keyboard cursor right.",
            show=False,
            priority=True,
        ),
        Binding(
            "down",
            "move_cursor('down')",
            "Move Down",
            tooltip="Move the keyboard cursor down.",
            show=False,
            priority=True,
        ),
        Binding(
            "left",
            "move_cursor('left')",
            tooltip="Move the keyboard cursor left.",
            show=False,
            priority=True,
        ),
        Binding(
            "up",
            "move_cursor('up')",
            "Move Up",
            tooltip="Move the keyboard cursor up.",
            show=False,
            priority=True,
        ),
        Binding(
            "enter",
            "select_tile",
            "Select",
            tooltip="Select the highlighted day.",
            show=False,
        ),
        Binding(
            "escape",
            "clear_cursor",
            "Clear Cursor",
            tooltip="Clear the cursor selection.",
            show=False,
        ),
    ]
    """All bindings for the `ActivityHeatmap`.

    | Key(s) | Description |
    | :- | :- |
    | right | Move Cursor Right |
    | down | Move Cursor Down |
    | left | Move Cursor Left |
    | up | Move Cursor Up |
    | enter | Select Highlighted Day |
    | escape | Clear Any Cursor Selection. |
    """

    DEFAULT_CSS: ClassVar[str] = """
    ActivityHeatmap {
        background: transparent;
        height: auto;
        .activityheatmap--empty {
            background: transparent;
            color: $primary;
            text-style: bold;
        }
        .activityheatmap--empty-alt {
            background: transparent;
            color: $secondary;
            text-style: bold;
        }
        .activityheatmap--color {
            background: $panel-darken-1;
            color: $secondary;
        }
        .activityheatmap--hover {
            background: $panel-darken-1;
            color: $accent;
            border-bottom: white;
        }
    }
    Tooltip {
        padding: 1;
        text-align: center;
    }
    """
    """Default CSS Styling for the `ActivityHeatmap`"""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "activityheatmap--color",
        "activityheatmap--empty",
        "activityheatmap--empty-alt",
        "activityheatmap--hover",
    }
    """All component classes that the `ActivityHeatmap` uses.

    | Class | Description |
    | :- | :- |
    | `activityheatmap--color` | Base color of the tiles |
    | `activityheatmap--empty` | Empty tile color for navigation. |
    | `activityheatmap--empty-alt` | Alternative empty tile color for navigation. |
    | `activityheatmap--hover` | Color when something is hovered. |
    """  # noqa: E501
    data = reactive[ActivityData](list, init=False, layout=True)
    """Two dimensional data that should be normalized between 0 and 1."""

    year = var[int](lambda: Date.today_in_system_tz().year, init=False)
    """Current year for calculating dates."""

    values = var[defaultdict[date, int]](
        lambda: defaultdict(lambda: 0), init=False
    )
    """Original pre normalized values for tooltips."""

    mouse_offset = var[Offset](Offset, init=False)
    """Current mouse offfset for tracking the cursor."""

    cursor = reactive[HeatmapCursor | None](None, init=False)
    """Current hovered day, week or month."""

    def __init__(
        self,
        year: int | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        select_on_focus: bool = True,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self.select_on_focus = select_on_focus
        self.virtual_size = Size(163, 18)
        if year:
            self.set_reactive(ActivityHeatmap.year, year)

    def _get_color_strength(
        self,
        value: float,
        base: Color,
        bg: Color,
    ) -> RColor:
        return base.blend(bg, value).rich_color

    def _get_day_style(
        self,
        day: int,
        week: int,
        value: float,
        background: Color,
        color: Color,
        hover_color: RStyle,
    ) -> RStyle:
        if self._is_tile_hovered(day=day, week=week):
            return hover_color

        return RStyle(color=self._get_color_strength(value, color, background))

    def _get_segment(
        self,
        day: int,
        week: int,
        background: Color,
        color: Color,
        hover_color: RStyle,
        empty: RStyle,
    ) -> Segment:
        if (value := self.data[week][day]) is not None:
            return Segment(
                "██",
                style=self._get_day_style(
                    day, week, value, background, color, hover_color
                ),
            )
        if self._is_tile_hovered(day=day, week=week):
            return Segment("██", hover_color)

        return Segment("  ")

    def _render_weekday(
        self,
        y: int,
        empty_bg: RStyle,
        empty_seg: Segment,
    ) -> Strip:
        base_color = self.get_component_rich_style("activityheatmap--color")
        empty_alt = self.get_component_rich_style("activityheatmap--empty-alt")
        hover_color = self.get_component_rich_style("activityheatmap--hover")
        day = y // 2

        color, background = (
            Color.from_rich_color(base_color.color),
            Color.from_rich_color(base_color.bgcolor),
        )
        segs = [
            Segment(day_abbr[day], empty_bg if day % 2 == 0 else empty_alt),
            empty_seg,
        ]
        empty_bg = empty_bg.background_style
        for week in range(len(self.data)):
            segs.append(empty_seg)
            segs.append(
                self._get_segment(
                    day, week, background, color, hover_color, empty_bg
                )
            )

        return Strip(segs)

    def _render_weeks(
        self,
        empty_background: RStyle,
        empty_seg: Segment,
    ) -> Strip:
        empty_alt = self.get_component_rich_style("activityheatmap--empty-alt")
        hover_color = self.get_component_rich_style("activityheatmap--hover")

        segments = [Segment(" " * 4, style=empty_seg.style)]
        for i in range(2, 108, 2):
            segments.append(empty_seg)
            style = (
                hover_color
                if self._is_tile_hovered(week=i // 2)
                else empty_background
                if i % 2 != 0
                else empty_alt
            )
            segments.append(Segment(str(i // 2).rjust(2), style=style))

        return Strip(segments)

    def _render_months(
        self,
        empty_background: RStyle,
        empty_seg: Segment,
    ) -> Strip:
        empty_alt = self.get_component_rich_style("activityheatmap--empty-alt")
        hover_color = self.get_component_rich_style("activityheatmap--hover")
        segments = [empty_seg] * 3
        for month in range(1, 13):
            segments.append(
                Segment(
                    month_abbr[month],
                    style=hover_color
                    if self._is_tile_hovered(month=month)
                    else empty_background
                    if month % 2 != 0
                    else empty_alt,
                )
            )
            segments.append(Segment(" " * 10, style=empty_background))
        return Strip(segments)

    def render_line(self, y: int) -> Strip:
        empty_background = self.get_component_rich_style(
            "activityheatmap--empty"
        )
        empty_seg = Segment(" ", style=empty_background)

        scroll_x, scroll_y = self.scroll_offset
        y += scroll_y

        if y == 15:
            strip = self._render_weeks(empty_background, empty_seg)
        elif y == 17:
            strip = self._render_months(empty_background, empty_seg)
        elif y % 2 == 0 or not self.data or (len(self.data[0]) * 2) < y - 2:
            strip = Strip.blank(self.size.width)
        else:
            strip = self._render_weekday(y, empty_background, empty_seg)

        return strip.crop(scroll_x, scroll_x + self.size.width)

    @work(name="heatmap", thread=True, exclusive=True)
    def process_data(self, data: ActivityData) -> None:
        """Entrypoint worker for the heatmap data.

        Normalizes & inverts the data into usable values.

        Args:
            data: Two dimensional data that is ready to be converted.
        """
        flat: list[float | None] = list(chain.from_iterable(data))
        normalized = [
            1 - v if v is not None else None for v in normalize_values(flat)
        ]
        self.app.call_from_thread(
            setattr, self, "data", flat_to_shape(normalized, data)
        )

    def _on_focus(self, event: Focus) -> None:
        self.action_move_cursor("right")

    def _on_leave(self, event: Leave) -> None:
        if not self.has_focus:
            self.cursor = None

    def _on_blur(self, event: Blur) -> None:
        self.cursor = None

    def _on_mouse_move(self, event: MouseMove) -> None:
        self.mouse_offset = event.offset + self.scroll_offset

    def _validate_date(self, day: Date) -> Date:
        return Date(day.year, 1, 1)

    def _watch_time_range(self) -> None:
        self.virtual_size = Size(110, 18)

    def _watch_cursor(self, cursor: HeatmapCursor | None) -> None:
        if cursor is None:
            return

        x = ((cursor.week - 1) * 3) + 4
        if not (
            self.scroll_offset.x < x < self.scroll_offset.x + self.size.width
        ):
            self.scroll_to(x=x)

        y = ((cursor.day - 1) * 2) + 1
        if not (
            self.scroll_offset.y < y < self.scroll_offset.y + self.size.height
        ):
            self.scroll_to(y=y)

    @on(Click)
    def _action_select_tile(self) -> None:
        if (day := self._date_lookup()) is not None:
            self.post_message(self.DateSelected(self, day))
        elif (week := self._week_lookup()) is not None:
            self.post_message(self.WeekSelected(self, week))
        elif (month := self._month_lookup()) is not None:
            self.post_message(self.MonthSelected(self, month))

        self.cursor = None

    def _watch_mouse_offset(self, new: Offset) -> None:
        self.cursor = (
            self._get_cursor_tile(new)
            or self._get_cursor_week(new)
            or self._get_cursor_month(new)
        )

    def _is_tile_hovered(
        self,
        *,
        day: int | None = None,
        week: int | None = None,
        month: int | None = None,
    ) -> bool:
        if self.cursor is None:
            return False

        if week is not None and self.cursor.is_week:
            if day is not None:
                week += 1
            return week == self.cursor.week

        if self.cursor.is_month:
            if month is not None:
                return month == self.cursor.month
            elif day is not None and week is not None:
                year = self.year
                if week == 52:
                    week = 0
                    year += 1
                try:
                    cal = date.fromisocalendar(year, week + 1, day + 1)
                except ValueError:
                    return False
                return cal.month == self.cursor.month and cal.year == self.year

        if day is None or week is None:
            return False

        return day + 1 == self.cursor.day and week + 1 == self.cursor.week

    def _is_offset_on_tile(self, offset: Offset) -> bool:
        return bool(
            4 <= offset.x <= 165
            and 1 <= offset.y <= 14
            and ((offset.x - 4) % 3 != 0)
            and offset.y % 2 != 0
        )

    def action_move_cursor(self, direction: Directions) -> None:
        """Move the keyboard cursor."""
        if self.cursor is None:
            self.cursor = HeatmapCursor(1, 1)

        elif direction == "right":
            self.cursor = self.cursor.move(self.year, week_delta=1)
        elif direction == "down":
            self.cursor = self.cursor.move(self.year, day_delta=1)
        elif direction == "left":
            self.cursor = self.cursor.move(self.year, week_delta=-1)
        elif direction == "up":
            self.cursor = self.cursor.move(self.year, day_delta=-1)

    def action_clear_cursor(self) -> None:
        """Clear the navigation cursor."""
        self.cursor = None

    def check_action(
        self,
        action: str,
        parameters: tuple[object, ...],
    ) -> bool | None:
        if action == "move_cursor" and self.cursor:
            if parameters[0] == "right":
                return self.cursor.week < 53
            elif parameters[0] == "down":
                return self.cursor.day < 9
            elif parameters[0] == "left":
                return self.cursor.week > 1
            else:
                return self.cursor.day > 1

        if action == "clear_cursor":
            return isinstance(self.cursor, HeatmapCursor)

        return True

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return 163

    def get_content_height(
        self,
        container: Size,
        viewport: Size,
        width: int,
    ) -> int:
        return 18

    def _get_cursor_tile(self, offset: Offset) -> HeatmapCursor | None:
        if self._is_offset_on_tile(offset):
            return HeatmapCursor(
                ((offset.x - 4) // 3) + 1,
                ((offset.y - 1) // 2) + 1,
            )

        return None

    def _get_cursor_week(self, offset: Offset) -> HeatmapCursor | None:
        if offset.y == 15 and 5 <= offset.x <= 165 and offset.x - 2 % 3 != 0:
            return HeatmapCursor(((offset.x - 4) // 3) + 1, 8)

        return None

    def _get_cursor_month(self, offset: Offset) -> HeatmapCursor | None:
        if month := self._is_offset_on_month(offset):
            return HeatmapCursor(((offset.x - 4) // 3) + 1, 9, month)

        return None

    def _is_offset_on_month(self, offset: Offset) -> int:
        if offset.y != 17 or not (3 <= offset.x <= 148):
            return 0

        month, rem = divmod(cast(int, offset.x) - 2, 13)

        if rem not in {0, 1, 2}:
            return 0

        return month + 1

    def _date_lookup(self) -> Date | None:
        if self.cursor is not None and self.cursor.is_day:
            if (
                day := self.cursor.to_date(self.year)
            ) is not None and day.year == self.year:
                return day

        return None

    def _week_lookup(self) -> Date | None:
        if self.cursor is not None and self.cursor.is_week:
            return self.cursor.to_date(self.year)

        return None

    def _month_lookup(self) -> Date | None:
        if self.cursor is not None and self.cursor.is_month:
            return self.cursor.to_date(self.year)

        return None

    def sum_week(self, week: Date) -> float:
        """Get the total for a week for any specified date."""
        return sum(
            self.values[day.py_date()]
            for day in iterate_timespan(week, days(1), 7)
        )

    def sum_month(self, month: Date) -> float:
        """Get the total for a month for any specified date."""
        return sum(
            self.values[day.py_date()]
            for day in iterate_timespan(
                month,
                days(1),
                monthrange(month.year, month.month)[1],
            )
        )

    @staticmethod
    def generate_empty_activity(year: int) -> list[list[date | None]]:
        """Generates empty data for a specified year.

        Args:
            year: Year to generate. Minimum year 1 to a maximum year 9998.

        Returns:
            A 2 dimensional array of dates or None if the day belongs to
                another year.
        """
        raw = list(
            chain.from_iterable(Calendar().yeardatescalendar(year, 12)[0])
        )
        new_cal: list[list[date | None]] = []
        for i, week in enumerate(raw):
            if i and week[0] in new_cal[-1]:
                continue

            new_cal.append([])
            for day in week:
                if day.year != year:
                    new_cal[-1].append(None)
                else:
                    new_cal[-1].append(day)

        return new_cal

    @property  # type: ignore[misc]  # NOTE: Tooltip is generated inside.
    def tooltip(self) -> str | None:  # type: ignore[override]
        if (tip_date := self._date_lookup()) is not None:
            total = int(self.values[tip_date.py_date()])
            tooltip = f"{tip_date.py_date():%-d %B}\n"
            return tooltip + format_seconds(total, include_seconds=False)

        if (tip_week := self._week_lookup()) is not None:
            total = int(self.sum_week(tip_week))
            tooltip = f"{tip_week.py_date():%U week of %Y}\n"
            return tooltip + format_seconds(total, include_seconds=False)

        if (tip_month := self._month_lookup()) is not None:
            total = int(self.sum_month(tip_month))
            tooltip = f"{tip_month.py_date():%B %Y}\n"
            return tooltip + format_seconds(total, include_seconds=False)

        return None


class HeatmapManager(BaseWidget):
    """Composite widget that manages navigating a heatmap.

    Params:
        year: Initial value for the year.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

    @dataclass
    class YearChanged(BaseMessage):
        """Message sent when the year is updated."""

        widget: HeatmapManager
        year: int

    DEFAULT_CSS: ClassVar[str] = """
    HeatmapManager {
        layout: vertical;
        align: center middle;
        height: auto;
        width: auto;

        Horizontal#navigation {
            align-horizontal: center;
            max-height: 1;
            hatch: vertical $secondary 10%;

            & > #year-input {
                align-horizontal: center;
                width: auto;
                min-width: 8;
                height: 1;
                border: none;
            }

            .nav {
                &Button {
                    max-width: 4;
                    text-align: center;

                    &#today-button {
                        width: auto;
                    }
                }
            }
        }

        &:focus-within {
            Horizontal#navigation {
                hatch: vertical $primary 30%;
            }
        }
    }
    """
    """Default CSS for the `HeatmapManager`."""

    year = var[int](
        lambda: Date.today_in_system_tz().year, init=False, bindings=True
    )
    """Current year that the widget is set to. Max is 9999 and minimum 1"""

    def __init__(
        self,
        year: int | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        if year:
            self.set_reactive(HeatmapManager.year, year)

    def _validate_year(self, year: int) -> int:
        return max(0, min(year, 9999))

    def compose(self) -> ComposeResult:
        with Horizontal(id="navigation"):
            yield Button(
                "<<",
                id="prev-year-5",
                classes="nav",
                tooltip="Jump Back Five Years",
            )
            yield Button(
                "<",
                id="prev-year",
                classes="nav",
                tooltip="View Previous Year",
            )
            yield MaskedInput(
                "9999",
                str(self.year),
                classes="nav",
                valid_empty=False,
                validators=[Integer(minimum=1, maximum=9998)],
                validate_on=("blur", "submitted"),
                id="year-input",
            )
            yield TargetButton(
                id="today-button",
                classes="nav",
                tooltip="View Current Year",
                disabled=True,
            )
            yield Button(
                ">",
                id="next-year",
                classes="nav",
                tooltip="View Next Year",
            )
            yield Button(
                ">>",
                id="next-year-5",
                classes="nav",
                tooltip="Jump Forward Five Years",
            )

        with Horizontal():
            yield Center(ActivityHeatmap().data_bind(HeatmapManager.year))

    def _watch_year(self, year: int) -> None:
        for button in self.navigation.query(Button):
            if button.id in {"prev-year-5", "prev-year"}:
                button.disabled = year <= 1
            elif button.id in {"next-year", "next-year-5"}:
                button.disabled = year >= 9998
            elif button.id == "today-button":
                button.disabled = year == Date.today_in_system_tz().year
        self.post_message(self.YearChanged(self, year))

    def _on_descendant_focus(self) -> None:
        self.navigation.refresh()

    def _on_descendant_blur(self) -> None:
        self.navigation.refresh()

    @on(Input.Submitted)
    @on(DescendantBlur)
    def _verify_year(self, message: Input.Submitted | DescendantBlur) -> None:
        message.stop()
        if not isinstance(message.control, Input):
            return

        if message.control.is_valid:
            try:
                year = int(message.control.value)
            except ValueError:
                return
            self.year = year

    def _on_button_pressed(self, message: Button.Pressed) -> None:
        message.stop()
        if message.button.id == "prev-year-5":
            self.year -= 5
        elif message.button.id == "prev-year":
            self.year -= 1
        elif message.button.id == "next-year":
            self.year += 1
        elif message.button.id == "next-year-5":
            self.year += 5
        elif message.button.id == "today-button":
            self.year = Date.today_in_system_tz().year

        with self.year_input.prevent(Input.Changed):
            self.year_input.value = str(self.year)

    @cached_property
    def navigation(self) -> Horizontal:
        """`Horizonal` bar holding all navigation widgets."""
        return self.query_one("#navigation", Horizontal)

    @cached_property
    def year_input(self) -> MaskedInput:
        """Input widget showing the selected year."""
        return self.query_exactly_one(MaskedInput)

    @cached_property
    def heatmap(self) -> ActivityHeatmap:
        """Underlying `ActivityHeatmap` displaying data."""
        return self.query_exactly_one(ActivityHeatmap)
