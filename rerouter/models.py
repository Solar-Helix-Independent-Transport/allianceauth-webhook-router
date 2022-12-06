from django.db import models
import uuid

import logging

logger = logging.getLogger(__name__)


class DiscordWebhook(models.Model):
    nickname = models.CharField(max_length=50, default="A Discord Webhook")
    discord_webhook = models.TextField()

    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nickname}"


class PingerIngressConfig(models.Model):

    nickname = models.CharField(max_length=50, default="A Webhook Router")

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4)

    active = models.BooleanField(default=True)

    routes = models.ManyToManyField(DiscordWebhook, blank=True)

    def __str__(self):
        return f"{self.nickname}"
