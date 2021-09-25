python manage.py migrate --no-input
python manage.py collectstatic --no-input
gunicorn coupons.wsgi:application --bind 0.0.0.0:8000 -w 4