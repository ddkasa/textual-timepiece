from __future__ import annotations

import sys
from abc import abstractmethod
from dataclasses import dataclass
from typing import ClassVar
from typing import cast
from uuid import uuid4

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from rich.console import RenderableType
from textual.await_remove import AwaitRemove
from textual.css.scalar import Scalar
from textual.events import Leave
from textual.events import MouseDown
from textual.events import MouseEvent
from textual.events import MouseMove
from textual.events import MouseUp
from textual.geometry import Offset
from textual.geometry import Size
from textual.visual import SupportsVisual
from textual.widgets import Static

from textual_timepiece._extra import BaseMessage

# Simpliefy Methods


class AbstractEntry(Static, can_focus=True):
    """Abstract entry widget for visual timeline widgets.

    Params:
        id: ID of the Widget.
        content: A Rich renderable, or string containing console markup.
        offset: Initial offset to use for the entry.
        size: Initial size to use for the entry.
        markup: True if markup should be parsed and rendered.
        name: Name of widget.
        classes: Space separated list of class names.
        disabled: Whether the static is disabled or not.
    """

    @dataclass
    class _EntryMessage(BaseMessage):
        """Base message for all entries."""

        widget: AbstractEntry

        @property
        def entry(self) -> AbstractEntry:
            return self.widget

    @dataclass
    class Resize(_EntryMessage):
        """Entry was resized by the user."""

        size: Size
        delta: int

    @dataclass
    class Moved(_EntryMessage):
        """Entry was moved by the user."""

        delta: int

    DIMENSION: ClassVar[str]
    DEFAULT_CSS: ClassVar[str] = """\
    AbstractEntry {
        box-sizing: content-box;
        position: absolute !important;
        background: $secondary-background-darken-2;
        content-align: center middle;
        text-align: center;
        color: auto;
        &:hover {
            border: thick $secondary;
        }
        &.selected {
            border: double $primary;
            color: $primary;
        }
        &:focus {
            color: $primary;
            text-style: bold;
        }
        &.moving {
            border: thick $primary;
        }
        &.-mime {
            opacity: 75%;
            color: auto;
        }
    }
    """

    EDGE_MARGIN: ClassVar[int]
    """The amount of space the margin takes up for the resizing grip."""

    ALLOW_MAXIMIZE = False

    offset: Offset
    _is_moving: bool | None = None
    _clicked: Offset | None = None
    _start_is_hovered: bool | None = None

    def __init__(
        self,
        id: str,
        content: RenderableType | SupportsVisual = "",
        offset: int | None = None,
        size: int | None = None,
        *,
        markup: bool = True,
        name: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            content,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            expand=False,
            shrink=False,
        )
        self.set_dims(offset, size)

    @classmethod
    def mime(
        cls,
        offset: int | None = None,
        size: int | None = None,
        *,
        name: str | None = None,
        markup: bool = True,
        disabled: bool = False,
    ) -> Self:
        """Instatiate a mime entry. For previewing resizing visually.

        Args:
            content: A Rich renderable, or string containing console markup.
            offset: Initial offset to use for the entry.
            size: Initial size to use for the entry.
            markup: True if markup should be parsed and rendered.
            name: Name of widget.
            disabled: Whether the static is disabled or not.

        Returns:
            Constructed timeline entry.
        """
        return cls(
            f"id-{uuid4()}",
            "",
            offset,
            size,
            markup=markup,
            name=name,
            classes="-mime",
            disabled=disabled,
        )

    async def _on_mouse_down(self, event: MouseDown) -> None:
        if self.app.mouse_captured is None:
            self.capture_mouse()
            self._is_focused(event.offset)

    def _on_mouse_move(self, event: MouseMove) -> None:
        if self._clicked:
            self._adjust(event)
        elif self.mouse_hover:
            self._add_edge(event.offset)
            self.add_class("hovered")

    async def _on_mouse_up(self, event: MouseUp) -> None:
        if self.app.mouse_captured == self:
            self.capture_mouse(False)
            await self._is_unfocused(event)

    def _adjust(self, event: MouseMove) -> None:
        if (
            self._clicked is not None
            and event.button != 0
            and self._is_moving is not None
        ):
            if self._is_moving:
                self.add_class("moving")
                self.move(self.sel_delta(event))
            elif self._start_is_hovered is not None:
                self.resize(
                    self.sel_delta(event),
                    tail=self._start_is_hovered,
                )

    def _on_leave(self, event: Leave) -> None:
        self.remove_class("size_end", "size_start")

    def _is_focused(self, offset: Offset) -> None:
        self._is_moving = self.is_moving(offset)
        if not self._is_moving:
            self._add_edge(offset)
            self._start_is_hovered = self.is_start(offset)

        self._clicked = offset

    async def _is_unfocused(self, event: MouseUp) -> None:
        self._clicked = None
        self._is_moving = None
        self._start_is_hovered = None
        self.remove_class("moving", "size_start", "size_end")

    def resize(self, delta: int, *, tail: bool) -> None:
        """Public method for resizing the widget.

        Args:
            delta: total amount to be moved.
            tail: Whether to adjust the end or the start of the widget.
        """
        delta = self._resize_helper(delta, tail=tail)
        self.post_message(AbstractEntry.Resize(self, self.size, delta))

    @abstractmethod
    def move(self, delta: int) -> None:
        """Public method for moving the entry.

        Args:
            delta: total amount to move the entry by.
        """

    @abstractmethod
    def _resize_helper(self, delta: int, *, tail: bool) -> int:
        """Resizing logic for the entry.

        Args:
            delta: Total amount to be moved.
            tail: Whether to adjust the end of the widget or the start.

        Returns:
            The total amount adjusted.
        """

    @abstractmethod
    def is_tail(self, offset: Offset) -> bool:
        """Is the offset hovering the tail of the widget?

        Args:
            offset: Mouse offset to the check against.

        Returns:
            True if its the tail else False.
        """

    @abstractmethod
    def is_head(self, offset: Offset) -> bool:
        """Is the offset hovering the head of the widget?

        Args:
            offset: Mouse offset to the check against.

        Returns:
            True if its the tail else False.
        """

    @abstractmethod
    def is_start(self, offset: Offset) -> bool:
        """Is the offset hovering the first half of the widget?

        Args:
            offset: Mouse offset to check against.

        Returns:
            True if the offset hovering the first half of the widget.
        """

    def is_moving(self, offset: Offset) -> bool:
        """Is the widget moving or resizing?

        Args:
            offset: Mouse offset to check against.

        Returns:
            True if the widget is moving else False.
        """
        return not (self.is_tail(offset) or self.is_head(offset))

    @abstractmethod
    def sel_delta(self, event: MouseEvent) -> int:
        """Select the correct delta for move/resize operations.

        Args:
            event: Mouse event to extract the delta from.

        Returns:
            The main delta of one mouse direction.
        """

    def _add_edge(self, offset: Offset) -> None:
        if self._clicked:
            # NOTE: Making sure the edge doesn't change after locking in.
            return

        self.set_class(self.is_tail(offset), "size_start")
        self.set_class(self.is_head(offset), "size_end")

    @abstractmethod
    def set_dims(
        self,
        offset: int | None = None,
        size: int | None = None,
    ) -> None:
        """Set entry dimensions directly.

        Args:
            offset: The offset of the entry in the core location.
            size: The size of the entry.
        """

    @abstractmethod
    def merge(self, other: Self) -> AwaitRemove:
        """Merge two entries into one taking the furthest extents.

        Args:
            other: The other entry to merge into.

        Returns:
            An `AwaitRemove` object for removing the supplied entry.
        """

    @property
    @abstractmethod
    def start(self) -> int:
        """The start of the entry."""

    @property
    def dimension(self) -> int:
        """Alias for the size of the entry depending on orientation."""
        return cast(int, getattr(self.styles, self.DIMENSION).value)

    @dimension.setter
    def dimension(self, value: int) -> None:
        """Set the size of the entry depening on orientation."""
        setattr(self.styles, self.DIMENSION, value)

    @property
    def end(self) -> int:
        return self.start + self.dimension


class VerticalEntry(AbstractEntry):
    """Vertical entry for a vertical timeline layout.

    Params:
        id: ID of the Widget.
        content: A Rich renderable, or string containing console markup.
        offset: Initial offset to use for the entry.
        size: Initial size to use for the entry.
        markup: True if markup should be parsed and rendered.
        name: Name of widget.
        classes: Space separated list of class names.
        disabled: Whether the static is disabled or not.
    """

    DIMENSION = "height"
    EDGE_MARGIN: ClassVar[int] = 1
    DEFAULT_CSS: ClassVar[str] = """\
    VerticalEntry {
        width: 100%;
        min-height: 2;
        height: 2;
        border-top: double $panel-lighten-2;
        border-bottom: double $panel-lighten-2;
        &:hover.size_start {
            border: none;
            border-top: double $secondary;
            border-bottom: double $panel-lighten-2;
        }
        &:hover.size_end {
            border: none;
            border-bottom: double $secondary;
            border-top: double $panel-lighten-2;
        }
        &:focus.size_start {
            border: none;
            border-top: thick $primary;
            border-bottom: double $primary;
        }
        &:focus.size_end {
            border: none;
            border-bottom: thick $primary;
            border-top: double $primary;
        }
        &:focus {
            border: double $primary;
        }
        &.-mime {
            hatch: horizontal white 5%;
        }
    }
    """
    """Default CSS for `VerticalEntry` widget."""

    def sel_delta(self, event: MouseEvent) -> int:
        return event.delta_y

    def is_tail(self, offset: Offset) -> bool:
        return 0 <= offset.y <= self.EDGE_MARGIN

    def is_head(self, offset: Offset) -> bool:
        height = cast(Scalar, self.styles.height).value
        return height - self.EDGE_MARGIN <= offset.y <= height

    def is_start(self, offset: Offset) -> bool:
        return offset.y < cast(Scalar, self.styles.height).value / 2

    def move(self, delta: int) -> None:
        offset = Offset(0, delta)
        self.offset = self.offset + offset
        self.post_message(VerticalEntry.Moved(self, delta))

    def merge(self, other: VerticalEntry) -> AwaitRemove:
        y1, y2 = self.offset.y, other.offset.y
        start = y1 if y1 <= y2 else y2
        self.offset = Offset(0, start)
        e1, e2 = self.end, other.end
        self.styles.height = abs(start - (e1 if e1 >= e2 else e2))
        return other.remove()

    def _resize_helper(self, delta: int, *, tail: bool) -> int:
        if tail:
            delta *= -1

        new_height = cast(Scalar, self.styles.height).value + delta

        if tail and new_height != cast(Scalar, self.styles.height).value:
            self.offset += Offset(0, -delta)

        self.styles.height = new_height
        return delta

    def set_dims(
        self,
        offset: int | None = None,
        size: int | None = None,
    ) -> None:
        if offset:
            self.offset = Offset(0, offset)
        if size:
            self.styles.height = size

    @property
    def start(self) -> int:
        return self.offset.y


class HorizontalEntry(AbstractEntry):
    """Horizontal entry for a horizontal timeline layout.

    Params:
        id: ID of the Widget.
        content: A Rich renderable, or string containing console markup.
        offset: Initial offset to use for the entry.
        size: Initial size to use for the entry.
        markup: True if markup should be parsed and rendered.
        name: Name of widget.
        classes: Space separated list of class names.
        disabled: Whether the static is disabled or not.
    """

    DIMENSION = "width"
    EDGE_MARGIN: ClassVar[int] = 2
    DEFAULT_CSS: ClassVar[str] = """\
    HorizontalEntry {
        min-width: 2;
        width: 4;
        height: 100%;
        border-left: double $panel-lighten-2;
        border-right: double $panel-lighten-2;
        &:hover.size_start {
            border: none;
            border-left: double $secondary;
            border-right: double $panel-lighten-2;
        }
        &:hover.size_end {
            border: none;
            border-right: double $secondary;
            border-left: double $panel-lighten-2;
        }
        &:focus.size_start {
            border: none;
            border-left: thick $primary;
            border-right: double $primary;
        }
        &:focus.size_end {
            border: none;
            border-left: double $primary;
            border-right: thick $primary;
        }
        &:focus {
            border: double $primary;
        }
        &.-mime {
            hatch: vertical white 5%;
        }
    }
    """
    """Default CSS for `HorizontalEntry` widget."""

    def sel_delta(self, event: MouseEvent) -> int:
        return event.delta_x

    def is_tail(self, offset: Offset) -> bool:
        return 0 <= offset.x <= self.EDGE_MARGIN

    def is_head(self, offset: Offset) -> bool:
        width = cast(Scalar, self.styles.width).value
        return width - self.EDGE_MARGIN <= offset.x <= width

    def is_start(self, offset: Offset) -> bool:
        return offset.x < cast(Scalar, self.styles.width).value / 2

    def move(self, delta: int) -> None:
        offset = Offset(delta, 0)
        self.offset = self.offset + offset
        self.post_message(HorizontalEntry.Moved(self, delta))

    def merge(self, other: AbstractEntry) -> AwaitRemove:
        x1, x2 = self.offset.x, other.offset.x
        start = x1 if x1 <= x2 else x2
        self.offset = Offset(start, 0)
        e1, e2 = self.end, other.end
        self.styles.width = abs(start - (e1 if e1 >= e2 else e2))
        return other.remove()

    def _resize_helper(self, delta: int, *, tail: bool) -> int:
        if tail:
            delta *= -1

        new_width = cast(Scalar, self.styles.width).value + delta

        if tail and new_width != cast(Scalar, self.styles.width).value:
            self.offset += Offset(-delta, 0)

        self.styles.width = new_width
        return delta

    def set_dims(
        self, offset: int | None = None, size: int | None = None
    ) -> None:
        if offset:
            self.offset = Offset(offset, 0)
        if size:
            self.styles.width = size

    @property
    def start(self) -> int:
        return self.offset.x
