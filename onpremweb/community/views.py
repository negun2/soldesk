# onpremweb/community/views.py
from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .permissions import IsAdminOrReadWriteBoard
from .models import Board, BoardImage, BestBoard, Notice, Feedback, FeedbackReply, FeedbackImage, Analysis, Recommend, Reply, Score, ErrorLog
from .serializers import (
    BoardSerializer, BoardImageSerializer, BestBoardSerializer, NoticeSerializer, FeedbackSerializer, FeedbackReplySerializer, FeedbackImageSerializer,
    AnalysisSerializer, RecommendSerializer, ReplySerializer, ScoreSerializer, ErrorLogSerializer, RegisterSerializer, UserSimpleSerializer, UserDetailSerializer
)
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import serializers


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
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)

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
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'post_date', 'recommend_count']  # 허용되는 필드
    ordering = ['-post_date']  # 기본값: 최신순
    search_fields = ['title', 'content', 'author__username']


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

    # 정렬/검색 옵션 추가
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'post_date', 'recommend_count', 'title', 'author__username']
    ordering = ['-recommend_count']  # 추천순 기본
    search_fields = ['title', 'content', 'author__username']

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]
 
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class BoardLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        board = Board.objects.get(pk=pk)
        user = request.user
        if Recommend.objects.filter(board=board, user=user).exists():
            return Response({"detail": "이미 좋아요를 눌렀습니다."}, status=400)
        Recommend.objects.create(board=board, user=user)
        board.recommend_count = Recommend.objects.filter(board=board).count()
        board.save(update_fields=['recommend_count'])
        return Response({"detail": "좋아요!"})

class FeedbackImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        feedback_id = request.data.get('feedback_id')
        feedback = Feedback.objects.get(id=feedback_id)
        image_files = request.FILES.getlist('images')
        image_objs = []
        for img in image_files:
            img_obj = FeedbackImage.objects.create(feedback=feedback, image=img)
            image_objs.append(img_obj)
        serializer = FeedbackImageSerializer(image_objs, many=True, context={'request': request})
        return Response(serializer.data)

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAdminOrReadWriteBoard]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # 정렬/검색 옵션 추가
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'created_at', 'title', 'user__username']
    ordering = ['-created_at']  # 기본: 최신순
    search_fields = ['title', 'content', 'user__username']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context  

class FeedbackReplyViewSet(viewsets.ModelViewSet):
    queryset = FeedbackReply.objects.all()
    serializer_class = FeedbackReplySerializer
    permission_classes = [IsAdminOrReadWriteBoard]  # or 필요시 관리자만 (IsAdminUser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class SetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSimpleSerializer
    permission_classes = [IsAdminUser]  # 관리자가 회원 관리만 가능

    def get_serializer_class(self):
        # /api/users/<id>/일 때는 상세, /api/users/는 목록(간단정보)
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSimpleSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        # 관리자 혹은 본인 계정 삭제 방지
        if user.is_staff or user == request.user:
            return Response({'detail': '관리자 또는 본인은 삭제할 수 없습니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='set_password')
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'detail': '현재 비밀번호가 올바르지 않습니다.'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': '비밀번호가 변경되었습니다.'})

from rest_framework.decorators import api_view, permission_classes
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)

# 나머지 게시판: 관리자만
class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminUser]

    # 정렬/검색 옵션 추가
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'created_at', 'title', 'user__username']
    ordering = ['-created_at']
    search_fields = ['title', 'content', 'user__username']

@api_view(['GET'])
@permission_classes([IsAdminUser])  # 관리자만
def user_list(request):
    users = User.objects.all()
    serializer = UserSimpleSerializer(users, many=True)
    return Response(serializer.data)

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
