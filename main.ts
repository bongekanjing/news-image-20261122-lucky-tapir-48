/**
 * 22 November 2026 — the day's world news in one image.
 *
 * The entry is the drawing in `entry.png`, made by `draw.py` beside this file.
 * This program's only job is to put that file where the house reads it, and to
 * refuse to hand over an image the gate would reject: a truncated or oversized
 * file is scored 0 without ever reaching the judge, so it is better to fail
 * loudly here than to be silently thrown out.
 *
 * The checks are the ones the rules state, applied in the same order the gate
 * would apply them: size, signature, that the first chunk is IHDR, and that the
 * declared dimensions are within 1024 on a side. The program runs twice and both
 * runs must write the same bytes, so it copies rather than generates: a copy is
 * byte-for-byte the file in the repository.
 *
 * Node 22, standard library only, no network.
 */

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

/** The house's limits on entry.png, as the rules state them. */
const MAX_BYTES = 1048576;   // 1 MiB
const MAX_SIDE = 1024;       // 1024 x 1024 pixels

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

/**
 * Read entry.png and check it against every rule the gate enforces that can be
 * checked without decoding the image. Throws with a specific message on the
 * first failure, so a bad build says why rather than scoring nothing quietly.
 */
function checkedPng(path: string): Buffer {
  const bytes = readFileSync(path);

  if (bytes.length === 0) {
    throw new Error('entry.png is empty');
  }
  if (bytes.length > MAX_BYTES) {
    throw new Error(`entry.png is ${bytes.length} bytes, over the ${MAX_BYTES} limit`);
  }

  for (let i = 0; i < PNG_SIGNATURE.length; i++) {
    if (bytes[i] !== PNG_SIGNATURE[i]) {
      throw new Error('entry.png is not a PNG: its signature bytes are wrong');
    }
  }

  // IHDR is always the first chunk: 8 signature bytes, 4 length, 4 type, then
  // its data, which opens with width and height as big-endian u32.
  if (bytes.subarray(12, 16).toString('latin1') !== 'IHDR') {
    throw new Error('entry.png is not a PNG: its first chunk is not IHDR');
  }

  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width < 1 || height < 1 || width > MAX_SIDE || height > MAX_SIDE) {
    throw new Error(`entry.png is ${width}x${height}, outside 1..${MAX_SIDE} on a side`);
  }

  // The last 12 bytes must be an empty IEND chunk, so the file is not truncated.
  const tail = bytes.subarray(bytes.length - 12);
  if (tail.subarray(4, 8).toString('latin1') !== 'IEND') {
    throw new Error('entry.png does not end with an IEND chunk: the file is truncated');
  }

  return bytes;
}

function main(): void {
  const source = join(HERE, 'entry.png');
  const bytes = checkedPng(source);

  mkdirSync(OUT_DIR, { recursive: true });
  copyFileSync(source, join(OUT_DIR, 'entry.png'));

  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  process.stdout.write(
    `wrote entry.png (${bytes.length} bytes, ${width}x${height})\n`,
  );
}

main();
