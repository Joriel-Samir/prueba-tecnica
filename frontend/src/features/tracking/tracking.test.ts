import { describe, expect, it } from 'vitest';
import { bearingBetween, distanceBetween } from './tracking';

describe('tracking domain calculations', () => {
  it('calculates a real-world distance in meters', () => {
    const distance = distanceBetween({ lat: 4.711, lng: -74.072 }, { lat: 4.721, lng: -74.072 });
    expect(distance).toBeGreaterThan(1_000);
    expect(distance).toBeLessThan(1_200);
  });

  it('calculates northbound bearing', () => {
    expect(bearingBetween({ lat: 4.711, lng: -74.072 }, { lat: 4.721, lng: -74.072 })).toBeCloseTo(0, 0);
  });
});
