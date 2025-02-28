from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimeDurationPicker
from whenever import LocalDateTime


class DateTimeDurationPickerApp(App[None]):
    
    def compose(self) -> ComposeResult:
        now = LocalDateTime(2025, 2, 10, 12, 13)
        yield (dp := DateTimeDurationPicker(now, now.add(days=1, hours=5, ignore_dst=True)))
        dp.set_reactive(DateTimeDurationPicker.expanded, True)


if __name__ == "__main__":
    DateTimeDurationPickerApp().run()
