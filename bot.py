import os
import random
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from sqlalchemy.orm import Session
from sqlalchemy import func
import pytz

from models import (
    init_db, get_db, User, Season, SeasonStats, 
    CommandUsage, SeasonControl, SessionLocal
)

load_dotenv()

MOSCOW_TZ = pytz.timezone('Europe/Moscow')
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_USER = os.getenv('ADMIN_USER')

async def check_command_cooldown(chat_id: int, command: str, cooldown_hours: int) -> bool:
    db = SessionLocal()
    try:
        last_usage = db.query(CommandUsage).filter(
            CommandUsage.chat_id == chat_id,
            CommandUsage.command == command
        ).first()

        if not last_usage:
            return True

        moscow_now = datetime.now(MOSCOW_TZ)
        if command in ['/run', '/pidor']:
            # Reset at midnight Moscow time
            last_midnight = moscow_now.replace(hour=0, minute=0, second=0, microsecond=0)
            if last_usage.last_used.astimezone(MOSCOW_TZ) < last_midnight:
                return True
        else:
            # Other commands use hour-based cooldown
            if last_usage.last_used.astimezone(MOSCOW_TZ) < moscow_now - timedelta(hours=cooldown_hours):
                return True

        return False
    finally:
        db.close()

async def update_command_usage(chat_id: int, command: str):
    db = SessionLocal()
    try:
        usage = db.query(CommandUsage).filter(
            CommandUsage.chat_id == chat_id,
            CommandUsage.command == command
        ).first()

        moscow_now = datetime.now(MOSCOW_TZ)
        if usage:
            usage.last_used = moscow_now
        else:
            usage = CommandUsage(
                chat_id=chat_id,
                command=command,
                last_used=moscow_now
            )
            db.add(usage)
        
        db.commit()
    finally:
        db.close()

async def get_random_user(update: Update) -> tuple:
    chat_members = await update.effective_chat.get_member_count()
    if chat_members <= 1:
        return None, None

    while True:
        random_offset = random.randint(0, chat_members - 1)
        try:
            member = await update.effective_chat.get_member(
                user_id=(await update.effective_chat.get_administrators())[random_offset].user.id
            )
            if not member.user.is_bot:
                return member.user.id, member.user.username
        except IndexError:
            continue

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_command_cooldown(update.effective_chat.id, '/run', 24):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Красавчик уже был выбран сегодня, приходите завтра"
        )
        return

    messages = ["КРУТИМ БАРАБАН🥁", "Гадаем на бинарных опционах📊", "Анализируем лунный гороскоп🌚", "Лунная призма дай мне силу💫", "Сектор приз на барабане🎯"]
    
    for msg in messages:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg
        )
        await asyncio.sleep(1.5)

    user_id, username = await get_random_user(update)
    if not user_id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Недостаточно участников в чате"
        )
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, username=username, run_count=1)
            db.add(user)
        else:
            user.run_count += 1
            user.username = username

        season_control = db.query(SeasonControl).first()
        if not season_control:
            season_control = SeasonControl(current_season=1, is_active=True)
            db.add(season_control)
            
            season = Season(
                season_number=1,
                start_date=datetime.now(MOSCOW_TZ)
            )
            db.add(season)
        
        db.commit()
        await update_command_usage(update.effective_chat.id, '/run')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🎉Красавчик сегодня - @{username}🥳"
        )
    finally:
        db.close()

async def pidor_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_command_cooldown(update.effective_chat.id, '/pidor', 24):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="^^^Пидор сверху^^^"
        )
        return

    messages = ["⚠️ВНИМАНИЕ⚠️", "ФЕДЕРАЛЬНЫЙ🔍РОЗЫСК🚨ПИДОРА", "Спутник запущен🚀", "Сводки👮Интерпола🚔проверены", "Твой🫵профиль в соцсетях👥проАНАЛизирован😨"]
    
    for msg in messages:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg
        )
        await asyncio.sleep(1.5)

    user_id, username = await get_random_user(update)
    if not user_id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Недостаточно участников в чате"
        )
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, username=username, pidor_count=1)
            db.add(user)
        else:
            user.pidor_count += 1
            user.username = username

        season_control = db.query(SeasonControl).first()
        if not season_control:
            season_control = SeasonControl(current_season=1, is_active=True)
            db.add(season_control)
            
            season = Season(
                season_number=1,
                start_date=datetime.now(MOSCOW_TZ)
            )
            db.add(season)
        
        db.commit()
        await update_command_usage(update.effective_chat.id, '/pidor')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🏳️‍🌈Сегодня ПИДОР ДНЯ - @{username}👬"
        )
    finally:
        db.close()

async def sosal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_command_cooldown(update.effective_chat.id, '/sosal', 1):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Команду можно использовать только раз в час"
        )
        return

    user_id = update.effective_user.id
    username = update.effective_user.username

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, username=username, sosal_count=1)
            db.add(user)
        else:
            user.sosal_count += 1
            user.username = username

        db.commit()
        await update_command_usage(update.effective_chat.id, '/sosal')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"@{username} сосал {user.sosal_count} раз(а)"
        )
    finally:
        db.close()

async def nesosal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_command_cooldown(update.effective_chat.id, '/nesosal', 1):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Команду можно использовать только раз в час"
        )
        return

    user_id = update.effective_user.id
    username = update.effective_user.username

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Сначала нужно хотя бы раз пососать))"
            )
            return

        user.sosal_count *= 2
        user.username = username
        db.commit()
        
        await update_command_usage(update.effective_chat.id, '/nesosal')
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"@{username} пиздабол, который отсосал {user.sosal_count} раз(а)"
        )
    finally:
        db.close()

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        run_stats = db.query(User).filter(User.run_count > 0).order_by(User.run_count.desc()).all()
        pidor_stats = db.query(User).filter(User.pidor_count > 0).order_by(User.pidor_count.desc()).all()

        if not run_stats and not pidor_stats:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Статистика пуста"
            )
            return

        if run_stats:
            run_message = "🏆Топ красавчиков дня🏆:\n"
            for i, user in enumerate(run_stats, 1):
                run_message += f"{i}. @{user.username}: {user.run_count}\n"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=run_message
            )

        if pidor_stats:
            pidor_message = "🍆Каждый из них ебался в жопу🍆:\n"
            for i, user in enumerate(pidor_stats, 1):
                pidor_message += f"{i}. @{user.username}: {user.pidor_count} раз(а)\n"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=pidor_message
            )
    finally:
        db.close()

async def sostats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        sosal_stats = db.query(User).filter(User.sosal_count > 0).order_by(User.sosal_count.desc()).all()

        if not sosal_stats:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Статистика пуста"
            )
            return

        message = "Сосущий ТОП:\n"
        for i, user in enumerate(sosal_stats, 1):
            message += f"{i}. @{user.username}: {user.sosal_count} раз(а)\n"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message
        )
    finally:
        db.close()

async def clear_season(update: Update, context: ContextTypes.DEFAULT_TYPE, force: bool = False):
    db = SessionLocal()
    try:
        season_control = db.query(SeasonControl).first()
        if not season_control:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Сезон еще не начался"
            )
            return

        moscow_now = datetime.now(MOSCOW_TZ)
        if not force:
            if not season_control.last_clear:
                season_control.last_clear = moscow_now - timedelta(days=91)
            
            days_since_last_clear = (moscow_now - season_control.last_clear.astimezone(MOSCOW_TZ)).days
            if days_since_last_clear < 90:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Сброс сезона возможен через {90 - days_since_last_clear} дней"
                )
                return

        # Save current season stats
        current_season = season_control.current_season
        users = db.query(User).all()
        
        for user in users:
            if user.run_count > 0 or user.pidor_count > 0 or user.sosal_count > 0:
                season_stat = SeasonStats(
                    season_id=current_season,
                    user_id=user.user_id,
                    username=user.username,
                    run_count=user.run_count,
                    pidor_count=user.pidor_count,
                    sosal_count=user.sosal_count
                )
                db.add(season_stat)

        # Update season control
        season_control.current_season += 1
        season_control.last_clear = moscow_now
        season_control.is_active = False

        # Reset current stats
        for user in users:
            user.run_count = 0
            user.pidor_count = 0
            user.sosal_count = 0

        db.commit()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Сезон {current_season} завершен"
        )
    finally:
        db.close()

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await clear_season(update, context, force=False)

async def admclear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USER:
        await update.message.reply_text("Команда доступна только администратору")
        return
    
    await clear_season(update, context, force=True)

async def create_season_keyboard(seasons_count: int):
    keyboard = []
    row = []
    for i in range(max(1, seasons_count - 7), seasons_count + 1):
        row.append(InlineKeyboardButton(f"Сезон {i}", callback_data=f"season_{i}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(keyboard)

async def seasons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        season_control = db.query(SeasonControl).first()
        if not season_control or season_control.current_season == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Нет завершенных сезонов"
            )
            return

        keyboard = await create_season_keyboard(season_control.current_season)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите сезон:",
            reply_markup=keyboard
        )
    finally:
        db.close()

async def soseasons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    try:
        season_control = db.query(SeasonControl).first()
        if not season_control or season_control.current_season == 0:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Нет завершенных сезонов"
            )
            return

        keyboard = await create_season_keyboard(season_control.current_season)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите сезон для просмотра статистики сосунов:",
            reply_markup=keyboard
        )
    finally:
        db.close()

async def handle_season_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("Отменено")
        return

    season_number = int(query.data.split("_")[1])
    db = SessionLocal()
    try:
        if "сосунов" in query.message.text:
            # Handle soseasons stats
            stats = db.query(SeasonStats).filter(
                SeasonStats.season_id == season_number,
                SeasonStats.sosal_count > 0
            ).order_by(SeasonStats.sosal_count.desc()).all()

            if not stats:
                await query.edit_message_text(f"Нет статистики сосунов для сезона {season_number}")
                return

            message = f"Статистика сосунов сезона {season_number}:\n"
            for i, stat in enumerate(stats, 1):
                message += f"{i}. @{stat.username}: {stat.sosal_count}\n"
        else:
            # Handle regular seasons stats
            run_stats = db.query(SeasonStats).filter(
                SeasonStats.season_id == season_number,
                SeasonStats.run_count > 0
            ).order_by(SeasonStats.run_count.desc()).all()

            pidor_stats = db.query(SeasonStats).filter(
                SeasonStats.season_id == season_number,
                SeasonStats.pidor_count > 0
            ).order_by(SeasonStats.pidor_count.desc()).all()

            if not run_stats and not pidor_stats:
                await query.edit_message_text(f"Нет статистики для сезона {season_number}")
                return

            message = f"Статистика сезона {season_number}:\n\n"
            
            if run_stats:
                message += "🎉Топ красавчиков:\n"
                for i, stat in enumerate(run_stats, 1):
                    message += f"{i}. @{stat.username}: {stat.run_count}\n"
                message += "\n"

            if pidor_stats:
                message += "🏳️‍🌈Топ пидоров:\n"
                for i, stat in enumerate(pidor_stats, 1):
                    message += f"{i}. @{stat.username}: {stat.pidor_count}\n"

        await query.edit_message_text(message)
    finally:
        db.close()

def main():
    init_db()
    
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("pidor", pidor_command))
    application.add_handler(CommandHandler("sosal", sosal_command))
    application.add_handler(CommandHandler("nesosal", nesosal_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("sostats", sostats_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("admclear", admclear_command))
    application.add_handler(CommandHandler("seasons", seasons_command))
    application.add_handler(CommandHandler("soseasons", soseasons_command))
    application.add_handler(CallbackQueryHandler(handle_season_callback))

    application.run_polling()

if __name__ == "__main__":
    main()
