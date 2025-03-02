from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimePicker
from whenever import Date


class DateTimePickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        yield (dp := DateTimePicker())
        dp.set_reactive(DateTimePicker.expanded, True)


if __name__ == "__main__":
    DateTimePickerApp().run()
