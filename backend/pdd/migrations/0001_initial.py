import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="LawReference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("article_number", models.CharField(max_length=64)),
                ("paragraph", models.CharField(blank=True, default="", max_length=64)),
                ("title", models.CharField(blank=True, default="", max_length=255)),
                ("text", models.TextField()),
                ("language", models.CharField(default="ru", max_length=8)),
                ("source_url", models.URLField(max_length=500)),
                ("last_updated", models.DateField()),
                ("source_hash", models.CharField(blank=True, default="", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["article_number", "paragraph"]},
        ),
        migrations.CreateModel(
            name="LearnerProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "experience_level",
                    models.CharField(
                        choices=[
                            ("novice", "Novice"),
                            ("intermediate", "Intermediate"),
                            ("experienced", "Experienced"),
                        ],
                        default="novice",
                        max_length=20,
                    ),
                ),
                ("exam_date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="learner_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pdd_questions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Answer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("answered", "Answered"),
                            ("no_source", "No source"),
                            ("blocked", "Blocked"),
                            ("error", "Error"),
                        ],
                        max_length=20,
                    ),
                ),
                ("short_answer", models.TextField(blank=True, default="")),
                ("explanation", models.TextField(blank=True, default="")),
                ("retrieval_score", models.FloatField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "law_reference",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="answers",
                        to="pdd.lawreference",
                    ),
                ),
                (
                    "question",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answer",
                        to="pdd.question",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="GuardrailLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "decision",
                    models.CharField(
                        choices=[
                            ("not_evaluated", "Not evaluated"),
                            ("allow", "Allow"),
                            ("block", "Block"),
                        ],
                        default="not_evaluated",
                        max_length=20,
                    ),
                ),
                ("risk_score", models.FloatField(blank=True, null=True)),
                ("attempts", models.PositiveSmallIntegerField(default=1)),
                ("ground_truth_label", models.BooleanField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "answer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="guardrail_logs",
                        to="pdd.answer",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="lawreference",
            constraint=models.UniqueConstraint(
                fields=("article_number", "paragraph", "language"),
                name="unique_law_reference",
            ),
        ),
    ]

