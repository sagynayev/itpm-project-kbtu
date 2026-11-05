# Official PDD data contract

The importer accepts UTF-8 JSON Lines: one JSON object per line.

Required fields:

```json
{
  "article_number": "string, stable and unique within the source version",
  "title": "string",
  "text": "non-empty official clause text",
  "source_url": "URL of the official publication",
  "last_updated": "YYYY-MM-DD"
}
```

Optional fields:

```json
{
  "paragraph": "string",
  "language": "ru",
  "source_hash": "sha256 hex digest"
}
```

Import rules:

1. Use the currently valid official text as the source of truth.
2. Preserve clause/article numbers and cross-references.
3. Normalize whitespace but do not paraphrase legal text.
4. Calculate `source_hash` after normalization when the producer can do so.
5. Re-import by `(article_number, paragraph, language)` must update, not duplicate.
6. Invalid rows are skipped and reported with the line number and reason.
7. A human checks at least 20 random imported rows against the official publication.

