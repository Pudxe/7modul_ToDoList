from django.db import transaction
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView

from goals.models import Board, Goal
from goals.serializers import BoardSerializer, BoardCreateSerializer, BoardListSerializer
from goals.permissions import BoardPermissions


class BoardView(RetrieveUpdateDestroyAPIView):
    model = Board
    permission_classes = [BoardPermissions, ]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(
            participants__user_id=self.request.user.id,
            is_deleted=False
        )

    def perform_destroy(self, instance: Board):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(
                status=Goal.Status.archived
            )

        return instance


class BoardCreateView(CreateAPIView):
    serializer_class = BoardCreateSerializer
    permission_classes = [IsAuthenticated, ]


class BoardListView(ListAPIView):
    model = Board
    serializer_class = BoardListSerializer
    permission_classes = [BoardPermissions, ]
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.prefetch_related('participants').filter(
            participants__user_id=self.request.user.id,
            is_deleted=False
        )
