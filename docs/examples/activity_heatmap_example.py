import random

from textual.app import App, ComposeResult
from textual_timepiece.activity_heatmap import ActivityHeatmap, HeatmapManager


class ActivityApp(App):
    def _on_heatmap_manager_year_changed(
        self,
        message: HeatmapManager.YearChanged,
    ) -> None:
        message.stop()
        self.set_heatmap_data(message.year)

    def retrieve_data(self, year: int) -> ActivityHeatmap.ActivityData:
        """Placeholder example on how the data could be generated."""
        random.seed(year)
        template = ActivityHeatmap.generate_empty_activity(year)
        return [
            [random.randint(5, 10) if day else None for day in week]
            for week in template
        ]

    def set_heatmap_data(self, year: int) -> None:
        """Sets the data based on the current data."""
        self.query_one(ActivityHeatmap).process_data(self.retrieve_data(year))

    def _on_mount(self) -> None:
        self.set_heatmap_data(2025)

    def compose(self) -> ComposeResult:
        yield HeatmapManager(2025)


if __name__ == "__main__":
    ActivityApp().run()
