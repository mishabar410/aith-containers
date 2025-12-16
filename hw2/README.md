- **web_app**: Flask-приложение, собранное из локального `Dockerfile`. Оно подключается к Redis и читает данные из общего тома (volume).
- **redis_db**: Сервис базы данных Redis, используемый для счетчика посещений.
- **init_service**: Временный контейнер на Alpine linux, который запускается один раз для записи конфигурационных данных в общий том, используемый веб-приложением.

## Реализация требований

1.  **3 Сервиса**: `init_service` (init), `web_app` (app), `redis_db` (db).
2.  **Автоматическая сборка**: `web_app` собирается из контекста `.` с присвоением имени образу.
3.  **Жесткое именование**: Контейнеры названы `hw2_init_container`, `hw2_app_container`, `hw2_redis_container`.
4.  **Depends On**: `web_app` ожидает `redis_db` (healthy) и `init_service` (completed).
5.  **Volume**: `shared_data` используется сервисами `init_service` и `web_app`.
6.  **Порты**: `web_app` прокидывает порт, определенный в `.env` (по умолчанию 5000).
7.  **Command/Entrypoint**: `web_app` использует `command: ["python", "app.py"]`. `init_service` использует `command` для записи файла.
8.  **Healthcheck**: Добавлен для `redis_db` (ping) и `web_app` (curl /health).
9.  **Только Env**: Все чувствительные/конфигурационные переменные находятся в `.env`.
10. **Network**: Все сервисы находятся в сети `app_network`.

## Запуск проекта

```bash
docker-compose up -d --build
```
- `http://localhost:5000/` (Приветственное сообщение)
- `http://localhost:5000/data` (Чтение из init volume)
- `http://localhost:5000/hits` (Счетчик Redis)

## Вопросы и Ответы

### 1. Можно ли ограничивать ресурсы (например, память или CPU) для сервисов в docker-compose.yml?

Да.
```yaml
services:
    myservice:
    deploy:
        resources:
        limits:
            cpus: '0.50'
            memory: 50M
```
Это устанавливает жесткий лимит на использование CPU (50% от одного ядра) и памяти (50 Мегабайт).

### 2. Как можно запустить только определенный сервис из docker-compose.yml, не запуская остальные?

указать имя сервиса после команды `up`.
Например:

```bash
docker-compose up -d redis_db
```
