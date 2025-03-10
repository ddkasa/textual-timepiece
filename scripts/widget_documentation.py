"""
Helper script to help document all widgets.

This goes through all textual_timepiece widgets and prints the scaffolding for
the tables that are used to document the classvars BINDINGS and
COMPONENT_CLASSES.

Original from https://github.com/Textualize/textual/blob/main/tools/widget_documentation.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import textual_timepiece.activity_heatmap
import textual_timepiece.pickers
import textual_timepiece.pickers._base_picker

if TYPE_CHECKING:
    from textual.binding import Binding


# TODO: Gather default CSS and nested bindings.
# TODO: Gather nested bindings


def print_bindings(widget: str, bindings: list[Binding]) -> None:
    """Print a table summarising the bindings.

    The table contains columns for the key(s) that trigger the binding,
    the method that it calls (and tries to link it to the widget itself),
    and the description of the binding.
    """
    if bindings:
        print("BINDINGS")
        print(f'"""All bindings for {widget}\n')
        print("| Key(s) | Description |")
        print("| :- | :- |")

    for binding in bindings:
        print(f"| {binding.key} | {binding.tooltip} |")

    if bindings:
        print('"""')


def print_component_classes(widget: str, classes: set[str]) -> None:
    """Print a table to document these component classes.

    The table contains two columns, one with the component class name and
    another for the description of what the component class is for.
    The second column is always empty.
    """
    if classes:
        print("COMPONENT_CLASSES")
        print(f'"""All component classes for {widget}\n')
        print("| Class | Description |")
        print("| :- | :- |")

    for cls in sorted(classes):
        print(f"| `{cls}` | XXX |")

    if classes:
        print('"""')


def module() -> None:
    """Main entrypoint.

    Iterates over all widgets and prints docs tables.
    """

    modules = [
        textual_timepiece.activity_heatmap,
        textual_timepiece.pickers,
        textual_timepiece.pickers._base_picker,
    ]

    for module in modules:
        print(module.__name__)
        for name in module.__all__:
            w = getattr(module, name)
            bindings: list[Binding] = w.__dict__.get("BINDINGS", [])
            component_classes: set[str] = getattr(
                w, "COMPONENT_CLASSES", set()
            )

            if bindings or component_classes:
                print(name)
                print()
                print_bindings(name, bindings)
                print_component_classes(name, component_classes)
                print()


def main() -> None:
    module()


if __name__ == "__main__":
    main()
