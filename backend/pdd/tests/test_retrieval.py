from datetime import date

from django.test import TestCase

from pdd.models import LawReference
from pdd.services.retrieval import rank_references


class RetrievalTests(TestCase):
    def setUp(self):
        self.priority = LawReference.objects.create(
            article_number="demo-1",
            title="Проезд перекрёстка",
            text="Демонстрационный текст про приоритет на перекрёстке.",
            source_url="https://example.test/demo-1",
            last_updated=date(2026, 1, 1),
        )
        self.parking = LawReference.objects.create(
            article_number="demo-2",
            title="Остановка и стоянка",
            text="Демонстрационный текст про место стоянки.",
            source_url="https://example.test/demo-2",
            last_updated=date(2026, 1, 1),
        )

    def test_best_matching_reference_is_first(self):
        matches = rank_references(
            "У кого приоритет на перекрёстке?",
            LawReference.objects.all(),
        )

        self.assertEqual(matches[0].reference, self.priority)
        self.assertGreater(matches[0].score, 0)

    def test_no_shared_terms_returns_no_matches(self):
        matches = rank_references("Совсем посторонний запрос", LawReference.objects.all())

        self.assertEqual(matches, [])

