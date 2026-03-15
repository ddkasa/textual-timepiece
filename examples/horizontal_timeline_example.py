from __future__ import annotations

from textual.reactive import var

from textual import on, work
from textual.app import ComposeResult, App
from textual.containers import Center, Horizontal, HorizontalGroup, Middle
from textual.screen import ModalScreen
from textual.validation import Integer
from textual.widgets import Button, Input, Label, Static

from textual_timepiece.timeline import RuledHorizontalTimeline
from textual_timepiece.timeline import HorizontalTimeline


NUMBERS: tuple[str, ...] = [
    "Zero",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
]


def header_factory(index: int) -> Label:
    return Label(
        f"{NUMBERS[index]}",
        variant="primary" if index % 2 == 0 else "secondary",
        classes="header",
    )


class TimelineApp(App[None]):
    """Example of how horizontal timelines could be implemented."""

    DEFAULT_CSS = """\
    Screen {
        Input {
            width: 1fr;
        }
        HorizontalRuler {
            padding-left: 11;  # Compensating for header size.
        }
        Label.header {
            color: auto;
            border: hkey $secondary;
            min-width: 11;
            max-width: 11;
            height: 100%;
            text-align: center;
            content-align: center middle;
            text-style: bold;
            padding: 0 2 0 2;
        }
    }
    """

    layers = var[int](2, init=False)
    """Total amount of timelines to display."""

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="layer-controls"):
            yield Button.warning("-", id="subtract")
            yield Input(
                "2",
                "Total Timelines",
                type="integer",
                valid_empty=False,
                validate_on=["changed"],
                validators=Integer(1, 10),
                tooltip=(
                    "Total Timelines Present\n"
                    "[b]Maximum[/]: 10\n"
                    "[b]Minimum[/]: 1"
                ),
            )
            yield Button.success("+", id="add")
        yield (timeline := RuledHorizontalTimeline(
            3,
            header_factory=header_factory,
        ).data_bind(total=TimelineApp.layers))
        timeline.length = 392

    def _on_input_changed(self, message: Input.Changed) -> None:
        if message.input.is_valid:
            self.layers = int(message.value)

    def _on_button_pressed(self, message: Button.Pressed) -> None:
        self.layers -= 1 if message.button.id == "subtract" else -1

    def watch_layers(self, total: int) -> None:
        self.query_one("#subtract").disabled = total == 1
        self.query_one("#add").disabled = total == 10
        with (input_widget := self.query_one(Input)).prevent(Input.Changed):
            input_widget.value = str(total)


if __name__ == "__main__":
    TimelineApp().run()
