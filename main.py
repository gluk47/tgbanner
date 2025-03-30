#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram.ext import ApplicationBuilder, MessageHandler, filters

import argparse
import datetime
import logging
import os

import config
import robots
import tg_calls

logger = logging.getLogger("banhammer")
def setup_logger():
    logger.setLevel(logging.INFO)
    h = logging.StreamHandler()
    h.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S %Z')
    )
    logger.addHandler(h)
setup_logger()

def parse_timedelta(delta: str):
    units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}
    kwargs = {}

    value_start = 0
    delta = delta.strip().lower()
    i = 0
    for i, c in enumerate(delta):
        if c.isalpha() and c.isascii():
            try:
                unit = units[c]
            except KeyError:
                raise ValueError(f"invalid unit {c!r}")
            kwargs[unit] = int(delta[value_start:i])
            value_start = i + 1
        elif c.isspace():
            pass
        elif c.isdigit():
            pass
        else:
            # Unknown character
            raise ValueError(f"Invalid character {c!r} in time delta: {delta!r}")
    if delta[-1].isdigit():
        kwargs['seconds'] = int(delta[value_start:])

    return datetime.timedelta(**kwargs)

def main():
    parser = argparse.ArgumentParser(
        description='Telegram bot to delete casino messages. '
        'If a user sends more than a limit messages in a time window, s/he will be banned.'
    )
    parser.add_argument('-t', '--token', default=None, help='Telegram bot token')
    parser.add_argument('-c', '--config', help='Path to the config file', default='config.yaml')
    parser.add_argument('-l', '--loglevel', help='Set log level', default='INFO')
    parser.add_argument(
        '-w', '--window',
        help='Time window for banhammer, seconds or a string like "1d 2h 3m 4s"',
        default='1h',
        type=parse_timedelta
    )
    parser.add_argument('-m', '--limit', help='Spam message limit for banhammer', default=3, type=int)
    args = parser.parse_args()

    logger.setLevel(args.loglevel)

    API_TOKEN, config.BLACKLIST_RE = config.load(args.config)
    API_TOKEN = args.token or API_TOKEN or os.environ.get('API_TOKEN')

    config.start_watcher(args.config)
    if not API_TOKEN:
        raise ValueError(
            'API token is required. Use -t, set API_TOKEN environment variable, '
            'or set "token" in the config file.'
        )

    app = (ApplicationBuilder()
        .token(API_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )
    
    app.bot_data["robot_banner"] = robots.RobotBanner(args.window, args.limit)

    app.add_error_handler(tg_calls.error_handler)
    app.add_handler(MessageHandler(filters.ALL, tg_calls.delete_casino_messages))
    app.run_polling()

if __name__ == '__main__':
    main()

