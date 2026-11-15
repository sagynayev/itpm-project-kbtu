from dataclasses import dataclass
from urllib.parse import urlparse

from pdd.models import LawReference
from pdd.services.retrieval import tokenize


TRUSTED_SOURCE_HOSTS = {"adilet.zan.kz", "old.adilet.zan.kz", "www.adilet.zan.kz"}


@dataclass(frozen=True)
class GuardrailResult:
    decision: str
    risk_score: float
    reasons: tuple[str, ...]


class GroundingGuardrail:
    """Block answers that cannot be traced to a trusted official clause."""

    threshold = 0.25

    def evaluate(self, answer: str, reference: LawReference | None) -> GuardrailResult:
        reasons: list[str] = []
        if reference is None:
            return GuardrailResult("block", 1.0, ("missing_reference",))

        source_host = (urlparse(reference.source_url).hostname or "").lower()
        if source_host not in TRUSTED_SOURCE_HOSTS:
            reasons.append("untrusted_source")

        answer_tokens = tokenize(answer)
        source_tokens = tokenize(reference.text)
        unsupported = answer_tokens - source_tokens
        unsupported_ratio = len(unsupported) / max(len(answer_tokens), 1)
        if unsupported_ratio > self.threshold:
            reasons.append("answer_not_grounded")

        risk_score = min(1.0, unsupported_ratio + (0.75 if "untrusted_source" in reasons else 0))
        return GuardrailResult("block" if reasons else "allow", risk_score, tuple(reasons))
