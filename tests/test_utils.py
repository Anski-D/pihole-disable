import pytest

from pihole_disable.utils import _clean_period_value, _check_client


@pytest.mark.parametrize("value_in, value_out", [(-1, 0), (1, 1), (10000, 10000), ("-1", 0), ("1", 1), ("10000", 10000)])
def test_clean_period_value(value_in: int | str, value_out: int) -> None:
    assert _clean_period_value(value_in) == value_out


class TestCheckClient:
    @pytest.mark.parametrize("value_in, bool_out", [("111.111.111.111", True), ("111.111.111.1111", False)])
    def test_len(self, value_in: str, bool_out: bool) -> None:
        assert _check_client(value_in) == bool_out

    @pytest.mark.parametrize("value_in, bool_out", [("1.1.1.1", True), ("1.1.1", False), ("1.1.1.1.1", False)])
    def test_parts_count(self, value_in: str, bool_out: bool) -> None:
        assert _check_client(value_in) == bool_out

    @pytest.mark.parametrize("value_in, bool_out", [("1.2.32.10", True), ("1.2.34.xxx", False), ("x.x.x.x", False)])
    def test_part_is_digit(self, value_in: str, bool_out: bool) -> None:
        assert _check_client(value_in) == bool_out

    @pytest.mark.parametrize("value_in, bool_out", [("0.0.0.0", True), ("255.255.255.255", True), ("1.1.1.300", False)])
    def test_part_value_in_range(self, value_in: str, bool_out: bool) -> None:
        assert _check_client(value_in) == bool_out