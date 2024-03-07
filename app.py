from telegram import update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


async def start_command(update, context):
    await update.message.reply_text('Привет')


async def error(update, context):
    print(f'{update} with error {context.error}')


def run_bot(token):
    app = Application.builder().token(token).build()

    app.add_handler(start_command)

    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=1)
