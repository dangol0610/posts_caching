# Posts API — Сервис управления постами с кэшированием

FastAPI-приложение для управления постами в блоге с кэшированием данных в Redis.

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI   │────▶│   Service   │────▶│ Repository  │
│             │     │  Endpoints  │     │   (Кэш)     │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘     └──────┬──────┘
                                               │                   │
                                               ▼                   ▼
                                         ┌─────────────┐   ┌─────────────┐
                                         │    Redis    │   │ PostgreSQL  │
                                         │   (Кэш)     │   │   (БД)      │
                                         └─────────────┘   └─────────────┘
```

### Компоненты

| Компонент | Версия | Порт | Описание |
|-----------|--------|------|----------|
| FastAPI | 0.135+ | 8000 | API сервер |
| PostgreSQL | latest | 5433 | Основное хранилище |
| Redis | latest | 6377 | Кэш популярных запросов |
| RedisInsight | latest | 5540 | Веб-интерфейс для Redis |

---

## Требования

- Python 3.13+
- Docker и Docker Compose
- uv (менеджер пакетов)

---

## Установка

### 1. Клонирование репозития

```bash
git clone <repository-url>
cd posts
```

### 2. Настройка переменных окружения

Создайте файл `.env` в папке `src/`:

```bash
cp src/.env.example src/.env
```

Отредактируйте `src/.env` при необходимости:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=posts

REDIS_HOST=redis
REDIS_PORT=6379

CACHE_TTL=3600
```

### 3. Установка зависимостей

```bash
uv sync
```

---

## Запуск

### Через Docker Compose (рекомендуется)

```bash
docker-compose up -d
```

Сервисы будут доступны по адресам:

- API: http://localhost:8000
- PostgreSQL: localhost:5433
- Redis: localhost:6377
- RedisInsight: http://localhost:5540

### Локальный запуск

1. Убедитесь, что PostgreSQL и Redis запущены:

```bash
docker-compose up -d postgres redis
```

2. Запустите приложение:

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## API Endpoints

### POST `/api/posts/`
Создание нового поста.

**Request:**
```json
{
  "title": "Заголовок",
  "content": "Содержимое поста"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "title": "Заголовок",
  "content": "Содержимое поста",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": null
}
```

---

### GET `/api/posts/{post_id}`
Получение поста по ID (с кэшированием).

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Заголовок",
  "content": "Содержимое поста",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": null
}
```

**Логика кэширования:**
1. Проверка Redis на наличие ключа `post:{id}`
2. При命中 — возврат из кэша
3. При промахе — запрос в БД + запись в кэш (TTL: 1 час)

---

### PATCH `/api/posts/{post_id}`
Обновление поста.

**Request:**
```json
{
  "title": "Новый заголовок",
  "content": "Новое содержимое"
}
```

**Response:** `200 OK`

Кэш обновляется новыми данными.

---

### DELETE `/api/posts/{post_id}`
Удаление поста.

**Response:** `200 OK`

Кэш инвалидируется (удаляется).

---

## Тесты

### Запуск всех тестов

```bash
uv run pytest
```

### Запуск интеграционных тестов

```bash
uv run pytest src/tests/integration/
```

### Запуск тестов с выводом логов

```bash
uv run pytest -s -v
```

### Запуск конкретного теста

```bash
uv run pytest src/tests/integration/test_caching.py::TestPostCaching::test_cache_miss_then_hit -v
```

### Подготовка к тестам

Тесты используют отдельные контейнеры:
- PostgreSQL: порт 5434
- Redis: порт 6377

Убедитесь, что они запущены:

```bash
docker-compose up -d postgres-test redis
```

---

## Структура проекта

```
posts/
├── src/
│   ├── app/
│   │   ├── models.py       # SQLAlchemy модели
│   │   ├── schemas.py      # Pydantic схемы
│   │   ├── repository.py   # Доступ к БД
│   │   ├── services.py     # Бизнес-логика с кэшированием
│   │   └── routers.py      # API endpoints
│   ├── settings/
│   │   └── settings.py     # Конфигурация приложения
│   ├── utils/
│   │   ├── database.py     # Подключение к БД
│   │   ├── redis.py        # Подключение к Redis
│   │   └── exceptions.py   # Кастомные исключения
│   ├── tests/
│   │   ├── conftest.py     # Фикстуры pytest
│   │   └── integration/
│   │       └── test_caching.py  # Интеграционные тесты кэша
│   ├── migrations/         # Alembic миграции
│   ├── main.py            # Точка входа FastAPI
│   ├── .env               # Переменные окружения
│   ├── .env.test          # Тестовые переменные
│   └── .env.docker        # Docker переменные
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Стратегия кэширования

### Почему Cache-Aside?

1. **Простота реализации** — минимальная логика в сервисе
2. **Отказоустойчивость** — при падении Redis запросы идут в БД
3. **Актуальность данных** — инвалидация при записи гарантирует свежесть

### Ключи Redis

- Формат: `post:{post_id}`
- TTL: 3600 секунд (1 час)
- Формат данных: JSON (сериализация через Pydantic)

### Инвалидация

| Операция | Действие с кэшем |
|----------|------------------|
| GET | Чтение (hit/miss) |
| POST | Не кэшируем (создание) |
| PATCH | Обновление кэша |
| DELETE | Удаление из кэша |

---

## Обработка ошибок

| Ошибка | HTTP статус | Описание |
|--------|-------------|----------|
| PostNotFoundError | 404 | Пост не найден |
| DatabaseError | 500 | Ошибка БД |
| CacheError | 500 | Ошибка Redis |

При ошибке Redis запросы всё ещё работают (данные из БД).

---

## Миграции БД

Alembic используется для управления миграциями:

```bash
# Создать новую миграцию
uv run alembic revision --autogenerate -m "description"

# Применить миграции
uv run alembic upgrade head

# Откатить миграцию
uv run alembic downgrade -1
```

---

## Лицензия

MIT
