import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

from db import get_texts, get_qtickets


filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# States
NUM_STATES = 5
DISPATCH, VIEWER, END, SINGER, BAND = range(0, NUM_STATES)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s %s started the conversation.", user.first_name, user.last_name)

    keyboard = [
        [
            InlineKeyboardButton("Прийти зрителем", callback_data=str(VIEWER)),
            InlineKeyboardButton("Спеть", callback_data=str(SINGER)),
            InlineKeyboardButton("Быть в хом-бэнде", callback_data=str(BAND)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_texts(DISPATCH)
    await update.message.reply_text(f"{text}", reply_markup=reply_markup)

    return DISPATCH


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Прийти зрителем", callback_data=str(VIEWER)),
            InlineKeyboardButton("Спеть", callback_data=str(VIEWER)),
            InlineKeyboardButton("Быть в хом-бэнде", callback_data=str(VIEWER)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_texts(DISPATCH)
    await query.edit_message_text(text=f"{text}", reply_markup=reply_markup)

    return DISPATCH


async def viewer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("Ок", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_texts(VIEWER)
    text = text.replace('$', get_qtickets())
    await query.edit_message_text(
        text=f"{text}", reply_markup=reply_markup
    )

    return END


async def singer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("В другой раз", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_texts(SINGER)
    text = text.replace('$', get_qtickets())
    await query.edit_message_text(
        text=f"{text}", reply_markup=reply_markup
    )

    return END


async def band(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("В другой раз", callback_data=str(END)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = get_texts(BAND)
    await query.edit_message_text(
        text=f"{text}", reply_markup=reply_markup
    )

    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = get_texts(END)
    await query.edit_message_text(text=f"{text}")

    return ConversationHandler.END


async def error(update, context):
    print(f'{update} with error {context.error}')


def run_bot(token):
    app = Application.builder().token(token).concurrent_updates(False).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DISPATCH: [
                CallbackQueryHandler(viewer, pattern="^" + str(VIEWER) + "$"),
                CallbackQueryHandler(singer, pattern="^" + str(SINGER) + "$"),
                CallbackQueryHandler(band, pattern="^" + str(BAND) + "$"),
            ],
            END: [
                CallbackQueryHandler(start_over, pattern="^" + str("123") + "$"),
                CallbackQueryHandler(end),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_error_handler(error)

    app.add_handler(conv_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)
