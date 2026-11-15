import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pdd.models import LawReference
from pdd.services.retrieval import rank_references


class Command(BaseCommand):
    help = "Evaluate top-1 retrieval against question/chapter labels in CSV."

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path)

    def handle(self, *args, **options):
        path: Path = options["path"]
        if not path.is_file():
            raise CommandError(f"Evaluation file does not exist: {path}")

        references = list(LawReference.objects.all())
        if not references:
            raise CommandError("Import the PDD snapshot before evaluation.")

        results = []
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                matches = rank_references(row["question"], references)
                best = matches[0] if matches and matches[0].score >= settings.PDD_RETRIEVAL_MIN_SCORE else None
                expected = row["expected_chapter"].strip()
                correct = best is None if not expected else bool(best and expected in best.reference.title)
                results.append((row, best, correct))

        correct_count = sum(1 for _, _, correct in results if correct)
        accuracy = correct_count / len(results) if results else 0
        self.stdout.write(f"Top-1 chapter accuracy: {correct_count}/{len(results)} = {accuracy:.1%}")
        for row, best, correct in results:
            if correct:
                continue
            actual = "no_source" if best is None else f"{best.reference.title} / point {best.reference.article_number} / {best.score:.2f}"
            self.stdout.write(
                self.style.WARNING(
                    f"{row['id']}: expected {row['expected_chapter'] or 'no_source'}, got {actual}"
                )
            )
