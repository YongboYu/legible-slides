# Mode: scaffold

Stamp a new Slidev deck wired to the theme, its palette and both checks. It is a **clean start**:
one blank slide per layout, for the author to write. The flagship deck in legible-slides is where
the method is taught.

## 1. Settle the four things the template cannot

Ask for whichever of these the author has not already said.

| What | And what to take as given |
|---|---|
| Where the deck goes | a new directory, named by the author. |
| Where the theme comes from | a checkout of legible-slides, at a commit that is on GitHub. Ask which checkout. The deck gets its own copy of the theme from that commit, and its checks install from the same one, so the deck builds anywhere and is checked against the rules it was built to. |
| Which palette it wears | the one the template carries, a copy of `themes/leuven-blue.json`. Change it only if the author names another. |
| Which marks the cover shows | the placeholders the theme bundles, unless the author names their own files. |

## 2. Stamp the template, and vendor the theme

`template/` beside this skill's `SKILL.md` is the deck. Copy all of it, dotfiles included, then copy
the theme from the checkout's commit and pin both checks to it:

```bash
cp -R /path/to/this/skill/template/. path/to/new-deck/

CHECKOUT=/path/to/legible-slides
git -C "$CHECKOUT" status --short                  # clean, so the commit is what you copy
git -C "$CHECKOUT" branch -r --contains HEAD       # on GitHub, so the pin can be fetched
REV=$(git -C "$CHECKOUT" rev-parse HEAD)
git -C "$CHECKOUT" archive "$REV" theme | tar -x -C path/to/new-deck
sed -i.bak "s|^REV=main$|REV=$REV|" path/to/new-deck/bin/legible
rm path/to/new-deck/bin/legible.bak
```

The trailing `/.` copies the dotfiles, which are the checks. `git archive` copies what the commit
holds and nothing a local build left beside it. `bin/legible` is the one place the pin lives: the
hooks, the workflow and every command below run the checks through it, so the deck is checked
against the rules it was built to, whatever `legible` is on the machine's PATH.

**Done when** `.github/workflows/method.yml`, `.pre-commit-config.yaml`, `bin/` and `theme/` are in
the new deck, and `bin/legible` reads `REV=` followed by the commit rather than `main`.

## 3. Fill in what the author named

| Where | What |
|---|---|
| the headmatter of `slides.md` | the title, the author, and the cover's own venue and date. The theme is already `./theme` |
| `package.json` | the deck's name and its description |
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
commit the deck is pinned to. The gate passes on a stamped deck; an error means the fault is in the
template, so fix it there and stamp again.

The warnings are the blanks: `assertion-headline` fires on every skeleton slide, because a headline
that says what belongs in it is not a claim, and each clears when the author writes the slide.
Report them as blanks, and leave the headlines to the author.

**Done when** the gate passes and every warning in the report is a blank.
