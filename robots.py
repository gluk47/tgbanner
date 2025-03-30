import logging
from datetime import timedelta

import tg_calls

logger = logging.getLogger("banhammer")

class RobotBanner:
    def __init__(
            self,
            time_window=timedelta(seconds=5),
            message_limit=3
        ):
        self.events = []
        self.time_window = time_window
        self.message_limit = message_limit

        self.events = []
        self.stats = {}

    async def message_erased(self, msg, context):
        self._cleanup(msg.date)

        user_id = msg.from_user.id

        self.events.append((msg.date, user_id))
        self.stats[user_id] = self.stats.get(user_id, 0) + 1
        if self.stats[user_id] < self.message_limit:
            return
        
        try:
            chat_name = msg.chat.title
            chat_id = msg.chat.id
            user_name = tg_calls.extract_user_name(msg)
            if msg.chat.type == 'private':
                logger.info(f'I want to ban user {user_name} in private chat')
                return
            
            await context.bot.ban_chat_member(chat_id, user_id)
            logger.info(f'Banned {user_name} in {chat_name}')
            del self.stats[user_id]
        except Exception as ban_ex:
            logger.error(f'Failed to ban {user_name} in {chat_name}: {ban_ex}')
    
    def _cleanup(self, date):   
        if not self.events:
            return    
        for i, e in enumerate(self.events):
            when, user_id = e
            if date - when < self.time_window:
                break
            if user_id not in self.stats:
                continue
            self.stats[user_id] -= 1
            if self.stats[user_id] == 0:
                del self.stats[user_id]
        self.events = self.events[i:]
