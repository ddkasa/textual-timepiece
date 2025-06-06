import pytest
from textual.app import App
from textual.css.query import NoMatches

from textual_timepiece.timeline._base_timeline import HorizontalTimeline
from textual_timepiece.timeline._base_timeline import VerticalTimeline


class TimelineApp(App[None]):
    def __init__(self, t_type, **kwargs):
        super().__init__()
        self.t_type = t_type

    async def on_mount(self):
        entry = self.t_type.Entry
        await self.timeline.mount_all(
            [entry(f"id-{i}", str(i), (i * 2), 3) for i in range(1, 5)]
        )

    def compose(self):
        yield self.t_type()

    @property
    def timeline(self):
        return self.query_one(self.t_type)


@pytest.fixture
def vert_tl_app():
    return TimelineApp(VerticalTimeline)


@pytest.fixture
def horz_tl_app():
    return TimelineApp(HorizontalTimeline)


@pytest.mark.snapshot
def test_vert_timeline_snapshot(vert_tl_app, snap_compare):
    assert snap_compare(vert_tl_app)


@pytest.mark.snapshot
def test_vert_timeline_no_tile_snapshot(vert_tl_app, snap_compare):
    async def run_before(pilot):
        pilot.app.timeline.tile = False
        await pilot.pause()

    assert snap_compare(vert_tl_app, run_before=run_before)


@pytest.mark.snapshot
def test_horz_timeline_snapshot(horz_tl_app, snap_compare):
    assert snap_compare(horz_tl_app)


@pytest.mark.snapshot
def test_horz_timeline_no_tile_snapshot(horz_tl_app, snap_compare):
    async def run_before(pilot):
        pilot.app.timeline.tile = False
        await pilot.pause()

    assert snap_compare(horz_tl_app, run_before=run_before)


@pytest.mark.unit
async def test_delete_entry(horz_tl_app):
    async with horz_tl_app.run_test() as pilot:
        horz_tl_app.timeline.action_delete_entry("id-3")
        await pilot.pause()

        with pytest.raises(NoMatches):
            horz_tl_app.timeline.query_one("#id-3")

        horz_tl_app.timeline.query_one("#id-2").focus()
        await pilot.pause()

        horz_tl_app.timeline.action_delete_entry()
        await pilot.pause()

        with pytest.raises(NoMatches):
            horz_tl_app.timeline.query_one("#id-2")

        horz_tl_app.timeline.query_one("#id-1").focus()
        await pilot.press("delete")

        with pytest.raises(NoMatches):
            horz_tl_app.timeline.query_one("#id-1")


@pytest.mark.unit
async def test_timeline_move_entry(horz_tl_app):
    async with horz_tl_app.run_test() as pilot:
        entry = horz_tl_app.timeline.query_one("#id-2").focus()
        current_end = entry.end
        await pilot.pause()

        await pilot.press("ctrl+right")
        assert entry.end == current_end + 1

        await pilot.press("ctrl+left")
        assert entry.end == current_end


@pytest.mark.unit
async def test_timeline_resize_entry(horz_tl_app):
    async with horz_tl_app.run_test() as pilot:
        entry = horz_tl_app.timeline.query_one("#id-2").focus()
        current_start = entry.start
        current_end = entry.end

        await pilot.press("shift+up")
        assert entry.start == current_start - 1

        await pilot.press("alt+shift+down")
        assert entry.start == current_start

        await pilot.press("shift+down")
        assert entry.end == current_end + 1

        await pilot.press("alt+shift+up")
        assert entry.end == current_end
