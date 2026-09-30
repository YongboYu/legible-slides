# The flagship deck

The primary teaching artifact of [`legible-slides`](../README.md): a deck that teaches the method by
being it. Every rule it demonstrates is stated once, in [`docs/method.md`](../docs/method.md), and
the [thirteen beats](../docs/method.md#the-flagship-deck-13-beats) it grows into are the outline
there.

Fourteen slides: the thirteen beats, then the sources they cite. Two of the beats are demonstrations
that could not be faked, and [the figures](#the-figures) below is where they come from.

## Running it

```bash
pnpm install
pnpm dev      # with hot reload
pnpm build    # what CI builds
```

The deck names the theme by path (`theme: ../theme`), which is how a deck consumes
[`slidev-theme-legible`](../theme/README.md) until the package is on npm. Nothing else is configured
here, because everything the method fixes arrives with the theme — see that README for what.

**No Python is needed to build it.** The palette reaches these slides as
[`theme/styles/tokens.css`](../theme/styles/tokens.css), which is generated from
[`themes/leuven-blue.json`](../themes/leuven-blue.json) and committed like a lockfile — so recolouring the
deck is an edit to that one file and a `legible gen-css` run, with nothing to change here. CI checks
that the colour on the built slides is still the colour in the theme file.

## A PDF to present from

```bash
pnpm exec playwright install chromium-headless-shell   # once: the renderer, ~95 MB
pnpm export                                            # → dist/legible-slides.pdf
```

The browser is a manual step because pnpm does not run a dependency's install scripts, and that is
the right default — a 95 MB download should be something you asked for. CI installs the package with
everything else and never downloads the browser, because it never exports.

## The figures

```bash
uv run --project ../python python figures.py
```

Three PNGs into `public/`, from [`themes/leuven-blue.json`](../themes/leuven-blue.json) under real Machado
simulation — figures are regenerated, never redrawn. Beat 3 shows the deck's five-series chart with
colour as the only channel and beat 10 shows it with the dash and the marker back on, under
deuteranomaly and in grayscale; a hand-drawn approximation of either would gut the demonstration.
[`figures.py`](figures.py) records why each of the three is drawn the way it is.

They are **committed**, and nothing regenerates them for you: the deck build never runs Python, the
same way it never runs `gen-css`. Re-run the line above when the palette changes.

## Held to the method

```bash
uv run --project ../python legible lint slides.md --theme ../themes/leuven-blue.json
```

Every rule [`docs/method.md`](../docs/method.md) marks *decided by script* — `bullet-ceiling`,
`word-ceiling`, `no-em-dash-headline`, `no-inflated-register`, `opener-variety` and
`separation-floor`. CI runs exactly this line, and a finding it calls an error turns the run red.

The rules the canon marks *judgment* — `one-message`, `assertion-headline`, `evidence-is-visual` and
the rest — are a reviewer's, human or agent. See
[`docs/agent-skill-contract.md`](../docs/agent-skill-contract.md).

## What lives where

| | |
|---|---|
| `slides.md` | the deck. The first frontmatter block is the deck's headmatter *and* the cover's own frontmatter, which is why the cover's props sit up there. |
| `figures.py` | the three generated figures, and why each is drawn as it is. |
| `style.css` | the two demonstrations the theme will not build, because the method refuses them: a stock-template slide, and body type below the floor. Slidev loads it for you. Every size in it derives from the theme's own custom properties, so nothing here invents one. |
| `public/` | what the deck serves: the generated figures, and the two logo placeholders — this project ships no institution's mark, so presenting under one is dropping it in here and pointing one line of `themeConfig` at it. |

The speaker and venue on the cover are the presenter's to set, and a `date` is theirs to add.
