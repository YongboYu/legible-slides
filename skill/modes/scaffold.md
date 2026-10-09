# Mode: scaffold

Stamp a new Slidev deck wired to the theme, its palette and both checks. It is a **clean start**:
one blank slide per layout, for the author to write. The flagship deck in legible-slides is where
the method is taught.

## 1. Settle the three things the template cannot

Ask for whichever of these the author has not already said.

| What | And what to take as given |
|---|---|
| Where the deck goes | a new directory, named by the author. |
| Which palette it wears | the one the template carries, a copy of `themes/leuven-blue.json`. Change it only if the author names another. |
| Which marks the cover shows | the placeholders the theme bundles, unless the author names their own files. |

The version is settled for you: the release that stamps the deck pins the theme and the checks to
itself, `slidev-theme-legible` from npm in `package.json` and `legible-slides` from PyPI on the
`VERSION=` line of `bin/legible`.

## 2. Stamp the template

Stamp it the way an author would, with the create command, naming the new directory:

```bash
npm create legible-slides path/to/new-deck
```

It stamps the starter as the latest release ships it, dotfiles included, since the dotfiles are the
checks. That release can be newer than this skill, which is why every check runs through the deck's
own launcher. It names the deck after its directory, and it refuses a directory that is not empty,
so name a new one.

`bin/legible` is the one place the checks' pin lives: the hooks, the workflow and every command
below run the checks through it, so the deck is checked against the rules it was built to, whatever
`legible` is on the machine's PATH.

**Done when** `.github/workflows/method.yml`, `.pre-commit-config.yaml` and `bin/` are in the new
deck, and the `VERSION=` line in `bin/legible` names the version `package.json` pins
`slidev-theme-legible` to.

## 3. Fill in what the author named

| Where | What |
|---|---|
| the headmatter of `slides.md` | the title, the author, and the cover's own venue and date. The theme is already `legible` |
| `package.json` | the deck's description. The create command has already named it after its directory |
| `themes/palette.json` | the chosen palette's contents, if it is not the one stamped. Keep the path: everything in the deck points at it, which makes a recolour one edit. |
| `public/`, `themeConfig.venueLogo` and `themeConfig.affiliationLogo` | the author's own marks, if they named any |
| `themeConfig.shareUrl`, `themeConfig.shareQr` and `themeConfig.contact` | where the slides will be shared and how to reach the author, if they said; a QR code for the link goes in `public/` |

The skeleton slides stay **blank**: what each slide is for is the author's decision.

## 4. Regenerate the stylesheet

The palette reaches the slides as a committed stylesheet, so the build never runs Python. A palette
changed in step 3 leaves it stale:

```bash
bin/cvd-validate themes/palette.json
bin/legible gen-css themes/palette.json --output styles/tokens.css
```

The floor first: the validator names the pair or pairing to move.

**Done when** `bin/cvd-validate` exits 0 and `styles/tokens.css` is regenerated from the palette.

## 5. Hand it over green

```bash
pnpm install && pnpm build
```

Then run [review](review.md) over the stamped deck, and hand the report over with it, naming the
version the deck is pinned to. The gate passes on a stamped deck; an error means the fault is in the
template, so fix it there and stamp again.

The warnings are the blanks: `assertion-headline` fires on every skeleton slide, because a headline
that says what belongs in it is not a claim, and each clears when the author writes the slide.
Report them as blanks, and leave the headlines to the author.

**Done when** the gate passes and every warning in the report is a blank.
