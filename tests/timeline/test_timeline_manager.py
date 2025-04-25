import pytest
from textual.app import App

from textual_timepiece.timeline._timeline_manager import (
    RuledHorizontalTimeline,
)
from textual_timepiece.timeline._timeline_manager import RuledVerticalTimeline


class TimelineManagerApp(App[None]):
    def __init__(self, t_type, **kwargs):
        super().__init__()
        self.t_type = t_type

    async def on_mount(self):
        entry = self.t_type.Timeline.Timeline.Entry
        total = 0
        for tl in self.manager.query("AbstractTimeline"):
            await tl.mount_all(
                [
                    entry(f"id-{i}", str(i), (i * 2) + total, 3)
                    for i in range(1, 4)
                ]
            )
            total += 5

    def compose(self):
        yield self.t_type()

    @property
    def manager(self):
        return self.query_one(self.t_type)


@pytest.fixture
def vert_tl_manager_app():
    return TimelineManagerApp(RuledVerticalTimeline)


@pytest.fixture
def horz_tl_manager_app():
    return TimelineManagerApp(RuledHorizontalTimeline)


@pytest.mark.snapshot
def test_vertical_manager_snapshot(vert_tl_manager_app, snap_compare):
    assert snap_compare(vert_tl_manager_app)


@pytest.mark.snapshot
def test_horizontal_manager_snapshot(horz_tl_manager_app, snap_compare):
    assert snap_compare(horz_tl_manager_app)
