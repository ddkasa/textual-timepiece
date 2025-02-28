from textual.app import App, ComposeResult
from textual_timepiece.pickers import DurationPicker
from whenever import TimeDelta


class DurationPickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        yield (dp := DurationPicker(TimeDelta()))
        dp.set_reactive(DurationPicker.expanded, True)


if __name__ == "__main__":
    DurationPickerApp().run()
