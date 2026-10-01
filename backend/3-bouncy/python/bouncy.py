"""Find the first integer whose bouncy-number ratio is an exact percentage."""

import argparse
from itertools import pairwise


def _is_bouncy(number: int) -> bool:
    """Return whether the decimal digits are neither monotone increasing nor decreasing."""
    digits = str(number)
    has_increase = False
    has_decrease = False

    for left, right in pairwise(digits):
        if left < right:
            has_increase = True
        elif left > right:
            has_decrease = True

        if has_increase and has_decrease:
            return True

    return False


def least_number_with_bouncy_ratio(percent: int) -> int:
    """Return the least positive integer with exactly ``percent``% bouncy numbers.

    Raises:
        TypeError: If ``percent`` is not an integer (booleans are not accepted).
        ValueError: If ``percent`` is outside the inclusive range 1..99.
    """
    if type(percent) is not int:
        raise TypeError("percent must be an integer")
    if not 1 <= percent <= 99:
        raise ValueError("percent must be between 1 and 99")

    bouncy_count = 0
    number = 1

    while True:
        if _is_bouncy(number):
            bouncy_count += 1

        if 100 * bouncy_count == percent * number:
            return number

        number += 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find the least number at an exact bouncy-number percentage."
    )
    parser.add_argument("percent", type=int, help="Target percentage (1 to 99).")
    args = parser.parse_args()

    try:
        print(least_number_with_bouncy_ratio(args.percent))
    except (TypeError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
