- `app.py`: простое flask приложение.
- `requirements.txt`: зависимости python.
- `Dockerfile.bad`: плохой Dockerfile.
- `Dockerfile.good`: хороший Dockerfile.

### Что плохого в `Dockerfile.bad`
1.  тег `latest`
2.  запуск от root
3.  несколько `RUN` инструкций
4.  `COPY . .` до установки зависимостей
5.  включает ненужные инструменты

### Что хорошего в `Dockerfile.good`
1.  не использует тег latest
2.  запуск не от root
3.  объединенная run инструкция 
4. оптимизация кэширования слоев. копирует `requirements.txt` и устанавливает зависимости до копирования остального кода
5.  `.dockerignore`

### Плохие практики использования контейнеров
1.  **Отношение к контейнерам как к виртуальным машинам**: Подключение по SSH внутрь контейнеров для перезапуска сервисов или ручного исправления кода.
    Контейнеры должны быть неизменяемыми. Если меняется конфигурация или код, нужно собрать новый образ и заменить контейнер.
2.  **Хранение постоянных данных внутри записываемого слоя контейнера**: Запись файлов базы данных или логов напрямую в файловую систему контейнера без использования томов.
    Данные теряются при удалении контейнера.


## как пользоваться

### bad container:
```bash
docker build -f Dockerfile.bad -t bad-app .
docker run -d -p 8080:5000 --name bad-container bad-app
```

### good container:
```bash
# создаем директорию для volume
mkdir -p data
echo "This is important data from the host!" > data/info.txt

docker build -f Dockerfile.good -t good-app .

docker run -d -p 8081:5000 \
  -v $(pwd)/data:/app/data \
  --name good-container \
  good-app
```