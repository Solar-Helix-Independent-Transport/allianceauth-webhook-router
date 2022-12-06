from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .tasks import send_ping
from .models import PingerIngressConfig


@csrf_exempt
def ingress(request, token, user):
    if request.method == 'POST':
        webhook = get_object_or_404(PingerIngressConfig, identifier=token)

        for r in webhook.routes.filter(active=True):
            send_ping.delay(r.discord_webhook, request.body.decode())

    return HttpResponse(status=204)
