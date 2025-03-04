---
title: Changelog
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
[0.3.1]: https://github.com/ddkasa/textual-timepiece/compare/v0.3.0..v0.3.1
[0.3.0]: https://github.com/ddkasa/textual-timepiece/compare/v0.2.0..v0.3.0
[0.2.0]: https://github.com/ddkasa/textual-timepiece/compare/v0.1.0..v0.2.0

<!-- generated by git-cliff -->
