"""Write runs/batch-prompt.md: the instruction plus the incident files to read.

Usage: python 4a-containment-copilot/scripts/make_batch.py [--base DIR]

DIR (default: the 4a-containment-copilot folder) must contain incidents/INC-*.md.
The paths in the prompt are relative to the repository root, because that is
where the copilot runs.
"""

import argparse
import sys
from pathlib import Path

DEFAULT_BASE = Path(__file__).resolve().parents[1]
REPO_ROOT = DEFAULT_BASE.parent

INSTRUCTION = """\
Draft a dry-run containment checklist for each incident file listed below.
Follow your standing instructions (five actions in order, every command line
starting with "# DRY RUN:", the === INC-nn === / === END === format, and the
final never-touch line).

Read ONLY these files, and nothing else:
"""


class NoIncidentsError(Exception):
    """Raised when there are no incidents/INC-*.md files to put in the prompt."""


def find_incidents(base):
    """Return the sorted list of incident files under base/incidents."""
    return sorted(Path(base).glob("incidents/INC-*.md"))


def display_path(path, base):
    """Path as shown in the prompt: relative to the repo root when possible."""
    path = Path(path).resolve()
    for root in (REPO_ROOT, Path(base).resolve()):
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            continue
    return path.as_posix()


def build_prompt(incidents, base):
    lines = [INSTRUCTION]
    for path in incidents:
        lines.append("- " + display_path(path, base))
    return "\n".join(lines) + "\n"


def make_batch(base=DEFAULT_BASE):
    """Write runs/batch-prompt.md under base and return its path."""
    incidents = find_incidents(base)
    if not incidents:
        raise NoIncidentsError(
            f"No incident files found at {Path(base) / 'incidents'}/INC-*.md. "
            "Eojin writes these (INC-01.md ... INC-05.md); the batch prompt "
            "cannot be made until they exist."
        )
    out = Path(base) / "runs" / "batch-prompt.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_prompt(incidents, base), encoding="utf-8")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--base", default=str(DEFAULT_BASE), help="folder holding incidents/"
    )
    args = parser.parse_args(argv)
    try:
        out = make_batch(args.base)
    except NoIncidentsError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"Wrote {out}")
    print(
        "REMINDER: move answer-keys/ out of the repo (for example to /tmp) before "
        "each run and put it back afterwards, so the copilot cannot read it."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
