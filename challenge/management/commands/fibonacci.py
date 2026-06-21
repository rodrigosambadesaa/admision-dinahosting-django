import json

from django.core.management.base import BaseCommand, CommandError

from challenge.services import build_fibonacci_sections, sanitize_range_input


class Command(BaseCommand):
    help = "Calcula timestamps Fibonacci para el mes actual, el año actual y un rango personalizado."

    def add_arguments(self, parser):
        parser.add_argument("start_date", type=str)
        parser.add_argument("end_date", type=str)

    def handle(self, *args, **options):
        try:
            start_date = sanitize_range_input(options["start_date"])
            end_date = sanitize_range_input(options["end_date"])
            sections = build_fibonacci_sections(start_date, end_date)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        payload = {}
        for section in sections:
            payload[section["label"]] = {
                "range": section["range"].to_dict(),
                "fibonacci_timestamps": [str(value) for value in section["values"]],
            }

        self.stdout.write(json.dumps(payload, indent=4, ensure_ascii=False))
