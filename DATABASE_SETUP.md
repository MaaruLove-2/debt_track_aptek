# Database Setup Guide - PostgreSQL

Bu layihə PostgreSQL verilənlər bazası istifadə edir.

## Tələblər

1. PostgreSQL quraşdırılmış olmalıdır
2. Python virtual environment aktiv olmalıdır

## Quraşdırma Addımları

### 1. PostgreSQL Quraşdırılması

Windows üçün:
- PostgreSQL rəsmi saytından yükləyin: https://www.postgresql.org/download/windows/
- Quraşdırma zamanı postgres istifadəçi parolunu yadda saxlayın

Linux (Ubuntu/Debian) üçün:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

macOS üçün:
```bash
brew install postgresql
brew services start postgresql
```

### 2. PostgreSQL-də Verilənlər Bazası Yaradılması

PostgreSQL-ə qoşulun:
```bash
# Windows (PowerShell)
psql -U postgres

# Linux/macOS
sudo -u postgres psql
```

Verilənlər bazasını və istifadəçini yaradın:
```sql
CREATE DATABASE pharmacy_db;
CREATE USER pharmacy_user WITH PASSWORD 'your_secure_password';
ALTER ROLE pharmacy_user SET client_encoding TO 'utf8';
ALTER ROLE pharmacy_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE pharmacy_user SET timezone TO 'Asia/Baku';
GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
\q
```

### 3. Python Paketlərinin Quraşdırılması

Virtual environment aktiv edin və paketləri quraşdırın:
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# Paketləri quraşdırın
pip install -r requirements.txt
```

### 4. Environment Variables Konfiqurasiyası

`.env` faylını yaradın (`.env.example` faylını əsas götürərək):
```env
DB_NAME=pharmacy_db
DB_USER=pharmacy_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Migrasiyaların İcra Edilməsi

Verilənlər bazası strukturu yaradılması:
```bash
python manage.py migrate
```

Superuser yaradılması (admin panel üçün):
```bash
python manage.py createsuperuser
```

### 6. SQLite-dən Məlumatların Köçürülməsi (Əgər lazımsa)

Əgər SQLite bazasında mövcud məlumatlarınız varsa:

1. SQLite məlumatlarını export edin:
```bash
python manage.py dumpdata > data.json
```

2. PostgreSQL-ə köçürün:
```bash
python manage.py loaddata data.json
```

## Problemlərin Həlli

### Bağlantı Xətası
- PostgreSQL xidmətinin işlədiyini yoxlayın
- `.env` faylındakı məlumatların düzgün olduğunu yoxlayın
- Firewall ayarlarını yoxlayın

### Parol Xətası
- PostgreSQL-də istifadəçi parolunu yeniləyin
- `.env` faylında parolu yeniləyin

### Verilənlər Bazası Tapılmadı
- Verilənlər bazasının yaradıldığını yoxlayın
- İstifadəçinin lazımi icazələri olduğunu yoxlayın

## İstehsal Mühiti

İstehsal mühitində:
1. Güclü parol istifadə edin
2. `DEBUG=False` təyin edin
3. Yeni `SECRET_KEY` yaradın
4. SSL bağlantısı istifadə edin (mümkünsə)



