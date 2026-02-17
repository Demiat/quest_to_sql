import asyncio
import os

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from giga_chat import get_access_token

load_dotenv()

COMMTOBOT_TOKEN = os.getenv("COMMTOBOT_TOKEN")

bot = Bot(token=COMMTOBOT_TOKEN)
dp = Dispatcher()


@dp.message()
async def echo(message: types.Message):
    await message.answer("Привет!")


async def main():
    access_token = await get_access_token()

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
