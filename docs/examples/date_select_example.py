from textual.app import App, ComposeResult
from textual import on
from textual.widgets import Label
from textual_timepiece.pickers import DatePicker, DateSelect
from whenever import Date, days


class DateSelectApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DateSelect(Date.today_in_system_tz(), date_range=days(3))
        yield Label(variant="accent")
    
    @on(DateSelect.DateChanged)
    @on(DateSelect.EndDateChanged)
    def on_date_changed(self, message: DateSelect.DateChanged | DateSelect.EndDateChanged) -> None:
        new_content = f"  {message.widget.date} - {message.widget.end_date}  "
        self.query_one(Label).update(new_content)


if __name__ == "__main__":
    DateSelectApp().run()
