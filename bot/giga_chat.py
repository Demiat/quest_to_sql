import os
from http import HTTPStatus
import certifi
import ssl

from aiohttp import (
    ClientSession,
    ClientResponseError,
    ClientConnectorError,
    TCPConnector
)
from dotenv import load_dotenv

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


async def get_access_token():
    """Получение giga_chat токена доступа."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.load_verify_locations('russian_trusted_root_ca.cer')

    connector = TCPConnector(ssl=ssl_context)

    try:
        async with ClientSession(connector=connector) as session:
            async with session.post(
                GIGA_AUTH_URL,
                headers=HEADERS,
                data=PAYLOAD
            ) as response:
                if response.status == HTTPStatus.OK:
                    data = await response.json()
                    return data.get("access_token")
                else:
                    raise ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=await response.text(),
                        headers=response.headers
                    )
    except ClientConnectorError as e:
        print(f"Ошибка соединения с GigaChat: {e}")
        raise
