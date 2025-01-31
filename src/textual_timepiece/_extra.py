from __future__ import annotations

import inspect
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar
from typing import Iterator
from typing import Self

from rich.console import RenderableType
from rich.console import Text
from textual.app import RenderResult
from textual.dom import DOMNode
from textual.geometry import Offset
from textual.message import Message
from textual.reactive import reactive
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Button


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
        index = 0

        for seg in self.render_line(
            offset.y - self._top_border_offset()
        )._segments:
            index += len(seg.text)
            if index > offset.x:
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
    }
    """

    locked: var[bool] = var(True, init=False)
    icon: reactive[Text] = reactive(Text("🔒"), init=False)

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
        return Text("🔒" if self.locked else "🔓", self.rich_style)

    def render(self) -> RenderResult:
        return self.icon

    def on_mouse_down(self) -> None:
        self.locked = not self.locked

    def watch_locked(self) -> None:
        if self._use_variant:
            self.variant = "warning" if self.locked else "success"


class ExpandButton(Button):
    """Toggl button which essentially acts like a checkbox/switch."""

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

    expanded: var[bool] = var(False, init=False)
    icon: reactive[Text] = reactive(Text(), init=False)

    def compute_icon(self) -> Text:
        return Text("▲" if self.expanded else "▼", self.rich_style)

    def watch_icon(self, icon: Text) -> None:
        self.label = icon


@dataclass
class BaseMessage(Message):
    """Generic message that overrides the control method."""

    widget: DOMNode

    @property
    def control(self) -> DOMNode:
        return self.widget
