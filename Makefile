
install:
	poetry install

lint:
	poetry run flake8 antibot --exclude=antibot/settings.py

run:
	poetry run python manage.py runserver


test:
	poetry run python manage.py test


test_coverage:
	poetry run coverage run --source='antibot' manage.py test
	poetry run coverage xml
	poetry run coverage report
