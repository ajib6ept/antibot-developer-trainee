from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

import time
from http import HTTPStatus

SUBNET1_IP1 = "123.45.67.89"
SUBNET1_IP2 = "123.45.67.1"
SUBNET1_IP3 = "123.45.67.11"

SUBNET2_IP1 = "122.44.66.88"

RESPONSE_TEXT = "Hello, world!"


class RateLimitTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_url = reverse("index")
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_home(self):
        resp = self.client.get(self.test_url)
        assert resp.status_code == HTTPStatus.OK
        assert resp.content.decode("utf-8") == RESPONSE_TEXT

    def test_rate_limit(self):

        """
        после 20 запросов с IP 123.45.67.89 и 80 запросов с IP 123.45.67.1
        сервис возвращает 429 ошибку на любой запрос с подсети 123.45.67.0/24
        в течение двух последующих минут.
        """

        for _ in range(20):
            resp = self.client.get(
                self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP1}
            )
            assert resp.status_code == HTTPStatus.OK

        for _ in range(80):
            resp = self.client.get(
                self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP2}
            )
            print(resp.status_code)
            assert resp.status_code == HTTPStatus.OK

        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP1}
        )
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP2}
        )
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP3}
        )
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET2_IP1}
        )
        assert resp.status_code == HTTPStatus.OK

    @override_settings(RATELIMIT_LIMIT="1/m", RATELIMIT_BLOCK="3s")
    def test_ban_time(self):
        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP1}
        )
        assert resp.status_code == HTTPStatus.OK

        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP2}
        )
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        time.sleep(3)

        resp = self.client.get(
            self.test_url, **{"HTTP_X_FORWARDED_FOR": SUBNET1_IP2}
        )
        assert resp.status_code == HTTPStatus.OK
