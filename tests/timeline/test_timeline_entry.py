import pytest
from textual.app import App

from textual_timepiece.timeline._timeline_entry import VerticalEntry


class TimelineApp(App[None]):
    def compose(self):
        yield VerticalEntry("first-entry", "Test Content", 5, 10)

    @property
    def entry(self) -> VerticalEntry:
        return self.query_one(VerticalEntry)


@pytest.fixture
def entry_app():
    return TimelineApp()


@pytest.mark.unit
async def test_entry_move(entry_app: TimelineApp):
    async with entry_app.run_test() as pilot:
        await pilot.pause()
        entry = entry_app.entry
        assert entry.offset.y == 5
        entry.move(5)
        assert entry.offset.y == 10


@pytest.mark.unit
async def test_entry_resize(entry_app: TimelineApp):
    async with entry_app.run_test() as pilot:
        await pilot.pause()
        entry = entry_app.entry
        assert entry.styles.height.value == 10
        entry.resize(2, tail=False)
        assert entry.styles.height.value == 12
        entry.resize(-2, tail=True)
        assert entry.styles.height.value == 14
        entry.resize(2, tail=True)
        assert entry.styles.height.value == 12


@pytest.mark.unit
async def test_entry_merge(entry_app: TimelineApp):
    async with entry_app.run_test() as pilot:
        entry = entry_app.entry

        new_entry = VerticalEntry("second-entry", "Test Content", 4, 16)
        await entry_app.mount(new_entry)
        await entry.merge(new_entry)
        await pilot.pause()

        assert entry.offset.y == 4
        assert entry.styles.height.value == 16
