# onpremweb/community/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadWriteBoard(BasePermission):
    """
    베스트/일반 게시판: 모든 사용자가 읽기/쓰기 가능. 수정/삭제는 작성자나 staff만.
    """
    def has_permission(self, request, view):
        # 로그인만 했으면 접근 가능 (쓰기까지 허용)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # 읽기는 누구나
        if request.method in SAFE_METHODS:
            return True
        # 수정/삭제는 작성자나 staff만
        return obj.author == request.user or request.user.is_staff