release: cd cv_platform && python manage.py migrate --noinput && python manage.py collectstatic --noinput
web: PYTHONPATH=$PWD gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT

