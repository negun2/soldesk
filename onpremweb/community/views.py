# onpremweb/community/views.py
from rest_framework import ( viewsets, generics )
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import (
    Analysis, Board, Recommend, Feedback, BestBoard,
    Notice, Reply, Score, ErrorLog
)
from .serializers import (
    AnalysisSerializer, BoardSerializer, RecommendSerializer,
    FeedbackSerializer, BestBoardSerializer, NoticeSerializer,
    ReplySerializer, ScoreSerializer, ErrorLogSerializer, RegisterSerializer
)
from django.contrib.auth.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    GET /api/me/ 로 토큰 검증 및
    현재 로그인된 사용자 정보를 반환
    """
    return Response({
        'id': request.user.id,
        'username': request.user.username,
    })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()           # User 모델 전체를 대상으로 생성
    serializer_class = RegisterSerializer

class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

class RecommendViewSet(viewsets.ModelViewSet):
    queryset = Recommend.objects.all()
    serializer_class = RecommendSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class BestBoardViewSet(viewsets.ModelViewSet):
    queryset = BestBoard.objects.all()
    serializer_class = BestBoardSerializer

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
