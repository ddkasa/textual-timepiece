from __future__ import annotations

import inspect
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar
from typing import Literal

from rich.console import RenderableType
from rich.pretty import Pretty
from rich.syntax import Syntax
from textual import on
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Horizontal
from textual.containers import ScrollableContainer
from textual.message import Message
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Label
from textual.widgets import Static
from textual.widgets import TabbedContent
from textual.widgets import TabPane

from textual_timepiece.__about__ import __version__
from textual_timepiece._activity_heatmap import ActivityHeatmap
from textual_timepiece._activity_heatmap import HeatmapManager
from textual_timepiece.pickers import DatePicker
from textual_timepiece.pickers import DateRangePicker
from textual_timepiece.pickers import DateTimeDurationPicker
from textual_timepiece.pickers import DateTimePicker
from textual_timepiece.pickers import DateTimeRangePicker
from textual_timepiece.pickers import DurationPicker
from textual_timepiece.pickers import TimePicker


class DemoWidget(Widget):
    @dataclass
    class ToggleFeature(Message):
        widget: type[Widget]
        preview: Literal[
            "docstring", "tcss", "code", "docs", "source", "bindings"
        ]

    def __init__(
        self,
        widget_call: type[Widget],
        *,
        notes: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._notes = notes
        self._widget_type = widget_call

    def _compose_navigation_bar(self) -> ComposeResult:
        with Horizontal(id="navigation"):
            yield Button("Docstring", id="docstring", classes="nav")
            yield Label(self._widget_type.__name__, classes="title")
            if (
                hasattr(self._widget_type, "DEFAULT_CSS")
                and self._widget_type.DEFAULT_CSS
            ):
                yield Button("Default CSS", id="default-css", classes="nav")
            if (
                hasattr(self._widget_type, "BINDINGS")
                and self._widget_type.BINDINGS
            ):
                yield Button("Bindings", id="bindings", classes="nav")

            yield Button("Code Preview", id="code", classes="nav")
            yield Button(
                "Documentation",
                id="external-documentation",
                disabled=True,
                classes="nav",
            )
            yield Button(
                "GitHub Source",
                id="github",
                disabled=True,
                classes="nav",
            )

    def compose(self) -> ComposeResult:
        yield from self._compose_navigation_bar()
        yield self._widget_type()

    @on(Button.Pressed, "#docstring")
    def open_docstring(self, message: Button.Pressed) -> None:
        self.post_message(self.ToggleFeature(self._widget_type, "docstring"))

    @on(Button.Pressed, "#default-css")
    def open_default_css(self, message: Button.Pressed) -> None:
        self.post_message(self.ToggleFeature(self._widget_type, "tcss"))

    @on(Button.Pressed, "#code")
    def open_source(self, message: Button.Pressed) -> None:
        self.post_message(self.ToggleFeature(self._widget_type, "code"))

    @on(Button.Pressed, "#bindings")
    def open_bindings(self, message: Button.Pressed) -> None:
        self.post_message(self.ToggleFeature(self._widget_type, "bindings"))


class PreviewScreen(ModalScreen[None]):
    BINDINGS: ClassVar = [
        ("escape", "hide_preview", "Close Preview"),
    ]

    def __init__(
        self,
        renderable: RenderableType,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self._renderable = renderable

    def on_mount(self) -> None:
        self.refresh_bindings()

    def compose(self) -> ComposeResult:
        with Container():
            with ScrollableContainer():
                yield Static(self._renderable, id="preview")

            with Horizontal():
                yield Button(
                    r"Quit\[esc]",
                    "warning",
                    action="screen.hide_preview",
                    classes="nav",
                )

    def action_hide_preview(self) -> None:
        self.dismiss()


class TimepieceDemo(App[None]):
    font: bool = True

    CSS_PATH = "main.tcss"

    TITLE = "Textual Timepiece"
    SUB_TITLE = __version__

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with TabbedContent(initial="pickers"):
            with TabPane("Pickers", id="pickers"):
                with Container(id="Pickers", classes="previews"):
                    for item in (
                        DatePicker,
                        DurationPicker,
                        TimePicker,
                        DateTimePicker,
                        DateRangePicker,
                        DateTimeRangePicker,
                        DateTimeDurationPicker,
                    ):
                        yield DemoWidget(item)
            with TabPane("Heatmap"):
                with Container(id="heatmap", classes="previews"):
                    for i in (ActivityHeatmap, HeatmapManager):
                        yield DemoWidget(i)

        yield Footer()

    def on_mount(self) -> None:
        fake_data = ActivityHeatmap.generate_empty_activity(2025)

        for m in self.query(ActivityHeatmap):
            m.process_data(fake_data)

    @on(DemoWidget.ToggleFeature)
    def open_tab(self, message: DemoWidget.ToggleFeature) -> None:
        data: RenderableType
        if message.preview == "tcss":
            data = message.widget.DEFAULT_CSS

        elif message.preview == "bindings":
            data = Pretty(message.widget.BINDINGS)

        elif message.preview == "docstring":
            data = str(message.widget.__doc__)

        elif message.preview == "code":
            data = Syntax(
                inspect.getsource(message.widget),
                "python",
                line_numbers=True,
                padding=1,
            )

        self.app.push_screen(PreviewScreen(data))

    @on(HeatmapManager.YearChanged)
    def change_heat_year(self, message: HeatmapManager.YearChanged) -> None:
        fake_data = ActivityHeatmap.generate_empty_activity(message.year)
        message.widget.heatmap.process_data(fake_data)

    @cached_property
    def preview_panel(self) -> Static:
        return self.query_one("#preview", Static)


def main() -> None:
    TimepieceDemo().run()


if __name__ == "__main__":
    main()
