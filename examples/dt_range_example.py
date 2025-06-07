from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimeRangePicker
from textual import on
from whenever import Date, SystemDateTime


class DTPickerRangeApp(App[None]):

    def on_mount(self) -> None:
        self.query_one(DateTimeRangePicker).disable_end()
        self.set_timer(10, self.stop_timer)
        self.notify("Started timer!")

    def compose(self) -> ComposeResult:
        yield DateTimeRangePicker(SystemDateTime.now().local())
    
    def stop_timer(self) -> None:
        dt_range = self.query_one(DateTimeRangePicker).disable_end(disable=False)
        dt_range.end_dt = SystemDateTime.now().local()


if __name__ == "__main__":
    DTPickerRangeApp().run()
