from __future__ import annotations

import sys
from abc import abstractmethod
from types import MappingProxyType
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import TypeAlias
from typing import cast

if sys.version_info >= (3, 13):
    from typing import TypeVar
else:
    from typing_extensions import TypeVar

from rich.segment import Segment
from rich.style import Style as RichStyle
from textual.binding import Binding
from textual.binding import BindingType
from textual.css.query import NoMatches
from textual.css.query import QueryType
from textual.geometry import Offset
from textual.geometry import Region
from textual.geometry import Size
from textual.reactive import Reactive
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

    from textual.app import ComposeResult
    from textual.await_remove import AwaitRemove
    from textual.css.scalar import Scalar
    from textual.events import DescendantBlur
    from textual.events import DescendantFocus
    from textual.events import MouseDown
    from textual.events import MouseMove
    from textual.events import MouseUp

EntryType = TypeVar("EntryType", bound="AbstractEntry")
TimelineType = TypeVar("TimelineType", bound="AbstractTimeline[Any]")

EntryT = TypeVar("EntryT", bound="AbstractEntry")


class AbstractTimeline(Widget, Generic[EntryType], can_focus=True):
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

    class Updated(BaseMessage[TimelineType], Generic[EntryT, TimelineType]):
        """Base class for all timeline messages."""

        def __init__(self, widget: TimelineType, entry: EntryT) -> None:
            super().__init__(widget)

            self.entry = entry
            """Entry that was updated."""

        @property
        def timeline(self) -> TimelineType:
            """Alias for `widget` attribute."""
            return self.widget

    class Created(Updated[EntryT, TimelineType]):
        """Sent when a new entry is created."""

    class Deleted(Updated[EntryT, TimelineType]):
        """Sent when an entry is deleted."""

    class Selected(Updated[EntryType, TimelineType]):
        """Sent when a new entry selected."""

    Markers: TypeAlias = MappingProxyType[int, tuple[RichStyle, str]]
    Entry: type[EntryType]
    Layout: type[AbstractTimelineLayout[Any]]

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

    children: list[EntryType]
    _start: Offset | None = None
    _mime: EntryType | None = None

    length = Reactive[int](96, init=False, layout=True)
    """Actual size of the widget with the direction size of the widget."""

    markers = Reactive[Markers](
        MappingProxyType({}),
        init=False,
        compute=False,
        repaint=False,
    )
    """Custom markers to place on the timeline."""

    def __init__(
        self,
        *children: EntryType,
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

        self._highlighted: EntryType | None = None
        # TODO: Convert to multiple selections.

        self._layout = self.Layout(tile=tile)
        if duration:
            self.length = duration

    async def _on_descendant_focus(self, event: DescendantFocus) -> None:
        self._highlighted = cast("EntryType", event.widget)
        self.post_message(self.Selected(self, self._highlighted))

    async def _on_descendant_blur(self, event: DescendantBlur) -> None:
        if event.widget is self._highlighted:
            self._highlighted = None

    @abstractmethod
    def _watch_markers(self, old: Markers, new: Markers) -> None: ...

    def mount(  # type: ignore[override] # NOTE: Making sure the user mounts the right widgets.
        self,
        *widgets: EntryType,
        before: str | int | EntryType | None = None,
        after: str | int | EntryType | None = None,
    ) -> AwaitMount:
        return super().mount(*widgets, before=before, after=after)

    def mount_all(  # type: ignore[override] # NOTE: Making sure the user mounts the right widgets.
        self,
        widgets: Iterable[EntryType],
        *,
        before: str | int | EntryType | None = None,
        after: str | int | EntryType | None = None,
    ) -> AwaitMount:
        return super().mount_all(widgets, before=before, after=after)

    async def _on_mouse_down(self, event: MouseDown) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse()
            self._start = event.offset
            if self._mime:
                self.post_message(self.Created(self, self._mime))
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
            self.post_message(self.Created(self, self._mime))
            self._start = None
            self._mime = None

    def remove_children(
        self,
        selector: str | type[QueryType] | Iterable[EntryType] = "*",  # type: ignore[override] # NOTE: Type should always be an AbstractEntry
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
        self.post_message(self.Deleted(self, entry))

    def _action_clear_active(self) -> None:
        if self._mime:
            self._mime.remove()
            self._start = None
            self._mime = None
        else:
            cast("EntryType", self.selected).blur()

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
            cast("EntryType", self.selected).resize(1, tail=tail)
        else:
            cast("EntryType", self.selected).move(1)

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
            cast("EntryType", self.selected).resize(-1, tail=not tail)
        else:
            cast("EntryType", self.selected).move(-1)

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
    def layout(self) -> AbstractTimelineLayout[EntryType]:
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
    def selected(self) -> EntryType | None:
        """Currently highlighted entry. None if there is nothing selected."""
        return self._highlighted


VerticalEntryType = TypeVar(
    "VerticalEntryType",
    bound=VerticalEntry,
    default=VerticalEntry,
)

VerticalEntryT = TypeVar(
    "VerticalEntryT",
    bound=VerticalEntry,
    default=VerticalEntry,
)

VerticalTimelineType = TypeVar(
    "VerticalTimelineType",
    bound="VerticalTimeline",
    default="VerticalTimeline",
)


class VerticalTimeline(AbstractTimeline[VerticalEntryType]):
    """Timeline that displays entries in a vertical view.

    Params:
        *children: Entries to intially add to the widget.
        duration: Size of the widget.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
        tile: Whether to tile the timeline or not. Set to `False` if a single
            column of entries is preferred.
    """

    Entry = VerticalEntry  # type: ignore[assignment] # FIX: Need to research to how to correctly accomplish this.
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

    class Created(
        AbstractTimeline.Created[VerticalEntryT, VerticalTimelineType]
    ):
        """Sent when a new entry is created."""

    class Deleted(
        AbstractTimeline.Deleted[VerticalEntryT, VerticalTimelineType]
    ):
        """Sent when an entry is deleted."""

    class Selected(
        AbstractTimeline.Selected[VerticalEntryT, VerticalTimelineType]
    ):
        """Sent when a new entry selected."""

    def _watch_markers(
        self,
        old: AbstractTimeline.Markers,
        new: AbstractTimeline.Markers,
    ) -> None:
        for line in old.keys() ^ new.keys():
            self.refresh_line(line)

    def refresh_line(self, y: int) -> None:
        """Refresh a single line.

        Args:
            y: Coordinate of line.
        """
        self.refresh(
            Region(
                0,
                y - self.scroll_offset.y,
                max(self.virtual_size.width, self.size.width),
                1,
            )
        )

    def render_lines(self, crop: Region) -> list[Strip]:
        self._basic_strip = Strip(
            [
                Segment(
                    "─" * self.size.width,
                    style=self.get_component_rich_style("timeline--normal"),
                )
            ]
        )
        return super().render_lines(crop)

    def render_line(self, y: int) -> Strip:
        if marker := self.markers.get(y):
            style, label = marker

            return Strip(
                [Segment(label.center(self.size.width, "─"), style=style)]
            )

        return self._basic_strip

    def _calc_entry_size(self, end: Offset) -> tuple[int, int]:
        start = cast("Offset", self._start)
        return start.y if start.y < end.y else end.y, abs(end.y - start.y)

    def pre_layout(self, layout: VerticalTimelineLayout) -> None:  # type: ignore[override]
        # Sorting with the public sort method will cause infinite layout calls.
        self._nodes._sort(  # TODO: This needs a public solution.
            key=lambda w: (w.offset.y, cast("Scalar", w.styles.height).value),
        )

    def get_content_height(
        self,
        container: Size,
        viewport: Size,
        width: int,
    ) -> int:
        return self.length


HorizontalEntryType = TypeVar(
    "HorizontalEntryType",
    bound=HorizontalEntry,
    default=HorizontalEntry,
)

HorizontalEntryT = TypeVar(
    "HorizontalEntryT",
    bound=HorizontalEntry,
    default=HorizontalEntry,
)
HorizontalTimelineType = TypeVar(
    "HorizontalTimelineType",
    bound="HorizontalTimeline",
    default="HorizontalTimeline",
)


class HorizontalTimeline(AbstractTimeline[HorizontalEntryType]):
    """Timeline that displays entries in a horizontal view.

    Params:
        *children: Entries to intially add to the widget.
        duration: Size of the widget.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
        tile: Whether to tile the timeline or not. Set to `False` if a single
            row of entries is preferred.
    """

    Entry = HorizontalEntry  # type: ignore[assignment] # FIX: Need to research to how to correctly accomplish this.
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

    class Created(
        AbstractTimeline.Created[HorizontalEntryT, HorizontalTimelineType]
    ):
        """Sent when a new entry is created."""

    class Deleted(
        AbstractTimeline.Deleted[HorizontalEntryT, HorizontalTimelineType]
    ):
        """Sent when an entry is deleted."""

    class Selected(
        AbstractTimeline.Selected[HorizontalEntryT, HorizontalTimelineType]
    ):
        """Sent when a new entry selected."""

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
        return self._cached_strip

    def _watch_markers(
        self,
        old: AbstractTimeline.Markers,
        new: AbstractTimeline.Markers,
    ) -> None:
        if old.keys() ^ new.keys():
            self.refresh()

    def _calc_entry_size(self, end: Offset) -> tuple[int, int]:
        start = cast("Offset", self._start)
        return start.x if start.x < end.x else end.x, abs(end.x - start.x)

    def pre_layout(self, layout: HorizontalTimelineLayout) -> None:  # type: ignore[override]
        # Sorting with the public sort method will cause infinite layout calls.
        self._nodes._sort(  # TODO: This needs a public solution .
            key=lambda w: (w.offset.x, cast("Scalar", w.styles.width).value),
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

    time_chunk = Reactive[int](3600, init=False, compute=False)
    """Time chunk for each subdivision that the ruler creates.

    Computed automatically when other reactives change.
    """

    marker_len = Reactive[int](4, init=False, compute=False)
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
    """Vertical ruler for marking vertical timelines.

    Params:
        duration: Total length of the ruler.
        marker_factory: Callable for creating the markers.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

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
    """Horizontal ruler for marking horizontal timelines.

    Params:
        duration: Total length of the ruler.
        marker_factory: Callable for creating the markers.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

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


ChildTimeline = TypeVar("ChildTimeline", bound="AbstractTimeline[Any]")


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


class VerticalTimelineNavigation(
    TimelineNavigation[VerticalTimeline[VerticalEntryType]]
):
    """Vertical widget containing a vertical timeline and header.

    Params:
        header: Header to use at the start of the timeline.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

    Timeline = VerticalTimeline[VerticalEntryT]

    DEFAULT_CSS: ClassVar[str] = """\
    VerticalTimelineNavigation {
        layout: vertical !important;
        height: auto !important;
    }
    """
    """Default CSS for `VerticalTimelineNavigation` widget."""


class HorizontalTimelineNavigation(
    TimelineNavigation[HorizontalTimeline[HorizontalEntryType]]
):
    """Horizontal widget containing a horizontal timeline and header.

    Params:
        header: Header to use at the start of the timeline.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
    """

    Timeline = HorizontalTimeline[HorizontalEntryT]

    DEFAULT_CSS: ClassVar[str] = """\
    HorizontalTimelineNavigation {
        layout: horizontal !important;
        width: auto !important;
    }
    """
    """Default CSS for `HorizontalTimelineNavigation` widget."""
