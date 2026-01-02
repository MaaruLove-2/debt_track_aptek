@echo off
echo ========================================
echo PostgreSQL Database Setup
echo ========================================
echo.

echo Step 1: Creating database and user...
echo Please enter PostgreSQL admin password when prompted
echo.

psql -U postgres -c "CREATE DATABASE pharmacy_db;" 2>nul
if %errorlevel% neq 0 (
    echo Database might already exist, continuing...
)

psql -U postgres -c "CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_pass123';" 2>nul
if %errorlevel% neq 0 (
    echo User might already exist, continuing...
)

psql -U postgres -c "ALTER ROLE pharmacy_user SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE pharmacy_user SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE pharmacy_user SET timezone TO 'Asia/Baku';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;"

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo Step 3: Creating superuser (optional)...
echo You can skip this step if you already have a superuser
python manage.py createsuperuser

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Don't forget to update .env file with your database credentials:
echo DB_NAME=pharmacy_db
echo DB_USER=pharmacy_user
echo DB_PASSWORD=pharmacy_pass123
echo DB_HOST=localhost
echo DB_PORT=5432
echo.
pause





