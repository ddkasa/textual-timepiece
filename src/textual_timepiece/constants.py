"""Constants that the widgets use. Mostly different unicode symbols.

Exposed as a public module in order to allow the user patch before importing
one of the widgets or setting them through environment variables.

Examples:
    >>> import textual_timepiece.constants
    >>> textual_timepiece.constants.LEFT_ARROW = "L"
    >>> textual_timepiece.constants.RIGHT_ARROW = "R"
    >>> from textual_timepiece.pickers import DatePicker
"""

import os

LEFT_ARROW: str = os.environ.get("TTIME_ICON_LEFT_ARROW", "←")
"""Left pointing symbol for navigational purposes. Mostly going back in time.
"""

RIGHT_ARROW: str = os.environ.get("TTIME_ICON_RIGHT_ARROW", "→")
"""Right pointing symbol for navigational purposes. Mostly going forward in
time.
"""

TARGET_ICON: str = os.environ.get("TTIME_ICON_TARGET", "◎")
"""Used as the default target icon. Mostly when going to the current
date and/or time.
"""

LOCKED_ICON: str = os.environ.get("TTIME_ICON_LOCKED", "🔒")
"""Icon that is rendered when a widget is locked."""

UNLOCKED_ICON: str = os.environ.get("TTIME_ICON_UNLOCKED", "🔓")
"""Icon that is rendered when a widget is unlocked."""
