from django.contrib import admin

from . import models

from django.conf import settings
import requests
import json
from django.contrib import messages

from django.utils.html import format_html
import logging

logger = logging.getLogger(__name__)


@admin.action(description='Send Test Ping')
def sendTestPing(DiscordWebhook, request, queryset):
    for w in queryset:
        payload = {"embeds": [
            {
                "title": "Ping Channel Test",
                "description": "Output Channel Configured",
                "color": 10181046,
            }
        ]
        }
        payload = json.dumps(payload)
        url = w.discord_webhook
        custom_headers = {'Content-Type': 'application/json'}
        response = requests.post(url,
                                 headers=custom_headers,
                                 data=payload,
                                 params={'wait': True})

        if response.status_code in [200, 204]:
            msg = f"{w.nickname}: Test Ping Sent!"
            messages.success(request, msg)
            logger.debug(msg)
        elif response.status_code == 429:
            errors = json.loads(response.content.decode('utf-8'))
            wh_sleep = (int(errors['retry_after']) / 1000) + 0.15
            msg = f"{w.nickname}: rate limited: try again in {wh_sleep} seconds..."
            messages.warning(request, msg)
            logger.warning(msg)
        else:
            msg = f"{w.nickname}: failed ({response.status_code})"
            messages.error(request, msg)
            logger.error(msg)


class DiscordWebhookAdmin(admin.ModelAdmin):
    list_display = ["__str__", "active"]
    actions = [sendTestPing]


admin.site.register(models.DiscordWebhook, DiscordWebhookAdmin)


class PingerIngressConfigAdmin(admin.ModelAdmin):
    list_display = ["__str__", "active"]
    filter_horizontal = ["routes"]


admin.site.register(models.PingerIngressConfig, PingerIngressConfigAdmin)
