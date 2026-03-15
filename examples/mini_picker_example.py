from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimeDurationPicker
from whenever import ZonedDateTime


class MiniPickerApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DateTimeDurationPicker(ZonedDateTime.now_in_system_tz().to_plain(), classes="mini")


if __name__ == "__main__":
    MiniPickerApp().run()
