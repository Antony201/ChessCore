from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):
    """
        Права на доступ админа
    """

    @staticmethod
    def is_admin(user) -> bool:
        """
            Проверить пользователя на роль админа
        """
        if user:
            return user.is_superuser

        return False

    def has_permission(self, request, view):
        return self.is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_admin(request.user)


class StaffPermission(BasePermission):
    @staticmethod
    def is_staff(user) -> bool:
        """
            Проверить пользователя на роль сотрудника
        """
        if user:
            return user.is_staff

        return False

    def has_permission(self, request, view):
        return self.is_staff(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_staff(request.user)


class AdminOrStaffPermission(StaffPermission, AdminPermission):
    """
        Права на доступ админа или сотрудника
    """
    def has_permission(self, request, view):
        return self.is_staff(request.user) or self.is_admin(request.user)

    def has_object_permission(self, request, view, obj):
        return self.is_staff(request.user) or self.is_admin(request.user)
