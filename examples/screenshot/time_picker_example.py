from textual.app import App, ComposeResult
from textual_timepiece.pickers import TimePicker
from whenever import Date, Time


class TimePickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        yield (dp := TimePicker(Time(12, 0, 0)))
        dp.set_reactive(TimePicker.expanded, True)


if __name__ == "__main__":
    TimePickerApp().run()
