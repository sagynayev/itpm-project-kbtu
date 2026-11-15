from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from pdd.models import LawReference, LearnerProfile


User = get_user_model()


class QuestionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="strong-pass-123")
        LearnerProfile.objects.create(user=self.user)
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.reference = LawReference.objects.create(
            article_number="demo-1",
            title="Приоритет на перекрёстке",
            text="Демонстрационный текст: приоритет на перекрёстке определяется тестовым пунктом.",
            source_url="https://old.adilet.zan.kz/rus/docs/V2300033003#demo-1",
            last_updated=date(2026, 1, 1),
        )

    def test_answer_is_grounded_in_reference(self):
        response = self.client.post(
            "/api/questions/",
            {"question": "Как определяется приоритет на перекрёстке?"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "answered")
        self.assertEqual(response.data["official_clause"]["id"], self.reference.id)
        self.assertEqual(response.data["guardrail"]["decision"], "allow")

    def test_unknown_question_returns_no_source(self):
        response = self.client.post(
            "/api/questions/",
            {"question": "Совсем посторонний запрос"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "no_source")
        self.assertIsNone(response.data["official_clause"])

    def test_question_requires_authentication(self):
        self.client.credentials()
        response = self.client.post(
            "/api/questions/",
            {"question": "Как определяется приоритет?"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_profile_can_be_updated(self):
        response = self.client.patch(
            "/api/profile/",
            {"display_name": "Алимжан", "experience_level": "intermediate"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["display_name"], "Алимжан")
        self.assertEqual(response.data["experience_level"], "intermediate")

    def test_user_can_rate_own_answer(self):
        answer_response = self.client.post(
            "/api/questions/",
            {"question": "Как определяется приоритет на перекрёстке?"},
            format="json",
        )
        response = self.client.post(
            "/api/feedback/",
            {"answer_id": answer_response.data["id"], "helpful": True, "comment": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data["helpful"])


class PublicStatsTests(APITestCase):
    def test_stats_are_public(self):
        response = self.client.get("/api/public/stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["source"], "ИПС Әділет")
        self.assertEqual(response.data["guardrail_mode"], "official-source-only")

