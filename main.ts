// Entrypoint for the news-image-20261122 entry.
//
// The poster is already finished and stored in this folder as entry.png.
// This script does not rebuild it. It only checks that the finished file
// is a valid PNG within the size limits, then copies it to the directory
// the grader names in MAKEFUN_OUTPUT_DIR (or to this folder when that
// variable is unset). It uses only the Node standard library, so it runs
// with no Python, no imaging packages and no fonts — even when the
// repository itself is mounted read-only.
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || here;
const out = join(outDir, "entry.png");

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1024 * 1024;
const MAX_SIDE = 1024;

const data = readFileSync(source);

if (data.length < 33) {
  throw new Error(`entry.png is only ${data.length} bytes, too short to be a PNG`);
}
if (!data.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png does not start with the PNG signature");
}
if (data.length >= MAX_BYTES) {
  throw new Error(`entry.png is ${data.length} bytes, over the 1 MiB limit`);
}
const width = data.readUInt32BE(16);
const height = data.readUInt32BE(20);
if (width > MAX_SIDE || height > MAX_SIDE) {
  throw new Error(`entry.png is ${width}x${height}, larger than the 1024x1024 limit`);
}

mkdirSync(outDir, { recursive: true });
writeFileSync(out, data);

const written = statSync(out).size;
console.log(`poster ready: ${out} (${written} bytes)`);
