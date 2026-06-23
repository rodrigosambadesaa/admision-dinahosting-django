import json
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .services import (
    CustomRangeProvider,
    FibonacciRangeResolver,
    FibonacciSequenceGenerator,
    parse_range_boundary,
    sanitize_range_input,
)


class ServiceTests(TestCase):
    def test_sanitize_accepts_bigint_range(self):
        self.assertEqual(
            sanitize_range_input(" ts:12345678901234567890 "),
            "ts:12345678901234567890",
        )

    def test_custom_range_is_normalized_when_reversed(self):
        date_range = CustomRangeProvider(
            "2026-06-30 23:59:59",
            "2026-06-01 00:00:00",
        ).get_range()

        self.assertLessEqual(date_range.start_timestamp, date_range.end_timestamp)
        self.assertEqual(date_range.start_label, "2026-06-01 00:00:00 UTC")
        self.assertEqual(date_range.end_label, "2026-06-30 23:59:59 UTC")

    def test_bigint_boundary_keeps_synthetic_mode(self):
        boundary = parse_range_boundary("ts:12345678901234567890")

        self.assertEqual(boundary.timestamp, 12345678901234567890)
        self.assertEqual(boundary.timezone, "synthetic-bigint")

    def test_resolver_returns_values_inside_range(self):
        resolver = FibonacciRangeResolver(FibonacciSequenceGenerator())
        date_range = CustomRangeProvider("ts:0", "ts:21").get_range()

        self.assertEqual(resolver.resolve(date_range), [0, 1, 1, 2, 3, 5, 8, 13, 21])


class ViewTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertContains(response, "Prueba técnica Dinahosting")

    def test_fibonacci_form_returns_results(self):
        response = self.client.get(
            "/fibonacci/",
            {
                "start_date": "ts:0",
                "end_date": "ts:21",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rango personalizado")
        self.assertContains(response, "<li>21</li>", html=True)


class CommandTests(TestCase):
    def test_management_command_outputs_json(self):
        stdout = StringIO()
        call_command("fibonacci", "ts:0", "ts:21", stdout=stdout)
        payload = json.loads(stdout.getvalue())

        self.assertIn("Rango personalizado", payload)
        self.assertEqual(
            payload["Rango personalizado"]["fibonacci_timestamps"],
            ["0", "1", "1", "2", "3", "5", "8", "13", "21"],
        )
