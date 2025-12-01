release: python cv_platform/manage.py migrate --noinput && python cv_platform/manage.py collectstatic --noinput
web: python cv_platform/manage.py migrate --noinput && PYTHONPATH=$PWD gunicorn cv_platform.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2

