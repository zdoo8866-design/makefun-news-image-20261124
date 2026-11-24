// Entry point for the news-image-20261124 submission.
//
// The deliverable is a single PNG front page for Tuesday 24 November
// 2026. The page is composed by tools/compose.py (Pillow); this script
// stages it: it runs the composer into a scratch file, verifies the
// result is a real PNG inside the intake limits (at most 1024x1024 and
// at most 1 MiB), and only then copies it to /output/entry.png.

import { spawnSync } from "node:child_process";
import { copyFileSync, statSync, readFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const scratch = join(here, "entry.png");
const outDir = "/output";
const outFile = join(outDir, "entry.png");

function fail(msg: string): never {
  console.error("entry: " + msg);
  process.exit(1);
}

const run = spawnSync("python3", [join(here, "tools", "compose.py"), scratch], {
  stdio: "inherit",
});
if (run.status !== 0) fail("composer exited with " + run.status);

const bytes = readFileSync(scratch);
const pngMagic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
if (!pngMagic.every((b, i) => bytes[i] === b)) fail("output is not a PNG");
if (bytes.length > 1_048_576) fail("output exceeds 1 MiB: " + bytes.length);

const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  fail(`output is ${width}x${height}, over the 1024 cap`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(scratch, outFile);
console.log(
  `entry: wrote ${outFile} (${width}x${height}, ${statSync(outFile).size} bytes)`,
);
