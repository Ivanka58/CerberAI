import os
import logging
import random
import string
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import db

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME')

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def generate_unique_link():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    if args:
        unique_link = args[0]
        code = generate_code()
        
        db.create_telegram_code(code, unique_link)
        
        await update.message.reply_text(
            f"🔐 Код для входа в CerberAI:\n\n"
            f"<code>{code}</code>\n\n"
            f"Введите этот код на сайте для авторизации.\n"
            f"Код действителен 10 минут.",
            parse_mode='HTML'
        )
        
        logger.info(f"Generated code {code} for user {user.id}")
    else:
        keyboard = [
            [InlineKeyboardButton("🔓 Войти в CerberAI", url=f"https://t.me/{BOT_USERNAME}?start={generate_unique_link()}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"Я бот авторизации для CerberAI — AI с памятью и 50+ моделями.\n\n"
            f"Нажми кнопку ниже, чтобы получить код для входа:",
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Доступные команды:\n\n"
        "/start — Получить код для входа\n"
        "/help — Помощь\n"
        "/status — Статус авторизации\n\n"
        "Для входа на сайт нажмите кнопку в сообщении бота "
        "и введите полученный 6-значный код на сайте."
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    db_user = db.get_user_by_telegram_id(user.id)
    
    if db_user:
        days = db_user['days_count']
        created = db_user['created_at'].strftime('%d.%m.%Y')
        
        await update.message.reply_text(
            f"✅ Вы авторизованы в CerberAI\n\n"
            f"👤 Имя: {db_user['first_name'] or db_user['username']}\n"
            f"📅 Регистрация: {created}\n"
            f"📊 Дней с нами: {days}\n\n"
            f"Для входа на сайт используйте кнопку /start"
        )
    else:
        await update.message.reply_text(
            "❌ Вы ещё не авторизованы в CerberAI\n\n"
            "Нажмите /start, чтобы получить код для входа."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я принимаю только команды.\n"
        "Используйте /start для получения кода входа."
    )

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
