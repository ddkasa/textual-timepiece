from textual.app import App, ComposeResult
from textual_timepiece.pickers import DatePicker
from whenever import Date


class DatePickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        yield (dp := DatePicker(Date.today_in_system_tz()))
        dp.set_reactive(DatePicker.expanded, True)


if __name__ == "__main__":
    DatePickerApp().run()
