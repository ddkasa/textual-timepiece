from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateRangePicker
from whenever import Date, weeks


class DateRangeApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DateRangePicker(Date(2025, 2, 5), date_range=weeks(1))


if __name__ == "__main__":
    DateRangeApp().run()
