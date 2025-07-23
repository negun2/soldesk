# onpremweb_aws/community/views.py
# community/views.py

from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import (
    Board, BoardImage, BestBoard, Notice, Feedback, FeedbackReply, FeedbackImage, Analysis,
    Recommend, Reply, Score, ErrorLog, Notification, NoticeReply, NoticeImage
)
from .serializers import (
    BoardSerializer, BoardImageSerializer, BestBoardSerializer, NoticeSerializer, FeedbackSerializer,
    FeedbackReplySerializer, FeedbackImageSerializer, AnalysisSerializer, RecommendSerializer, ReplySerializer,
    ScoreSerializer, ErrorLogSerializer, RegisterSerializer, UserSimpleSerializer, UserDetailSerializer,
    NotificationSerializer, NoticeReplySerializer, NoticeImageSerializer
)
from .permissions import IsAdminOrReadWriteBoard, IsAdminOrReadOnly
import boto3
import uuid

### JWT Token View
token_obtain_pair_view = TokenObtainPairView.as_view()

### CSRF 테스트용
@ensure_csrf_cookie
def test_csrf_view(request):
    return JsonResponse({"result": "ok"})

####################
# S3 Presigned URL (프론트가 직접 업로드)
####################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def s3_presigned_upload(request):
    """
    파일명/타입을 받아 S3 presigned 업로드 URL 반환 (프론트가 직접 S3에 업로드)
    """
    file_name = request.data['file_name']
    file_type = request.data['file_type']
    s3_key = f"user_uploads/{request.user.id}/{uuid.uuid4()}_{file_name}"
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': settings.AWS_S3_BUCKET,
            'Key': s3_key,
            'ContentType': file_type,
            'ACL': 'public-read'
        },
        ExpiresIn=300,
        HttpMethod='PUT'
    )
    return Response({
        'url': url,
        's3_url': f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
    })

####################
# S3 이미지 삭제
####################
def delete_s3_file(s3_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=s3_key)

####################
# 유저 관련 기능
####################
@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return Response({'exists': exists})

@api_view(['GET'])
def check_email(request):
    email = request.GET.get('email', '')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_list(request):
    users = User.objects.all()
    serializer = UserSimpleSerializer(users, many=True)
    return Response(serializer.data)

####################
# 알림(Notification)
####################
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(to_user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': '읽음'})

####################
# Board/Feedback/Notice Image 업로드 - S3 URL을 DB에 저장
####################
class BoardImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        board_id = request.data.get('board_id')
        board = Board.objects.get(id=board_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = [BoardImage.objects.create(board=board, image=url) for url in s3_urls]
        serializer = BoardImageSerializer(image_objs, many=True)
        return Response(serializer.data)

class FeedbackImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        feedback_id = request.data.get('feedback_id')
        feedback = Feedback.objects.get(id=feedback_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = [FeedbackImage.objects.create(feedback=feedback, image=url) for url in s3_urls]
        serializer = FeedbackImageSerializer(image_objs, many=True)
        return Response(serializer.data)

class NoticeImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        notice_id = request.data.get('notice_id')
        notice = Notice.objects.get(pk=notice_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = [NoticeImage.objects.create(notice=notice, image=url) for url in s3_urls]
        serializer = NoticeImageSerializer(image_objs, many=True)
        return Response(serializer.data)

class BoardImageViewSet(viewsets.ModelViewSet):
    queryset = BoardImage.objects.all()
    serializer_class = BoardImageSerializer
    permission_classes = [IsAuthenticated]
    def perform_destroy(self, instance):
        # S3 URL에서 key 추출 후 S3에서 삭제
        s3_key = instance.image.replace(
            f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/", ""
        )
        delete_s3_file(s3_key)
        instance.delete()

####################
# 게시글/피드백/공지사항/댓글 CRUD (댓글 생성 시 알림까지)
####################
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'post_date', 'recommend_count']
    ordering = ['-post_date']
    search_fields = ['title', 'content', 'author__username']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        my = self.request.query_params.get('my')
        if my and self.request.user.is_authenticated:
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

class BestBoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAdminOrReadWriteBoard]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'post_date', 'recommend_count', 'title', 'author__username']
    ordering = ['-recommend_count']
    search_fields = ['title', 'content', 'author__username']

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
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'created_at', 'title', 'user__username']
    ordering = ['-created_at']
    search_fields = ['title', 'content', 'user__username']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        my = self.request.query_params.get('my')
        if my and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'created_at', 'title', 'user__username']
    ordering = ['-created_at']
    search_fields = ['title', 'content', 'user__username']

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

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
        if board.author != self.request.user:
            Notification.objects.create(
                to_user=board.author,
                board=board,
                reply=reply,
                notif_type='comment',
                message=f"{self.request.user.username}님이 회원님의 게시글에 댓글을 남겼습니다."
            )
        return reply

class FeedbackReplyViewSet(viewsets.ModelViewSet):
    queryset = FeedbackReply.objects.all()
    serializer_class = FeedbackReplySerializer
    permission_classes = [IsAdminOrReadWriteBoard]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    def perform_create(self, serializer):
        reply = serializer.save(author=self.request.user)
        feedback = reply.feedback
        if feedback.user != self.request.user:
            Notification.objects.create(
                to_user=feedback.user,
                feedback=feedback,
                feedback_reply=reply,
                notif_type='feedback_reply',
                message=f"{self.request.user.username}님이 회원님의 피드백에 댓글을 남겼습니다."
            )
        return reply

class NoticeReplyViewSet(viewsets.ModelViewSet):
    queryset = NoticeReply.objects.all()
    serializer_class = NoticeReplySerializer
    permission_classes = [IsAuthenticated]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    def perform_create(self, serializer):
        reply = serializer.save(author=self.request.user)
        notice = reply.notice
        if notice.user != self.request.user:
            Notification.objects.create(
                to_user=notice.user,
                notice=notice,
                notice_reply=reply,
                notif_type='notice_reply',
                message=f"{self.request.user.username}님이 회원님의 공지사항에 댓글을 남겼습니다."
            )
        return reply

####################
# 관리자/분석/추천/점수/에러 로그 뷰셋
####################
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

####################
# 회원가입/Register
####################
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

####################
# 유저 뷰셋 (자기 자신/관리자만 상세/삭제/비번변경)
####################
class SetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSimpleSerializer
    permission_classes = [IsAdminOrSelf]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        return UserSimpleSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_staff:
            return Response({'detail': '관리자는 삭제할 수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
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
