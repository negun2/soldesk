# onpremweb/community/views.py
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Board, BestBoard, Notice, Feedback, Analysis, Recommend, Reply, Score, ErrorLog
from .serializers import BoardSerializer, BestBoardSerializer, NoticeSerializer, FeedbackSerializer, \
    AnalysisSerializer, RecommendSerializer, ReplySerializer, ScoreSerializer, ErrorLogSerializer, RegisterSerializer
from .permissions import IsAdminOrReadWriteBoard
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """ GET /api/me/ → 유저 정보 """
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'is_staff': request.user.is_staff,
    })

# 게시판(일반/베스트): 전체 사용자 허용 (쓰기 포함), 수정/삭제는 작성자/관리자만
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]

class BestBoardViewSet(viewsets.ModelViewSet):
    queryset = BestBoard.objects.all()
    serializer_class = BestBoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]

# 나머지 게시판: 관리자만
class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminUser]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminUser]

class AnalysisViewSet(viewsets.ModelViewSet):
    queryset = Analysis.objects.all()
    serializer_class = AnalysisSerializer
    permission_classes = [IsAdminUser]

class RecommendViewSet(viewsets.ModelViewSet):
    queryset = Recommend.objects.all()
    serializer_class = RecommendSerializer
    permission_classes = [IsAdminUser]

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAdminUser]

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [IsAdminUser]

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAdminUser]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
