from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable
from math import floor
from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar
from typing import cast

from textual.css.scalar import Scalar
from textual.geometry import NULL_SPACING
from textual.geometry import Offset
from textual.geometry import Region
from textual.geometry import Size
from textual.layout import ArrangeResult
from textual.layout import Layout
from textual.layout import WidgetPlacement
from textual.layouts.horizontal import HorizontalLayout
from textual.layouts.vertical import VerticalLayout

from ._timeline_entry import AbstractEntry
from ._timeline_entry import HorizontalEntry
from ._timeline_entry import VerticalEntry

if TYPE_CHECKING:
    from ._base_timeline import AbstractTimeline


T = TypeVar("T", bound=AbstractEntry)


class AbstractTimelineLayout(Layout, Generic[T]):
    SubLayout: type[Layout]
    name = "timeline"

    def __init__(self, *, tile: bool = True) -> None:
        self.tile = tile
        self._layout = self.SubLayout()

    def arrange(  # type: ignore[override] # NOTE: Always will be attached to a timeline widget.
        self,
        parent: AbstractTimeline[T],
        entries: list[T],
        size: Size,
    ) -> ArrangeResult:
        if not self.tile:
            return self._layout.arrange(parent, entries, size)  # type: ignore[arg-type] # NOTE: Asking for a parent class anyway.

        parent.pre_layout(self)
        # NOTE: Sorts the widgets in pre-layout by offset and size.

        return [
            WidgetPlacement(
                region=region,
                offset=offset,
                margin=NULL_SPACING,
                widget=entry,
                absolute=True,
            )
            for entry, (region, offset) in zip(
                entries, self._tile_entries(size, entries), strict=False
            )
        ]

    def _process_group(
        self,
        add_tile: Callable[[tuple[int, int]], None],
        slots: list[T],
        size: int,
    ) -> None:
        n = len(slots)
        tile_size = round(size / n)

        for i in range(n):
            add_tile((i * tile_size, tile_size))

    @abstractmethod
    def _tile_entries(
        self,
        size: Size,
        entries: list[T],
    ) -> list[tuple[Region, Offset]]: ...


class VerticalTimelineLayout(AbstractTimelineLayout[VerticalEntry]):
    SubLayout = VerticalLayout
    name = "vertical_timeline"

    def _tile_entries(
        self,
        size: Size,
        entries: list[VerticalEntry],
    ) -> list[tuple[Region, Offset]]:
        # NOTE: Uses this as reference: https://github.com/rajeshdavidbabu/Javascript-Event-Calender
        previous_end = None
        columns = list[VerticalEntry]()
        add_column = columns.append
        tiling = list[tuple[int, int]]()
        add_tile = tiling.append
        for entry in entries:
            if previous_end is not None and entry.offset.y >= previous_end:
                self._process_group(add_tile, columns, size.width)
                previous_end = None
                columns.clear()

            add_column(entry)

            end = entry.offset.y + cast("Scalar", entry.styles.height).value
            if previous_end is None or end > previous_end:
                previous_end = end

        if columns:
            self._process_group(add_tile, columns, size.width)

        return [
            (
                Region(
                    0,
                    0,
                    tile_width,
                    round(cast("Scalar", entry.styles.height).value),
                ),
                Offset(col, floor(entry.offset.y)),
            )
            for entry, (col, tile_width) in zip(entries, tiling, strict=False)
        ]


class HorizontalTimelineLayout(AbstractTimelineLayout[HorizontalEntry]):
    SubLayout = HorizontalLayout
    name = "horizontal_timeline"

    def _tile_entries(
        self,
        size: Size,
        entries: list[HorizontalEntry],
    ) -> list[tuple[Region, Offset]]:
        # NOTE: Uses this as reference: https://github.com/rajeshdavidbabu/Javascript-Event-Calender
        previous_end = None
        rows = list[HorizontalEntry]()
        add_row = rows.append
        tiling = list[tuple[int, int]]()
        add_tile = tiling.append
        for entry in entries:
            if previous_end is not None and entry.offset.x >= previous_end:
                self._process_group(add_tile, rows, size.height)
                previous_end = None
                rows.clear()

            add_row(entry)

            end = entry.offset.x + cast("Scalar", entry.styles.width).value
            if previous_end is None or end > previous_end:
                previous_end = end

        if rows:
            self._process_group(add_tile, rows, size.height)

        return [
            (
                Region(
                    0,
                    0,
                    round(cast("Scalar", entry.styles.width).value),
                    tile_height,
                ),
                Offset(floor(entry.offset.x), row),
            )
            for entry, (row, tile_height) in zip(entries, tiling, strict=False)
        ]
