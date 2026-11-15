import hashlib
import json
import re
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError

from pdd.models import LawReference


ADILET_URL = "https://old.adilet.zan.kz/rus/docs/V2300033003"
POINT_RE = re.compile(r"^\s*(\d{1,3})\.\s+")
DATE_RE = re.compile(r"\b(\d{2}\.\d{2}\.\d{4})\b")
SPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    return SPACE_RE.sub(" ", value.replace("\xa0", " ")).strip()


class AdiletRulesParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.capture: str | None = None
        self.capture_id = ""
        self.buffer: list[str] = []
        self.heading = "Общие положения"
        self.rows: list[dict[str, str]] = []
        self.active_text: list[str] = []
        self.current_point = ""

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "h3":
            self.capture = "h3"
            self.buffer = []
        elif tag == "p" and self.active and attributes.get("id", "").startswith("z"):
            self.capture = "p"
            self.capture_id = attributes["id"]
            self.buffer = []
        elif tag == "br" and self.capture:
            self.buffer.append(" ")

    def handle_data(self, data):
        if self.active:
            self.active_text.append(data)
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "h3" and self.capture == "h3":
            heading = normalize_text("".join(self.buffer))
            self.capture = None
            self.buffer = []
            if heading == "Правила дорожного движения":
                self.active = True
                self.active_text.append(heading)
            elif self.active and heading.startswith("Основные положения по допуску"):
                self.active = False
            elif self.active and heading:
                self.heading = heading
            return

        if tag == "p" and self.capture == "p":
            text = normalize_text("".join(self.buffer))
            anchor = self.capture_id
            self.capture = None
            self.capture_id = ""
            self.buffer = []
            if not text:
                return
            point_match = POINT_RE.match(text)
            if point_match:
                self.current_point = point_match.group(1)
            article_number = self.current_point or anchor
            self.rows.append(
                {
                    "article_number": article_number,
                    "paragraph": anchor,
                    "title": self.heading,
                    "text": text,
                    "source_url": f"{ADILET_URL}#{anchor}",
                    "language": "ru",
                }
            )

    def effective_date(self) -> date:
        parsed_dates = []
        for value in DATE_RE.findall(" ".join(self.active_text)):
            try:
                parsed_dates.append(datetime.strptime(value, "%d.%m.%Y").date())
            except ValueError:
                continue
        return max(parsed_dates, default=date.today())


def fetch_rules(url: str = ADILET_URL) -> tuple[list[dict[str, str]], date]:
    request = Request(url, headers={"User-Agent": "PDD-ChatBot/1.0 educational-project"})
    with urlopen(request, timeout=45) as response:
        encoding = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(encoding, errors="replace")
    parser = AdiletRulesParser()
    parser.feed(html)
    if len(parser.rows) < 100:
        raise CommandError("The official page structure changed or returned too few PDD clauses.")
    return parser.rows, parser.effective_date()


class Command(BaseCommand):
    help = "Fetch the current Russian PDD text from the official Adilet act and import it."

    def add_arguments(self, parser):
        parser.add_argument("--output", type=Path, help="Optional UTF-8 JSONL snapshot path.")
        parser.add_argument("--no-import", action="store_true", help="Create snapshot without database import.")
        parser.add_argument("--url", default=ADILET_URL)

    def handle(self, *args, **options):
        rows, effective_date = fetch_rules(options["url"])
        prepared = []
        for row in rows:
            item = {**row, "last_updated": effective_date.isoformat()}
            item["source_hash"] = hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
            prepared.append(item)

        output: Path | None = options["output"]
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("w", encoding="utf-8", newline="\n") as target:
                for item in prepared:
                    target.write(json.dumps(item, ensure_ascii=False) + "\n")

        created = updated = 0
        if not options["no_import"]:
            for item in prepared:
                _, was_created = LawReference.objects.update_or_create(
                    article_number=item["article_number"],
                    paragraph=item["paragraph"],
                    language=item["language"],
                    defaults={
                        "title": item["title"],
                        "text": item["text"],
                        "source_url": item["source_url"],
                        "last_updated": effective_date,
                        "source_hash": item["source_hash"],
                    },
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Adilet snapshot: {len(prepared)} clauses, effective {effective_date}; "
                f"created {created}, updated {updated}."
            )
        )
