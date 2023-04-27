from rest_framework import serializers
from django.db import transaction
from django.core.exceptions import PermissionDenied

from core.models import User
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from core.serializers import ProfileSerializer


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.filter(is_deleted=False)
    )

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"

    def validate_board(self, value: Board):
        if value.is_deleted:
            raise serializers.ValidationError('Board is deleted')
        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


class GoalCategorySerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "board")
        fields = "__all__"


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "user", "created", "updated")

    def validate_category(self, value: GoalCategory):
        if value.is_deleted:
            raise serializers.ValidationError('Category is deleted')

        if not BoardParticipant.objects.filter(
                board=value.board.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user.id
        ):
            raise PermissionDenied
        return value


class GoalSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "user", "created", "updated")


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def validate_goal(self, value: Goal):
        if not BoardParticipant.objects.filter(
                board=value.category.board.id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ):
            raise PermissionDenied
        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')


class BoardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'


class BoardCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", "is_deleted")
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data.pop("user")
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(
            user=user, board=board, role=BoardParticipant.Role.owner
        )
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        required=True, choices=BoardParticipant.Role.choices[1:]
    )

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = BoardParticipant
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "board")


class BoardSerializer(serializers.ModelSerializer):
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance, validated_data):
        owner: User = validated_data.pop('user')
        new_participants = validated_data.pop('participants')
        old_participants = instance.participants.exclude(user=owner)
        new_by_id = {part['user'].id: part for part in new_participants}
        with transaction.atomic():
            # определить и выкинуть тех, кого не будет в новом списке участников
            for old_part in old_participants:
                if old_part.user_id not in new_by_id.keys():
                    old_part.delete()
                # для всех, кто остался
                else:
                    # проверяем, изменилась ли роль -> изменяем
                    if old_part.role != new_by_id[old_part.user_id]['role']:
                        old_part.role = new_by_id[old_part.user_id]['role']
                        old_part.save()
                    # получаем обработанного старого участника и удаляем из словаря новых
                    new_by_id.pop(old_part.user_id)
            # для всех, кто остался в новых
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    user=new_part['user'],
                    board=instance,
                    role=new_part['role']
                )

                if title := validated_data.get('title'):
                    instance.title = title
                    instance.save()

        return instance
