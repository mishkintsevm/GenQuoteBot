import aiohttp
import asyncio
import random

from typing import Any, Dict, List, Optional, Tuple


BASE = "https://quotes-db.vercel.app"


# Список всех цитат, загруженных из API- служит локальным кэшем
_all_quotes: List[Dict[str, Any]] = []

# Флаг, указывающий, что кэш (_all_quotes) уже заполнен
_quotes_loaded = False

# Асинхронный замок, чтобы только одна корутина одновременно делала запрос к API
_lock = asyncio.Lock()


async def _load_all_quotes() -> None:
    """
    Скачивает полный набор цитат из QuotesDB (/api/quotes)
    и сохраняет их в переменную _all_quotes.
    Эта функция запускается только один раз — дальше используется кэш.
    """
    # делаем переменные глобальными для использования в других функциях
    global _all_quotes, _quotes_loaded

    # ставим _lock, чтобы этот код выполнялся только одним потоком/корутиной одновременно.
    async with _lock:
        # проверяем наличие загруженных цитат и если да, то выходим
        if _quotes_loaded:
            return

        # url получения цитат
        url = f"{BASE}/api/quotes"

        # открываем соединение и делаем запрос
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                # если ошибка — прерываем
                resp.raise_for_status()
                # считываем тело ответа как JSON в переменную payload
                payload = await resp.json()

        # проверка, что payload- это список цитат.
        if isinstance(payload, dict):
            _all_quotes = payload.get("data", []) or []
        elif isinstance(payload, list):
            _all_quotes = payload
        else:
            _all_quotes = []

        # отмечаем, что цитаты загружены, чтобы следующие вызовы сразу выходили и не делали новых запросов
        _quotes_loaded = True


async def get_random_quote() -> Optional[Dict[str, Any]]:
    """
    Возвращает одну случайную цитату из локального кэша.
    Если кэш не загружен — вызывает _load_all_quotes().
    """
    if not _quotes_loaded:
        await _load_all_quotes()
    return random.choice(_all_quotes) if _all_quotes else None


async def get_quotes_by_category(category: str,
                                 exclude_quote_id: int | None = None
                                 ) -> Optional[Dict[str, Any]]:
    """
    Фильтрует по полю "category" и возвращает одну случайную цитату этой категории.
    """
    if not _quotes_loaded:
        await _load_all_quotes()

    matches = [
        quote
        for quote in _all_quotes
        if quote.get("category", "").lower() == category.lower()
    ]

    # исключение уже показанной цитаты
    if exclude_quote_id is not None:
        matches = [quote for quote in matches if quote["id"] != exclude_quote_id]

    return random.choice(matches) if matches else None


async def get_quotes_by_author(author: str,
                               exclude_quote_id: int | None = None
                               ) -> Optional[Dict[str, Any]]:
    """
    Фильтрует по полю "author" и возвращает одну случайную цитату этого автора.
    """
    # если в кэше нет цитат, загружаем их из API
    if not _quotes_loaded:
        await _load_all_quotes()

    # получение всех цитат автор
    matches = [
        quote
        for quote in _all_quotes
        if quote.get("author", "") == author
    ]

    # для избежания повторения цитат
    if exclude_quote_id is not None:
        matches = [quote for quote in matches if quote["id"] != exclude_quote_id]

    # если есть совпадения-возвращаем случайную, иначе None
    return random.choice(matches) if matches else None


# Запросы для формирования меню жанров и авторов
async def get_topics() -> List[str]:
    """
    Запрашивает и возвращает список жанров (тем).
    """
    url = f"{BASE}/api/categories"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()


async def get_authors(page: int = 1, limit: int = 10) -> Tuple[List[str], int]:
    """
    Запрашивает и возвращает полный список авторов.
    """
    url = f"{BASE}/api/authors"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            authors: List[str] = await resp.json()

    total_pages = max(1, (len(authors) + limit - 1) // limit)
    start = (page - 1) * limit
    end = start + limit
    return authors[start:end], total_pages
