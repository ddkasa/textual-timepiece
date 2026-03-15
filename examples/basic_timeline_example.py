from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult, App
from textual.containers import Center, Middle
from textual.screen import ModalScreen
from textual.widgets import Input

from textual_timepiece.timeline import RuledVerticalTimeline
from textual_timepiece.timeline import VerticalTimeline


class NamingModal(ModalScreen[str]):
    """Modal screen for naming entries."""

    DEFAULT_CSS = """\
    NamingModal {
        align: center middle;
        Center{
            border: tall $primary;
            border-top: panel $primary;
            border-title-align: center;
            border-title-style: bold;
            min-width: 34;
            width: 50%;
            min-height: 5;
            height: 20%;
        }
        Input {
            min-width: 30;
        }
    }
    """
    BINDINGS = [("escape", "dismiss")]

    def compose(self) -> ComposeResult:
        with Center() as center, Middle():
            center.border_title = "What would you like to name the entry?"
            yield Input(
                placeholder="Name",
                valid_empty=False,
                validate_on=["submitted"],
            )

    def on_input_submitted(self, message: Input.Submitted) -> None:
        message.stop()
        if message.input.is_valid:
            self.dismiss(message.value)


class TimelineApp(App[None]):
    """Example of how timelines could be implemented."""

    def compose(self) -> ComposeResult:
        yield RuledVerticalTimeline(3)

    @work(name="naming-worker")
    async def on_vertical_timeline_created(
        self,
        message: VerticalTimeline.Created,
    ) -> None:
        result = await self.push_screen_wait(NamingModal())
        message.entry.remove_class("-mime").update(result or "To Be Named")

    def on_vertical_timeline_deleted(
        self,
        message: VerticalTimeline.Deleted,
    ) -> None:
        self.notify(f"Successfully deleted {message.entry.visual!s}!")


if __name__ == "__main__":
    TimelineApp().run()
