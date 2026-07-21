web: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py loaddata seed && gunicorn whetstone.wsgi --bind 0.0.0.0:$PORT
release: python manage.py collectstatic --noinput && python manage.py migrate && python manage.py loaddata seed


