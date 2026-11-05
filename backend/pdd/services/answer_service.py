from dataclasses import dataclass
from typing import Protocol

from django.conf import settings

from pdd.models import LawReference
from pdd.services.retrieval import rank_references


@dataclass(frozen=True)
class AnswerRequest:
    question: str
    user_id: int
    experience_level: str = "novice"
    language: str = "ru"


@dataclass(frozen=True)
class AnswerResult:
    status: str
    short_answer: str = ""
    explanation: str = ""
    official_clause: LawReference | None = None
    retrieval_score: float = 0.0
    guardrail_decision: str = "not_evaluated"
    guardrail_risk_score: float | None = None
    attempts: int = 1


class AnswerService(Protocol):
    def answer(self, request: AnswerRequest) -> AnswerResult: ...


class ExtractiveAnswerService:
    """Safe Sprint 1 fallback that only returns stored official source text."""

    def answer(self, request: AnswerRequest) -> AnswerResult:
        references = LawReference.objects.filter(language=request.language)
        matches = rank_references(request.question, references)
        if not matches or matches[0].score < settings.PDD_RETRIEVAL_MIN_SCORE:
            return AnswerResult(
                status="no_source",
                short_answer="Официальный пункт не найден.",
                explanation="Переформулируйте вопрос или уточните дорожную ситуацию.",
            )

        match = matches[0]
        return AnswerResult(
            status="answered",
            short_answer=match.reference.text,
            explanation=(
                "Это предварительный ответ без генерации: показан наиболее релевантный "
                "официальный пункт. Сверьте его с источником по ссылке."
            ),
            official_clause=match.reference,
            retrieval_score=match.score,
        )

