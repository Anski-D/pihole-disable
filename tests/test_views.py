import pytest

from pihole_disable.views import _clean_period_value

class TestCleanPeriodValue:
    def test_clean_period_value_negative(self) -> None:
        assert _clean_period_value(-1) == 0
