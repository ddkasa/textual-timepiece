import pytest
from textual.app import App
from textual.widget import Widget


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
