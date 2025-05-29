import os
import logging
import random
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# env setup
load_dotenv()

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor()
        self.init_database()

    def init_database(self):
        # main table setup
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT,
                username VARCHAR(255),
                blue_count INT DEFAULT 0,
                red_count INT DEFAULT 0,
                sosal_count BIGINT DEFAULT 0,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # /clear timer setup
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS season_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                last_clear TIMESTAMP,
                current_season INT DEFAULT 0
            )
        ''')
        self.connection.commit()

    def get_or_create_user(self, user_id, username):
        self.cursor.execute(
            "SELECT * FROM statistics WHERE user_id = %s",
            (user_id,)
        )
        result = self.cursor.fetchone()
        if not result:
            self.cursor.execute(
                "INSERT INTO statistics (user_id, username) VALUES (%s, %s)",
                (user_id, username)
            )
            self.connection.commit()

    async def update_run_stats(self, user_id, username, is_blue):
        self.get_or_create_user(user_id, username)
        field = 'blue_count' if is_blue else 'red_count'
        self.cursor.execute(
            f"UPDATE statistics SET {field} = {field} + 1 WHERE user_id = %s",
            (user_id,)
        )
        self.connection.commit()

    async def get_stats(self):
        self.cursor.execute(
            "SELECT username, blue_count, red_count FROM statistics WHERE blue_count > 0 OR red_count > 0"
        )
        return self.cursor.fetchall()

    async def update_sosal(self, user_id, username):
        self.get_or_create_user(user_id, username)
        self.cursor.execute(
            "UPDATE statistics SET sosal_count = sosal_count + 1 WHERE user_id = %s",
            (user_id,)
        )
        self.connection.commit()

    async def get_sosal_count(self, user_id):
        self.cursor.execute(
            "SELECT sosal_count FROM statistics WHERE user_id = %s",
            (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    async def multiply_sosal(self, user_id):
        self.cursor.execute(
            "UPDATE statistics SET sosal_count = sosal_count * 2 WHERE user_id = %s",
            (user_id,)
        )
        self.connection.commit()

    async def can_clear_season(self):
        self.cursor.execute("SELECT last_clear FROM season_info ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        if not result:
            return True
        last_clear = result[0]
        return datetime.now() - last_clear >= timedelta(days=90)

    async def clear_season(self):
        # get current season name
        self.cursor.execute("SELECT current_season FROM season_info ORDER BY id DESC LIMIT 1")
        result = self.cursor.fetchone()
        current_season = 1 if not result else result[0] + 1

        # new season table setup
        self.cursor.execute(f'''
            CREATE TABLE season_{current_season} AS
            SELECT * FROM statistics
        ''')

        # clearing current stats
        self.cursor.execute("TRUNCATE TABLE statistics")

        # updating season info
        self.cursor.execute('''
            INSERT INTO season_info (last_clear, current_season)
            VALUES (CURRENT_TIMESTAMP, %s)
        ''', (current_season,))
        
        self.connection.commit()
        return current_season

    async def get_season_stats(self, season_number):
        self.cursor.execute(f"SHOW TABLES LIKE 'season_{season_number}'")
        if not self.cursor.fetchone():
            return None
        
        self.cursor.execute(
            f"SELECT username, blue_count, red_count FROM season_{season_number} "
            "WHERE blue_count > 0 OR red_count > 0"
        )
        return self.cursor.fetchall()

class TelegramBot:
    def __init__(self):
        self.db = Database()
        self.app = Application.builder().token(os.getenv('BOT_TOKEN')).build()
        self.setup_handlers()

    def setup_handlers(self):
        self.app.add_handler(CommandHandler("run", self.run_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        self.app.add_handler(CommandHandler("sosal", self.sosal_command))
        self.app.add_handler(CommandHandler("nesosal", self.nesosal_command))
        self.app.add_handler(CommandHandler("clear", self.clear_command))
        self.app.add_handler(CommandHandler("admclear", self.admclear_command))
        self.app.add_handler(CommandHandler("seasons", self.seasons_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_season_selection))

    async def run_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_members = await context.bot.get_chat_administrators(update.effective_chat.id)
        members = [(member.user.id, member.user.username or member.user.first_name) for member in chat_members]
        
        if len(members) < 2:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Недостаточно участников в группе!"
            )
            return

        blue_user, red_user = random.sample(members, 2)

        # krasavchik roll ## blue
        messages = ["КРУТИМ БАРАБАН🥁", "Гадаем на бинарных опционах📊", "Анализируем лунный гороскоп🌚", "Лунная призма дай мне силу💫", "Сектор приз на барабане🎯"]
        for msg in messages:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
            await asyncio.sleep(1)

        blue_mention = f"@{blue_user[1]}" if blue_user[1] else blue_user[1]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🎉Красавчик сегодня - {blue_mention}🥳"
        )
        await self.db.update_run_stats(blue_user[0], blue_user[1], True)

        await asyncio.sleep(1)

        # pidor roll ## red
        messages = ["⚠️ВНИМАНИЕ⚠️", "ФЕДЕРАЛЬНЫЙ🔍РОЗЫСК🚨ПИДОРА", "Спутник запущен🚀", "Сводки👮Интерпола🚔проверены", "Твой🫵профиль в соцсетях👥проанализирован😨"]
        for msg in messages:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
            await asyncio.sleep(1)

        red_mention = f"@{red_user[1]}" if red_user[1] else red_user[1]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🏳‍🌈Сегодня ПИДОР ДНЯ - {red_mention}👬"
        )
        await self.db.update_run_stats(red_user[0], red_user[1], False)

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        stats = await self.db.get_stats()
        
        blue_stats = "🥳Статистика красавчиков:\n" + "\n".join(
            f"{username}: {blue_count}" for username, blue_count, _ in stats if blue_count > 0
        )
        
        red_stats = "👬Самые сексуальные ПИДОРЫ:\n" + "\n".join(
            f"{username}: {red_count}" for username, _, red_count in stats if red_count > 0
        )

        await context.bot.send_message(chat_id=update.effective_chat.id, text=blue_stats)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=red_stats)

    async def sosal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await self.db.update_sosal(user.id, user.username or user.first_name)
        count = await self.db.get_sosal_count(user.id)
        
        formatted_count = f"{count:,}".replace(",", " ")
        mention = f"@{user.username}" if user.username else user.first_name
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Уважаемый {mention} сосал {formatted_count} раз(а)"
        )

    async def nesosal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await self.db.multiply_sosal(user.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="За пиздёж взял два 🍆 в рот."
        )

    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self.db.can_clear_season():
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Очистка сезона возможна только раз в 90 дней!"
            )
            return

        season_number = await self.db.clear_season()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Сезон №{season_number} запущен! Статистика сброшена."
        )

    async def admclear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.username != os.getenv('ADMIN_USERNAME'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="У вас нет прав для выполнения этой команды!"
            )
            return

        season_number = await self.db.clear_season()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"season force-cleared. season num: {season_number}"
        )

    async def seasons_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['waiting_for_season'] = True
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите номер сезона"
        )

    async def handle_season_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.user_data.get('waiting_for_season'):
            return

        try:
            season_number = int(update.message.text)
            stats = await self.db.get_season_stats(season_number)
            
            if stats is None:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Такого сезона не существует"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Введите номер сезона"
                )
                return

            blue_stats = "🥳Статистика красавчиков:\n" + "\n".join(
                f"{username}: {blue_count}" for username, blue_count, _ in stats if blue_count > 0
            )
            
            red_stats = "👬Самые сексуальные ПИДОРЫ:\n" + "\n".join(
                f"{username}: {red_count}" for username, _, red_count in stats if red_count > 0
            )

            await context.bot.send_message(chat_id=update.effective_chat.id, text=blue_stats)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=red_stats)
            
            context.user_data['waiting_for_season'] = False
            
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Пожалуйста, введите корректный номер сезона"
            )

    def run(self):
        self.app.run_polling()

if __name__ == '__main__':
    bot = TelegramBot()
    bot.run() 
