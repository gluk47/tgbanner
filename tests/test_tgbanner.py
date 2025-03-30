import datetime
import pytest

from unittest.mock import AsyncMock, MagicMock

from tg_calls import delete_casino_messages
from main import parse_timedelta
import config
import robots

BANNED = [
    'kazino', 'kaзиNo', 'kaзиho', 'кaзиNo',
    'cмотри бuo',
    '0бнажёночки',
    'Hyжны люди',
    'Bceм привет',

    'пρедлагаю ρаботу', 'пρедлагаем ρаботу', 'ищу водителя',
    'помогу с деньгами', 'помогу с финансами',

    'uнтuм', 'ᴄᴧиʙы', 'ᴛʙᴏᴇᴦᴏ', 'интим04ки', 'инᴛиʍᴏчᴋи',
    'ᴏбнᴀжᴇнᴋи', 'ɯʍᴀᴩы', 'обнажёно4ки',
    'full video',
    'пробей женщину',
    'пробей любую девушку',
    'раздень любую девушку',
    'строго 18+', 'чат 18+',

    'пиши + в лс', 'пишите + в лс', 'пиши в лс', 'пишите в лс',
]

NON_BANNED = [
    'Пошли на Фрушку',
    'строго 18',
]


def test_make_re():
    re = config.make_re({'adult': [r'строго 18\+']})
    assert re.match('строго 18+') is not None


def load():
    mock_message = AsyncMock()
    config.load('../config.yaml')
    return mock_message


def setup_mocks(mock_message, text):
    mock_message.text = text
    mock_message.caption = None
    mock_message.delete = AsyncMock()

    mock_update = MagicMock()
    mock_update.message = mock_message
    mock_update.edited_message = None

    mock_context = MagicMock()
    mock_context.bot_data = {"robot_banner": robots.RobotBanner()}
    mock_context.bot = MagicMock()
    mock_context.bot.ban_chat_member = AsyncMock()

    return mock_update, mock_context


@pytest.mark.asyncio
async def test_delete_casino_messages_banned():
    mock_message = load()
    for query in BANNED:
        mock_update, mock_context = setup_mocks(mock_message, query)
        await delete_casino_messages(mock_update, mock_context)
        assert \
            mock_message.delete.call_count == 1, \
            f"Message with text '{query}' was not deleted as expected"
        mock_message.delete.reset_mock()


@pytest.mark.asyncio
async def test_delete_casino_messages_non_banned():
    mock_message = load()
    for query in NON_BANNED:
        mock_update, mock_context = setup_mocks(mock_message, query)
        await delete_casino_messages(mock_update, mock_context)
        assert \
            mock_message.delete.call_count == 0, \
            f"Message with text '{query}' was incorrectly deleted"


def test_parse_timedelta():
    assert parse_timedelta('1s') == datetime.timedelta(seconds=1)
    assert parse_timedelta('1m') == datetime.timedelta(minutes=1)
    assert parse_timedelta('1h') == datetime.timedelta(hours=1)
    assert parse_timedelta('1d') == datetime.timedelta(days=1)
    assert parse_timedelta('1d 2h 3m 4s') == datetime.timedelta(
        days=1, hours=2, minutes=3, seconds=4)
    assert parse_timedelta('2d 3h 4m 5s') == datetime.timedelta(
        days=2, hours=3, minutes=4, seconds=5)
