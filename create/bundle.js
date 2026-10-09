// Bundles the starter into this package at pack time, so `npm create legible-slides` needs no
// clone. The starter lives once, in skill/template/, and the copy here is an artifact: gitignored,
// written fresh before every pack, and removed after it with --remove.
//
// npm leaves every .gitignore out of a package, so the starter's travels as `gitignore` and
// index.js names it back.
import { cpSync, renameSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const bundled = join(here, "template");

rmSync(bundled, { recursive: true, force: true });
if (process.argv[2] !== "--remove") {
  cpSync(join(here, "..", "skill", "template"), bundled, { recursive: true });
  renameSync(join(bundled, ".gitignore"), join(bundled, "gitignore"));
}
