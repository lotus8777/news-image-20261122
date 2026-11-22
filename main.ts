import { execFileSync } from "node:child_process";
import { existsSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entrypoint: build the poster by running build_poster.py in this folder,
// then confirm the output exists and is under the 1 MiB limit. The build
// itself is deterministic (fixed fonts, geometry and assets, no clock or
// randomness), so running this twice yields a byte-identical entry.png.
const here = dirname(fileURLToPath(import.meta.url));
const script = join(here, "build_poster.py");
const out = join(here, "entry.png");

execFileSync("python3", [script], { cwd: here, stdio: "inherit" });

if (!existsSync(out)) {
  throw new Error("entry.png was not produced by build_poster.py");
}
const bytes = statSync(out).size;
if (bytes >= 1024 * 1024) {
  throw new Error(`entry.png is ${bytes} bytes, over the 1 MiB limit`);
}
console.log(`poster ready: entry.png (${bytes} bytes)`);
