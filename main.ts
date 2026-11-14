// news-image-01 entry: "The World in One Day"
// Copies the front-page image (entry.jpg, 1024x1024, JPEG) to the output
// path the harness reads, after validating the gate rules from RULES.txt:
// a whole JPEG, at most 1 MiB, at most 1024 by 1024 pixels.
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SOURCE = join(HERE, "entry.jpg");
const OUT_DIR = process.env.OUTPUT_DIR ?? "/output";
const OUT = join(OUT_DIR, "entry.png");

const MAX_BYTES = 1048576;
const MAX_SIDE = 1024;

function fail(message: string): never {
  throw new Error(`entry rejected: ${message}`);
}

// Read the JPEG's SOF segment to get its pixel dimensions.
function jpegSize(bytes: Buffer): { width: number; height: number } {
  if (bytes[0] !== 0xff || bytes[1] !== 0xd8 || bytes[2] !== 0xff) {
    fail("not a JPEG (bad magic bytes)");
  }
  let offset = 2;
  while (offset + 9 < bytes.length) {
    if (bytes[offset] !== 0xff) fail("corrupt JPEG marker stream");
    const marker = bytes[offset + 1];
    if (marker === 0xd9) break; // end of image
    const length = bytes.readUInt16BE(offset + 2);
    if (length < 2) fail("corrupt JPEG segment length");
    // SOF0 (0xc0), SOF1 (0xc1), SOF2 (0xc2): height then width.
    if (marker === 0xc0 || marker === 0xc1 || marker === 0xc2) {
      const height = bytes.readUInt16BE(offset + 5);
      const width = bytes.readUInt16BE(offset + 7);
      return { width, height };
    }
    offset += 2 + length;
  }
  fail("no JPEG start-of-frame segment found");
}

const bytes = readFileSync(SOURCE);
const size = statSync(SOURCE).size;
if (size > MAX_BYTES) fail(`entry.jpg is ${size} bytes, over the 1 MiB limit`);
const { width, height } = jpegSize(bytes);
if (width > MAX_SIDE || height > MAX_SIDE) {
  fail(`entry.jpg is ${width}x${height}, over the 1024x1024 limit`);
}
if (bytes[bytes.length - 2] !== 0xff || bytes[bytes.length - 1] !== 0xd9) {
  fail("JPEG is truncated (no end-of-image marker)");
}

mkdirSync(OUT_DIR, { recursive: true });
copyFileSync(SOURCE, OUT);
console.log(`wrote ${OUT}: ${width}x${height}, ${size} bytes`);
