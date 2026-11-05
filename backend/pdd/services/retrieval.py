import re
from dataclasses import dataclass
from typing import Iterable

from pdd.models import LawReference


TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)


def tokenize(value: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(value) if len(token) > 2}


@dataclass(frozen=True)
class RetrievalMatch:
    reference: LawReference
    score: float


def rank_references(question: str, references: Iterable[LawReference]) -> list[RetrievalMatch]:
    """Rank references with a transparent token-overlap baseline.

    This baseline is intentionally simple and deterministic. It gives the AI/ML
    owner a measurable point of comparison before embeddings or reranking are added.
    """
    question_tokens = tokenize(question)
    if not question_tokens:
        return []

    matches: list[RetrievalMatch] = []
    for reference in references:
        document_tokens = tokenize(f"{reference.title} {reference.text}")
        overlap = question_tokens & document_tokens
        if not overlap:
            continue
        score = len(overlap) / len(question_tokens)
        matches.append(RetrievalMatch(reference=reference, score=score))

    return sorted(matches, key=lambda match: (-match.score, match.reference.pk))

