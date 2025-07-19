# onpremweb/community/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadWriteBoard(BasePermission):
    """
    읽기/쓰기는 로그인 사용자 모두,
    수정/삭제는 관리자만
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.method == "POST":
            return request.user and request.user.is_authenticated
        # PUT/PATCH/DELETE만 관리자
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.method == "POST":
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

class IsAdminOrReadOnly(BasePermission):
    """
    읽기(GET/HEAD/OPTIONS)는 모두,
    나머지(POST/PUT/PATCH/DELETE)는 관리자만
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # 누구나 읽기 허용
        return request.user and request.user.is_staff    
    
