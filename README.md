# pdefAI Backend — Django REST API

Kitob (book writer) ilovasi uchun backend. Django REST Framework + JWT.

## Quick Start (local)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # .env ichida SECRET_KEY ni o'zgartiring

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API: `http://localhost:8000`

## Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/auth/register/` | — | Ro'yxatdan o'tish |
| POST | `/api/auth/login/` | — | Kirish |
| POST | `/api/auth/refresh/` | — | Access token yangilash |
| GET | `/api/auth/me/` | Bearer | Hozirgi foydalanuvchi |
| GET | `/api/projects/` | Bearer | Barcha loyihalar |
| POST | `/api/projects/` | Bearer | Yangi loyiha yaratish |
| GET | `/api/projects/{id}/` | Bearer | Bitta loyiha |
| PATCH | `/api/projects/{id}/` | Bearer | Loyihani yangilash |
| DELETE | `/api/projects/{id}/` | Bearer | Loyihani o'chirish |

## Curl misollar

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"pass1234"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"pass1234"}'

# Projects list (TOKEN ni almashtiring)
curl http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <access_token>"

# Yangi loyiha
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Mening kitobim","meta":{},"format":{},"margins":{},"numbering":{},"typography":{},"content":""}'

# Partial update
curl -X PATCH http://localhost:8000/api/projects/<id>/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Yangi nom"}'
```

## PythonAnywhere Deploy

1. `git clone` → `/home/<username>/pdefai-backend`
2. `python3.10 -m venv venv && pip install -r requirements.txt`
3. `.env` → `DEBUG=False`, `DJANGO_SETTINGS_MODULE=kitob.settings.prod`
4. `prod.py` ichida `yourusername` ni o'zgartiring
5. `python manage.py migrate && python manage.py collectstatic`
6. Web tab: source `/home/<username>/pdefai-backend`, WSGI faylni `wsgi.py` komentidagi snippet bilan almashtiring
