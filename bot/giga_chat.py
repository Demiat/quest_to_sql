import os
from http import HTTPStatus
import certifi
import ssl
from typing import Optional

from aiohttp import (
    ClientSession,
    ClientResponseError,
    TCPConnector
)
from sqlalchemy import text
from dotenv import load_dotenv

from core import DBDependency
from .constants import SYS_PROMT

load_dotenv()

SBER_AUTH_TOKEN = os.getenv('SBER_AUTH_TOKEN')
RqUID = os.getenv('RqUID')

GIGA_URL = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
GIGA_AUTH_URL = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
GIGA_FILES_URL = (
    'https://gigachat.devices.sberbank.ru/api/v1/files/{file_uid}/content'
)
PAYLOAD = 'scope=GIGACHAT_API_PERS'
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': RqUID,
    'Authorization': f'Basic {SBER_AUTH_TOKEN}'
}


class GigaChatAPI:
    """GigaChat API."""

    def __init__(self):
        self.connector = None
        self.aiohttp_session = None
        self.token = None
        self.db = DBDependency()

    async def _get_aiohttp_session(self):
        """Создает сессию, либо использует созданную ранее."""
        if not self.aiohttp_session:
            self.aiohttp_session = ClientSession(connector=self.connector)
        return self.aiohttp_session

    async def get_answer_from_sql(self, answer_from_AI):
        """Выполняет SQL запрос, полученный в виде текста от ИИ."""
        async with self.db.db_session() as db_session:
            result = await db_session.execute(text(answer_from_AI))
            return str(result.scalar())

    async def get_access_token(self):
        """Получает access token."""
        aiohttp_session = await self._get_aiohttp_session()

        async with aiohttp_session .post(
            GIGA_AUTH_URL,
            headers=HEADERS,
            data=PAYLOAD
        ) as response:
            if response.status == HTTPStatus.OK:
                data = await response.json()
                self.token = data.get("access_token")
            else:
                raise ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=await response.text(),
                    headers=response.headers
                )

    async def request_to_sql(self, message: str) -> Optional[str]:
        """Получает от ИИ SQL код на текстовый запрос."""
        aiohttp_session = await self._get_aiohttp_session()

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": SYS_PROMT},
                {"role": "user", "content": message}
            ],
            "temperature": 0.3,
            "top_p": 0.1,
            "n": 1,
            "max_tokens": 512,
            "repetition_penalty": 1.0
        }

        async with aiohttp_session .post(
            GIGA_URL,
            headers=headers,
            json=payload
        ) as response:
            if response.status == HTTPStatus.OK:
                data = await response.json()
                sql_query = data['choices'][0]['message']['content'].strip()

                return await self.get_answer_from_sql(sql_query)
            elif response.status == HTTPStatus.UNAUTHORIZED:  # Токен протух
                await self.get_access_token()
                return await self.request_to_sql(message)  # Повторяем запрос
            else:
                error_text = await response.text()
                print(f"Ошибка GigaChat: {response.status} - {error_text}")
                return None

    async def __aenter__(self):
        """Создаем connector при входе в контекст (уже есть event loop)."""
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.load_verify_locations('russian_trusted_root_ca.cer')
        self.connector = TCPConnector(ssl=ssl_context)
        return self

    async def __aexit__(self, *args):
        # Закроем сессию после работы
        if self.aiohttp_session:
            await self.aiohttp_session.close()
