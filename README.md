# Telegram Bot

Бот для Telegram с функциями случайного выбора участников и ведения статистики.

## Требования

- Docker
- Docker Compose
- mysql-server
- python3

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/kzarkaPY/GayOfTheDay/edit/main
cd telegram_bot
```

2. Создайте файл `.env`:
```bash
nano .env
```

3. Отредактируйте файл `.env` и укажите необходимые значения:
- BOT_TOKEN - токен вашего Telegram бота (получите у @BotFather)
- DB_USER - имя пользователя базы данных
- DB_PASSWORD - пароль для базы данных
- DB_NAME - имя базы данных
- ADMIN_USERNAME - имя пользователя администратора (для команды /admclear)

4. Запустите контейнеры:
```bash
docker-compose up -d
```

## Команды бота

- `/run` - случайный выбор двух участников группы
- `/stats` - показать статистику выборов
- `/sosal` - подсчет использования команды для пользователя
- `/nesosal` - умножение результата команды /sosal на 2
- `/clear` - очистка текущей статистики и создание нового сезона (раз в 90 дней)
- `/admclear` - принудительная очистка статистики (только для администратора)
- `/seasons` - просмотр статистики предыдущих сезонов

## Обслуживание

- Для просмотра логов:
```bash
docker-compose logs -f
```

- Для перезапуска:
```bash
docker-compose restart
```

- Для остановки:
```bash
docker-compose down
```

## Резервное копирование

Данные базы данных сохраняются в Docker volume `db_data`. Для создания резервной копии используйте:

```bash
docker-compose exec db mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > backup.sql
```

Для восстановления:

```bash
cat backup.sql | docker-compose exec -T db mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME
``` 
