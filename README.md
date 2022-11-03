## Задача

Необходимо создать HTTP-сервис, способный ограничивать количество запросов (rate limit) из одной подсети IPv4. Если ограничения отсутствуют, то нужно выдавать одинаковый статический контент.

### Tests and linter status:
[![Actions Status](https://github.com/ajib6ept/antibot-developer-trainee/workflows/check-code/badge.svg)](https://github.com/ajib6ept/antibot-developer-trainee/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/1192252f3a36d4862172/maintainability)](https://codeclimate.com/github/ajib6ept/antibot-developer-trainee/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/1192252f3a36d4862172/test_coverage)](https://codeclimate.com/github/ajib6ept/antibot-developer-trainee/test_coverage)
***

### Требования:
- язык: Go или Python
- код должен быть выложен на GitHub
- ответ должен соответствовать спецификации RFC 6585
- IP должен извлекаться из заголовка X-Forwarded-For
- подсеть: /24 (маска 255.255.255.0)
- лимит: 100 запросов в минуту
- время ожидания после ограничения: 2 минуты

**Пример**: после 20 запросов с IP 123.45.67.89 и 80 запросов с IP 123.45.67.1 сервис возвращает 429 ошибку на любой запрос с подсети 123.45.67.0/24 в течение двух последующих минут.

### Усложнения (плюс в карму за каждый пункт):
- покрытие тестами
- контейнеризация, возможность запустить с помощью `docker-compose up`
- размер префикса подсети, лимит и время ожидания можно задавать при старте сервиса
- отдельный handler для сброса лимита по префиксу
