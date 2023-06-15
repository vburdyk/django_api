from telegram import Bot
from django.conf import settings


async def post_order_on_telegram(message):
    bot_token = settings.TOKEN_TELEGRAM
    tg_bot = Bot(token=bot_token)
    await tg_bot.send_message(chat_id="-1001802212243", text=message)
