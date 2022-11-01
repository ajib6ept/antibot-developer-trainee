
lint:
	poetry run flake8 antibot --exclude=antibot/settings.py

run:
	poetry run python manage.py runserver


test:
	poetry run python manage.py test -v 2
