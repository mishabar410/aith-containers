# HW4: More Kubernetes

## Описание
Развертывание сервиса в Kubernetes, состоящего из Python веб-приложения и базы данных Redis.
Приложение использует ConfigMap и Secrets для конфигурации, Init-контейнер для инициализации данных, Liveness/Readiness пробы для проверки здоровья, и разделяемый Volume.

## Структура репозитория
- `app/`: Исходный код приложения (Python Flask).
- `manifests/`: Kubernetes манифесты.
    - `00-namespace.yaml`: Создает namespace `hw4`.
    - `01-config-and-secret.yaml`: ConfigMap и Secret.
    - `02-redis.yaml`: Deployment и Service для Redis.
    - `03-app.yaml`: Deployment и Service для Python приложения.

## Как запустить

### 1. Подготовка окружения
Переключитесь на использование Docker демона внутри Minikube (если используете Minikube):
```bash
eval $(minikube docker-env)
```

### 2. Сборка образа
Соберите Docker образ приложения:
```bash
cd app
docker build -t hw4-app:latest .
cd ..
```

### 3. Применение манифестов
Примените все манифесты из папки `manifests`:
```bash
kubectl apply -f manifests/
```

### 4. Проверка
Посмотрите статус подов:
```bash
kubectl get pods -n hw4
```

Получите URL сервиса (если используете minikube tunnel или хотите пробросить порт):
```bash
# В отдельном терминале
kubectl port-forward -n hw4 service/python-app-service 8080:80
```
Теперь приложение доступно по адресу `http://localhost:8080`.

## Скриншоты

![alt text](<Снимок экрана 2025-12-24 в 21.52.36.png>)
![alt text](<Снимок экрана 2025-12-24 в 21.53.10.png>)