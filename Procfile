release: cd cv_platform && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: cd cv_platform && gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT

