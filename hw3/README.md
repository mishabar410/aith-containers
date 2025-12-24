# ЛР 3. Kubernetes - Развертывание Nextcloud на PostgreSQL

## Описание


### Выполненные модификации


1. **PostgreSQL**: Перенесены `POSTGRES_USER` и `POSTGRES_PASSWORD` из ConfigMap в Secret (`pg_secret.yml`)
2. **Nextcloud**: Перенесены переменные окружения (`NEXTCLOUD_UPDATE`, `ALLOW_EMPTY_PASSWORD`, `NEXTCLOUD_TRUSTED_DOMAINS`, `NEXTCLOUD_ADMIN_USER`) из Deployment в ConfigMap (`nextcloud_configmap.yml`)
3. **Nextcloud**: Добавлены Liveness и Readiness пробы для проверки состояния контейнера (с заголовком `Host: 127.0.0.1` для корректной проверки)
4. **PostgreSQL**: Значение `POSTGRES_DB` в ConfigMap изменено на `nextcloud` для корректной инициализации прав доступа.

## Структура манифестов

```
hw3/
├── pg_secret.yml           # Secret для PostgreSQL (user, password)
├── pg_configmap.yml        # ConfigMap для PostgreSQL (database name)
├── pg_service.yml          # NodePort Service для PostgreSQL
├── pg_deployment.yml       # Deployment для PostgreSQL
├── nextcloud_secret.yml    # Secret для Nextcloud (admin password)
├── nextcloud_configmap.yml # ConfigMap для Nextcloud (env variables)
├── nextcloud.yml           # Deployment для Nextcloud с пробами
└── README.md
```

## Инструкция по развертыванию

### 1. Предварительные требования

- Установлен и запущен Docker Desktop
- Установлен kubectl
- Установлен и запущен minikube

```bash
minikube start
```

### 2. Развертывание PostgreSQL

```bash
kubectl create -f pg_secret.yml
kubectl create -f pg_configmap.yml
kubectl create -f pg_service.yml
kubectl create -f pg_deployment.yml
```

### 3. Развертывание Nextcloud

```bash
kubectl create -f nextcloud_secret.yml
kubectl create -f nextcloud_configmap.yml
kubectl create -f nextcloud.yml
```

### 4. Проверка статуса

```bash
# Проверка всех ресурсов
kubectl get secrets
kubectl get configmaps
kubectl get services
kubectl get deployments
kubectl get pods

# Просмотр логов
kubectl logs -l app=postgres
kubectl logs -l app=nextcloud

# Проверка проб
kubectl describe deployment nextcloud | grep -A5 "Liveness\|Readiness"
```

### 5. Доступ к Nextcloud

```bash
# Создание сервиса для Nextcloud
kubectl expose deployment nextcloud --type=NodePort --port=80

# Открытие в браузере через minikube
minikube service nextcloud
```

**Данные для входа:**
- Логин: `admin` (указан в `nextcloud_configmap.yml`)
- Пароль: `nextcloudadminpass123` (указан в `nextcloud_secret.yml`)

### 6. Dashboard (опционально)

```bash
minikube dashboard --url
```

---

## Ответы на вопросы

### Вопрос 1: Важен ли порядок выполнения манифестов? Почему?

**Да, порядок важен.**

Причины:
Deployment ссылается на ConfigMap и Secret через `configMapRef` и `secretRef`. Если эти ресурсы не существуют на момент создания пода, он не сможет запуститься и перейдет в состояние ошибки (например, `CreateContainerConfigError`).


### Вопрос 2: Что произойдет, если отскейлить postgres-deployment в 0, затем обратно в 1, и попробовать зайти на Nextcloud?

**Произойдет потеря данных и возможные ошибки.**

---

## Скриншоты

![alt text](<Снимок экрана 2025-12-24 в 21.38.11.png>)

---

## Описание Liveness и Readiness проб

В `nextcloud.yml` добавлены следующие пробы:

### Liveness Probe (Проба живости)
```yaml
livenessProbe:
  httpGet:
    path: /status.php
    port: 80
  initialDelaySeconds: 60
  periodSeconds: 30
  timeoutSeconds: 5
  failureThreshold: 3
```
- Проверяет, что контейнер "жив" и отвечает
- Если проверка не проходит 3 раза подряд - контейнер перезапускается
- Начальная задержка 60 секунд для инициализации Nextcloud

### Readiness Probe (Проба готовности)
```yaml
readinessProbe:
  httpGet:
    path: /status.php
    port: 80
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```
- Проверяет готовность контейнера принимать трафик
- Если проверка не проходит - под исключается из Service (не получает трафик)
- Более частая проверка (каждые 10 секунд)

---

