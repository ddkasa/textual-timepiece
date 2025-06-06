from __future__ import annotations

import inspect
import sys
from functools import cached_property
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Generic
from typing import Iterator
from typing import TypeVar

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from rich.text import Text
from textual.dom import DOMNode
from textual.message import Message
from textual.reactive import reactive
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Button

from textual_timepiece.constants import LOCKED_ICON
from textual_timepiece.constants import TARGET_ICON
from textual_timepiece.constants import UNLOCKED_ICON

if TYPE_CHECKING:
    from rich.console import RenderableType
    from textual.app import RenderResult
    from textual.geometry import Offset


class BaseWidget(Widget):
    """Base class with a bunch of utility methods."""

    async def recompose(self) -> None:
        self.clear_cached_properties()
        await super().recompose()

    def clear_cached_properties(self) -> None:
        for prop in self.get_cached_properties():
            if hasattr(self, prop):
                delattr(self, prop)

    @classmethod
    def get_cached_properties(cls) -> Iterator[str]:
        for n, v in inspect.getmembers(cls):
            if isinstance(v, cached_property):
                yield n

    def get_line_offset(self, offset: Offset) -> str:
        x = offset.x - int(self.styles.border_left[0] != "")
        index = 0

        for seg in self.render_line(
            offset.y - self._top_border_offset()
        )._segments:
            # REFACTOR: Look for a public method for this.
            index += len(seg.text)
            if index > x:
                return str(seg.text.strip())

        return ""

    def _top_border_offset(self) -> int:
        return int(self.styles.border_top[0] != "")

    def disable(self, *, disable: bool = True) -> Self:
        self.disabled = disable
        return self

    def disable_messages(  # type: ignore[override]  # NOTE: Easier access to disabling in compose.
        self,
        *messages: type[Message],
    ) -> Self:
        super().disable_messages(*messages)
        return self


class LockButton(Button, BaseWidget):
    DEFAULT_CSS: ClassVar[str] = """
    LockButton {
        background: transparent;
        color: auto;
        min-width: 4;
        max-width: 4;
        height: 3;
        content-align-vertical: middle;
        text-style: bold;
        border: none;

        &:focus {
            background-tint: $primary 50%;
        }
    }
    """

    locked = var[bool](False, init=False)
    icon = reactive[Text](Text(LOCKED_ICON), init=False)

    def __init__(
        self,
        *,
        is_locked: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        action: str | None = None,
        use_variant: bool = False,
    ) -> None:
        self._use_variant = use_variant
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
            action=action,
        )
        self.locked = is_locked

    def compute_icon(self) -> Text:
        return Text(
            LOCKED_ICON if self.locked else UNLOCKED_ICON,
            self.rich_style,
        )

    def render(self) -> RenderResult:
        return self.icon

    def press(self) -> Self:
        self.locked = not self.locked
        return super().press()

    def watch_locked(self) -> None:
        if self._use_variant:
            self.variant = "warning" if self.locked else "success"


class ExpandButton(Button):
    """Button with a special icon."""

    DEFAULT_CSS: ClassVar[str] = """
    ExpandButton {
        background: transparent;
        height: 3;
        min-width: 3;
        max-width: 5;
        border: none;
        padding: 0;
    }
    """

    expanded = var[bool](False, init=False)
    icon = reactive[Text](Text, init=False)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        action: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
            action=action,
        )

    def compute_icon(self) -> Text:
        return Text("▲" if self.expanded else "▼", self.rich_style)

    def watch_icon(self, icon: Text) -> None:
        self.label = icon


class TargetButton(Button):
    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
        action: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
            action=action,
        )

    def render(self) -> RenderResult:
        return Text(TARGET_ICON, self.rich_style)


WidgetType = TypeVar("WidgetType", bound=DOMNode)


class BaseMessage(Message, Generic[WidgetType]):
    """Generic message that overrides the control method."""

    def __init__(self, widget: WidgetType) -> None:
        super().__init__()
        self.widget = widget

    @property
    def control(self) -> WidgetType:
        return self.widget
