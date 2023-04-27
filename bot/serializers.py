from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    telegram_chat_id = serializers.SlugField(source='chat_id', read_only=True)

    class Meta:
        model = TgUser
        fields = ('telegram_chat_id', 'telegram_user_id', 'user', 'verification_code')
        read_only_fields = ('telegram_chat_id', 'telegram_user_id', 'user')

    def validate_verification_code(self, value: str):
        try:
            self.instance = TgUser.objects.get(verification_code=value)
        except TgUser.DoesNotExist:
            raise ValidationError('Code is incorrect')
        return value

    def update(self, instance, validated_data):
        self.instance.user = self.context['request'].user
        return super().update(instance, validated_data)
