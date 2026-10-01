import subprocess
import sys
from pathlib import Path

import pytest
from bouncy import least_number_with_bouncy_ratio


@pytest.mark.parametrize(
    ("percent", "expected"),
    [(50, 538), (90, 21_780), (99, 1_587_000)],
)
def test_least_number_reaches_known_bouncy_ratio(percent: int, expected: int) -> None:
    assert least_number_with_bouncy_ratio(percent) == expected


@pytest.mark.parametrize("percent", [0, 100, -1, 101, 1.5, True, "50"])
def test_rejects_invalid_percentages(percent: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        least_number_with_bouncy_ratio(percent)  # type: ignore[arg-type]


def test_cli_prints_result() -> None:
    script = Path(__file__).parents[1] / "bouncy.py"
    result = subprocess.run(
        [sys.executable, str(script), "50"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "538"


def test_cli_rejects_invalid_percentage() -> None:
    script = Path(__file__).parents[1] / "bouncy.py"
    result = subprocess.run(
        [sys.executable, str(script), "100"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
