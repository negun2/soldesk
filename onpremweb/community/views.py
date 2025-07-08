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
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@csrf_exempt
def token_obtain_pair_view(request, *args, **kwargs):
    view = TokenObtainPairView.as_view()
    return view(request, *args, **kwargs)

@ensure_csrf_cookie
def test_csrf_view(request):
    resp = HttpResponse("csrf cookie set!")
    resp.set_cookie("testcookie", "TESTCOOKIE", path="/")
    resp['Set-Cookie'] = "testcustomcookie=MYTEST; Path=/"
    return resp

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """ GET /api/me/ → 유저 정보 """
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'is_staff': request.user.is_staff,
    })

class BoardImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        board_id = request.data.get('board_id')
        board = Board.objects.get(id=board_id)
        image_files = request.FILES.getlist('images')
        image_objs = []
        for img in image_files:
            img_obj = BoardImage.objects.create(board=board, image=img)
            image_objs.append(img_obj)
        serializer = BoardImageSerializer(image_objs, many=True, context={'request': request})
        return Response(serializer.data)

# 게시판(일반/베스트): 전체 사용자 허용 (쓰기 포함), 수정/삭제는 작성자/관리자만
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        print("BoardViewSet.retrieve 호출됨!!")
        return super().retrieve(request, *args, **kwargs)    

class BestBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.order_by('-recommend_count')[:10]   # 추천순 TOP 10
    serializer_class = BoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]

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

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all().order_by('created_at')
    serializer_class = ScoreSerializer
    permission_classes = [IsAdminUser]

class ErrorLogViewSet(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
    permission_classes = [IsAdminUser]

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
