# onpremweb_aws/community/views.py

from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework_simplejwt.views import TokenObtainPairView
import boto3
import uuid

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

######################################
# S3 Presigned URL 발급 (프론트가 S3 직접 업로드 후, S3 URL만 서버로 보내는 방식)
######################################
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def s3_presigned_upload(request):
    """
    프론트에서 파일명/타입 보내면 S3 presigned 업로드 URL 반환
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

######################################
# S3 이미지 파일 삭제 (DB에서 이미지 삭제할 때 S3에서도 삭제)
######################################
def delete_s3_file(s3_key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=s3_key)

######################################
# 회원가입, 유저 정보, 이메일/아이디 중복 체크
######################################
@api_view(['GET'])
def check_username(request):
    """
    ?username=abc
    → { exists: true/false }
    """
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return Response({'exists': exists})

@api_view(['GET'])
def check_email(request):
    """
    ?email=abc@naver.com
    → { exists: true/false }
    """
    email = request.GET.get('email', '')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """
    현재 로그인 유저 정보
    """
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)

######################################
# 알림(Notification) ViewSet (내 알림만, 읽음 처리 등)
######################################
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 내 알림만
        return Notification.objects.filter(to_user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        POST /notifications/{id}/mark_read/
        알림 읽음 처리
        """
        notif = self.get_object()
        notif.is_read = True
        notif.save()
        return Response({'status': '읽음'})

######################################
# BoardImage/FeedbackImage/NoticeImage 업로드 (S3 URL을 받는다)
######################################
class BoardImageUploadView(APIView):
    """
    게시글(Board) 이미지 업로드: S3 URL 받아서 DB 등록
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        board_id = request.data.get('board_id')
        board = Board.objects.get(id=board_id)
        s3_urls = request.data.getlist('s3_urls[]')  # 프론트에서 s3_urls[]로 전송
        image_objs = [
            BoardImage.objects.create(board=board, image=url) for url in s3_urls
        ]
        serializer = BoardImageSerializer(image_objs, many=True)
        return Response(serializer.data)

class BoardImageViewSet(viewsets.ModelViewSet):
    """
    BoardImage 삭제시 S3에서 파일도 삭제
    """
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

class FeedbackImageUploadView(APIView):
    """
    피드백(Feedback) 이미지 업로드: S3 URL 받아서 DB 등록
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        feedback_id = request.data.get('feedback_id')
        feedback = Feedback.objects.get(id=feedback_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = [
            FeedbackImage.objects.create(feedback=feedback, image=url) for url in s3_urls
        ]
        serializer = FeedbackImageSerializer(image_objs, many=True)
        return Response(serializer.data)

class NoticeImageUploadView(APIView):
    """
    공지사항(Notice) 이미지 업로드: S3 URL 받아서 DB 등록
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        notice_id = request.data.get('notice_id')
        notice = Notice.objects.get(pk=notice_id)
        s3_urls = request.data.getlist('s3_urls[]')
        image_objs = [
            NoticeImage.objects.create(notice=notice, image=url) for url in s3_urls
        ]
        serializer = NoticeImageSerializer(image_objs, many=True)
        return Response(serializer.data)

######################################
# 게시글/피드백/공지사항 CRUD ViewSet (아래는 기본 구조, 상세는 기존 코드 유지해도 됨)
######################################
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
        board = serializer.save(author=self.request.user)
        return board

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

class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'created_at', 'title', 'user__username']
    ordering = ['-created_at']
    search_fields = ['title', 'content', 'user__username']

######################################
# 댓글/대댓글 CRUD (Board/Feedback/Notice)
######################################
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

######################################
# 기타 ViewSet: 추천, 점수, 에러, 관리자용 유저 등
######################################
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
        user = request.use
