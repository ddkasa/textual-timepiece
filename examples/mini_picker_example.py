from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimeDurationPicker
from whenever import Date, SystemDateTime, weeks


class MiniPickerApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DateTimeDurationPicker(SystemDateTime.now().local(), classes="mini")


if __name__ == "__main__":
    MiniPickerApp().run()
