import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase

from pdd.models import LawReference


class ImportPddCommandTests(TestCase):
    def test_import_is_idempotent_and_reports_invalid_rows(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "pdd.jsonl"
            report = Path(directory) / "report.json"
            valid = {
                "article_number": "demo-1",
                "title": "Демо",
                "text": "  Проверочный   официальный текст. ",
                "source_url": "https://example.test/demo-1",
                "last_updated": "2026-01-01",
            }
            source.write_text(
                json.dumps(valid, ensure_ascii=False) + "\n" + "{invalid json}\n",
                encoding="utf-8",
            )

            call_command("import_pdd", source, report=report)
            call_command("import_pdd", source, report=report)

            self.assertEqual(LawReference.objects.count(), 1)
            self.assertEqual(
                LawReference.objects.get().text,
                "Проверочный официальный текст.",
            )
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(payload["updated"], 1)
            self.assertEqual(payload["skipped"][0]["line"], 2)

