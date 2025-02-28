from textual.app import App, ComposeResult
from textual_timepiece.pickers import TimeSelect


class TimeSelectApp(App[None]):

    def compose(self) -> ComposeResult:
        yield TimeSelect()
    

if __name__ == "__main__":
    TimeSelectApp().run()
