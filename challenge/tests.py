import json
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .forms import FibonacciForm
from .services import (
    CurrentMonthRangeProvider, CurrentYearRangeProvider, CustomRangeProvider,
    FibonacciRangeResolver, FibonacciSequenceGenerator, build_fibonacci_sections,
    parse_range_boundary, parse_utc_datetime, sanitize_range_input,
)


class ServiceTests(TestCase):
    def test_strict_synthetic_inputs(self):
        self.assertEqual(sanitize_range_input(" ts:12345678901234567890 "), "ts:12345678901234567890")
        self.assertEqual(sanitize_range_input("ts:+" + "9" * 256), "ts:+" + "9" * 256)
        for invalid in ("", "   ", "ts:1e9", "ts:1\n", "ts:\u0661",
                        "ts:" + "9" * 257, "ts:" + "9" * 3000,
                        "2026-01-01T00:00:00", "<img src=x onerror=alert(1)>"):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                sanitize_range_input(invalid)

    def test_custom_range_normalization(self):
        r = CustomRangeProvider("2026-06-30 23:59:59", "2026-06-01 00:00:00").get_range()
        self.assertLessEqual(r.start_timestamp, r.end_timestamp)
        self.assertEqual(r.start_label, "2026-06-01 00:00:00 UTC")
        self.assertEqual(r.to_dict()["start"], "2026-06-01 00:00:00")

    def test_bigint_boundaries(self):
        b = parse_range_boundary("ts:12345678901234567890")
        self.assertEqual(b.timestamp, 12345678901234567890)
        self.assertEqual(b.timezone, "synthetic-bigint")
        with self.assertRaises(ValueError):
            parse_range_boundary("ts:" + "9" * 257)

    def test_fibonacci_inclusive(self):
        resolver = FibonacciRangeResolver(FibonacciSequenceGenerator())
        for start, end, values in [
            ("ts:0", "ts:21", [0, 1, 1, 2, 3, 5, 8, 13, 21]),
            ("ts:21", "ts:5", [5, 8, 13, 21]),
            ("ts:0", "ts:0", [0]),
            ("ts:1", "ts:1", [1, 1]),
            ("ts:-50", "ts:-1", []),
            ("ts:354224848179261915075", "ts:354224848179261915075", [354224848179261915075]),
        ]:
            with self.subTest(start=start, end=end):
                self.assertEqual(resolver.resolve(CustomRangeProvider(start, end).get_range()), values)

    def test_strict_utc_year_zero_and_leap_days(self):
        for date, expected in [
            ("1970-01-01 00:00:00", 0),
            ("0001-01-01 00:00:00", -62135596800),
            ("0000-01-01 00:00:00", -62167219200),
            ("0000-02-29 00:00:00", -62162121600),
            ("2024-02-29 00:00:00", 1709164800),
        ]:
            with self.subTest(date=date):
                self.assertEqual(parse_utc_datetime(date), expected)
        for invalid in ("2023-02-29 00:00:00", "1900-02-29 00:00:00",
                        "2024-02-30 00:00:00", "2024-13-01 00:00:00",
                        "2024-01-01 24:00:00", "2024-01-01T00:00:00"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_utc_datetime(invalid)

    def test_form_and_current_ranges(self):
        form = FibonacciForm({"start_date": "ts:+" + "9" * 256, "end_date": "ts:0"})
        self.assertTrue(form.is_valid(), form.errors)
        for provider in (CurrentMonthRangeProvider(), CurrentYearRangeProvider()):
            r = provider.get_range()
            self.assertLessEqual(r.start_timestamp, r.end_timestamp)
            self.assertEqual(r.timezone, "UTC")
        self.assertEqual([x["label"] for x in build_fibonacci_sections("ts:5", "ts:13")],
                         ["Mes actual", "Año actual", "Rango personalizado"])


class ViewTests(TestCase):
    def test_pages_and_security_headers(self):
        for url in ("/", "/fibonacci/", "/login/"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
                self.assertIn("form-action 'self'", response["Content-Security-Policy"])
                self.assertEqual(response["X-Frame-Options"], "DENY")
                self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_web_fibonacci_and_invalid_date(self):
        response = self.client.get("/fibonacci/", {"start_date": "ts:0", "end_date": "ts:21"})
        self.assertContains(response, "Rango personalizado")
        self.assertContains(response, "<li>21</li>", html=True)
        invalid = self.client.get("/fibonacci/", {
            "start_date": "2023-02-29 00:00:00", "end_date": "ts:21"
        })
        self.assertContains(invalid, "La fecha indicada no es válida.")
        self.assertNotContains(invalid, 'class="results-grid"')

    def test_login_is_local_demo(self):
        response = self.client.get("/login/")
        self.assertContains(response, "Demostración sin autenticación")
        self.assertContains(response, 'action="/login/"')
        self.assertNotContains(response, "dinahosting.com/login-usuarios")
        self.assertEqual(self.client.post("/login/", {"usuario": "fake@example.com",
                       "contrasena": "Fake1234"}).status_code, 405)


class CommandTests(TestCase):
    def run_cli(self, start, end):
        stdout = StringIO()
        call_command("fibonacci", start, end, stdout=stdout)
        return json.loads(stdout.getvalue())

    def test_php_json_contract(self):
        payload = self.run_cli("ts:0", "ts:21")
        self.assertEqual(list(payload), ["current_month", "current_year", "custom_range"])
        self.assertEqual(payload["custom_range"]["fibonacci_timestamps"],
                         ["0", "1", "1", "2", "3", "5", "8", "13", "21"])
        self.assertEqual(payload["custom_range"]["range"], {
            "start": "ts:0", "end": "ts:21", "timezone": "synthetic-bigint",
            "start_timestamp": "0", "end_timestamp": "21"
        })

    def test_reversed_date_cli(self):
        p = self.run_cli("2024-02-29 23:59:59", "2024-02-29 00:00:00")
        self.assertEqual(p["custom_range"]["range"]["start"], "2024-02-29 00:00:00")

    def test_invalid_cli(self):
        with self.assertRaises(CommandError):
            self.run_cli("ts:" + "1" * 257, "ts:0")
