import hashlib
import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from pdd.models import LawReference


REQUIRED_FIELDS = {"article_number", "title", "text", "source_url", "last_updated"}


class Command(BaseCommand):
    help = "Import cleaned official PDD clauses from a UTF-8 JSONL file."

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path)
        parser.add_argument("--report", type=Path)

    def handle(self, *args, **options):
        path: Path = options["path"]
        report_path: Path | None = options["report"]
        if not path.is_file():
            raise CommandError(f"Input file does not exist: {path}")

        report = {"source": str(path), "created": 0, "updated": 0, "skipped": []}
        with path.open("r", encoding="utf-8") as source:
            for line_number, raw_line in enumerate(source, start=1):
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                try:
                    payload = json.loads(raw_line)
                    missing = sorted(REQUIRED_FIELDS - payload.keys())
                    if missing:
                        raise ValueError(f"missing fields: {', '.join(missing)}")
                    text = " ".join(str(payload["text"]).split())
                    if not text:
                        raise ValueError("text must not be empty")
                    last_updated = date.fromisoformat(str(payload["last_updated"]))
                    source_hash = payload.get("source_hash") or hashlib.sha256(
                        text.encode("utf-8")
                    ).hexdigest()
                    _, created = LawReference.objects.update_or_create(
                        article_number=str(payload["article_number"]).strip(),
                        paragraph=str(payload.get("paragraph", "")).strip(),
                        language=str(payload.get("language", "ru")).strip(),
                        defaults={
                            "title": str(payload["title"]).strip(),
                            "text": text,
                            "source_url": str(payload["source_url"]).strip(),
                            "last_updated": last_updated,
                            "source_hash": source_hash,
                        },
                    )
                    report["created" if created else "updated"] += 1
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    report["skipped"].append({"line": line_number, "reason": str(exc)})

        if report_path:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {report['created']}, updated {report['updated']}, "
                f"skipped {len(report['skipped'])}."
            )
        )

