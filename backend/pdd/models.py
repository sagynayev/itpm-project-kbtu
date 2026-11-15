from django.conf import settings
from django.db import models


class LearnerProfile(models.Model):
    class ExperienceLevel(models.TextChoices):
        NOVICE = "novice", "Novice"
        INTERMEDIATE = "intermediate", "Intermediate"
        EXPERIENCED = "experienced", "Experienced"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_profile",
    )
    display_name = models.CharField(max_length=120, blank=True, default="")
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.NOVICE,
    )
    exam_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username}: {self.experience_level}"


class LawReference(models.Model):
    article_number = models.CharField(max_length=64)
    paragraph = models.CharField(max_length=64, blank=True, default="")
    title = models.CharField(max_length=255, blank=True, default="")
    text = models.TextField()
    language = models.CharField(max_length=8, default="ru")
    source_url = models.URLField(max_length=500)
    last_updated = models.DateField()
    source_hash = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["article_number", "paragraph", "language"],
                name="unique_law_reference",
            )
        ]
        ordering = ["article_number", "paragraph"]

    def __str__(self) -> str:
        suffix = f".{self.paragraph}" if self.paragraph else ""
        return f"{self.article_number}{suffix} {self.title}".strip()


class Question(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pdd_questions",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Answer(models.Model):
    class Status(models.TextChoices):
        ANSWERED = "answered", "Answered"
        NO_SOURCE = "no_source", "No source"
        BLOCKED = "blocked", "Blocked"
        ERROR = "error", "Error"

    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name="answer",
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    short_answer = models.TextField(blank=True, default="")
    explanation = models.TextField(blank=True, default="")
    law_reference = models.ForeignKey(
        LawReference,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="answers",
    )
    retrieval_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class GuardrailLog(models.Model):
    class Decision(models.TextChoices):
        NOT_EVALUATED = "not_evaluated", "Not evaluated"
        ALLOW = "allow", "Allow"
        BLOCK = "block", "Block"

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="guardrail_logs")
    decision = models.CharField(
        max_length=20,
        choices=Decision.choices,
        default=Decision.NOT_EVALUATED,
    )
    risk_score = models.FloatField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=1)
    ground_truth_label = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AnswerFeedback(models.Model):
    answer = models.OneToOneField(
        Answer,
        on_delete=models.CASCADE,
        related_name="feedback",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="answer_feedback",
    )
    helpful = models.BooleanField()
    comment = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

