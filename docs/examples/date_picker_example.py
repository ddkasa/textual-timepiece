from textual.app import App, ComposeResult
from textual_timepiece.pickers import DatePicker


class DatePickerApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DatePicker()

    def on_date_picker_date_changed(self, message: DatePicker.DateChanged) -> None:
        message.stop()
        if message.date:
            msg = f"Date changed to {message.date.format_common_iso()}."
        else:
            msg = "Date was removed."

        self.notify(msg)


if __name__ == "__main__":
    DatePickerApp().run()
