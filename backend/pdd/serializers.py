from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Answer, AnswerFeedback, LawReference, LearnerProfile, Question


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


class LearnerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = LearnerProfile
        fields = ("username", "email", "display_name", "experience_level", "exam_date")


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
            "id",
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


class AnswerFeedbackSerializer(serializers.ModelSerializer):
    answer_id = serializers.PrimaryKeyRelatedField(
        source="answer",
        queryset=Answer.objects.all(),
    )

    class Meta:
        model = AnswerFeedback
        fields = ("answer_id", "helpful", "comment")

    def validate_answer_id(self, answer):
        request = self.context["request"]
        if answer.question.user_id != request.user.id:
            raise serializers.ValidationError("You can rate only your own answer.")
        return answer

    def create(self, validated_data):
        feedback, _ = AnswerFeedback.objects.update_or_create(
            answer=validated_data["answer"],
            defaults={
                "user": self.context["request"].user,
                "helpful": validated_data["helpful"],
                "comment": validated_data.get("comment", ""),
            },
        )
        return feedback

