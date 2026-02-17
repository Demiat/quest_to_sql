import asyncio
import os

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from bot.giga_chat import GigaChatAPI

load_dotenv()

COMMTOBOT_TOKEN = os.getenv("COMMTOBOT_TOKEN")

bot = Bot(token=COMMTOBOT_TOKEN)
dp = Dispatcher()
giga = GigaChatAPI()


@dp.message()
async def request_for_sql(message: types.Message):
    answer = await giga.request_to_sql(message.text)
    await message.answer(answer)


async def main():

    async with giga:
        await giga.get_access_token()
        print("Бот запущен...")
        await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
