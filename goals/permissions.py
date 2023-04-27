from rest_framework import permissions

from goals.models import BoardParticipant, Board, Goal, GoalCategory


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.id == obj.user_id


class BoardPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Board):
        _filters: dict = {'user': request.user, 'board': obj}
        if request.method not in permissions.SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner
        return BoardParticipant.objects.filter(**_filters).exists()


class CategoryPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalCategory):
        _filters: dict = {'user': request.user, 'board': obj.board}
        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**_filters).exists()


class GoalBoardPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Goal):
        _filters: dict = {'user': request.user, 'board': obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**_filters).exists()
