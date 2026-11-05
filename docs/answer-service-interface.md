# Answer-service interface

Owner: Alimzhan (AI/ML). Consumers: Django API and React UI.

The web layer calls a service with this logical input:

```json
{
  "question": "string",
  "user_id": 42,
  "experience_level": "novice",
  "language": "ru"
}
```

The service returns:

```json
{
  "status": "answered",
  "short_answer": "string",
  "explanation": "string",
  "official_clause": {
    "id": 17,
    "article_number": "13.4",
    "title": "string",
    "text": "string",
    "source_url": "https://official.example/...",
    "last_updated": "2026-01-01"
  },
  "retrieval_score": 0.73,
  "guardrail": {
    "decision": "allow",
    "risk_score": 0.14,
    "attempts": 1
  }
}
```

Valid `status` values are `answered`, `no_source`, `blocked`, and `error`. If no sufficiently relevant official clause exists, the service must return `no_source` and empty answer fields. It must not generate a legal answer from model memory.

For Sprint 1, `ExtractiveAnswerService` returns a selected official clause with a deterministic explanation and leaves `guardrail` as `not_evaluated`. Sprint 2 may replace it with RAG, but it must keep the response contract stable.

