from bot.management.condition import UnverifiedUserCondition, VerifiedUserCondition, BaseTgUserCondition, NewUserCondition
from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message


class Chat:
    def __init__(self, message: Message):
        self.message = message
        self.__condition: BaseTgUserCondition | None = None

    @property
    def condition(self):
        if self.__condition:
            return self.__condition
        else:
            raise RuntimeError('''Состояния не существует''')

    def set_condition(self, tg_client: TgClient) -> None:
        tg_user, created = TgUser.objects.get_or_create(
            telegram_chat_id=self.message.chat.id,
            defaults={
                'telegram_user_id': self.message.from_.id
            }
        )
        if created:
            self.__condition = NewUserCondition(tg_client=tg_client, tg_user=tg_user)
        elif not tg_user.user:
            self.__condition = UnverifiedUserCondition(tg_client=tg_client, tg_user=tg_user)
        else:
            self.__condition = VerifiedUserCondition(tg_client=tg_client, tg_user=tg_user, message=self.message)
