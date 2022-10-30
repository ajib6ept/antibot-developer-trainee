

from django.test import Client, TestCase
from django.urls import reverse

from http import HTTPStatus

SUBNET1_IP1 = '123.45.67.89'
SUBNET1_IP2 = '123.45.67.1'
SUBNET1_IP3 = '123.45.67.11'

SUBNET2_IP1 = '122.44.66.88'

RESPONSE_TEXT = 'Hello, world!'



class RateLimitTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_url = reverse("index")

    def test_home(self):
        resp = self.client.get(self.test_url)
        assert resp.status_code == HTTPStatus.OK
        assert resp.content.decode('utf-8') == RESPONSE_TEXT

    def test_rate_limit(self):

        """
        после 20 запросов с IP 123.45.67.89 и 80 запросов с IP 123.45.67.1 
        сервис возвращает 429 ошибку на любой запрос с подсети 123.45.67.0/24 
        в течение двух последующих минут.
        """

        for _ in range(20):
            resp = self.client.get(self.test_url, headers={"X-Forwarded-For": SUBNET1_IP1})
            assert resp.status_code == HTTPStatus.OK

        for _ in range(80):
            resp = self.client.get(self.test_url,  headers={"X-Forwarded-For": SUBNET1_IP2})
            assert resp.status_code == HTTPStatus.OK

        
        resp = self.client.get(self.test_url, headers={"X-Forwarded-For": SUBNET1_IP1})
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        resp = self.client.get(self.test_url, headers={"X-Forwarded-For": SUBNET1_IP2})
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        resp = self.client.get(self.test_url, headers={"X-Forwarded-For": SUBNET1_IP3})
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS

        resp = self.client.get(self.test_url,  headers={"X-Forwarded-For": SUBNET2_IP1})
        assert resp.status_code == HTTPStatus.OK

