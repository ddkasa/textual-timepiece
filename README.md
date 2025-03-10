[![PyPI - Version](https://img.shields.io/pypi/v/textual-timepiece)](https://pypi.org/project/textual-timepiece/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/textual-timepiece?link=https%3A%2F%2Fpypi.org%2Fproject%2Ftextual-timepiece%2F)](https://pypi.org/project/textual-timepiece/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ddkasa/textual-timepiece/ci.yaml?link=https%3A%2F%2Fgithub.com%2Fddkasa%2Ftextual-timepiece%2Factions%2Fworkflows%2Fci.yaml)](https://github.com/ddkasa/textual-timepiece/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/github/ddkasa/textual-timepiece/graph/badge.svg?token=47OPXLN8J6)](https://codecov.io/github/ddkasa/textual-timepiece)

# Textual Timepiece

> Various time management related widgets for the [Textual](https://github.com/Textualize/textual) framework.

[Documentation](https://ddkasa.github.io/textual-timepiece/) | [Changelog](/docs/CHANGELOG.md) | [PyPi](https://pypi.org/project/textual-timepiece/)

<details>
<summary>Included Widgets</summary>

| Pickers                                                                                                                                  | Description                                                     |
| :--------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| [DatePicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.DatePicker)                         | A visual date picker with an input and overlay.                 |
| [DurationPicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.DurationPicker)                 | Visual duration picker with duration up to 99 hours.            |
| [TimePicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.TimePicker)                         | Visual time picker for setting a time in a 24 hour clock.       |
| [DateTimePicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.DateTimePicker)                 | Datetime picker that combines a date and time.                  |
| [DateRangePicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.DateRangePicker)               | Date range picker for picking an interval between two dates.    |
| [DateTimeRangePicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.DateTimeRangePicker)       | Range picker for picking an interval between two times.         |
| [DateTimeDurationPicker](https://ddkasa.github.io/textual-timepiece/reference/pickers/#textual_timepiece.pickers.DateTimeDurationPicker) | Pick an interval between two times, including a duration input. |

| Activity Heatmap                                                                                                                             | Description                                                                           |
| :------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| [ActivityHeatmap](https://ddkasa.github.io/textual-timepiece/reference/activity_heatmap/#textual_timepiece.activity_heatmap.ActivityHeatmap) | Activity Heatmap for displaying yearly data similar to the GitHub contribution graph. |
| [HeatmapManager](https://ddkasa.github.io/textual-timepiece/reference/activity_heatmap/#textual_timepiece.activity_heatmap.HeatmapManager)   | Widget for browsing the Activity Heatmap with yearly navigation builtin.              |

| Selector                                                                                                                   | Description                                                           |
| :------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| [DateSelect](https://ddkasa.github.io/textual-timepiece/reference/selectors/#textual_timepiece.pickers.DateSelect)         | Date selection widget with calendar panes.                            |
| [TimeSelect](https://ddkasa.github.io/textual-timepiece/reference/selectors/#textual_timepiece.pickers.TimeSelect)         | Time selection widget with various times in 30 minute intervals.      |
| [DurationSelect](https://ddkasa.github.io/textual-timepiece/reference/selectors/#textual_timepiece.pickers.DurationSelect) | Duration selection widget with modifiers for adjust time or duration. |

| Input                                                                                                                | Description                                                    |
| :------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------- |
| [DateInput](https://ddkasa.github.io/textual-timepiece/reference/input/#textual_timepiece.pickers.DateInput)         | Date input which takes in a iso-format date.                   |
| [TimeInput](https://ddkasa.github.io/textual-timepiece/reference/input/#textual_timepiece.pickers.TimeInput)         | Time input that takes in 24 hour clocked in a HH:MM:SS format. |
| [DurationInput](https://ddkasa.github.io/textual-timepiece/reference/input/#textual_timepiece.pickers.DurationInput) | Duration input with a duration up to 99 hours.                 |
| [DateTimeInput](https://ddkasa.github.io/textual-timepiece/reference/input/#textual_timepiece.pickers.DateTimeInput) | An input with a combination of a date and time in iso-format.  |

</details>

## Demo

### [UVX](https://docs.astral.sh/uv/)

```sh
uvx --from textual-timepiece demo
```

### [PIPX](https://github.com/pypa/pipx)

```sh
pipx run textual-timepiece
```

## Install

### Pip

```sh
pip install textual-timepiece
```

### [UV](https://docs.astral.sh/uv/)

```sh
uv add textual-timepiece
```

### [Poetry](https://python-poetry.org)

```sh
poetry add textual-timepiece
```

> [!NOTE]
> Requires [whenever](https://github.com/ariebovenberg/whenever) as an additional dependency.

## Quick Start

#### DatePicker

##### Code

```py
from textual.app import App, ComposeResult
from textual_timepiece.pickers import DatePicker
from whenever import Date

class DatePickerApp(App[None]):
    def compose(self) -> ComposeResult:
        yield DatePicker(Date(2025, 3, 4))

if __name__ == "__main__":
    DatePickerApp().run()
```

##### Result

![DateTimePicker Example](https://github.com/ddkasa/textual-timepiece/blob/main/docs/media/images/date-picker-example.png)

#### DateTimePicker

##### Code

```py
from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimePicker
from whenever import SystemDateTime

class DateTimePickerApp(App[None]):
    def compose(self) -> ComposeResult:
        yield DateTimePicker(SystemDateTime(2025, 3, 4, 9, 42, 47)))

if __name__ == "__main__":
    DateTimePickerApp().run()
```

##### Result

![DatePicker Example](https://github.com/ddkasa/textual-timepiece/blob/main/docs/media/images/datetime-picker-example.png)

#### ActivityHeatmap

##### Code

```py
import random
from collections import defaultdict

from textual.app import App, ComposeResult
from textual_timepiece.activity_heatmap import ActivityHeatmap, HeatmapManager


class ActivityApp(App[None]):
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
        return defaultdict(
            lambda: 0,
            {
                day: random.randint(6000, 20000)
                for week in template
                for day in week
                if day
            },
        )

    def set_heatmap_data(self, year: int) -> None:
        """Sets the data based on the current data."""
        self.query_one(ActivityHeatmap).values = self.retrieve_data(year)

    def _on_mount(self) -> None:
        self.set_heatmap_data(2025)

    def compose(self) -> ComposeResult:
        yield HeatmapManager(2025)


if __name__ == "__main__":
    ActivityApp().run()
```

##### Result

![ActivityHeatmap Example](https://github.com/ddkasa/textual-timepiece/blob/4a5d9439b2ee436e1b89a1e3189c0d6d5bc6f704/docs/media/images/activity-heatmap-example.png)

- More examples can be found [here](https://ddkasa.github.io/textual-timepiece/examples)

## License

MIT. Check [LICENSE](LICENSE.md) for more information.
