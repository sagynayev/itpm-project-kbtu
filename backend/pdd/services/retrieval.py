import re
from collections import Counter
from dataclasses import dataclass
from math import log
from typing import Iterable

from pdd.models import LawReference


TOKEN_RE = re.compile(r"[\w-]+", re.UNICODE)
PRIMARY_CLAUSE_RE = re.compile(r"^\s*\d{1,3}(?:-\d+)?\.\s+")
OUT_OF_SCOPE_PATTERNS = (
    re.compile(r"\bкакой\s+штраф\b", re.IGNORECASE),
    re.compile(r"\bсколько\b.*\bштраф", re.IGNORECASE),
    re.compile(r"\bкак\s+(?:быстрее\s+)?получить\b.*\bудостоверен", re.IGNORECASE),
    re.compile(r"\bстоимост\w*\b.*\bэкзамен", re.IGNORECASE),
)
CHAPTER_HINTS = (
    (re.compile(r"светофор|стоп[- ]?лини", re.IGNORECASE), "Глава 5."),
    (re.compile(r"аварийн", re.IGNORECASE), "Глава 7."),
    (re.compile(r"автобус|маршрутн", re.IGNORECASE), "Глава 18."),
    (re.compile(r"обгон", re.IGNORECASE), "Глава 11."),
    (re.compile(r"парков|стоянк|остановк.*стоянк|стоянк.*остановк", re.IGNORECASE), "Глава 12."),
    (re.compile(r"железнодорож|переезд", re.IGNORECASE), "Глава 15."),
    (re.compile(r"автомагистрал", re.IGNORECASE), "Глава 16."),
    (re.compile(r"жилой зон|жилая зон", re.IGNORECASE), "Глава 17."),
    (re.compile(r"развор|перестро|задн\w* ход|сигнал поворот|маневр", re.IGNORECASE), "Глава 8."),
    (re.compile(r"пешеход|бел\w* трост", re.IGNORECASE), "Глава 14."),
    (re.compile(r"перекр[её]ст", re.IGNORECASE), "Глава 13."),
    (re.compile(r"полос|расположен\w* транспорт", re.IGNORECASE), "Глава 9."),
    (re.compile(r"скорост", re.IGNORECASE), "Глава 10."),
    (re.compile(r"ближн\w* свет|дальн\w* свет|светов\w* прибор", re.IGNORECASE), "Глава 19."),
    (re.compile(r"буксир", re.IGNORECASE), "Глава 20."),
    (re.compile(r"обуч\w* вожден|учебн\w* езд", re.IGNORECASE), "Глава 21."),
    (re.compile(r"пассажир|реб[её]н|удерживающ", re.IGNORECASE), "Глава 22."),
    (re.compile(r"груз", re.IGNORECASE), "Глава 23."),
    (re.compile(r"самокат|велосипед|гужев", re.IGNORECASE), "Глава 24."),
    (re.compile(r"опорно-двигатель|инвалидн\w* коляск", re.IGNORECASE), "Глава 25."),
    (re.compile(r"колонн.*видимост|видимост.*колонн", re.IGNORECASE), "Глава 26."),
    (re.compile(r"беспилот", re.IGNORECASE), "Глава 27."),
)
STOP_WORDS = {
    "как", "что", "где", "кто", "когда", "какой", "какая", "какие", "это", "или",
    "при", "для", "если", "мне", "надо", "можно",
    "нужно", "должен", "должна", "дороге", "дорога", "правило", "правила", "пдд",
}
RUSSIAN_SUFFIXES = (
    "ается", "яется", "иться", "аться", "яться", "ются", "ится", "ется",
    "иями", "ями", "ами", "ого", "ему", "ому", "ими", "ыми", "ена", "ены", "ено",
    "ий", "ый", "ая",
    "яя", "ое", "ее", "ие", "ые", "ую", "юю", "ам", "ям", "ах", "ях", "ов",
    "ев", "ом", "ем", "ой", "ей", "ить", "ать", "ять", "ет", "ют", "ит", "ят",
    "ы", "и", "а", "я", "у", "ю", "е", "о",
)


def normalize_token(token: str) -> str:
    token = token.lower().replace("ё", "е")
    for suffix in RUSSIAN_SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]
    return token


def tokenize(value: str) -> set[str]:
    return {
        normalize_token(token)
        for token in TOKEN_RE.findall(value)
        if len(token) > 2 and token.lower() not in STOP_WORDS
    }


@dataclass(frozen=True)
class RetrievalMatch:
    reference: LawReference
    score: float


def rank_references(question: str, references: Iterable[LawReference]) -> list[RetrievalMatch]:
    """Rank references with a transparent token-overlap baseline.

    This baseline is intentionally simple and deterministic. It gives the AI/ML
    owner a measurable point of comparison before embeddings or reranking are added.
    """
    if any(pattern.search(question) for pattern in OUT_OF_SCOPE_PATTERNS):
        return []

    question_tokens = tokenize(question)
    if not question_tokens:
        return []

    reference_list = list(references)
    chapter_hint = next((chapter for pattern, chapter in CHAPTER_HINTS if pattern.search(question)), None)
    if chapter_hint:
        hinted = [reference for reference in reference_list if chapter_hint in reference.title]
        if hinted:
            reference_list = hinted

    prepared = []
    document_frequency: Counter[str] = Counter()
    for reference in reference_list:
        title_tokens = tokenize(reference.title)
        document_tokens = tokenize(reference.text)
        prepared.append((reference, title_tokens, document_tokens))
        document_frequency.update(title_tokens | document_tokens)

    corpus_size = max(len(prepared), 1)
    weights = {
        token: log((corpus_size + 1) / (document_frequency[token] + 1)) + 1
        for token in question_tokens
    }
    total_weight = sum(weights.values()) or 1

    matches: list[RetrievalMatch] = []
    for reference, title_tokens, document_tokens in prepared:
        overlap = question_tokens & document_tokens
        title_overlap = question_tokens & title_tokens
        if not overlap and not title_overlap:
            continue
        body_recall = sum(weights[token] for token in overlap) / total_weight
        title_recall = sum(weights[token] for token in title_overlap) / total_weight
        score = body_recall + title_recall * 0.22
        if chapter_hint:
            score += 0.22
        if PRIMARY_CLAUSE_RE.match(reference.text):
            score += 0.035
        score = min(1.0, score)
        matches.append(RetrievalMatch(reference=reference, score=score))

    return sorted(matches, key=lambda match: (-match.score, match.reference.pk))

