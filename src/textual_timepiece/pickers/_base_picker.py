from __future__ import annotations

from abc import abstractmethod
from functools import cached_property
from typing import Callable
from typing import ClassVar
from typing import Generic
from typing import Literal
from typing import TypeAlias
from typing import TypeVar
from typing import cast

from textual import on
from textual.binding import Binding
from textual.events import DescendantBlur
from textual.events import MouseDown
from textual.events import MouseMove
from textual.events import MouseScrollDown
from textual.events import MouseScrollUp
from textual.events import MouseUp
from textual.events import Resize
from textual.geometry import Offset
from textual.geometry import Size
from textual.message import Message
from textual.reactive import var
from textual.widget import Widget
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import MaskedInput

from textual_timepiece._extra import BaseWidget

Directions: TypeAlias = Literal["up", "right", "down", "left"]


class AbstractSelect(BaseWidget):
    """Base Class that defines the interal widgets of the dialog."""

    can_focus = True

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)


class AbstractDialog(BaseWidget):
    """Base class for the widget that drops down for an easier selection."""

    class Close(Message):
        pass

    DEFAULT_CSS = """
    AbstractDialog {
        overlay: screen !important;
        constrain: inside !important;
        position: absolute !important;
        height: auto;
        width: auto;
        background: $surface;
        box-sizing: content-box;
        opacity: 0;

        border: round $secondary;

        &:focus,
        &:focus-within {
            border: round $primary;
        }

        AbstractSelect {
            width: 40;
            height: auto;
        }
    }
    """

    can_focus = True

    BINDINGS: ClassVar = [
        Binding("escape", "close_dialog", "Close dialog."),
    ]

    show: var[bool] = var(False, init=False)

    def __init__(
        self,
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
        )

        self.display = False

    def action_close_dialog(self) -> None:
        self.post_message(self.Close())

    def watch_show(self, show: bool) -> None:
        def anim(on_complete: Callable | None) -> None:
            self.styles.animate(
                "opacity",
                1 if show else 0,
                duration=0.4,
                easing="in_out_expo",
                on_complete=on_complete,
            )

        if show:
            self.display = show
            anim(None)
        else:
            anim(lambda: setattr(self, "display", show))

        self.set_class(show, "-expanded")

    def on_resize(self, event: Resize) -> None:
        # TODO: Need a better way to calculate this.
        # NOTE: Might have to set a constant height in a class var
        parent = cast(Widget, self.parent)
        offset = 1 if parent.has_class("mini") else 3
        bottom = self.app.size.height // 2 > cast(Widget, parent).region.y
        self.offset = Offset(0, offset if bottom else -(self.size.height + 2))

    def on_focus(self) -> None:
        self.app.action_focus_next()

    def check_action(
        self, action: str, parameters: tuple[object, ...]
    ) -> bool | None:
        if action == "focus_next_select":
            return len(self.children) > 1

        return bool(super().check_action(action, parameters))


T = TypeVar("T")


class BaseInput(MaskedInput, BaseWidget, Generic[T]):
    """Abstract class that defines behaviour for all datetime input widgets.

    Default Input messages are disabled and are meant to be replaced by a
    custom message that returns a date/time object.

    Params:
        value: Generic value that will be placed into initialize the widget.
        name: Name of the widget.
        id: Unique DOM indentifier for the widget.
        classes: CSS classes to add.
        tooltip: Tooltip for the widget. None if not showing anything.
        disabled: Whether to disable the widget at the start.
        select_on_focus: Focus the first position on wiget focus.
        valid_empty: If the widget is valid when empty or not.
        spinbox_sensitivity: How sensitive the spinbox features are.
    """

    can_focus = True

    DEFAULT_CSS = """
    BaseInput {
        background: transparent;
        width: auto;
        border: none;
    }
    """

    BINDING_GROUP_TITLE = "Datetime Picker"
    BINDINGS: ClassVar = [
        Binding("escape", "leave", tooltip="Defocus the input."),
        Binding(
            "up",
            "adjust_time(1)",
            "Increment",
            tooltip="Increment value depending on keyboard cursor location.",
            priority=True,
        ),
        Binding(
            "down",
            "adjust_time(-1)",
            "Decrement",
            tooltip="Decrement value depending on keyboard cursor location.",
            priority=True,
        ),
    ]

    ALIAS: ClassVar[str]
    PATTERN: ClassVar[str]

    def __init__(
        self,
        value: T | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        tooltip: str | None = None,
        *,
        disabled: bool = False,
        select_on_focus: bool = True,
        valid_empty: bool = True,
        spinbox_sensitivity: int = 1,
    ) -> None:
        super().__init__(
            template=self.PATTERN,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            select_on_focus=select_on_focus,
            tooltip=tooltip,
            valid_empty=valid_empty,
        )
        self.alias = value
        self._sbox_sensitivity = max(1, spinbox_sensitivity)
        self.disable_messages(Input.Changed, Input.Submitted)

    def watch_updated(self, value: bool) -> None:
        self.set_class(value, "updated")

    @abstractmethod
    def convert(self) -> T | None: ...

    def _action_leave(self) -> None:
        self.blur()

    async def _on_mouse_down(self, event: MouseDown) -> None:
        if not self.app.mouse_captured:
            self.capture_mouse()

    async def _on_mouse_move(self, event: MouseMove) -> None:
        if self.app.mouse_captured == self:
            self.action_adjust_time(-event.delta_y * self._sbox_sensitivity)

    async def _on_mouse_up(self, event: MouseUp) -> None:
        if self.app.mouse_captured == self:
            self.capture_mouse(False)

    def _on_mouse_scroll_up(self, event: MouseScrollUp) -> None:
        if self.has_focus:
            self.action_adjust_time(1 * self._sbox_sensitivity)
            event.stop()

    def _on_mouse_scroll_down(self, event: MouseScrollDown) -> None:
        if self.has_focus:
            self.action_adjust_time(-1 * self._sbox_sensitivity)
            event.stop()

    @abstractmethod
    def action_adjust_time(self, value: int) -> None: ...

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return len(self.PATTERN) + 1

    @property
    def alias(self) -> T | None:
        """Alias for whatever value the input may be holding."""
        return getattr(self, self.ALIAS)

    @alias.setter
    def alias(self, value: T | None) -> None:
        """Alias for whatever value the input may be holding."""
        self.set_reactive(getattr(self.__class__, self.ALIAS), value)


class AbstractPicker(BaseWidget, Generic[T]):
    """Abstract Picker class that defines most of the base behaviour."""

    DEFAULT_CSS = """
    AbstractPicker {
        layers: base dialog;
        layout: vertical;
        height: 3;
        width: auto;

        &.mini {
            max-height: 1;
            & > #input-control {
                border: none;
                height: 1;
                padding: 0;

                &:blur {
                    padding: 0;
                }
                &:focus-within {
                    padding: 0;
                    border: none;
                }
                Button, BaseInput {
                    border: none;
                    padding: 0;
                    height: 1;

                    &:focus {
                        color: $accent;
                        text-style: none;
                    }
                    &:disabled {
                        opacity: 50%;
                        text-style: italic;
                    }
                }
            }
        }

        & > #input-control {
            background: $surface;
            width: auto;

            &:blur {
                padding: 1;
            }
            &:focus-within {
                border: tall $primary;
                padding: 0;
            }

            Button, BaseInput {
                border: none;
                padding: 0;
                height: 1;

                &:focus {
                    color: $accent;
                    text-style: none;
                }
            }
            & > TargetButton {
                min-width: 1;
                max-width: 3;
            }

            & > BaseInput {
                padding: 0 2;
                &.-invalid {
                    color: $error;
                    text-style: italic;
                }
                &:focus {
                    tint: $primary 2%;
                }
            }
        }
        & > AbstractDialog {
            overlay: screen !important;
            constrain: inside;
            position: absolute;
            height: auto;
            width: auto;
            background: $surface;
            box-sizing: content-box;
            opacity: 0;

            border: round $secondary;

            &:focus,
            &:focus-within {
                border: round $primary;
            }

            AbstractSelect {
                width: 40;
                height: auto;
            }
        }
    }
    """

    BINDINGS: ClassVar = [
        Binding("shift+enter", "expand", "Open Dialog."),
    ]

    expanded: var[bool] = var(False, init=False)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.tooltip = tooltip

    def _on_abstract_dialog_close(self, message: AbstractDialog.Close) -> None:
        self.expanded = False
        message.stop()

    @on(Button.Pressed, "#toggle-button")
    def action_expand(self) -> None:
        self.expanded = not self.expanded

    @on(DescendantBlur)
    def close_dialog(self) -> None:
        if not self.has_focus_within:
            self.expanded = False

    def watch_expanded(self, expanded: bool) -> None:
        if expanded:
            self.query_one(AbstractDialog).focus()


TI = TypeVar("TI", bound=BaseInput)


class BasePicker(AbstractPicker, Generic[TI, T]):
    """Base Picker class for combining various single ended widgets."""

    INPUT: type[TI]

    def __init__(
        self,
        value: T | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        *,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            tooltip=tooltip,
        )
        self.value = value
        self.default = value

    @on(Button.Pressed, "#target-default")
    def _action_target_today(
        self, message: Button.Pressed | None = None
    ) -> None:
        if message:
            message.stop()
        self.to_default()

    @abstractmethod
    def to_default(self) -> None:
        """Behaviour when using the target-default button or action."""

    @cached_property
    def input_widget(self) -> TI:
        return self.query_exactly_one(self.INPUT)

    @property
    @abstractmethod
    def value(self) -> T | None:
        """Alias for whatever value the picker may be holding."""

    @value.setter
    @abstractmethod
    def value(self, value: T | None) -> None:
        """Alias for whatever value the picker may be holding."""
