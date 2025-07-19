# onpremweb/community/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Analysis, Board, BoardImage, Recommend, Feedback, FeedbackImage, FeedbackReply, BestBoard,
    Notice, Reply, Score, ErrorLog, Notification, NoticeReply, NoticeImage
)

class NotificationSerializer(serializers.ModelSerializer):
    board_title = serializers.CharField(source='board.title', read_only=True)
    reply_comment = serializers.CharField(source='reply.comment', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notif_type', 'message', 'is_read', 'created_at', 'board', 'board_title', 'reply', 'reply_comment']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff']

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'date_joined', 'last_login']

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = '__all__'

class ReplySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Reply
        fields = ['id', 'board', 'author', 'author_username', 'comment', 'parent', 'created_at', 'children']
    def get_children(self, obj):
        return ReplySerializer(obj.children.all(), many=True, context=self.context).data
    
    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError("댓글 내용을 입력하세요.")
        return value    

    def create(self, validated_data):
        request = self.context.get('request')
        # author 할당
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)

class BoardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardImage
        fields = ['id', 'image', 'uploaded_at']

class BoardSerializer(serializers.ModelSerializer):
    images = BoardImageSerializer(many=True, read_only=True)
    cost = serializers.CharField(required=False, allow_blank=True)
    replies = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    recommended_by_me = serializers.SerializerMethodField()
 
      
    class Meta:
        model = Board
        fields = [
            'id', 'author', 'author_username', 'title', 'content', 'cost',
            'images', 'replies', 'recommend_count', 'recommended_by_me',
            'post_date'
        ]
        read_only_fields = ['author', 'id', 'post_date']  # author를 읽기 전용

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)

    def get_recommended_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Recommend.objects.filter(board=obj, user=request.user).exists()
        return False

    def get_replies(self, obj):
        # parent가 null인(=최상위) 댓글만!
        root_replies = obj.replies.filter(parent__isnull=True)
        return ReplySerializer(root_replies, many=True, context=self.context).data

class RecommendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommend
        fields = '__all__'

class FeedbackImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackImage
        fields = ['id', 'image', 'uploaded_at']

class FeedbackSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    images = FeedbackImageSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = '__all__'
        read_only_fields = ['user']

    def get_replies(self, obj):
        root_replies = obj.replies.filter(parent__isnull=True)
        return FeedbackReplySerializer(root_replies, many=True, context=self.context).data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user   # ← 로그인 유저를 자동 할당
        return super().create(validated_data)


class FeedbackReplySerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    children = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = FeedbackReply
        fields = ['id', 'feedback', 'author', 'author_username', 'comment', 'parent', 'created_at', 'children']

    def get_children(self, obj):
        return FeedbackReplySerializer(obj.children.all(), many=True, context=self.context).data

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError("댓글 내용을 입력하세요.")
        return value

class BestBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestBoard
        fields = '__all__'

class NoticeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeImage
        fields = ['id', 'image', 'uploaded_at']

class NoticeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    images = NoticeImageSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

    def get_replies(self, obj):
        root_replies = obj.replies.filter(parent__isnull=True)
        return NoticeReplySerializer(root_replies, many=True, context=self.context).data


class NoticeReplySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = NoticeReply
        fields = ['id', 'notice', 'author', 'author_username', 'comment', 'parent', 'created_at', 'children']
        read_only_fields = ['author']

    def get_children(self, obj):
        return NoticeReplySerializer(obj.children.all(), many=True).data

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError("댓글 내용을 입력하세요.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'

class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = '__all__'
        
