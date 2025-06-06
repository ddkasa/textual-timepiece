"""Holds mostly composite widgets that build upon the timeline."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import TypeVar
from typing import cast

from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.reactive import var

from textual_timepiece._utility import format_seconds
from textual_timepiece.timeline._base_timeline import HorizontalRuler
from textual_timepiece.timeline._base_timeline import VerticalRuler

from ._base_timeline import AbstractRuler
from ._base_timeline import HorizontalEntryType
from ._base_timeline import HorizontalTimelineNavigation
from ._base_timeline import TimelineNavigation
from ._base_timeline import VerticalEntryType
from ._base_timeline import VerticalTimelineNavigation

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widget import Widget

# NOTE: How many premade widgets do I create?
# TODO: Calculate subdivisions dynamically.
# TODO: Header widgets for each timeline.
# TODO: Header Padding

# Approaches
# 1. Allow to set full distance.
# 2. Allow to set intervals.


def _default_marker_factory(index: int) -> str:
    return format_seconds(index, include_seconds=False)


Navigation = TypeVar("Navigation", bound=TimelineNavigation[Any])
Ruler = TypeVar("Ruler", bound=AbstractRuler)


class AbstractRuledTimeline(ScrollableContainer, Generic[Navigation, Ruler]):
    """Ruled timelines with markers.

    Params:
        total: Total amount of timelines to draw.
        marker_factory: Factory function for creating markers on the ruler.
            Defaults to generating markers in the *HH:mm* format.
        header_factory: Factory function for creating headers.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
        can_maximize: Whether the widget can be maximized or not.
    """

    Timeline: type[Navigation]

    total = var[int](1, init=False)
    """Total amount of timelines to compose. Minimum 1."""

    duration = var[int](86400, init=False)
    """Total time included in widget in seconds."""

    length = reactive[int](96, init=False, layout=True)
    """Actual length of the timelines."""

    def __init__(
        self,
        total: int | None = None,
        marker_factory: AbstractRuler.MarkerFactory | None = None,
        header_factory: Callable[[int], Widget] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        can_maximize: bool | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            can_maximize=can_maximize,
        )
        if total:
            self.set_reactive(
                AbstractRuledTimeline.total,
                self._validate_total(total),
            )

        self._marker_factory = marker_factory or _default_marker_factory
        self._header_factory = header_factory

    def compose(self) -> ComposeResult:
        for i in range(1, self.total + 1):
            header = self._header_factory(i) if self._header_factory else None
            yield self.Timeline(header, id=f"timeline-{i}").data_bind(
                AbstractRuledTimeline.length
            )

    def _validate_total(self, value: int) -> int:
        return max(value, 1)

    async def _watch_total(self, old: int, new: int) -> None:
        if old < new:
            await self.mount(
                *(
                    self.Timeline(
                        self._header_factory(i)
                        if self._header_factory
                        else None,
                        id=f"timeline-{i}",
                    ).data_bind(AbstractRuledTimeline.length)
                    for i in range(old + 1, new + 1)
                )
            )
        else:
            timelines: list[Navigation] = []
            for i in range(old, new, -1):
                try:
                    tl = self.query_one(f"#timeline-{i}", self.Timeline)
                except NoMatches as err:
                    self.log.debug(err)
                else:
                    timelines.append(tl)
            await self.remove_children(timelines)

    @property
    def ruler(self) -> Ruler:
        return cast("Ruler", self.query_exactly_one(AbstractRuler))

    @property
    def subdivisions(self) -> int:
        return self.ruler.subdivisions

    @subdivisions.setter
    def subdivisions(self, value: int) -> None:
        self.ruler.subdivisions = value


class RuledVerticalTimeline(
    AbstractRuledTimeline[VerticalTimelineNavigation, VerticalRuler]
):
    """Ruled vertical timeline with markers.

    !!! note
        If providing a headers with with the `header_factory` parameter make
        sure to compensate with top padding for the ruler to keep alignment
        in place.

    Params:
        total: Total amount of timelines to draw.
        marker_factory: Factory function for creating markers on the ruler.
            Defaults to generating markers in the *HH:mm* format.
        header_factory: Factory function for creating headers.
        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
        can_maximize: Whether the widget can be maximized or not.
    """

    Timeline = VerticalTimelineNavigation[VerticalEntryType]
    DEFAULT_CSS: ClassVar[str] = """\
    RuledVerticalTimeline {
        layout: horizontal;
        width: 1fr;
        & > VerticalTimelineNavigation {
            width: 1fr;
            & > VerticalTimeline {
                width: 1fr;
            }
        }
    }
    """
    """Default CSS for `RuledVerticalTimeline` widget."""

    def compose(self) -> ComposeResult:
        yield VerticalRuler(marker_factory=self._marker_factory).data_bind(
            RuledVerticalTimeline.length
        )
        yield from super().compose()


class RuledHorizontalTimeline(
    AbstractRuledTimeline[HorizontalTimelineNavigation, HorizontalRuler]
):
    """Ruled horizontal timeline with markers.

    !!! note
        If providing a headers with with the `header_factory` parameter make
        sure to compensate with left padding for the ruler to keep alignment
        in place.

    Params:
        total: Total amount of timelines to draw.
        marker_factory: Factory function for creating markers on the ruler.
            Defaults to generating markers in the *HH:mm* format.
        header_factory: Factory function for creating headers.

        name: The name of the widget.
        id: The ID of the widget in the DOM.
        classes: The CSS classes for the widget.
        disabled: Whether the widget is disabled or not.
        can_maximize: Whether the widget can be maximized or not.
    """

    Timeline = HorizontalTimelineNavigation[HorizontalEntryType]
    DEFAULT_CSS: ClassVar[str] = """\
    RuledHorizontalTimeline {
        height: 1fr;
        & > HorizontalTimelineNavigation {
            height: 1fr;
            & > HorizontalTimeline {
                height: 1fr;
            }
        }
    }
    """
    """Default CSS for `RuledHorizontalTimeline` widget."""

    def __init__(
        self,
        total: int | None = None,
        marker_factory: AbstractRuler.MarkerFactory | None = None,
        header_factory: Callable[[int], Widget] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        can_maximize: bool | None = None,
    ) -> None:
        super().__init__(
            total,
            marker_factory,
            header_factory,
            name,
            id,
            classes,
            disabled=disabled,
            can_maximize=can_maximize,
        )
        self.length = 192

    def compose(self) -> ComposeResult:
        yield HorizontalRuler(marker_factory=self._marker_factory).data_bind(
            RuledHorizontalTimeline.length
        )
        yield from super().compose()
