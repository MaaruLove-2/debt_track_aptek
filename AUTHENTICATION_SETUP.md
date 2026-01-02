# Pharmacist Authentication System

## Overview

Hər aptekçi indi öz istifadəçi hesabı ilə daxil ola bilər və yalnız öz borclarını görə bilər. Müştərilər bütün aptekçilər arasında paylaşılır.

## Əsas Xüsusiyyətlər

1. **Hər aptekçi üçün ayrı hesab**: İstifadəçi adı və parol
2. **Təcrid olunmuş borclar**: Hər aptekçi yalnız öz borclarını görür
3. **Paylaşılan müştərilər**: Bütün aptekçilər eyni müştəri bazasını görür
4. **Təhlükəsizlik**: Bütün səhifələr login tələb edir

## Quraşdırma

### 1. Migrasiyaları İcra Edin

Yeni `user` sahəsi üçün migrasiya yaradın və icra edin:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Mövcud Aptekçilər üçün İstifadəçi Hesabları Yaradın

Mövcud aptekçilər üçün istifadəçi hesabları yaratmaq lazımdır. Bunu Django admin panelindən və ya aşağıdakı skript ilə edə bilərsiniz:

```python
from django.contrib.auth.models import User
from main.models import Pharmacist

# Mövcud aptekçilər üçün istifadəçi yaradın
for pharmacist in Pharmacist.objects.filter(user__isnull=True):
    username = f"{pharmacist.name.lower()}_{pharmacist.surname.lower()}"
    password = "default_password_123"  # Aptekçiyə dəyişdirməyi xatırlatın!
    
    user = User.objects.create_user(
        username=username,
        password=password,
        email=pharmacist.email or '',
        first_name=pharmacist.name,
        last_name=pharmacist.surname
    )
    pharmacist.user = user
    pharmacist.save()
    print(f"Created user for {pharmacist}: {username}")
```

### 3. Yeni Aptekçi Əlavə Etmək

Yeni aptekçi əlavə edərkən:
- İstifadəçi adı və parol tələb olunur
- Sistem avtomatik olaraq User hesabı yaradır
- Aptekçi dərhal daxil ola bilər

## İstifadə

### Aptekçi Daxil Olması

1. `/login/` səhifəsinə daxil olun
2. İstifadəçi adı və parolu daxil edin
3. Sistem sizi ana səhifəyə yönləndirir

### Aptekçi Çıxışı

1. Sağ yuxarı küncdəki istifadəçi menyusuna klikləyin
2. "Çıxış" seçin

### Müştəri Əlavə Etmək

- Bütün aptekçilər eyni müştəri bazasını görür
- Bir aptekçi müştəri əlavə etdikdə, digər aptekçilər də görə bilər
- Müştərilər paylaşılan resursdur

### Borc Əlavə Etmək

- Hər aptekçi yalnız öz borclarını əlavə edə bilər
- Borc avtomatik olaraq daxil olmuş aptekçiyə təyin edilir
- Formda aptekçi seçimi göstərilmir (avtomatik)

## Təhlükəsizlik

- Bütün səhifələr `@login_required` dekoratoru ilə qorunur
- Aptekçilər yalnız öz borclarını görə bilər
- Aptekçilər yalnız öz profillərinə baxa bilər
- Müştərilər bütün aptekçilər üçün əlçatandır

## Admin Panel

Django admin panelindən:
- Aptekçiləri və istifadəçi hesablarını idarə edə bilərsiniz
- Yeni aptekçi əlavə edə bilərsiniz
- Parolları sıfırlaya bilərsiniz

## Qeydlər

- İlk dəfə quraşdırmada superuser yaradın: `python manage.py createsuperuser`
- Superuser admin panelə daxil ola bilər və bütün aptekçiləri idarə edə bilər
- Mövcud aptekçilər üçün istifadəçi hesabları yaratmaq lazımdır (yuxarıdakı skriptə baxın)




