import pytest
from textual.app import App
from textual.widget import Widget
from whenever import Date
from whenever import Instant
from whenever import patch_current_time


class TestApp(App):
    def __init__(self, widget):
        super().__init__()
        if isinstance(widget, Widget):
            self.widget = widget
        else:
            self.widget = widget()

    def compose(self):
        yield self.widget


@pytest.fixture
def create_app():
    def generate_app(widget):
        return TestApp(widget)

    return generate_app


@pytest.fixture
def freeze_time():
    time = Instant.from_utc(2025, 2, 6)

    with patch_current_time(time, keep_ticking=False):
        yield Date(2025, 2, 6)
