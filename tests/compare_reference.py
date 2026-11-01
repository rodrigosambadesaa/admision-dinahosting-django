"""Differential tests against the verified PHP and JavaScript original."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "reference"
PHP = REF / "PHP" / "fibonacci.php"
JS = REF / "JAVASCRIPT" / "fibonacci.js"
DJANGO = ROOT / "manage.py"

CASES = (
    ("ts:0", "ts:21"),
    ("ts:21", "ts:0"),
    ("ts:-50", "ts:-1"),
    ("ts:5", "ts:13"),
    ("ts:354224848179261915075", "ts:354224848179261915075"),
    ("ts:" + "9" * 150, "ts:" + "9" * 150),
    ("ts:+" + "9" * 256, "ts:+" + "9" * 256),
    ("2024-02-29 00:00:00", "2024-02-29 23:59:59"),
    ("2026-06-30 23:59:59", "2026-06-01 00:00:00"),
    ("ts:0", "1970-01-01 00:00:13"),
)

NODE_SCRIPT = r"""
const s = require(process.argv[1]);
const range = new s.CustomRangeProvider(process.argv[2], process.argv[3]).getRange();
const values = new s.FibonacciRangeResolver(new s.FibonacciSequenceGenerator()).resolve(range);
console.log(JSON.stringify({
    start: String(range.startTimestamp),
    end: String(range.endTimestamp),
    startLabel: range.startLabel,
    endLabel: range.endLabel,
    timezone: range.timezone,
    values: values.map(String)
}));
"""


def capture(args):
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True,
                          env={**os.environ, "DJANGO_DEBUG": "1"}, check=False)
    if proc.returncode:
        raise AssertionError(f"{args[0]} failed ({proc.returncode}): {proc.stderr}")
    return json.loads(proc.stdout)


def check_case(start, end, compare_php=True):
    from challenge.services import CustomRangeProvider, FibonacciRangeResolver
    date_range = CustomRangeProvider(start, end).get_range()
    values = [str(n) for n in FibonacciRangeResolver().resolve(date_range)]
    django = capture([sys.executable, str(DJANGO), "fibonacci", start, end])
    assert django["custom_range"]["range"] == date_range.to_dict()
    assert django["custom_range"]["fibonacci_timestamps"] == values
    js = capture(["node", "-e", NODE_SCRIPT, str(JS.resolve()), start, end])
    assert (js["start"], js["end"], js["values"]) == (
        str(date_range.start_timestamp), str(date_range.end_timestamp), values), (start, end, js)
    assert (js["startLabel"], js["endLabel"], js["timezone"]) == (
        date_range.start_label, date_range.end_label, date_range.timezone), (start, end, js)
    if compare_php:
        expected = capture(["php", str(PHP), start, end])
        assert django == expected, (
            f"CLI JSON mismatch for {start!r} and {end!r}\n"
            f"Django: {json.dumps(django, indent=2)}\n"
            f"PHP: {json.dumps(expected, indent=2)}"
        )


def main():
    assert PHP.is_file() and JS.is_file(), "Checkout original repository in reference/"
    for start, end in CASES:
        check_case(start, end)
        print(f"PASS PHP / JS / Django: {start} .. {end}")
    for value in ("0000-01-01 00:00:00", "0001-01-01 00:00:00",
                  "0000-02-29 00:00:00", "0099-12-31 23:59:59"):
        check_case(value, value, compare_php=False)
        print(f"PASS JS / Django: {value}")
    print(f"All {len(CASES) + 4} cross-language cases passed")


if __name__ == "__main__":
    main()
