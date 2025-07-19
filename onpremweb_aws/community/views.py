# onpremweb/community/views.py
from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from .permissions import IsAdminOrReadWriteBoard, IsAdminOrReadOnly
from .models import ( 
    Board, BoardImage, BestBoard, Notice, Feedback, FeedbackReply, FeedbackImage, Analysis, Recommend, Reply, 
    Score, ErrorLog, Notification, NoticeReply, NoticeImage
)
from .serializers import (
    BoardSerializer, BoardImageSerializer, BestBoardSerializer, NoticeSerializer, FeedbackSerializer, FeedbackReplySerializer, FeedbackImageSerializer,
    AnalysisSerializer, RecommendSerializer, ReplySerializer, ScoreSerializer, ErrorLogSerializer, RegisterSerializer, UserSimpleSerializer, UserDetailSerializer,
    NotificationSerializer, NoticeReplySerializer, NoticeImageSerializer
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
import boto3
import uuid

def delete_s3_file(s3_key):
    s3 = boto3.client(
        's3',
        region_name=settings.AWS_REGION
    )
    s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=s3_key)

class BoardImageViewSet(viewsets.ModelViewSet):
    queryset = BoardImage.objects.all()
    serializer_class = BoardImageSerializer
    permission_classes = [IsAuthenticated]
    def perform_destroy(self, instance):
        s3_key = instance.image.replace(
            f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/", ""
        )
        delete_s3_file(s3_key)
        instance.delete()


class FeedbackImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        feedback_id = request.data.get('feedback_id')
        feedback = Feedback.objects.get(id=feedback_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = []
        for url in s3_urls:
            img_obj = FeedbackImage.objects.create(feedback=feedback, image=url)
            image_objs.append(img_obj)
        serializer = FeedbackImageSerializer(image_objs, many=True, context={'request': request})
        return Response(serializer.data)


class NoticeImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        notice_id = request.data.get('notice_id')
        notice = Notice.objects.get(pk=notice_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = []
        for url in s3_urls:
            img_obj = NoticeImage.objects.create(notice=notice, image=url)
            image_objs.append(img_obj)
        serializer = NoticeImageSerializer(image_objs, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def s3_presigned_upload(request):
    file_name = request.data['file_name']  # 예: car1.jpg
    file_type = request.data['file_type']  # 예: image/jpeg
    s3_key = f"user_uploads/{request.user.id}/{uuid.uuid4()}_{file_name}"
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='ap-northeast-1'  # 도쿄 이미지 버킷
    )
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': 'hidcars-image-2',
            'Key': s3_key,
            'ContentType': file_type,
            'ACL': 'public-read',   # public 업로드일 때
        },
        ExpiresIn=300,
        HttpMethod='PUT'
    )
    return Response({'url': url, 's3_url': f"https://hidcars-image-2.s3.ap-northeast-1.amazonaws.com/{s3_key}"})

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

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 내 알림만
        return Notification.objects.filter(to_user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': '읽음'})

class BoardImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        board_id = request.data.get('board_id')
        board = Board.objects.get(id=board_id)
        # 이미지를 프론트에서 S3 presigned로 올린 뒤, s3_url을 POST로 전달
        s3_urls = request.data.getlist('s3_urls[]')  # 여러 개일 경우
        image_objs = []
        for url in s3_urls:
            img_obj = BoardImage.objects.create(board=board, image=url)
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
    queryset = Board.objects.all()  # 슬라이싱 제거!
    serializer_class = BoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'post_date', 'recommend_count', 'title', 'author__username']
    ordering = ['-recommend_count']  # 기본 정렬: 추천순
    search_fields = ['title', 'content', 'author__username']

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

    def perform_create(self, serializer):
        reply = serializer.save(author=self.request.user)
        board = reply.board
        # 자기 댓글이 아니고, 본인이 쓴 글이 아니면 알림
        if board.author != self.request.user:
            from .models import Notification
            Notification.objects.create(
                to_user=board.author,
                board=board,
                reply=reply,
                notif_type='comment',
                message=f"{self.request.user.username}님이 회원님의 게시글에 댓글을 남겼습니다."
            )

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

class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSimpleSerializer
    permission_classes = [IsAdminOrSelf]  # 관리자가 회원 관리만 가능

    def get_serializer_class(self):
        # /api/users/<id>/일 때는 상세, /api/users/는 목록(간단정보)
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSimpleSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        # 관리자만 삭제 불가 (본인 삭제는 허용)
        if user.is_staff:
            return Response({'detail': '관리자는 삭제할 수 없습니다.'},
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
    permission_classes = [IsAdminOrReadOnly]

    # 정렬/검색 옵션 추가
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'created_at', 'title', 'user__username']
    ordering = ['-created_at']
    search_fields = ['title', 'content', 'user__username']

class NoticeReplyViewSet(viewsets.ModelViewSet):
    queryset = NoticeReply.objects.all()
    serializer_class = NoticeReplySerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


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
