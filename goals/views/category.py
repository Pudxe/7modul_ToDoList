from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import LimitOffsetPagination

from goals.models import GoalCategory
from goals.serializers import GoalCategorySerializer, GoalCategoryCreateSerializer
from goals.filters import CategoryBoardFilter
from goals.permissions import CategoryPermissions


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [CategoryPermissions, ]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [CategoryPermissions, ]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryBoardFilter
    search_fields = ['title']
    ordering_fields = ['title', 'created']
    ordering = ['title']

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            is_deleted=False, board__participants__user_id=self.request.user.id,
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [CategoryPermissions, ]

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(
            is_deleted=False, board__participants__user_id=self.request.user.id,
        )

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance
