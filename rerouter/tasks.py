import time
import datetime
import logging
import json
import requests
import hashlib

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone


logger = logging.getLogger(__name__)


alliances = []
corporations = []
min_time = 60
last_update = 0


def _build_wh_cache_key(wh_url):
    md5 = hashlib.md5(wh_url.encode('utf-8')).hexdigest()
    return f"re-router-wh-{md5}"


def _get_wh_cooloff(wh_url):
    return cache.get(_build_wh_cache_key(wh_url), False)


def _set_wh_cooloff(wh_url, cooloff):
    ready_time = timezone.now() + datetime.timedelta(seconds=cooloff)
    unixtime = time.mktime(ready_time.timetuple())
    cache.set(_build_wh_cache_key(wh_url), unixtime, cooloff+.5)


def _get_cooloff_time(wh_url):
    cached = _get_wh_cooloff(wh_url)
    if cached:
        unixtime = time.mktime(timezone.now().timetuple())
        return (cached - unixtime) + 0.15
    else:
        return 0


@shared_task(bind=True, max_retries=None)
def send_ping(self, url, payload):
    wh_sleep = _get_cooloff_time(url)
    if wh_sleep > 0:
        logger.warning(
            f"Webhook rate limited: trying again in {wh_sleep} seconds...")
        self.retry(countdown=wh_sleep)

    logger.debug(payload)

    custom_headers = {'Content-Type': 'application/json'}

    response = requests.post(url,
                             headers=custom_headers,
                             data=payload,
                             params={'wait': True})

    if response.status_code in [200, 204]:
        logger.debug(f"Ping Sent!")
    elif response.status_code == 429:
        errors = json.loads(response.content.decode('utf-8'))
        wh_sleep = (int(errors['retry_after']) / 1000) + 0.15
        logger.warning(
            f"Webhook rate limited: trying again in {wh_sleep} seconds...")
        _set_wh_cooloff(url, wh_sleep)
        self.retry(countdown=wh_sleep)
    else:
        logger.error(
            f"failed ({response.status_code}) to: {url}")
        response.raise_for_status()
    # TODO 404/403/500 etc etc etc etc
