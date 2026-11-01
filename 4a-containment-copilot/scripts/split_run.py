"""Split runs/<model>/raw.md into runs/<model>/INC-nn.md, one file per incident.

Usage: python 4a-containment-copilot/scripts/split_run.py <model> [--base DIR]

It stops with an error if a block has no "=== END ===", if the same incident
appears twice, or if a new "=== INC-nn ===" starts before the last one ended.
If incidents/INC-*.md exist, it also stops when an incident has no block or a
block has no incident file.
It also replaces GUID-shaped strings (8-4-4-4-12 hex digits) with
<guid-redacted> in raw.md and in every output file.
"""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_BASE = Path(__file__).resolve().parents[1]

START_RE = re.compile(r"^\s*=== (INC-\d+) ===\s*$")
END_RE = re.compile(r"^\s*=== END ===\s*$")
# 8-4-4-4-12 hex digits, any letter case.
GUID_RE = re.compile(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}")
REDACTION = "<guid-redacted>"


class SplitError(Exception):
    """Raised when raw.md does not have the expected block format."""


def redact_guids(text):
    """Return (text with GUID-shaped strings replaced, number replaced)."""
    return GUID_RE.subn(REDACTION, text)


def split_blocks(text):
    """Return {incident id: block text} from the raw model output."""
    blocks = {}
    current_id = None
    current_lines = []
    for number, line in enumerate(text.splitlines(), start=1):
        start = START_RE.match(line)
        if start:
            if current_id is not None:
                raise SplitError(
                    f"line {number}: {start.group(1)} starts before {current_id} ended"
                )
            if start.group(1) in blocks:
                raise SplitError(f"line {number}: duplicate block for {start.group(1)}")
            current_id = start.group(1)
            current_lines = [line]
        elif END_RE.match(line):
            if current_id is None:
                raise SplitError(f"line {number}: '=== END ===' without a start")
            current_lines.append(line)
            blocks[current_id] = "\n".join(current_lines) + "\n"
            current_id = None
            current_lines = []
        elif current_id is not None:
            current_lines.append(line)
    if current_id is not None:
        raise SplitError(f"{current_id} has no '=== END ==='")
    if not blocks:
        raise SplitError("no '=== INC-nn ===' blocks found")
    return blocks


def check_against_incidents(blocks, base):
    """If incidents/INC-*.md exist, the blocks must match them exactly."""
    expected = {p.stem for p in (Path(base) / "incidents").glob("INC-*.md")}
    if not expected:
        return  # no incident files to compare with
    missing = sorted(expected - set(blocks))
    extra = sorted(set(blocks) - expected)
    if missing:
        raise SplitError("no block for " + ", ".join(missing))
    if extra:
        raise SplitError("block for an incident with no file: " + ", ".join(extra))


def split_run(model, base=DEFAULT_BASE):
    """Split runs/<model>/raw.md. Returns (list of files written, redaction count)."""
    run_dir = Path(base) / "runs" / model
    raw_path = run_dir / "raw.md"
    if not raw_path.is_file():
        raise SplitError(f"{raw_path} not found")
    try:
        raw_text, count = redact_guids(raw_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as err:
        raise SplitError(f"{raw_path} is not valid UTF-8 text") from err
    blocks = split_blocks(raw_text)  # raises before anything is written
    check_against_incidents(blocks, base)
    raw_path.write_text(raw_text, encoding="utf-8")
    written = []
    for incident_id, block in blocks.items():
        path = run_dir / f"{incident_id}.md"
        path.write_text(redact_guids(block)[0], encoding="utf-8")
        written.append(path)
    return written, count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("model", help="model folder name under runs/, e.g. haiku")
    parser.add_argument(
        "--base", default=str(DEFAULT_BASE), help="4a folder holding runs/"
    )
    args = parser.parse_args(argv)
    try:
        written, count = split_run(args.model, args.base)
    except SplitError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"Wrote {len(written)} incident files for {args.model}")
    print(f"GUID-shaped strings redacted: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
