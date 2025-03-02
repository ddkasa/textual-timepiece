[![PyPI - Version](https://img.shields.io/pypi/v/textual-timepiece)](https://pypi.org/project/textual-timepiece/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/textual-timepiece?link=https%3A%2F%2Fpypi.org%2Fproject%2Ftextual-timepiece%2F)](https://pypi.org/project/textual-timepiece/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ddkasa/textual-timepiece/ci.yaml?link=https%3A%2F%2Fgithub.com%2Fddkasa%2Ftextual-timepiece%2Factions%2Fworkflows%2Fci.yaml)](https://github.com/ddkasa/textual-timepiece/actions/workflows/ci.yaml)

# Textual Timepiece

> Various time management related widgets for the [Textual](https://github.com/Textualize/textual) framework.

[Documentation](https://ddkasa.github.io/textual-timepiece/) | [Changelog](/docs/CHANGELOG.md) | [PyPi](https://pypi.org/project/textual-timepiece/)

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

#### DateTimePicker

```py
from textual.app import App, ComposeResult
from textual_timepiece.pickers import DateTimePicker
from whenever import SystemDateTime

class DateTimePickerApp(App[None]):
    def compose(self) -> ComposeResult:
        yield DateTimePicker(SystemDateTime.now().local())

if __name__ == "__main__":
    DateTimePickerApp().run()
```

- More examples can be found [here](https://ddkasa.github.io/textual-timepiece/examples).

## Included Widgets

- `DatePicker`
- `DurationPicker`
- `TimePicker`
- `DateTimePicker`
- `DateRangePicker`
- `DateTimeRangePicker`
- `ActivityHeatmap`
- `HeatmapManager`
- _And more to come..._

## License

MIT. Check [LICENSE](LICENSE.md) for more information.
