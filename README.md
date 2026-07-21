# MediaTracker API

Backend сервис для трекинга фильмов, сериалов и аниме - REST API на FastAPI с аунтификацией, кэшированием и частичным тестированием.

**Deploy-версия**: https://media-tracker-27zw.onrender.com/docs

## Стек

 - **Backend**: FastAPI, Python 3.10, asyncio
  - **База данных**: PostgreSQL, SQLAchemy (async), Alembic
  - **Аутентификация**: JWT, bcrypt
  - **Кэширование**: Redis (cache-aside pattern)
  - **Инфраструктура**: Docker, docker-compose
  - **Тестирование**: pytest, pytest-asyncio, httpx

## Возможности

  - CRUD для медиа-контента (фильмы/сериалы/аниме) с фильтрацией и поиском
  - JWT-аунтификация с защищенными эндпоинтами
  - Redis-кэш с автоматической инвалидацией при изменении данных
  - Фоновые задачи (BackgroundTasks) для неблокирующих операций
  - Частичное покрытие тестами с изолированной тестовой БД

## Архитектурные решения

  - Модульная структура (routers/models/schemas/database разделены)
  - Асинхронный стек - эндпоинты, работа БД и Redis
  - Cache-aside с точечной инвалидацией по ключам (а не полным сбросом кэша)
  - Изолированая тестовая БД, пересоздаваемая для каждого теста

## Запуск локально

```bash
git clone https://github.com/Artem-pcode/media-tracker.git
cd media-tracker
cp .env.example .env  # заполнить своими значениями
docker-compose up --build
```

API будет доступен на `http://localhost:8000/docs`

## Roadmap

  - [ ] Полное покрытие тестами
  - [ ] UserEntry - пользовательские списки просмотра, оценки, прогресс
  - [ ] Роли пользователей
  - [ ] Celary для гарантированной доставки фоновых задач