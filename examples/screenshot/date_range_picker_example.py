from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateRangePicker
from whenever import Date


class DateRangePickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        yield (dp := DateRangePicker(Date.today_in_system_tz()))
        dp.set_reactive(DateRangePicker.expanded, True)


if __name__ == "__main__":
    DateRangePickerApp().run()
