from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimeRangePicker
from whenever import ZonedDateTime


class DateTimeRangePickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        now = ZonedDateTime.now_in_system_tz().to_plain()
        yield (dp := DateTimeRangePicker(now, now.add(hours=14, ignore_dst=True)))
        dp.set_reactive(DateTimeRangePicker.expanded, True)


if __name__ == "__main__":
    DateTimeRangePickerApp().run()
