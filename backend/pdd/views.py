from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Answer, GuardrailLog, LearnerProfile, Question
from .serializers import (
    AnswerSerializer,
    AskQuestionSerializer,
    QuestionHistorySerializer,
    RegisterSerializer,
)
from .services.answer_service import AnswerRequest, ExtractiveAnswerService


class HealthAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(
            request=request,
            username=request.data.get("username", ""),
            password=request.data.get("password", ""),
        )
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})


class QuestionAPIView(APIView):
    service_class = ExtractiveAnswerService

    @transaction.atomic
    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data["question"]
        question = Question.objects.create(user=request.user, text=text)
        profile, _ = LearnerProfile.objects.get_or_create(user=request.user)

        result = self.service_class().answer(
            AnswerRequest(
                question=text,
                user_id=request.user.id,
                experience_level=profile.experience_level,
            )
        )
        answer = Answer.objects.create(
            question=question,
            status=result.status,
            short_answer=result.short_answer,
            explanation=result.explanation,
            law_reference=result.official_clause,
            retrieval_score=result.retrieval_score,
        )
        GuardrailLog.objects.create(
            answer=answer,
            decision=result.guardrail_decision,
            risk_score=result.guardrail_risk_score,
            attempts=result.attempts,
        )
        return Response(AnswerSerializer(answer).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        questions = Question.objects.filter(user=request.user).select_related(
            "answer", "answer__law_reference"
        )[:50]
        return Response(QuestionHistorySerializer(questions, many=True).data)

