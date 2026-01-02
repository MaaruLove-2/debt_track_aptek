# Quick Fix for Database Error

## If you're getting a database connection error:

### Option 1: Use SQLite (Easiest - No Setup Required)

The system will automatically use SQLite if PostgreSQL is not configured. Just make sure you don't have a `.env` file with `DB_ENGINE=postgresql`.

**No action needed** - SQLite is the default!

### Option 2: Set up PostgreSQL

1. **Create a `.env` file** in the `pharmacy_website` folder with:
   ```
   DB_ENGINE=postgresql
   DB_NAME=pharmacy_db
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

2. **Make sure PostgreSQL is installed and running**

3. **Create the database:**
   ```sql
   CREATE DATABASE pharmacy_db;
   ```

### Option 3: Remove PostgreSQL Configuration

If you want to use SQLite and you have a `.env` file:
- Delete the `.env` file, OR
- Change `DB_ENGINE=postgresql` to `DB_ENGINE=sqlite` in `.env`

## Common Errors:

### Error: "could not connect to server"
- PostgreSQL is not running
- Solution: Start PostgreSQL service or use SQLite

### Error: "database does not exist"
- Database hasn't been created
- Solution: Create database or use SQLite

### Error: "password authentication failed"
- Wrong password in `.env`
- Solution: Check password or use SQLite

### Error: "No module named 'psycopg2'"
- Missing PostgreSQL adapter
- Solution: Run `pip install psycopg2-binary` or use SQLite





