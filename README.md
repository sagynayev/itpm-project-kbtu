# PDD Check

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sagynayev/itpm-project-kbtu)

**Production:** [pdd-check-kbtu.onrender.com](https://pdd-check-kbtu.onrender.com)

Помощник по ПДД Казахстана с проверяемым официальным источником.

> Спросите как водитель. Проверьте как юрист.

Пользователь описывает дорожную ситуацию своими словами, получает короткий ориентир и открывает точный фрагмент действующих ПДД в ИПС «Әділет». Если подтверждаемого источника нет, сервис возвращает `no_source`, а не придумывает ответ.

**Project planning baseline:** 29 October 2026.

**Initial repository publication:** 5 November 2026.

**Product-ready MVP update:** 15 November 2026.

Бесплатный production-деплой подготовлен для Render + Neon. Краткая инструкция: [docs/deployment.md](docs/deployment.md).

## Что готово

- marketing landing с чётким позиционированием;
- registration и token login;
- профиль: имя, уровень, дата экзамена;
- история вопросов;
- retrieval по актуальному официальному тексту;
- source-only grounding guardrail;
- короткий ответ, контекст и раскрываемый официальный пункт;
- feedback на ответы;
- Django admin и guardrail logs;
- автоматическая синхронизация ИПС «Әділет»;
- JSONL snapshot: **883 фрагмента**, редакция **3 ноября 2026 года**;
- адаптивный React UI;
- tests, GitHub Actions и Docker Compose.

## Быстрый запуск через Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Открыть: `http://localhost:8080`. При старте backend применяет миграции и импортирует [официальный snapshot](data/pdd_official_ru.jsonl) в PostgreSQL.

`docker compose config` проверен. Полную сборку образов нужно повторить на машине с запущенным Docker daemon.

## Локальная разработка

Backend — Python 3.12+:

```powershell
cd backend
py -m venv ..\.venv
..\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py manage.py migrate
py manage.py import_pdd ..\data\pdd_official_ru.jsonl
py manage.py runserver
```

Frontend — Node.js 20+:

```powershell
cd frontend
npm ci
npm run dev
```

Для Vite development используется `VITE_API_URL=http://localhost:8000/api`.

Для production задайте сильные `DJANGO_SECRET_KEY`, `POSTGRES_PASSWORD`, домен в `DJANGO_ALLOWED_HOSTS` и включите `DJANGO_SECURE_SSL=true` за TLS reverse proxy.

## Обновить официальный текст

```powershell
cd backend
py manage.py sync_adilet --output ..\data\pdd_official_ru.jsonl
```

Команда загружает раздел «Правила дорожного движения» из официального акта МВД РК №534, сохраняет дату редакции, anchor, URL и SHA-256 каждого фрагмента. После синхронизации команда должна пройти ручную проверку 20 случайных записей.

## Проверка

```powershell
cd backend
py manage.py test
py manage.py check

cd ..\frontend
npm run build
npm audit
```

## Команда

| Участник | Ответственность |
|---|---|
| Nurdos | PM / Product Owner, UI/UX, QA и scope |
| Alikhan | Django, PostgreSQL, authentication и React |
| Alimzhan | PDD cleaning, retrieval, guardrail и evaluation |

## Документы

- [TSIS 4–7: что сделано](docs/TSIS-4-7-summary-ru.md)
- [Brand & marketing](docs/brand-and-marketing.md)
- [Demo script](docs/demo-script.md)
- [Release checklist](docs/release-checklist.md)
- [Usability test](docs/usability-test.md)
- [Sprint status](docs/sprint-status.md)
- [Evaluation set and baseline](evaluation/README.md)
- [Answer-service contract](docs/answer-service-interface.md)
- [PDD data contract](docs/pdd-data-contract.md)
- [Definition of Done](docs/definition-of-done.md)

## Ограничение MVP

Retrieval и короткий ответ сейчас детерминированы: пользователю показывается только текст, который можно связать с сохранённым официальным фрагментом. Это безопасная база для последующей RAG-генерации, но не юридическая консультация. Перед реальным запуском нужны размеченные 100 ответов, метрики guardrail, usability test на пяти пользователях, production TLS и резервное копирование PostgreSQL.
