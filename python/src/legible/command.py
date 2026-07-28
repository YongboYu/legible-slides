"""`legible` — the commands an author of a deck runs.

Two console scripts, on purpose. `cvd-validate` stands alone because it is the artifact external
theme authors are pointed at, and a stranger's palette is all it needs. Everything else this
package does acts on a *deck* — emitting its tokens, linting its slides, and drawing its figures in
due course — and hangs off this one command instead.

Each subcommand stays a thin shell over the package's public functions: what a stylesheet contains
is ``gen_css``' business and what breaks a rule is ``lint``'s, and what follows here is only where
the bytes go and what the exit code says about them.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from itertools import groupby
from pathlib import Path

from legible.css import gen_css
from legible.lint import ERROR, WARNING, Finding, LintReport, lint
from legible.method import DECIDERS, MethodError, Rule, read_canon, rules
from legible.palette import PaletteError, load_palette

#: 0 says the stylesheet is current — just written, or already matching its palette. 1 says it is
#: stale, the shape `ruff format --check` has and the one the CI gate keys on. 2 keeps the meaning
#: it has in ``cli`` and in argparse: nothing was measured, because the arguments or the theme
#: behind them could not be read, and a file nobody generated makes no claim about being stale.
CURRENT, STALE, NOT_GENERATED = 0, 1, 2

#: The same three, for a deck: clean, broke a rule, or was never read. `lint` is a hard gate
#: (``docs/agent-skill-contract.md`` §5), so 1 is what blocks a merge — and only a finding the
#: canon calls an error reaches it. A warning is reported and costs nothing.
CLEAN, VIOLATIONS, NOT_LINTED = 0, 1, 2

#: Two of the three, for the canon: printed, or asked for something the canon does not carry.
#: There is no middle code, because quoting a rule is not a check and nothing about it can fail.
QUOTED, NOT_QUOTED = 0, 2

#: Column widths for the severity and the rule, so a report of many findings reads as a table. The
#: severity column is measured off the severities themselves; the rule column off the rules a run
#: actually found, because the canon may grow one longer than any here today.
_SEVERITY_WIDTH = max(len(severity) for severity in (ERROR, WARNING)) + 2


def main(argv: Sequence[str] | None = None) -> int:
    """Run one subcommand. Returns the process exit code."""
    args = _parser().parse_args(argv)
    return args.run(args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="legible",
        description="Build-time commands for a deck: the palette's tokens, and what follows them.",
    )
    subcommands = parser.add_subparsers(metavar="COMMAND", required=True)

    gen_css_parser = subcommands.add_parser(
        "gen-css",
        help="emit a theme's colours as CSS custom properties",
        description=(
            "Emit a theme's colours as the deck's CSS custom properties. The result is committed "
            "and regenerated when the palette changes, like a lockfile, so the deck build imports "
            "it rather than invoking Python."
        ),
    )
    gen_css_parser.add_argument("theme", metavar="THEME", type=Path, help="the theme JSON file")
    gen_css_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write the stylesheet here instead of to stdout, creating its directory if needed",
    )
    gen_css_parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "write nothing; exit 1 if the file at --output is not what this theme emits today. "
            "This is the CI gate against a committed stylesheet going stale."
        ),
    )
    gen_css_parser.set_defaults(run=_gen_css, parser=gen_css_parser)

    lint_parser = subcommands.add_parser(
        "lint",
        help="check a deck against the rules the canon decides by script",
        description=(
            "Check a Slidev deck against every rule docs/method.md marks as decided by script — "
            "the bullet and word ceilings, em-dashes in a headline, inflated register, the "
            "sentence-opener share, and, for each theme named, the separation floor. Exits 0 when "
            "clean, 1 on any violation, and 2 if the deck or a theme could not be read. Findings "
            "the canon marks a warning are reported and never change the exit code."
        ),
    )
    lint_parser.add_argument("deck", metavar="DECK", type=Path, help="the deck's slides markdown")
    lint_parser.add_argument(
        "--theme",
        dest="themes",
        metavar="THEME",
        type=Path,
        action="append",
        default=[],
        help=(
            "check this theme's palette too, by running cvd-validate over it; repeatable. A deck "
            "does not record which palette it wears, so naming none checks the slides alone."
        ),
    )
    lint_parser.add_argument(
        "--json",
        action="store_true",
        help="emit the report verbatim as JSON instead of the per-slide report",
    )
    lint_parser.set_defaults(run=_lint, parser=lint_parser)

    rules_parser = subcommands.add_parser(
        "rules",
        help="print the method's rules as docs/method.md states them",
        description=(
            "Print rules of the method, verbatim from docs/method.md — the canon, and the only "
            "place any of them is stated. This is how a reviewer loads what it reviews against "
            "rather than carrying a copy that can drift, and it reads the canon the package was "
            "built around, so it works with no checkout on the machine. Name rules to print "
            "those; name none and pass a filter to let the canon say which they are. Exits 0 "
            "having printed, and 2 if the canon could not be read or carries nothing that was "
            "asked for."
        ),
    )
    rules_parser.add_argument(
        "rules",
        metavar="RULE",
        nargs="*",
        help="a rule's stable ID, as the canon writes it in backticks; repeatable",
    )
    rules_parser.add_argument(
        "--decided-by",
        choices=DECIDERS,
        help=(
            "only rules the canon marks this way. A mixed rule names both, so it matches either. "
            "This is the seam the review is built along: `script` is what `legible lint` settles."
        ),
    )
    rules_parser.add_argument(
        "--section",
        metavar="SECTION",
        help="only rules stated under this section of the canon, named as in `voice`",
    )
    rules_parser.add_argument(
        "--json",
        action="store_true",
        help="emit each rule as an object — its ID, section, seam, thresholds and markdown",
    )
    rules_parser.set_defaults(run=_rules, parser=rules_parser)

    return parser


def _gen_css(args: argparse.Namespace) -> int:
    if args.check and args.output is None:
        args.parser.error("--check needs --output: a stylesheet on stdout is nothing to compare")

    try:
        palette = load_palette(args.theme)
    except (OSError, PaletteError) as error:
        print(f"legible gen-css: {error}", file=sys.stderr)
        return NOT_GENERATED

    stylesheet = gen_css(palette)

    if args.output is None:
        print(stylesheet, end="")
        return CURRENT

    if args.check:
        return _report_if_stale(stylesheet, args.output, args.theme)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Newlines fixed rather than translated: the file is committed, and a diff that says only
    # "generated on Windows" is the one thing a lockfile must never produce.
    args.output.write_text(stylesheet, encoding="utf-8", newline="\n")
    print(f"legible gen-css: wrote {args.output}")
    return CURRENT


def _lint(args: argparse.Namespace) -> int:
    try:
        report = lint(args.deck, themes=args.themes)
    except OSError as error:
        print(f"legible lint: {error}", file=sys.stderr)
        return NOT_LINTED

    print(_as_json(report) if args.json else _as_report(args.deck, report, args.themes))
    for unchecked in report.unchecked:
        # On stderr, and never as a finding: the deck did not break a rule here, and a theme
        # nobody could measure makes no claim about its colours either way.
        print(f"legible lint: {unchecked.detail}", file=sys.stderr)

    # A rule broken outranks a theme that went unmeasured — it is the more actionable of the two,
    # and both are non-zero, so a gate blocks either way. The same order `cvd-validate` takes.
    if not report.passed:
        return VIOLATIONS
    return NOT_LINTED if report.unchecked else CLEAN


def _rules(args: argparse.Namespace) -> int:
    try:
        canon = read_canon()
    except MethodError as error:
        print(f"legible rules: {error}", file=sys.stderr)
        return NOT_QUOTED

    stated = rules(canon)
    unknown = [named for named in args.rules if named not in {rule.id for rule in stated}]
    if unknown:
        # Named and absent is its own failure, and a different one from a filter that matched
        # nothing: a reviewer asking for a rule by ID has a stale ID, and should hear which.
        print(f"legible rules: the canon carries no rule {_quoted(unknown)}", file=sys.stderr)
        return NOT_QUOTED

    selected = rules(canon, decided_by=args.decided_by, section=args.section)
    if args.rules:
        selected = tuple(rule for rule in selected if rule.id in set(args.rules))

    if not selected:
        # Loudly, because the caller is a review: one that loaded no rule would find no fault and
        # read as a pass.
        print(f"legible rules: the canon carries nothing {_selection(args)}", file=sys.stderr)
        return NOT_QUOTED

    print(_as_rules_json(selected) if args.json else _as_rules(selected))
    return QUOTED


def _as_rules(selected: Sequence[Rule]) -> str:
    """The rules as the canon writes them, in the order it writes them.

    Verbatim markdown and nothing around it: a rule paraphrased on the way out is a second copy of
    it, which is the one thing ``docs/agent-skill-contract.md`` §2 asks this command not to be.
    """
    return "\n\n".join(rule.text for rule in selected)


def _as_rules_json(selected: Sequence[Rule]) -> str:
    return json.dumps(
        [
            {
                "id": rule.id,
                "section": rule.section,
                "statement": rule.statement,
                "decided_by": list(rule.decided_by),
                "thresholds": dict(rule.thresholds),
                "text": rule.text,
            }
            for rule in selected
        ]
    )


def _selection(args: argparse.Namespace) -> str:
    """The selection that matched nothing, said back the way it was asked for."""
    asked = (
        f"in section {args.section}" if args.section else "",
        f"decided by {args.decided_by}" if args.decided_by else "",
        f"among {_quoted(args.rules)}" if args.rules else "",
    )
    return " ".join(part for part in asked if part)


def _quoted(names: Sequence[str]) -> str:
    return ", ".join(f"`{name}`" for name in names)


def _as_report(deck: Path, report: LintReport, themes: Sequence[Path]) -> str:
    """The findings as an author reads them: grouped by slide, each tagged and named by its rule."""
    errors = sum(1 for finding in report.findings if finding.severity == ERROR)
    verdict = "PASS" if report.passed else "FAIL"

    lines = [f"{verdict}  {deck} — {_tally(errors, len(report.findings) - errors)}"]
    if not themes:
        # Said out loud rather than left to be inferred from a report with no palette line in it.
        # A deck does not record which palette it wears, so silence here would read as a pass.
        lines.append("      no theme named, so `separation-floor` was not checked")

    width = max((len(finding.rule) for finding in report.findings), default=0) + 2
    for slide, findings in groupby(report.findings, key=lambda finding: finding.slide):
        lines.append("")
        lines.append(f"  {'deck' if slide is None else f'slide {slide}'}")
        lines.extend(f"    {_as_line(finding, width)}" for finding in findings)
    return "\n".join(lines)


def _as_line(finding: Finding, width: int) -> str:
    return f"{finding.severity:<{_SEVERITY_WIDTH}}{finding.rule:<{width}}{finding.message}"


def _tally(errors: int, warnings: int) -> str:
    if not errors and not warnings:
        return "no findings"
    return f"{_count(errors, 'error')}, {_count(warnings, 'warning')}"


def _count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"


def _as_json(report: LintReport) -> str:
    """The report verbatim — every field under its own name, and nothing added."""
    data = asdict(report)
    data["findings"] = [finding._asdict() for finding in report.findings]
    data["unchecked"] = [unchecked._asdict() for unchecked in report.unchecked]
    return json.dumps(data)


def _report_if_stale(stylesheet: str, output: Path, theme: Path) -> int:
    """Compare, and never write — a gate that repairs what it measures can only ever pass."""
    # Reading translates newlines back, so a checkout that materialised CRLF still compares equal:
    # this gate is a claim about the palette, not about how the file reached the disk.
    committed = output.read_text(encoding="utf-8") if output.is_file() else None
    if committed == stylesheet:
        print(f"legible gen-css: {output} is current")
        return CURRENT

    state = "is stale" if committed is not None else "has not been generated"
    print(
        f"legible gen-css: {output} {state}. Regenerate it and commit the result:\n"
        f"    legible gen-css {theme} --output {output}",
        file=sys.stderr,
    )
    return STALE
