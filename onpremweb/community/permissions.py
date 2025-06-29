from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadWriteBoard(BasePermission):
    """
    - GET, POST, PUT, PATCH, DELETE: 로그인된 사용자는 모두 가능
    - (특정 메소드 제한 필요시 아래에 추가)
    """
    def has_permission(self, request, view):
        # 로그인 사용자면 허용
        return request.user and request.user.is_authenticated

class IsAdminUserOnly(BasePermission):
    """
    관리자만 허용
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
