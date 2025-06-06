---
title: Changelog
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-06-06

### Added
- `demo`: Add `Mount` event as argument by @ddkasa
- `timeline`: Add subclassed messages to timelines by @ddkasa
- `AbstractTimeline`: Add entry generic to messages by @ddkasa
- `demo`: Add `Mount` event as argument by @ddkasa
- Add missing future annotations imports by @ddkasa
- `timeline-layout`: Add explicit `strict` parameters to `zip` by @ddkasa
- `AbstractTimeline`: Add `refresh_line` helper method by @ddkasa
- `timeline`: Add timeline widgets to module by @ddkasa
- `utility`: Add `breakdown_seconds` as a public helper function by @ddkasa
- `demo`: Add timelines to demo app by @ddkasa
- `utility`: Add `format_seconds` as a public helper function by @ddkasa
- `message`: Add widget types to messages by @ddkasa
- `DateTimeInput`: Add `value` alias to `DateTimeChanged` message by @ddkasa
- Add additional info to __about__ module by @ddkasa

### Changed
- `timeline`: Update generics for type hints by @ddkasa
- `DateRangePicker`: Items get disabled on default target by @ddkasa
- **Breaking** `ActivityHeatmap`: Rename `DateSelected` to `DaySelected` by @ddkasa
- `DateTimeInput`: Replace `PlainDateTime.strptime` with `parse_strptime` by @ddkasa
- **Breaking** `pickers`: Replace all `LocalDateTime` occurences with `PlainDateTime` by @ddkasa
- `timeline`: Move `refresh_line` method to `VerticaTimeline` by @ddkasa
- `AbstractRuledTimeline`: Make sure to `await` removals and mounts by @ddkasa
- `AbstractTimeline`: Use local instance `Deleted` message by @ddkasa
- `timelines`: Use different marker logic for horizontal and vertical timelines by @ddkasa
- `timeline`: Use generic timeline type for messages by @ddkasa
- `AbstractTimeline`: Simplify message names to single past-participle verbs by @ddkasa
- `demo`: Combine `with` statements in `compose` method by @ddkasa
- `ActivityHeatmap`: Combine `_date_lookup` if statement by @ddkasa
- Move types into `TYPE_CHECKING` by @ddkasa
- `TimeSelect`: Replace `action_focus_neighbor` if blocks with ternary statements by @ddkasa
- Quote all `cast` types by @ddkasa
- `pickers`: Rename `T` generic to `ValueType` by @ddkasa
- `pickers`: Rename `TI` generic to `InputType` by @ddkasa
- `demo`: Rename `__main__` to `_demo` by @ddkasa
- `EndDateSelect`: Reword docstring summary to single line by @ddkasa
- `timeline`: Use generics for all timelines by @ddkasa
- `AbstractTimeline`: Rename messages and remove `dataclass` decorator by @ddkasa
- `TimelineEntry`: Rename messages and remove `dataclass` decorator by @ddkasa
- `VerticalTimeline`: Update `render_lines` to cache basic strip by @ddkasa
- `AbstractRuler`: Prevent compute methods from firing on generated reactives by @ddkasa
- `AbstractEntry`: Convert `clicked` to reactive by @ddkasa
- `AbstractTimeline`: Make sure to update layout on `length` update by @ddkasa
- `AbstractTimeline`: Update only marker lines that have changed by @ddkasa
- `AbstractEntry`: Use keywords for mime creation by @ddkasa
- `timeline`: Implement timeline manager classes by @ddkasa
- `timeline`: Implement base timeline classes by @ddkasa
- `timeline`: Implement timeline layouts by @ddkasa
- `timeline`: Implement timeline entry classes by @ddkasa
- `ActivityHeatmap`: Implement `Selected` base message by @ddkasa
- `BaseMessage`: Implement generic type for node by @ddkasa
- `DateTimeRangePicker`: Convert `Changed` to normal class by @ddkasa
- **Breaking** `DateTimeRangePicker`: Rename `DTRangeChanged` message to `Changed` by @ddkasa
- `DateRangePicker`: Convert `Changed` to normal class by @ddkasa
- **Breaking** `DateRangePicker`: Rename `DateRangeChanged` message to `Changed` by @ddkasa
- `TimePicker`: Implement `Changed.value` property by @ddkasa
- `TimePicker`: Convert `Changed` to normal class by @ddkasa
- **Breaking** `TimePicker`: Rename `TimeChanged` message to `Changed` by @ddkasa
- `TimeInput`: Implement `Updated.value` property by @ddkasa
- `TimeInput`: Convert `Updated` to normal class by @ddkasa
- **Breaking** `TimeInput`: Rename `TimeChanged` message to `Updated` by @ddkasa
- `DurationPicker`: Implement `Changed.value` property by @ddkasa
- `DurationPicker`: Convert `Changed` to normal class by @ddkasa
- **Breaking** `DurationPicker`: Rename `DurationChanged` message to `Changed` by @ddkasa
- `DurationInput`: Implement `Updated.value` property by @ddkasa
- `DurationInput`: Convert `Updated` to normal class by @ddkasa
- **Breaking** `DurationInput`: Rename `DurationChanged` message to `Updated` by @ddkasa
- `TimeSelect`: Implement `Selected.value` property by @ddkasa
- **Breaking** `TimeSelect`: Rename `TimeSelected` message to `Selected` by @ddkasa
- `TimeSelect`: Convert `TimeSelected` to normal class by @ddkasa
- **Breaking** `DurationSelect`: Rename `DurationRounded` message to `Rounded` by @ddkasa
- **Breaking** `DurationSelect`: Rename `DurationAdjusted` message to `Adjusted` by @ddkasa
- `DurationSelect`: Convert `DurationRounded` to normal class by @ddkasa
- `DurationSelect`: Convert `DurationAdjusted` to normal class by @ddkasa
- `DateSelect`: Implement `Changed.value` alias by @ddkasa
- **Breaking** `DateSelect`: Rename `EndDateChanged` to `EndChanged` by @ddkasa
- **Breaking** `DateSelect`: Rename `DateChanged` to `StartChanged` by @ddkasa
- `DateSelect`: Implement `Changed` base message by @ddkasa
- `DatePicker`: Implement `Changed.value` property by @ddkasa
- `DatePicker`: Convert `Changed` to normal class by @ddkasa
- **Breaking** `DatePicker`: Rename `DateChanged` message to `Changed` by @ddkasa
- `DateInput`: Implement `Updated.value` property by @ddkasa
- `DateInput`: Convert `Updated` to normal class by @ddkasa
- **Breaking** `DateInput`: Rename `DateChanged` message to `Updated` by @ddkasa
- `DateTimePicker`: Convert `Changed` to normal class by @ddkasa
- **Breaking** `DateTimePicker`: Rename `DateTimeChanged` message to `Changed` by @ddkasa
- **Breaking** `DateTimeInput`: Rename `DateTimeChanged` to `Updated` by @ddkasa
- `DateTimeInput`: Convert `DateTimeChanged` message to standard class by @ddkasa
- `HeatmapManager`: Convert `YearChanged` message to standard class by @ddkasa
- `ActivityHeatmap`: Move `can_focus` into class arguments by @ddkasa
- `ActivityHeatmap`: Convert messages to standard classes by @ddkasa
- `base-widgets`: Move `can_focus` into class arguments by @ddkasa
- `BaseMessage`: Convert `BaseMessage` to standard class by @ddkasa
- `BaseOverlay`: Rename `Close` message to `Closed` by @ddkasa
- **Breaking** `demo`: Rename `demo` command to `textual-timepiece` by @ddkasa

### Fixed
- `range-picker`: Update snapshots by @ddkasa
- `AbstractTimeline`: Make sure to clear `_start` value during cancellation by @ddkasa
- `timeline`: Update all snapshots by @ddkasa
- `snapshots`: Update all snapshots by @ddkasa
- `nox`: Correctly test all python versions locally by @ddkasa
- `typing`: Update typing to adhere to strict checks by @ddkasa

### Removed
- `timeline`: Remove old todo notes by @ddkasa
- `AbstractEntry`: Remove unnecessary `Offset` hint by @ddkasa
- `HorizontalTimeline`: Remove `_cached_strip` initial value by @ddkasa
- `time-picker`: Remove yoda expressions by @ddkasa
- Remove unnecessary elif statements after return by @ddkasa
- `date-picker`: Remove unnecessary `TYPE_CHECKING by @ddkasa
- `pickers`: Remove unnecessary spaces after docstring by @ddkasa
- `AbstractTimeline`: Remove spaces after docstring by @ddkasa

## [0.4.0] - 2025-03-10

### Changed
- **Breaking** `heatmap`: Use values reactive as entry point by @ddkasa

### Removed
- `heatmap-manager`: Remove border from navigation by @ddkasa

## [0.3.1] - 2025-03-04

### Changed
- `bindings`: Reverse binding type override by @ddkasa
- `heatmap`: Reduce loops in `_render_weeks` method by @ddkasa
- `heatmap`: Reduce loop count in `_render_weekday` method by @ddkasa
- `heatmap`: Use sum builtin for sum methods by @ddkasa

### Fixed
- `heatmap`: Incorrect offset set on tile by @ddkasa

### Removed
- `demo`: Remove documentation & github buttons by @ddkasa

## [0.3.0] - 2025-02-28

### Added
- `pickers`: Add DateTimeInput to module by @ddkasa
- `pickers`: Add DateInput to module by @ddkasa
- `date-select`: Add default border & background by @ddkasa
- `demo`: Add visual select widgets to demo by @ddkasa

### Changed
- **Breaking** `dur-picker`: Convert `on_mount` to private method by @ddkasa
- `pickers`: Convert `watch_expanded` to private method by @ddkasa
- **Breaking** `date-picker`: Convert watch_date to private method by @ddkasa
- **Breaking** `time-input`: Convert watch_time to private method by @ddkasa
- **Breaking** `pickers`: Disable input blurred message by @ddkasa
- `heatmap`: More accurate type for input by @ddkasa
- **Breaking** `heatmap`: Use `int` instead of `Date` for heatmap year by @ddkasa
- `heatmap`: Use cached property for heatmap navigation by @ddkasa
- **Breaking** `dt-dur-range`: Convert on_mount to private method by @ddkasa
- `constants`: Use constants for special unicode characters by @ddkasa
- `date-picker`: Use new date add method by @ddkasa
- **Breaking** `date-picker`: Convert to private method by @ddkasa
- `date-picker`: Improve render month method by @ddkasa
- `date-picker`: Re-order methods by @ddkasa
- `date-picker`: Improve render weekday by @ddkasa
- `demo`: Move tcss to app by @ddkasa
- `pickers`: Improve default tcss by @ddkasa

### Fixed
- `pickers`: Validate all mini picker variants by @ddkasa
- `dt-picker`: Use LocalDateTime in input generic by @ddkasa
- `pickers`: Update all snapshots by @ddkasa
- `dt-picker`: Extra edge case tests by @ddkasa
- `range-pickers`: Use correct widget identifier by @ddkasa
- `activity-heatmap`: Override tooltip type by @ddkasa
- `extra`: Include left border with get_line_offset by @ddkasa

### Removed
- **Breaking** `heatmap`: Remove unnecessary parent parameters by @ddkasa
- `heatmap`: Remove unnecessary tabs property by @ddkasa
- **Breaking** `widgets`: Remove imports from base module by @ddkasa
- `time-picker`: Remove unnecessary focus bool by @ddkasa

## [0.2.0] - 2025-02-13

### Added
- `pickers`: Add default message argument by @ddkasa

### Changed
- `date-range-picker`: Allow picking the end date first by @ddkasa
- **Breaking** `pickers`: Rename dialogs to overlays by @ddkasa
- **Breaking** `pickers`: Switch all SystemDateTime to LocalDateTime by @ddkasa
- `dt-picker`: Use a datetime format for parsing by @ddkasa
- `dt-picker`: Verify edge cases by @ddkasa
- `date-picker`: Verify edge cases by @ddkasa
- Move directions alias by @ddkasa
- `date-picker`: Use add method for location reactive by @ddkasa
- `range-pickers`: Update default & clear action functionality by @ddkasa
- `pickers`: Use a base method for expand button by @ddkasa
- `pickers`: Update default & clear action functionality by @ddkasa
- Make reactive typing more consistent by @ddkasa
- Use dedicated target button by @ddkasa
- `date-picker`: Use first row for aligning only by @ddkasa
- `pickers`: Simplify some typing by @ddkasa
- `pickers`: Rename binding by @ddkasa
- `date-select`: Use max unicode 1.1 icons by @ddkasa

### Fixed
- `heatmap`: Deal with year edge cases by @ddkasa
- `range-pickers`: Lock button using click method by @ddkasa
- `dt-picker`: Wrong reactive bound to overlay by @ddkasa
- `pickers`: Update snapshots by @ddkasa
- `heatmap`: Adjust keyboard month navigation by @ddkasa

### Removed
- `datetime-picker`: Remove unnecessary action by @ddkasa
- `pickers`: Remove unused placeholder class by @ddkasa

## [0.1.0] - 2025-02-09

### Added
- `pickers`: Add module __init__ file by @ddkasa
- Add about module by @ddkasa

### Changed
- `heatmap`: Implement activity heatmap by @ddkasa
- `utility`: Implement helper functionality by @ddkasa
- `widgets`: Supplementary widgets by @ddkasa
- `pickers`: Import pickers into base module by @ddkasa
- `pickers`: Implement timerange picker classes by @ddkasa
- `pickers`: Implement datetime picker classes by @ddkasa
- `pickers`: Implement time & duration picker classes by @ddkasa
- `pickers`: Implement date picker classes by @ddkasa
- `pickers`: Implement base picker classes by @ddkasa
- `demo`: Implement demo app by @ddkasa
- Init commit by @ddkasa

### Fixed
- Implement freeze_time fixture by @ddkasa
- Implement test app fixture by @ddkasa

## New Contributors
* @ddkasa made their first contribution
[0.5.0]: https://github.com/ddkasa/textual-timepiece/compare/v0.4.0..v0.5.0
[0.4.0]: https://github.com/ddkasa/textual-timepiece/compare/v0.3.1..v0.4.0
[0.3.1]: https://github.com/ddkasa/textual-timepiece/compare/v0.3.0..v0.3.1
[0.3.0]: https://github.com/ddkasa/textual-timepiece/compare/v0.2.0..v0.3.0
[0.2.0]: https://github.com/ddkasa/textual-timepiece/compare/v0.1.0..v0.2.0

<!-- generated by git-cliff -->
