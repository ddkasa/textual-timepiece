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

/// tab | PIP
```sh
pip install textual-timepiece && demo
```
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

#### DatePicker


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

#### DateTimePicker

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
