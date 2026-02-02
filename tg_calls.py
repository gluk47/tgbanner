from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from telegram.error import NetworkError, TimedOut, TelegramError

import asyncio
import logging

import config
from text import normalize

logger = logging.getLogger("banhammer")


def join_filter(data, sep=' ') -> str:
    return sep.join([_ for _ in data if _])


def extract_user_name(msg) -> str:
    try:
        user = msg.from_user
        return join_filter([
            msg.from_user.first_name,
            msg.from_user.last_name,
            msg.from_user.username,
            str(msg.from_user.id),
        ])
    except Exception as x:
        return ''


def extract_forward(msg) -> str:
    try:
        fwd = msg.forward_origin
        return join_filter([fwd.chat.title, fwd.chat.username])
    except Exception:
        return ''


def extract_keyboard_labels(msg) -> str:
    try:
        markup = msg.reply_markup.inline_keyboard
        labels = join_filter([b[0].text for b in markup], sep='; ')
        return labels
    except Exception as x:
        return ''


async def error_handler(update: Update, context: CallbackContext):
    try:
        raise context.error
    except TelegramError as e:
        print(f"Telegram error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


async def with_retries(f):
    sleep = .2
    backoff = 1.2
    for attempt in range(10):
        try:
            await f()
            return
        except (NetworkError, TimedOut) as e:
            print(f'... {e}')
            await asyncio.sleep(sleep)
            sleep *= backoff


def is_username_joined_message(msg):
    """Check if this is a system message about a user joining with a username."""
    if not msg.new_chat_members:
        return False

    logging.info('New chat members:', msg.new_chat_members)
    for member in msg.new_chat_members:
        if member.username:
            return True
    return False


async def delete_casino_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # print(f'+++ +++\n{update}\n--- ---\n')
    try:
        msg = update.message or update.edited_message

        chat_config = config.get_chat_config(msg.chat.id)
        chat_name = msg.chat.title or 'Private message'
        user = extract_user_name(msg)

        if msg.chat.id:
            chat_name += f' ({msg.chat.id})'

        if chat_config.get('clean_system_messages', False) and is_username_joined_message(msg):
            logger.info(f'{chat_name}: Deleting {user} joined message')
            await with_retries(msg.delete)
            return

        txt_orig = msg.text or msg.caption
        kb = extract_keyboard_labels(msg)
        forward = extract_forward(msg)
        txt_orig = join_filter([user, forward, txt_orig, kb], sep='; ')
        if not txt_orig:
            logger.info(f'Got a non-text message: {update}')
            return
        txt = normalize(txt_orig)
    except Exception as ex:
        logger.exception(ex)
        logger.info(f'Got a non-text message: {update}')
        return

    re_match = config.BLACKLIST_RE.search(txt)
    if re_match:
        logger.info(
            f'[{re_match.group(0)}] {chat_name}: Deleting: {txt_orig}'
        )
        await with_retries(msg.delete)

        robot_banner = context.bot_data.get("robot_banner")
        await robot_banner.message_erased(msg, context)

    else:
        logger.info(f'{chat_name}: Got {txt_orig}')
