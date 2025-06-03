# Gay of the Day Bot

Telegram bot that randomly selects users from a group chat and maintains statistics across seasons.

## Features

- Random user selection with `/run` and `/pidor` commands
- Season-based statistics tracking
- User interaction tracking with `/sosal` and `/nesosal` commands
- Historical season data viewing
- Admin controls for season management

## Requirements

- Python 3.11+
- PostgreSQL
- Docker and Docker Compose

## Setup

1. Create a `.env` file in the project root with the following content:
```
BOT_TOKEN=your_telegram_bot_token
ADMIN_USER=you_admin_user
DB_HOST=db
DB_PORT=5432
DB_NAME=gayoftheday
DB_USER=postgres
DB_PASSWORD=your_password
```

2. Build and run the containers:
```bash
docker-compose up -d --build
```

## Commands

- `/run` - Select a random user as "красавчик дня" (once per day)
- `/pidor` - Select a random user as "pidor дня" (once per day)
- `/sosal` - Increment user's "sosal" counter (once per hour)
- `/nesosal` - Double user's "sosal" counter (once per hour)
- `/stats` - Show current season statistics
- `/sostats` - Show current season "sosal" statistics
- `/clear` - Start a new season (90 days cooldown)
- `/admclear` - Force start a new season (admin only)
- `/seasons` - View historical season statistics
- `/soseasons` - View historical season "sosal" statistics

## Deployment

1. Clone the repository to your Ubuntu server
2. Make sure Docker and Docker Compose are installed
3. Create the `.env` file with your configuration
4. Run `docker-compose up -d` to start the bot
5. The bot will automatically create all necessary database tables on first run

## Notes

- The bot uses Moscow timezone (Europe/Moscow) for all time-based operations
- Season statistics are preserved when starting a new season
- Only the last 8 seasons are shown in the seasons menu
- Commands that select random users have a 1.5-second delay between messages to avoid Telegram's rate limits

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
