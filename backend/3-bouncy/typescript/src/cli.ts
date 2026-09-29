#!/usr/bin/env node
import { leastNumberWithBouncyRatio } from "./index.js";

const args = process.argv.slice(2);

if (args.length !== 1 || !/^\d+$/.test(args[0] ?? "")) {
  console.error("Usage: bouncy-ratio <percent: 1..99>");
  process.exitCode = 1;
} else {
  try {
    console.log(leastNumberWithBouncyRatio(Number(args[0])));
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
