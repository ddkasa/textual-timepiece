import pytest
from rich.segment import Segment
from textual.geometry import Offset
from textual.strip import Strip

from textual_timepiece._extra import BaseWidget

DATA = [
    ["what", "is", "this", "today"],
    ["who", "are", "you", "today"],
]


class LineApiWidget(BaseWidget):
    DEFAULT_CSS = """
    LineApiWidget {
        height: 2;
    }
    """

    def render_line(self, y: int):
        return Strip([Segment(t) for t in DATA[y]])


@pytest.mark.unit
def test_get_line_offset(create_app):
    app = create_app(LineApiWidget)

    assert app.widget.get_line_offset(Offset(4, 0)) == "is"

    app.widget.styles.border = ("tall", "green")

    assert app.widget.get_line_offset(Offset(5, 1)) == "is"
    assert app.widget.get_line_offset(Offset(5, 2)) == "are"
