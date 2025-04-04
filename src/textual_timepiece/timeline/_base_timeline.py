from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import TypeAlias
from typing import TypeVar
from typing import cast

from rich.segment import Segment
from rich.style import Style as RichStyle
from textual.app import ComposeResult
from textual.await_remove import AwaitRemove
from textual.binding import Binding
from textual.binding import BindingType
from textual.css.query import NoMatches
from textual.css.query import QueryType
from textual.css.scalar import Scalar
from textual.events import DescendantBlur
from textual.events import DescendantFocus
from textual.events import MouseDown
from textual.events import MouseMove
from textual.events import MouseUp
from textual.geometry import Offset
from textual.geometry import Region
from textual.geometry import Size
from textual.reactive import reactive
from textual.reactive import var
from textual.strip import Strip
from textual.widget import AwaitMount
from textual.widget import Widget

from textual_timepiece._extra import BaseMessage
from textual_timepiece._utility import format_seconds

from ._timeline_entry import AbstractEntry
from ._timeline_entry import HorizontalEntry
from ._timeline_entry import VerticalEntry
from ._timeline_layouts import AbstractTimelineLayout
from ._timeline_layouts import HorizontalTimelineLayout
from ._timeline_layouts import VerticalTimelineLayout

if TYPE_CHECKING:
    from collections.abc import Iterable

T = TypeVar("T", bound=AbstractEntry)


class AbstractTimeline(Widget, Generic[T], can_focus=True):
    """Abstract timeline implementation with various items.

    Describes a few abstract methods for creating entry with user input.
    The chain goes as follows:
        `_on_mouse_down` -> `_on_mouse_move` -> `_on_mouse_up`
        -> `calculate_entry_size` -> Post `EntryCreated` message.

    Params:
        *children: Entries to intially add to the widget.
        duration: Duration of size of the widget.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
        tile: Whether to tile the timeline or not.
    """

    @dataclass
    class _TimelineUpdate(BaseMessage):
        """Base message that the timeline sends."""

        widget: AbstractTimeline[Any]
        entry: AbstractEntry

        @property
        def timeline(self) -> AbstractTimeline[T]:
            return self.widget

    @dataclass
    class EntryCreated(_TimelineUpdate):
        """Sent when a new entry is created."""

    @dataclass
    class EntryDeleted(_TimelineUpdate):
        """Sent when an entry is deleted."""

    @dataclass
    class EntrySelected(_TimelineUpdate):
        """Sent when a new entry selected."""

    Markers: TypeAlias = MappingProxyType[int, tuple[RichStyle, str]]
    Entry: type[T]
    Layout: type[AbstractTimelineLayout[T]]

    DURATION: ClassVar[str]
    BINDING_GROUP_TITLE: str = "Timeline"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding(
            "ctrl+down,ctrl+right",
            "adjust_tail",
            tooltip="Move entry to the backward.",
        ),
        Binding(
            "ctrl+up,ctrl+left",
            "adjust_head",
            tooltip="Move entry to the forward.",
        ),
        Binding(
            "alt+shift+down,alt+shift+left",
            "adjust_tail(True, True)",
            tooltip="Resize the tail end of the entry.",
        ),
        Binding(
            "alt+shift+up,alt+shift+right",
            "adjust_head(True, True)",
            tooltip="Resize the end of the entry forward.",
        ),
        Binding(
            "shift+up,shift+left",
            "adjust_head(False, True)",
            tooltip="Resize the start of the entry backward.",
        ),
        Binding(
            "shift+down,shift+right",
            "adjust_tail(False, True)",
            tooltip="Move the head of the entry forward.",
        ),
        Binding(
            "ctrl+d,delete,backspace",
            "delete_entry",
            "Delete Entry",
            tooltip="Delete the selected entry.",
        ),
        Binding(
            "escape",
            "clear_active",
            "Clear",
            priority=True,
            show=False,
            tooltip="Cancel creating an entry or deselect entries.",
        ),
    ]

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "timeline--normal",
    }
    DEFAULT_CSS: ClassVar[str] = """\
    AbstractTimeline {
        background: $panel-darken-1;
        .timeline--normal {
            color: white 5%;
        }
    }
    """

    children: list[T]
    _start: Offset | None = None
    _mime: T | None = None

    length = var[int](96, init=False)
    """Actual size of the widget with the direction size of the widget."""

    # TODO: Only refresh positions that have changed.
    markers = reactive[Markers](MappingProxyType({}), init=False)
    """Custom markers to place in on the timeline."""

    def __init__(
        self,
        *children: T,
        duration: int | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tile: bool = True,
    ) -> None:
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self._highlighted: T | None = None
        # TODO: Convert to multiple selections.

        self._layout = self.Layout(tile=tile)
        if duration:
            self.length = duration

    async def _on_descendant_focus(self, event: DescendantFocus) -> None:
        self._highlighted = cast(T, event.widget)
        self.post_message(self.EntrySelected(self, self._highlighted))

    async def _on_descendant_blur(self, event: DescendantBlur) -> None:
        if event.widget is self._highlighted:
            self._highlighted = None

    def mount(  # type: ignore[override] # NOTE: Making sure the user mounts the right widgets.
        self,
        *widgets: T,
        before: str | int | T | None = None,
        after: str | int | T | None = None,
    ) -> AwaitMount:
        return super().mount(*widgets, before=before, after=after)

    def mount_all(  # type: ignore[override] # NOTE: Making sure the user mounts the right widgets.
        self,
        widgets: Iterable[T],
        *,
        before: str | int | T | None = None,
        after: str | int | T | None = None,
    ) -> AwaitMount:
        return super().mount_all(widgets, before=before, after=after)

    async def _on_mouse_down(self, event: MouseDown) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse()
            self._start = event.offset
            if self._mime:
                self.post_message(self.EntryCreated(self, self._mime))
                self._mime = None

    async def _create_mime(self, offset: Offset) -> None:
        self._mime = self.Entry.mime(*self._calc_entry_size(offset))
        self.refresh_bindings()

        await self.mount(self._mime)

    async def _on_mouse_move(self, event: MouseMove) -> None:
        if self._start is None or self.app.mouse_captured != self:
            return

        if self._mime is None:
            await self._create_mime(event.offset)
        else:
            self._mime.set_dims(*self._calc_entry_size(event.offset))

    async def _on_mouse_up(self, event: MouseUp) -> None:
        if self.app.mouse_captured == self:
            self.capture_mouse(False)
        if self._mime:
            self.post_message(self.EntryCreated(self, self._mime))
            self._start = None
            self._mime = None

    def remove_children(
        self,
        selector: str | type[QueryType] | Iterable[T] = "*",  # type: ignore[override] # NOTE: Type should always be an AbstractEntry
    ) -> AwaitRemove:
        return super().remove_children(selector)

    def check_action(
        self,
        action: str,
        parameters: tuple[object, ...],
    ) -> bool | None:
        if action == "clear_active":
            return self._mime is not None or self.selected is not None
        if action in {"adjust_tail", "adjust_head"}:
            return self.selected is not None

        return True

    def action_delete_entry(self, id: str | None = None) -> None:
        """Remove the selected or provided entry from the timeline.

        Args:
            id: If removing an un-highlighted widget.
        """

        if id:
            try:
                entry = self.query_one(f"#{id}", self.Entry)
            except NoMatches:
                return
        elif self.selected:
            entry = self.selected
        else:
            return

        entry.remove()
        self.post_message(AbstractTimeline.EntryDeleted(self, entry))

    def _action_clear_active(self) -> None:
        if self._mime:
            self._mime.remove()
            self._mime = None
        else:
            cast(T, self.selected).blur()

    def action_adjust_tail(
        self,
        tail: bool = False,
        resize: bool = False,
    ) -> None:
        """Adjust the tail of the selected timeline entry.

        Args:
            tail: Increase the size if resizing.
            resize: Resize the entry instead of moving.
        """

        if resize:
            cast(T, self.selected).resize(1, tail=tail)
        else:
            cast(T, self.selected).move(1)

    def action_adjust_head(
        self,
        tail: bool = False,
        resize: bool = False,
    ) -> None:
        """Adjust the head of the selected timeline entry.

        Args:
            tail: Increase the size if resizing.
            resize: Resize the entry instead of moving.
        """

        if resize:
            cast(T, self.selected).resize(-1, tail=not tail)
        else:
            cast(T, self.selected).move(-1)

    @abstractmethod
    def _calc_entry_size(self, end: Offset) -> tuple[int, int]:
        """Calculate the size of an entry based off the offsets.

        Assumes that self._start is not None.

        Args:
            end: Offset were this method was called.

        Returns:
            A start point and size of the new widget.
        """

    def _watch_duration(self, value: int) -> None:
        setattr(self.styles, self.DURATION, value)

    @property
    def layout(self) -> AbstractTimelineLayout[T]:
        return self._layout

    @property
    def tile(self) -> bool:
        """Is calendar tiling enabled?"""
        return self._layout.tile

    @tile.setter
    def tile(self, value: bool) -> None:
        self._layout.tile = value
        self.refresh(layout=True)

    @property
    def selected(self) -> T | None:
        """Currently highlighted entry. None if there is nothing selected."""
        return self._highlighted


class VerticalTimeline(AbstractTimeline[VerticalEntry]):
    """Basic timeline widget that displays entries in a vertical view."""

    Entry = VerticalEntry
    Layout = VerticalTimelineLayout
    DURATION = "height"
    DEFAULT_CSS: ClassVar[str] = """\
    VerticalTimeline {
        height: auto !important;
        border-left: wide $secondary;
        border-right: wide $secondary;
        &:hover {
            border-left: thick $secondary;
            border-right: thick $secondary;
        }
        &:focus {
            border-left: outer $primary;
            border-right: outer $primary;
        }
    }
    """
    """Default CSS for `VerticalTimeline` widget."""

    def render_line(self, y: int) -> Strip:
        style, label = self.markers.get(
            y,
            (self.get_component_rich_style("timeline--normal"), ""),
        )

        return Strip(
            [Segment(label.center(self.size.width, "─"), style=style)]
        )

    def _calc_entry_size(self, end: Offset) -> tuple[int, int]:
        start = cast(Offset, self._start)
        return start.y if start.y < end.y else end.y, abs(end.y - start.y)

    def pre_layout(self, layout: VerticalTimelineLayout) -> None:  # type: ignore[override]
        self._nodes._sort(
            key=lambda w: (w.offset.y, cast(Scalar, w.styles.height).value),
        )

    def get_content_height(
        self,
        container: Size,
        viewport: Size,
        width: int,
    ) -> int:
        return self.length


class HorizontalTimeline(AbstractTimeline[HorizontalEntry]):
    """Basic timeline widget that displays entries in a horizontal view."""

    Entry = HorizontalEntry
    Layout = HorizontalTimelineLayout
    DURATION: ClassVar[str] = "width"
    DEFAULT_CSS: ClassVar[str] = """\
    HorizontalTimeline {
        width: auto !important;
        height: 28;
        border-top: tall $secondary;
        border-bottom: tall $secondary;
        &:hover {
            border-top: thick $secondary;
            border-bottom: thick $secondary;
        }
        &:focus {
            border-top: outer $primary;
            border-bottom: outer $primary;
        }
    }
    """
    """Default CSS for `HorizontalTimeline` widget."""

    _cached_strip = None

    def _create_strip(self) -> Strip:
        """Prerenders the strip for reuse on each line."""
        defaults = (self.get_component_rich_style("timeline--normal"), "")

        segs = list[Segment]()
        add_seg = segs.append
        prev_style = None
        current_strip = ""
        for x in range(self.size.width):
            style, _ = self.markers.get(x, defaults)
            if prev_style and style != prev_style:
                add_seg(Segment(current_strip, prev_style))
                current_strip = ""

            prev_style = style
            current_strip += "│"

        add_seg(Segment(current_strip, prev_style))

        return Strip(segs, self.size.width).simplify()

    def render_lines(self, crop: Region) -> list[Strip]:
        self._cached_strip = self._create_strip()
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        return cast("Strip", self._cached_strip)

    def _calc_entry_size(self, end: Offset) -> tuple[int, int]:
        start = cast(Offset, self._start)
        return start.x if start.x < end.x else end.x, abs(end.x - start.x)

    def pre_layout(self, layout: HorizontalTimelineLayout) -> None:  # type: ignore[override]
        self._nodes._sort(
            key=lambda w: (w.offset.x, cast(Scalar, w.styles.width).value),
        )

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.length


class AbstractRuler(Widget):
    """Abstract ruler class for marking timelines with custom markers.

    Params:
        duration: Total length of the ruler.
        marker_factory: Callable for creating the markers.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

    MarkerFactory: TypeAlias = Callable[[int], str]

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "abstractruler--label",
        "abstractruler--empty",
    }
    DEFAULT_CSS: ClassVar[str] = """\
    AbstractRuler {
        background: $panel-darken-3;

        .abstractruler--label {
            color: $secondary;
            text-style: italic;
        }
        .abstractruler--empty {
            color: $panel 50%;
        }
    }
    """
    """Default CSS for the `AbstractRuler` widget."""

    duration = var[int](86400, init=False)
    """Total time actual time the ruler spans in seconds."""

    length = reactive[int](96, layout=True, init=False)
    """Actual length of the widget."""

    subdivisions = reactive[int](24, init=False)
    """Amount of subdivisions to use when calculating markers.

    Generator gets called this amount of times.
    """

    time_chunk = var[int](3600, init=False)
    """Time chunk for each subdivision that the ruler creates.

    Computed automatically when other reactives change.
    """

    marker_len = var[int](4, init=False)
    """The marker length of the each time_chunk."""

    def __init__(
        self,
        duration: int | None = None,
        subdivisions: int | None = None,
        marker_factory: MarkerFactory | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=False,
        )
        if duration:
            self.length = duration
        if subdivisions:
            self.subdivisions = subdivisions

        self._factory = marker_factory or format_seconds

    def _compute_time_chunk(self) -> int:
        return self.duration // self.subdivisions

    def _compute_marker_len(self) -> int:
        return self.length // self.subdivisions


class VerticalRuler(AbstractRuler):
    """Vertical ruler for marking vertical timelines."""

    DEFAULT_CSS: ClassVar[str] = """\
    VerticalRuler {
        border-left: wide $secondary;
        border-right: wide $secondary;
        height: auto !important;
        width: 8;
    }
    """
    """Default CSS for the `VerticalRuler` widget."""

    def render_line(self, y: int) -> Strip:
        marker_pos, rem = divmod(y, self.marker_len)
        if y and not rem:
            return Strip(
                [
                    Segment(
                        self._factory(marker_pos * self.time_chunk).center(
                            self.size.width
                        ),
                        style=self.get_component_rich_style(
                            "abstractruler--label"
                        ),
                    )
                ]
            )

        return Strip(
            [
                Segment(
                    f" {'─' * (self.size.width - 2)} ",
                    style=self.get_component_rich_style(
                        "abstractruler--empty"
                    ),
                )
            ]
        )

    def get_content_height(
        self,
        container: Size,
        viewport: Size,
        width: int,
    ) -> int:
        return self.length


class HorizontalRuler(AbstractRuler):
    """Horizontal ruler for marking horizontal timelines."""

    DEFAULT_CSS: ClassVar[str] = """\
    HorizontalRuler {
        border-top: tall $secondary;
        border-bottom: tall $secondary;
        width: auto !important;
        height: 3;
        hatch: vertical white 5%;
    }
    """
    """Default CSS for `HorizontalRuler` widget."""

    def render_line(self, y: int) -> Strip:
        if y != (self.size.height // 2):
            return Strip.blank(self.size.width)

        style = self.get_component_rich_style("abstractruler--label")
        return Strip(
            [
                Segment(self._factory(t).rjust(self.marker_len), style)
                for t in range(self.time_chunk, self.duration, self.time_chunk)
            ]
        ).simplify()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.length


ChildTimeline = TypeVar("ChildTimeline", bound=AbstractTimeline[Any])


class TimelineNavigation(Widget, Generic[ChildTimeline]):
    """Container Widget for a single timline and its header.

    Params:
        header: Header to use at the start of the timeline.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

    Timeline: type[ChildTimeline]

    length = var[int](96, init=False)
    """Actual length of the actual timeline navigation."""

    def __init__(
        self,
        header: Widget | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=False,
        )

        self._header = header
        if header:
            header.add_class("-timeline-header")

    def compose(self) -> ComposeResult:
        if self._header:
            yield self._header
        yield self.Timeline().data_bind(TimelineNavigation.length)

    @property
    def timeline(self) -> ChildTimeline:
        return self.query_exactly_one(self.Timeline)


class VerticalTimelineNavigation(TimelineNavigation[VerticalTimeline]):
    """Vertical widget containing a vertical timeline and header."""

    Timeline = VerticalTimeline

    DEFAULT_CSS: ClassVar[str] = """
    VerticalTimelineNavigation {
        layout: vertical !important;
        height: auto !important;
    }
    """
    """Default CSS for `VerticalTimelineNavigation` widget."""


class HorizontalTimelineNavigation(TimelineNavigation[HorizontalTimeline]):
    """Horizontal widget containing a horizontal timeline and header."""

    Timeline = HorizontalTimeline

    DEFAULT_CSS: ClassVar[str] = """
    HorizontalTimelineNavigation {
        layout: horizontal !important;
        width: auto !important;
    }
    """
    """Default CSS for `HorizontalTimelineNavigation` widget."""
