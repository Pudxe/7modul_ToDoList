import logging

from django.core.management.base import BaseCommand

from bot.management.chat import Chat
from bot.tg.client import TgClient
from todolist import settings


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.tg_client: TgClient = TgClient(token=settings.BOT_TOKEN)
        self.logger = logging.getLogger(__name__)
        self.logger.info('Бот запущен')

    def handle(self, *args, **options):
        offset: int = 0
        while True:
            # Получение обновлений в бесконечном цикле.
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.logger.info(item.message)
                chat = Chat(message=item.message)
                chat.set_condition(tg_client=self.tg_client)
                # Запуск исполнения команд, доступных юзеру каждого состояния.
                chat.condition.run()
