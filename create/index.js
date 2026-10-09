#!/usr/bin/env node
// npm create legible-slides my-talk: stamps the starter into a new directory, named for it.
//
// The starter is bundled into this package when it is packed (bundle.js). Run from a checkout of
// legible-slides, it stamps the starter in skill/template/ instead, the one being edited, even over
// a bundle an interrupted pack left behind. Node's standard library only, so the command installs
// nothing before it runs.
import {
  chmodSync,
  cpSync,
  existsSync,
  readdirSync,
  readFileSync,
  renameSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const inCheckout = join(here, "..", "skill", "template");
const starter = existsSync(inCheckout) ? inCheckout : join(here, "template");

function fail(message) {
  console.error(`create-legible-slides: ${message}`);
  process.exit(1);
}

// The `cd` an author pastes into a shell: quoted when the path holds anything a shell would read,
// and after `--` when it would otherwise be taken for an option.
function cdInto(path) {
  const quoted = /^[\w@%+=:,./-]+$/.test(path) ? path : `'${path.replaceAll("'", "'\\''")}'`;
  return path.startsWith("-") ? `cd -- ${quoted}` : `cd ${quoted}`;
}

const [target] = process.argv.slice(2);
if (!target) {
  fail("name the directory for the new deck: npm create legible-slides my-talk");
}
const deck = resolve(target);

// Checked before anything is written, so a refusal leaves the directory exactly as it was.
if (existsSync(deck) && (!statSync(deck).isDirectory() || readdirSync(deck).length > 0)) {
  fail(`${target} is not an empty directory, so nothing was written. Name a new one.`);
}

cpSync(starter, deck, { recursive: true });

// npm leaves a .gitignore out of a package, so the bundled starter carries it under another name.
if (existsSync(join(deck, "gitignore"))) {
  renameSync(join(deck, "gitignore"), join(deck, ".gitignore"));
}

// Every check runs through bin/, so the launchers have to run straight away, whatever modes the
// package kept on its way here.
for (const launcher of readdirSync(join(deck, "bin"))) {
  chmodSync(join(deck, "bin", launcher), 0o755);
}

const manifestPath = join(deck, "package.json");
const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
manifest.name = basename(deck);
writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

console.log(`Stamped a new deck in ${target}. Next:

  ${cdInto(target)}
  pnpm install
  pnpm dev
`);
