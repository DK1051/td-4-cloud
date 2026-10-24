#!/usr/bin/env bash
# Shared by the three steps of .github/workflows/cannot-do.yml (sourced, not run on its own).
#
#   verdict WHAT EXIT_CODE OUTPUT WANTED_CODE...
#
# Each cannot-do check runs a command that Azure should REFUSE, captures its exit code and
# output, and calls verdict:
#   - exit code 0 (the command worked)            -> "FAIL: WHAT" and the job stops.
#   - failed, output holds a WANTED_CODE          -> "PASS".
#   - failed, but without any WANTED_CODE         -> "FAIL: failed for another reason: <codes>".
# Optional: set REQUIRE_ALSO to a text that must ALSO be in the output (used by check (a) to
# prove the refusal came from our location rule, not from something else).
#
# The captured text is only searched, never printed: it can contain object IDs that GitHub does
# not mask. Only short error codes are ever printed.
verdict() {
  local what="$1" code="$2" out="$3" want codes
  shift 3
  if [ "$code" -eq 0 ]; then
    echo "FAIL: $what"
    exit 1
  fi
  # Codes appear as "(Code)", "Code: Name" or "code": "Name"; a denied deployment nests them.
  # (|| true: no match is not an error, even under bash -e with pipefail.)
  codes=$(grep -oE '\([A-Za-z]+\)|(Error )?Code: *[A-Za-z]+|"code": *"[A-Za-z]+"' <<<"$out" | sort -u | tr '\n' ' ') || true
  for want in "$@"; do
    if grep -q "$want" <<<"$out"; then
      if [ -n "${REQUIRE_ALSO:-}" ] && ! grep -q "$REQUIRE_ALSO" <<<"$out"; then
        echo "FAIL: refused with $want, but not by the expected rule ($REQUIRE_ALSO). Codes: $codes"
        exit 1
      fi
      echo "PASS: $what (refused with $want)"
      return 0
    fi
  done
  echo "FAIL: failed for another reason: $codes"
  exit 1
}
