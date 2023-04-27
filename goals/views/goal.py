from django.db.models import Q
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from goals.models import Goal
from goals.serializers import GoalSerializer, GoalCreateSerializer
from goals.filters import GoalDateFilter
from goals.permissions import GoalBoardPermissions


class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [IsAuthenticated, ]
    serializer_class = GoalCreateSerializer


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    permission_classes = [IsAuthenticated, GoalBoardPermissions, ]
    serializer_class = GoalSerializer

    def get_queryset(self):
        return Goal.objects.select_related('category').filter(
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False) &
            Q(category__board__participants__user_id=self.request.user.id)
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save()
        return instance


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [IsAuthenticated, ]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    search_fields = ['title', 'description']
    ordering_fields = ['due_date']
    ordering = ['due_date', '-priority']

    def get_queryset(self):
        return Goal.objects.select_related('category').filter(
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False) &
            Q(category__board__participants__user_id=self.request.user.id)
        )
