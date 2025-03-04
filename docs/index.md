# Textual Timepiece

[![PyPI - Version](https://img.shields.io/pypi/v/textual-timepiece)](https://pypi.org/project/textual-timepiece/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/textual-timepiece?link=https%3A%2F%2Fpypi.org%2Fproject%2Ftextual-timepiece%2F)](https://pypi.org/project/textual-timepiece/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ddkasa/textual-timepiece/ci.yaml?link=https%3A%2F%2Fgithub.com%2Fddkasa%2Ftextual-timepiece%2Factions%2Fworkflows%2Fci.yaml)](https://github.com/ddkasa/textual-timepiece/actions/workflows/ci.yaml)

> Welcome to the Textual Timepiece Documentation.

---

Textual Timepiece is a collection of widgets related to time management and manipulation. It includes various time and date [pickers](reference/pickers.md), an [activity heatmap](reference/activity_heatmap.md) for displaying year dates and some extras.


## Demo


/// tab | UV
    new: true

!!! note
    Requires [uv](https://docs.astral.sh/uv/) to be installed and configured.

```sh
uvx --from textual-timepiece demo
```
///


/// tab | PIPX

```sh
pipx run textual-timepiece
```
///

/// tab | PIP
```sh
pip install textual-timepiece && demo
```
///


## Included Widgets
/// tab | Pickers
    new: true 
| Widget | Description |
|:-------|:-------|
|[DatePicker][textual_timepiece.pickers.DatePicker]|A visual date picker with an input and overlay.|
|[DurationPicker][textual_timepiece.pickers.DurationPicker]|Visual duration picker with duration up to 99 hours.|
|[TimePicker][textual_timepiece.pickers.TimePicker]|Visual time picker for setting a time in a 24 hour clock.|
|[DateTimePicker][textual_timepiece.pickers.DateTimePicker]|Datetime picker that combines a date and time.|
|[DateRangePicker][textual_timepiece.pickers.DateRangePicker]|Date range picker for picking an interval between two dates.|
|[DateTimeRangePicker][textual_timepiece.pickers.DateTimeRangePicker]|Range picker for picking an interval between two times. |
|[DateTimeDurationPicker][textual_timepiece.pickers.DateTimeDurationPicker]|Pick an interval between two times, including a duration input.|
///

/// tab | Activity Heatmap
| Widget | Description |
|:-------|:-------|
|[ActivityHeatmap][textual_timepiece.activity_heatmap.ActivityHeatmap]|Activity Heatmap for displaying yearly activity similar to the GitHub contribution graph. |
|[HeatmapManager][textual_timepiece.activity_heatmap.HeatmapManager]|Widget for browsing the Activity Heatmap with yearly navigation builtin.|
///

/// tab | Selector
| Widget | Description |
|:-------|:-------|
|[DateSelect][textual_timepiece.pickers.DateSelect]|Date selection widget with calendar panes.|
|[TimeSelect][textual_timepiece.pickers.TimeSelect]|Time selection widget with various times in 30 minute intervals.|
|[DurationSelect][textual_timepiece.pickers.DurationSelect]|Duration selection widget with modifiers for adjust time or duration.|
///

/// tab | Input
| Widget | Description |
|:-------|:-------|
|[DateInput][textual_timepiece.pickers.DateInput]|Date input which takes in a iso-format date.|
|[TimeInput][textual_timepiece.pickers.TimeInput]|Time input that takes in 24 hour clocked in a HH:MM:SS format.|
|[DurationInput][textual_timepiece.pickers.DurationInput]|Duration input with a duration up to 99 hours.|
|[DateTimeInput][textual_timepiece.pickers.DateTimeInput]|An input with a combination of a date and time in iso-format.|
///




## Installation

/// tab | PIP
    new: true
```sh
pip install textual-timepiece
```
///

/// tab | UV
```sh
uv add textual-timepiece
```
///

/// tab | Poetry
```sh
poetry add textual-timepiece
```
///

!!! info
    Requires [whenever](https://github.com/ariebovenberg/whenever) as an additional dependency.

## Quick Start

### DatePicker


/// tab | Result
    new: true

```{.textual path="docs/examples/screenshot/date_picker_example.py"}
```
///
/// tab | Source

```py
from textual.app import App, ComposeResult
from textual_timepiece.pickers import DatePicker
from whenever import Date

class DatePickerApp(App[None]):
    def compose(self) -> ComposeResult:
        yield DatePicker(Date.today_in_system_tz())

if __name__ == "__main__":
    DatePickerApp().run()
```
///

### DateTimePicker

/// tab | Result
    new: true
```{.textual path="docs/examples/screenshot/datetime_picker_example.py"}
```
/// 
/// tab | Source

```py
from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimePicker
from whenever import SystemDateTime

class DateTimePickerApp(App[None]):
    def compose(self) -> ComposeResult:
        yield DateTimePicker()

if __name__ == "__main__":
    DateTimePickerApp().run()
```
///
