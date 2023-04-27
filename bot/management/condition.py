from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory


class BaseTgUserCondition:
    """Базовый класс состояния юзера."""

    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        self.tg_user = tg_user
        self.tg_client = tg_client
        self._text: str | None = None

    def get_verification_code(self) -> str:
        return self.tg_user.set_verification_code()

    def send_message(self, text: str) -> None:
        self.tg_client.send_message(
            chat_id=int(self.tg_user.telegram_chat_id),
            text=text
        )

    def run(self) -> None:
        self.send_message(text=self._text)


class NewUserCondition(BaseTgUserCondition):
    """Класс юзера, впервые активировавшего бота"""

    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        super().__init__(tg_user, tg_client)
        self._text = f'''Добро пожаловать в бот ToDoList!
Для продолжения работы необходимо привязать Ваш аккаунт edenerus.online:8001.
Код для верификации: {self.get_verification_code()}.'''


class UnverifiedUserCondition(BaseTgUserCondition):
    """Класс юзера, не прошедшего верификацию."""

    def __init__(self, tg_user: TgUser, tg_client: TgClient):
        super().__init__(tg_user, tg_client)
        self._text = f'Код для верификации: {self.get_verification_code()}.'


class VerifiedUserCondition(BaseTgUserCondition):
    """Класс верифицированного юзера."""
    is_create_command: bool = False
    category_for_create: int | None = None

    def __init__(self, tg_user: TgUser, tg_client: TgClient, message: Message):
        super().__init__(tg_user, tg_client)
        self.message = message

    def run(self) -> None:
        if self.message.text.startswith('/'):
            self._handle_command()
        else:
            self._handle_message()

    def _handle_message(self) -> None:
        if VerifiedUserCondition.is_create_command is False:
            self.send_message(
                text='''Доступные команды:\n/goals — получить список целей\n/create — создать новую цель.'''
            )
        elif VerifiedUserCondition.is_create_command and not VerifiedUserCondition.category_for_create:
            self._handle_create_command(self.message)
        else:
            self.create_goal()

    def _handle_command(self) -> None:
        match self.message.text:
            case '/start':
                self._handle_message()
            case '/goals':
                self._handle_goals_command()
            case '/create':
                self._handle_choose_cat_command()
            case '/cancel':
                self._handle_cancel_create()
                self._handle_message()
            case _:
                self.send_message(
                    text='''Неизвестная команда.'''
                )
                self._handle_message()

    def _handle_goals_command(self) -> None:
        goals: list[str] = list(
            Goal.objects.filter(user_id=self.tg_user.user.id)
            .exclude(status=Goal.Status.archived).values_list('title', flat=True)
        )

        self.send_message(
            text='\n'.join(goals) if goals else 'Целей пока нет.'
        )

    def _handle_create_command(self, message: Message):
        categories_id: list[int] = [
            cat.id for cat in GoalCategory.objects.filter(user_id=self.tg_user.user.id, is_deleted=False)
        ]
        if int(message.text) in categories_id:
            VerifiedUserCondition.category_for_create = int(message.text)
            self.send_message(
                text='''Введите название цели.'''
            )
        else:
            self.send_message(
                text='''Такой категории нет. Чтобы создать цель введите /create.'''
            )

    def create_goal(self):
        goal = Goal.objects.create(user_id=self.tg_user.user.id, category_id=VerifiedUserCondition.category_for_create,
                                   title=self.message.text)
        VerifiedUserCondition.is_create_command = False
        VerifiedUserCondition.category_for_create = None
        self.send_message(
            text=f'''Создана цель {self.message.text} в категории {GoalCategory.objects.get(id=goal.category_id)}.'''
        )

    def _handle_choose_cat_command(self):
        categories: list[str] = [
            f'{cat.id}) {cat.title}'
            for cat in GoalCategory.objects.filter(user_id=self.tg_user.user.id, is_deleted=False)
        ]
        if categories:
            VerifiedUserCondition.is_create_command = True
            categories_msg: str = '\n'.join(categories)
            self.send_message(
                text=f'''Выберите категорию:\n{categories_msg}\nДля отмены введите /cancel.'''
                if categories
                else 'Необходимо создать категорию.'
            )

    def _handle_cancel_create(self):
        VerifiedUserCondition.is_create_command = False
        self.send_message(
            text='''Создание цели отменено.'''
        )
