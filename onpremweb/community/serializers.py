# onpremweb/community/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Analysis, Board, BoardImage, Recommend, Feedback, BestBoard,
    Notice, Reply, Score, ErrorLog
)

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
        return ReplySerializer(obj.children.all(), many=True).data
    
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

class FeedbackSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Feedback
        fields = '__all__'

class BestBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestBoard
        fields = '__all__'

class NoticeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Notice
        fields = '__all__'

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'

class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = '__all__'
