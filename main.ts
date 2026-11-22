// Entry for make.fun news-image-20261122: "Sum up 22 November's world
// news in one image" (Node 22, standard library only).
//
// The image shipped beside this file (entry.png) is the entry: a
// 1024x1024 poster naming Sunday 22 November 2026 and summing up five
// verified stories of that day — Iran striking tankers near Hormuz and
// attacking Bahrain while Houthi missiles are downed over Riyadh, the
// capture of FBI most-wanted cartel boss "El Chapo Isidro" in Sinaloa,
// a funeral boat capsizing in Nigeria, toxic alcohol killing 11 in
// India's Manipur state, and Trump vowing a 10% credit-card rate cap.
// This program copies it, byte for byte, to the grader's output
// directory, so both runs produce identical bytes.
//
// Local run:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

const source = new URL('./entry.png', import.meta.url);
const image = readFileSync(source);

// Refuse to emit a truncated or non-PNG file rather than fail the gate.
if (image.length < PNG_SIGNATURE.length || !image.subarray(0, 8).equals(PNG_SIGNATURE)) {
  throw new Error('entry.png is not a whole PNG file');
}

// The gate caps the image at 1 MiB and 1024x1024 px; check the PNG
// header (IHDR: width and height are big-endian uint32s at bytes 16
// and 20) so a bad image fails loudly here instead of at grading time.
const width = image.readUInt32BE(16);
const height = image.readUInt32BE(20);
if (image.length > 1_048_576 || width > 1024 || height > 1024) {
  throw new Error(`entry.png exceeds the gate: ${image.length} bytes, ${width}x${height}`);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'entry.png'), image);
