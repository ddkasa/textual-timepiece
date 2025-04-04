from datetime import datetime

import pytest

from textual_timepiece._utility import format_seconds
from textual_timepiece._utility import time_to_seconds


@pytest.mark.unit
def test_format_seconds():
    dt = time_to_seconds(datetime(2025, 4, 2, 12, 30, 30))
    assert format_seconds(dt) == "12:30:30"
    assert format_seconds(dt, include_seconds=False) == "12:30"
