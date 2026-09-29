import { execFileSync, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import { leastNumberWithBouncyRatio } from "../src/index.js";

const projectDirectory = fileURLToPath(new URL("..", import.meta.url));

describe("leastNumberWithBouncyRatio", () => {
  it.each([
    [50, 538],
    [90, 21_780],
    [99, 1_587_000],
  ])("returns %i%% at %i", (percent, expected) => {
    expect(leastNumberWithBouncyRatio(percent)).toBe(expected);
  });

  it.each([0, 100, -1, 101, 1.5, "50", true])(
    "rejects invalid percentage %s",
    (percent) => {
      expect(() => leastNumberWithBouncyRatio(percent as number)).toThrow(
        RangeError,
      );
    },
  );
});

describe("CLI", () => {
  it("prints the result", () => {
    const output = execFileSync(
      process.execPath,
      ["--import", "tsx", "src/cli.ts", "50"],
      { cwd: projectDirectory, encoding: "utf8" },
    );
    expect(output.trim()).toBe("538");
  });

  it("rejects an invalid percentage", () => {
    const result = spawnSync(
      process.execPath,
      ["--import", "tsx", "src/cli.ts", "100"],
      { cwd: projectDirectory, encoding: "utf8" },
    );
    expect(result.status).not.toBe(0);
  });
});
