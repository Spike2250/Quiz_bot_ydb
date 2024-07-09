import os
import logging
from aiogram import Bot, Dispatcher, types
import json

from quiz_bot.handlers import router


logging.basicConfig(level=logging.INFO)

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def process_event(event):
    update = types.Update.model_validate(
        json.loads(event['body']),
        context={"bot": bot}
    )
    await dp.feed_update(bot, update)


async def webhook(event, context):
    if event['httpMethod'] == 'POST':
        await process_event(event)
        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}
