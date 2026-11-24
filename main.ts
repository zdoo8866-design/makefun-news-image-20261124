// Entry point for the make.fun "news-image-20261124" submission.
//
// The deliverable is entry.png beside this file: a 1024x1024 newspaper
// front page that sums up the world news of Tuesday 24 November 2026
// in 36 stories — 13 drawn cards, a where-it-happened map and 23
// one-line briefs, closed by a date-check box. The
// grader mounts this repository read-only and expects the program to
// stage the image into $MAKEFUN_OUTPUT_DIR (falling back to /output).
// Before staging, the program checks the file against the competition's
// intake limits (real PNG, no side over 1024 px, at most 1 MiB), and
// after staging it proves the copy is byte-identical via SHA-256.

import { createHash } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const BYTE_LIMIT = 1024 * 1024; // 1 MiB
const SIDE_LIMIT = 1024; // px, width and height

const dir = dirname(fileURLToPath(import.meta.url));
const src = join(dir, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const dst = join(outDir, "entry.png");

function die(msg: string): never {
  console.error(`entry check failed: ${msg}`);
  process.exit(1);
}

if (!existsSync(src)) die(`missing entry.png next to main.ts (${src})`);

const data = readFileSync(src);
if (data.length === 0) die("entry.png is empty");
if (data.length > BYTE_LIMIT) {
  die(`entry.png is ${data.length} bytes; the limit is ${BYTE_LIMIT}`);
}

// A PNG opens with an 8-byte signature, then the IHDR chunk: 4 bytes of
// length, the letters "IHDR", then width and height as uint32 BE.
const SIG = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
if (!SIG.every((b, i) => data[i] === b)) die("entry.png is not a PNG file");
if (data.subarray(12, 16).toString("ascii") !== "IHDR") {
  die("entry.png has no IHDR chunk where one belongs");
}
const w = data.readUInt32BE(16);
const h = data.readUInt32BE(20);
if (w > SIDE_LIMIT || h > SIDE_LIMIT) {
  die(`entry.png is ${w}x${h}; the limit is ${SIDE_LIMIT}x${SIDE_LIMIT}`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(src, dst);

const sha = (p: string) => createHash("sha256").update(readFileSync(p)).digest("hex");
if (statSync(dst).size !== data.length) die("staged copy is truncated");
if (sha(dst) !== sha(src)) die("staged copy differs from the original");

console.log(`entry.png verified: PNG, ${w}x${h}, ${data.length} bytes`);
console.log(`sha256 ${sha(src)}`);
console.log(`staged at ${dst}`);
