import os
import requests

from dotenv import load_dotenv


load_dotenv()

MEASUREMENT_ID = os.getenv("GA4_MEASUREMENT_ID")
API_SECRET = os.getenv("GA4_API_SECRET")


def send_ga4_act(
        client_id: str,
        act_name: str,
        params: dict = None
) -> None:
    """
    Функция для отправки сообщений о действиях пользователей в боте в Google Analytics
    :param client_id: id пользователя(user_id telegram).
    :param act_name: Название действия.
    :param params: Дополнительные параметры действия в виде словаря.
    """
    url = (
        "https://www.google-analytics.com/mp/collect"
        f"?measurement_id={MEASUREMENT_ID}"
        f"&api_secret={API_SECRET}"
    )
    payload = {
        "client_id": client_id,
        "events": [
            {'name': act_name,
             'params': params or {}}
        ]
    }
    try:
        requests.post(url, json=payload, timeout=0.5)
    except requests.RequestException:
        # на случай если гугл аналитика не отвечает пропускаем во избежание ошибок в работе бота
        pass