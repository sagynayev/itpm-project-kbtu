from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Answer, LawReference, LearnerProfile, Question


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already in use.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        LearnerProfile.objects.create(user=user)
        return user


class LawReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawReference
        fields = (
            "id",
            "article_number",
            "paragraph",
            "title",
            "text",
            "source_url",
            "last_updated",
        )


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=3, max_length=2000, trim_whitespace=True)


class AnswerSerializer(serializers.ModelSerializer):
    official_clause = LawReferenceSerializer(source="law_reference", read_only=True)
    guardrail = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            "status",
            "short_answer",
            "explanation",
            "official_clause",
            "retrieval_score",
            "guardrail",
        )

    def get_guardrail(self, obj: Answer) -> dict:
        log = obj.guardrail_logs.order_by("-created_at").first()
        if log is None:
            return {"decision": "not_evaluated", "risk_score": None, "attempts": 1}
        return {
            "decision": log.decision,
            "risk_score": log.risk_score,
            "attempts": log.attempts,
        }


class QuestionHistorySerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "created_at", "answer")

