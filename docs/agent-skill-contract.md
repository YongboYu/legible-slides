# The agent-skill contract

_Resolves [#12](https://github.com/YongboYu/legible-slides/issues/12). Depends on the method canon
([#3](https://github.com/YongboYu/legible-slides/issues/3), `method.md` — the single source of
truth for the rules), and consumes the CVD-validator contract
([#9](https://github.com/YongboYu/legible-slides/issues/9),
[`cvd-validator-contract.md`](cvd-validator-contract.md)) and the Slidev reference impl
([#10](https://github.com/YongboYu/legible-slides/issues/10),
[`slidev-reference-impl.md`](slidev-reference-impl.md))._

The skill is the delivery that lets a **coding agent build to the method** — it stamps a
method-compliant starting point (**scaffold**) and holds a deck to the standard afterwards
(**review**). The review half is the high-value part: it turns the method's rules from prose a human
must remember into checks an agent runs. It never restates those rules — it points at `method.md`.

---

## 1. Shape — one `SKILL.md` skill, two modes

A single **Claude Code skill** defined by a `SKILL.md`, living in **`skill/`** at the repo root (a
shippable delivery, not a project-private `.claude/skills/` helper). One skill covering two modes:

- **scaffold** — start a new method-compliant Slidev deck of your own.
- **review** — check an existing deck against the method.

**Deferred to future work** (same "seed, extensible" posture as the rest of the map):

- **Plugin packaging** — distributing the skill as an installable Claude Code plugin.
- **Cross-agent targeting** — re-expressing the same contract as `AGENTS.md` guidance for non-Claude
  agents. The contract is designed to make this cheap: every rule lives in tool-neutral `method.md`,
  and every mechanical check is a tool-neutral CLI, so nothing about the skill is Claude-specific
  except the `SKILL.md` wrapper.

## 2. Rule sourcing — a thin pointer, never a second copy

`method.md` is the single source of truth (#3: `AGENTS.md` and `design-provenance.md` *point to* it
rather than restate). The skill obeys the same rule:

- `SKILL.md` carries only the **review procedure** — the ordered workflow, which checks are
  mechanical vs judgment, and the report format. It does **not** restate what a good slide is.
- The **rule content and thresholds are loaded from `method.md` at review time**. A rule change in
  `method.md` therefore never silently un-syncs the reviewer.
- Every rule there carries a **stable ID** (`one-message`, `bullet-ceiling`, `separation-floor`, …)
  and, where it has a number, a `key = value` **threshold line**. The skill addresses rules by ID and
  **quotes** those lines, so the thin pointer never forces the reviewer to re-derive a number at
  runtime.
- `method.md` also marks each rule **`script`** or **`judgment`**, which is the same seam §4 splits
  the engine along. The canon decides which side a rule falls on; the skill only implements it.

Built in **#23** as [`skill/SKILL.md`](../skill/SKILL.md), whose review procedure loads rules by
running `legible rules [RULE …] [--decided-by script|judgment] [--section SECTION]`. It prints the
canon's own markdown, and the package carries that canon into a wheel, so a review on a machine with
no checkout still reads the rules rather than remembering them. The filters matter as much as the
IDs: asking for a section and a side of the seam is how the anti-slop pass picks up a rule the canon
grows without an edit here. See [`python/README.md`](../python/README.md#legible-rules).

## 3. Review surface — Slidev-coupled for v1

The review parses a **Slidev deck**: the markdown slides, the `themes/*.json` palette, and the
generated figure PNGs. The mechanical linter is Slidev-markdown-aware. PPTX is **not** a review
target in v1 — it is a hand-authored static *proof* (#11), not a user-authoring surface.

**Future work** (noted, not v1): the review goes **format-agnostic** — working on extracted textual
content + figures from any deck — and the scaffold side grows to let users work with PPTX / Keynote /
other-format templates through the skill + a coding agent.

## 4. Review engine — a hybrid seam

Checks split by whether a script can decide them with certainty. Mechanical checks are reproducible
and CI-able; semantic checks need an LLM's judgment.

### 4a. Mechanical — a deterministic linter

Lives in the existing **`legible` Python package** (one Python home, alongside the figure helper and
the validator, sharing the pinned `colorspacious`). Objective, reproducible, CI-integratable.

Built in **#19** as `legible lint DECK [--theme THEME …]`, exiting 0 clean, 1 on any violation and 2
when the deck or a theme could not be read — the same three the validator publishes. Its report is
grouped by slide and names each finding's rule; see
[`python/README.md`](../python/README.md#legible-lint).

| Check | Rule | How |
|---|---|---|
| Bullet ceiling | `bullet-ceiling` | count list items per slide, against the rule's threshold |
| Word ceiling | `word-ceiling` | word count per list item, against the rule's threshold |
| No em-dashes in headlines | `no-em-dash-headline` | scan headline text |
| No inflated-register words | `no-inflated-register` | the rule's wordlist, at the severity the rule assigns |
| Sentence-opener distribution | `opener-variety` | opener share per passage, against the rule's ceiling |
| **Palette passes CVD** | `separation-floor` | **shell out to `cvd-validate`** over `themes/*.json` — never reimplement CVD |

Each row's numbers, wordlist and severity are read from that rule in `method.md`. The linter carries
none of its own.

### 4b. Semantic — LLM judgment

The four calls that need understanding, applied by the agent against the rules loaded from
`method.md`. The canon marks many more rules `judgment`; these are the four the v1 review covers:

- **`one-message`** — is this one slide or two?
- **`assertion-headline`** — claim, or bare label?
- **`never-sole-channel`, hand-made visuals only** — generated figures carry the redundancy by
  construction (#10), so this targets pasted-in images.
- **The canon's judgment anti-slop rules** (`no-contrast-for-emphasis`, `no-reflexive-tricolon`,
  `no-hedging-or-boilerplate`, `rhythm-variety`, `concrete-over-abstract`) — the structural tells a
  wordlist cannot catch.

## 5. Review posture & output

- **Flag + suggest, human applies.** Each finding is surfaced **with a proposed fix** (rewrite a
  label into a claim, split a two-message slide, trim a bullet), but the skill **never silently
  rewrites**. The author — or the agent under the author's direction — accepts or rejects. This keeps
  the skill honest to the method: it can enforce structure, but it cannot decide your message for
  you.
- **Two-tier authority.**
  - **Mechanical linter = hard gate** — exit 0/1, CI-integratable, mirroring `cvd-validate` (#9).
    Objective violations block. One exception, declared by the canon rather than by the skill: a rule
    whose threshold line sets its own severity to `warning` reports without blocking. The canon says
    which rules those are and why — `no-inflated-register` is one, because
    `established-terminology` can legitimately override it.
  - **Semantic review = advisory** — LLM judgments are fallible, so they never block CI.
- **Output = one merged per-slide markdown report.** Findings grouped by slide, each tagged severity
  **error** (mechanical gate) or **warning** (advisory judgment) and **linked to the `method.md`
  rule** it enforces; semantic findings carry a suggested rewrite.

The report's shape is fixed in [`skill/SKILL.md`](../skill/SKILL.md), and
[`skill/fixtures/`](../skill/fixtures) is a deck built to fail it with the answer key beside it —
every planted violation, by slide and by rule, and which half of the review surfaces it.

## 6. Scaffold — a minimal starter

Scaffold stamps a **fresh, method-compliant Slidev deck** — distinct from the flagship (which
remains the teaching artifact per #10). It is deliberately lean: a clean start that is review-ready
from slide one, not a fully worked deck.

It stamps:

- a new Slidev deck wired to the in-repo **`slidev-theme-legible`**;
- the **`palette.json → tokens.css`** pipeline wired (Python emits the committed `tokens.css`, per
  #10 — one palette authority);
- **`cvd-validate` + the mechanical lint hooked as checks** (pre-commit / CI stub);
- **one skeleton slide per AE layout** — `cover`, `assertion-evidence`, `two-col-evidence`,
  `references` — as fill-in placeholders.

**Theme default = `neutral`.** The repo's default validated theme is `kuleuven` (with
non-endorsement), but scaffolding a *third party's* deck onto KU Leuven branding would be wrong;
since `neutral` is a one-file swap (#11), scaffold defaults to `neutral` and offers `kuleuven` as the
worked example. Slidev-only for v1.

Built in **#24** as the scaffold mode of [`skill/SKILL.md`](../skill/SKILL.md), which stamps
[`skill/template/`](../skill/template) — files rather than instructions, so what a stamp produces is
something a suite can be run over. It is: the deck wired to the theme by path, the palette at
`themes/palette.json` with the stylesheet `legible gen-css` emits from it committed beside it, both
checks as a pre-commit config and a workflow, and one skeleton slide per layout.

The palette is named for its job rather than for the palette it arrives holding, because everything
else in the stamped deck points at that path: choosing another one is a change to the file's
contents and to nothing that names it, which is the same "one palette authority" this document asks
of the theme.

**The acceptance bar is §5's own review**, and it is enforced rather than asserted:
`python/tests/test_scaffold.py` lints the template, so a template that would stamp an error fails
this repo's CI, and the same suite holds it to the theme's layouts and to the palette it copies. CI
also stamps the template and builds it, which is where the claim that the deck's own tokens outrank
the theme checkout's is settled — a stamped deck wearing the wrong brand would be visible in the
built CSS and nowhere else.

---

## Summary

| Facet | Decision |
|---|---|
| Packaging | One Claude Code `SKILL.md` in `skill/`; two modes; plugin + cross-agent deferred |
| Rule sourcing | Thin pointer — procedure in `SKILL.md`, rules + thresholds loaded from `method.md` |
| Review surface | Slidev-coupled (v1); format-agnostic + other-format templates later |
| Review engine | Hybrid — mechanical linter in `legible` (palette via `cvd-validate`) + LLM for 4 semantic checks |
| Review posture | Flag + suggest (human applies); two-tier gate/advisory; merged per-slide markdown report |
| Scaffold | Minimal Slidev starter, `neutral` default, review-ready from slide one |
