/** Return whether the decimal digits are neither monotone increasing nor decreasing. */
function isBouncy(number: number): boolean {
  const digits = String(number);
  let hasIncrease = false;
  let hasDecrease = false;

  for (let index = 1; index < digits.length; index += 1) {
    const previous = digits[index - 1]!;
    const current = digits[index]!;

    if (previous < current) {
      hasIncrease = true;
    } else if (previous > current) {
      hasDecrease = true;
    }

    if (hasIncrease && hasDecrease) {
      return true;
    }
  }

  return false;
}

/**
 * Find the least positive integer whose bouncy-number ratio is exactly `percent`%.
 *
 * The ratio equality is evaluated with integer arithmetic to avoid rounding errors.
 * @throws {RangeError} If percent is not an integer in the range 1..99.
 */
export function leastNumberWithBouncyRatio(percent: number): number {
  if (!Number.isInteger(percent) || percent < 1 || percent > 99) {
    throw new RangeError("percent must be an integer between 1 and 99");
  }

  let bouncyCount = 0;
  let number = 1;

  while (true) {
    if (isBouncy(number)) {
      bouncyCount += 1;
    }

    if (100 * bouncyCount === percent * number) {
      return number;
    }

    number += 1;
  }
}

/** Python-compatible alias for callers that share the same API name across languages. */
export const least_number_with_bouncy_ratio = leastNumberWithBouncyRatio;
