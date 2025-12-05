@echo off
echo Setting up Component Stock Management System...
echo.

echo 1. Installing Django...
pip install Django==4.2.7

echo.
echo 2. Creating database migrations...
python manage.py makemigrations components

echo.
echo 3. Applying migrations...
python manage.py migrate

echo.
echo 4. Creating static directory...
if not exist "static" mkdir static

echo.
echo Setup complete! 
echo.
echo To create a superuser for admin access, run:
echo   python manage.py createsuperuser
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Then open your browser to http://127.0.0.1:8000/
pause