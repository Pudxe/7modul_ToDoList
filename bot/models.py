import os
from django.db import models

from core.models import User


class TgUser(models.Model):
    telegram_chat_id = models.CharField(max_length=100, unique=True)
    telegram_user_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, blank=True)
    verification_code = models.CharField(max_length=80, null=True, blank=True, default=None)

    @staticmethod
    def _gen_code():
        return os.urandom(15).hex()

    def set_verification_code(self):
        self.verification_code = self._gen_code()
        self.save(update_fields=('verification_code',))
        return self.verification_code
