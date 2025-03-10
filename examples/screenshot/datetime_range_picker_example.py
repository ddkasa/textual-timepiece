from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimeRangePicker
from whenever import Date, SystemDateTime


class DateTimeRangePickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        now = SystemDateTime.now().local()
        yield (dp := DateTimeRangePicker(now, now.add(hours=14, ignore_dst=True)))
        dp.set_reactive(DateTimeRangePicker.expanded, True)


if __name__ == "__main__":
    DateTimeRangePickerApp().run()
