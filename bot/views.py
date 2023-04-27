from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient
from todolist import settings


class BotVerificationView(UpdateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TgUserSerializer

    def update(self, request, *args, **kwargs):
        serializer: TgUserSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        tg_user = serializer.save()
        tg_client = TgClient(settings.BOT_TOKEN)
        tg_client.send_message(chat_id=tg_user.telegram_chat_id,
                               text='''Аккаунт успешно привязан!\n
    Доступные команды:\n"/goals" — получить список целей\n"/create" — создать новую цель''')
