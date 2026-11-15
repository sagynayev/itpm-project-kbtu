# Бесплатный деплой

Production-схема состоит из одного Render Web Service и одной базы Neon PostgreSQL. React и Django работают на одном домене, поэтому отдельный CORS и второй сервер не нужны.

**Рабочий production:** [https://pdd-check-kbtu.onrender.com](https://pdd-check-kbtu.onrender.com)

## 1. Создать базу Neon

1. Открыть [Neon Console](https://console.neon.tech/) и создать бесплатный проект `pdd-check`.
2. Выбрать ближайший европейский регион.
3. В блоке **Connection details** включить **Pooled connection**.
4. Скопировать строку подключения. Она должна начинаться с `postgresql://` и содержать `sslmode=require`.

## 2. Запустить Render Blueprint

Нажать кнопку ниже и войти в Render:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sagynayev/itpm-project-kbtu)

При создании Blueprint Render попросит только секрет `DATABASE_URL`. Вставить туда pooled connection string из Neon и подтвердить создание бесплатного сервиса.

Render автоматически:

- соберёт React;
- установит Django;
- применит миграции;
- импортирует 883 фрагмента ПДД;
- запустит Gunicorn;
- включит HTTPS и последующие автодеплои из `main`.

## 3. Проверить

После статуса **Live** открыть выданный адрес `https://...onrender.com`.

- интерфейс: `/`;
- health check: `/api/health/` → `{"status":"ok"}`;
- админ-панель: `/admin/`.

Для создания администратора открыть Render Shell и выполнить:

```bash
python manage.py createsuperuser
```

## Ограничения бесплатного тарифа

Render останавливает неактивный бесплатный сервис, поэтому первый запрос после паузы может запускаться около минуты. Neon также засыпает при простое и автоматически просыпается при подключении. Для учебной демонстрации откройте сайт за 1–2 минуты до выступления.

Актуальные условия: [Render Free](https://render.com/docs/free), [Neon Free Plan](https://neon.com/pricing).
