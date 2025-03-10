from textual.app import App, ComposeResult
from textual import on
from textual_timepiece.pickers import DurationSelect


class DurationSelectApp(App[None]):

    def compose(self) -> ComposeResult:
        yield DurationSelect()
    

if __name__ == "__main__":
    DurationSelectApp().run()
