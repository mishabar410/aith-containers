# ЛР 3. Kubernetes - Развертывание Nextcloud на PostgreSQL

## Описание

В данной лабораторной работе развернут веб-сервис Nextcloud с использованием базы данных PostgreSQL в кластере Kubernetes (minikube).

### Выполненные модификации

Согласно заданию, были внесены следующие изменения в исходные манифесты:

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
1. **Зависимости ресурсов**: Deployment ссылается на ConfigMap и Secret через `configMapRef` и `secretRef`. Если эти ресурсы не существуют на момент создания пода, он не сможет запуститься и перейдет в состояние ошибки (например, `CreateContainerConfigError`).

2. **Service → Deployment**: Хотя Service можно создать до Deployment, логичнее сначала создать Deployment, чтобы Service сразу обнаружил целевые поды.

3. **Nextcloud → PostgreSQL**: Nextcloud зависит от PostgreSQL. Если БД недоступна при запуске Nextcloud, сервис не сможет корректно инициализироваться.

**Рекомендуемый порядок:**
1. Secrets и ConfigMaps (нет внешних зависимостей)
2. Services (для обеспечения DNS-резолвинга)
3. Deployments (используют все вышеперечисленное)

### Вопрос 2: Что произойдет, если отскейлить postgres-deployment в 0, затем обратно в 1, и попробовать зайти на Nextcloud?

**Произойдет потеря данных и возможные ошибки.**

Подробнее:
1. **Масштабирование в 0**: Под PostgreSQL удаляется вместе со всеми данными (т.к. используется ephemeral storage - данные хранятся внутри контейнера, а не в PersistentVolume).

2. **Масштабирование обратно в 1**: Создается новый под PostgreSQL с чистой базой данных. Все таблицы и данные Nextcloud (пользователи, файлы, настройки) будут потеряны.

3. **Попытка зайти на Nextcloud**: 
   - Nextcloud не найдет свои таблицы в БД
   - Возможно, запустится повторная инициализация
   - Или появится ошибка подключения к БД
   - Все ранее загруженные файлы и созданные пользователи будут потеряны

**Решение**: Для production-среды необходимо использовать **PersistentVolume (PV)** и **PersistentVolumeClaim (PVC)** для хранения данных PostgreSQL вне жизненного цикла пода.

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

## Удаление ресурсов

```bash
kubectl delete deployment nextcloud postgres
kubectl delete service nextcloud postgres-service
kubectl delete configmap nextcloud-configmap postgres-configmap
kubectl delete secret nextcloud-secret postgres-secret
```

Или удалить всё через манифесты:
```bash
kubectl delete -f .
```
