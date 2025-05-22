from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, FSInputFile

from data.get_quotes_api import get_topics, get_authors
from keyboards.inline import get_main_menu_kb, get_topic_kb, get_author_kb
from utils.paginator import Paginator


async def get_menu_content(
    level: int,
    menu_name: str,
    page: int | None = None,
    topic: str | None = None,
    author_name: str | None = None,
) -> tuple[InputMediaPhoto, InlineKeyboardMarkup]:
    if level == 0:
        return await main_menu()

    if level == 1 and menu_name == "topics":
        return await topic_list(page or 1)

    if level == 1 and menu_name == "authors":
        return await author_list(page or 1)

    return await main_menu()


async def main_menu() -> tuple[InputMediaPhoto, InlineKeyboardMarkup]:
    """
    Баннер + кнопки главного меню
    """
    media = InputMediaPhoto(
        media=FSInputFile("assets/images/start-banner.png"),
        caption=(
            "📚 <b>Главное меню</b>\n\n"
            "✨ Вы можете получить <b>случайную цитату</b>, "
            "а также выбрать цитаты по <i>тематике</i> или <i>автору</i>.\n\n"
            "👇 Используйте кнопки ниже, чтобы начать."
        ),
        parse_mode="HTML"
    )
    return media, get_main_menu_kb()


async def topic_list(page: int = 1) -> tuple[InputMediaPhoto, InlineKeyboardMarkup]:
    all_topics = await get_topics()
    total = len(all_topics)

    paginator = Paginator(
        total_items=total,
        page=page,
        items_per_page=10,
        level=1,
        menu_name="topics",
    )

    slice_ = all_topics[(page - 1) * paginator.per_page : page * paginator.per_page]

    media = InputMediaPhoto(
        media=FSInputFile("assets/images/start-banner.png"),
        caption=(
            "📚 <b>Жанры цитат</b>\n\n"
            "🔍 Здесь вы можете выбрать на какую тему цитату вы хотите получить\n\n"
            "👇 Список жанров представлен внизу."
        ),
        parse_mode="HTML"
    )
    return media, get_topic_kb(
        topics=slice_,
        total_pages=paginator.total_pages,
        level=1,
        page=page
    )


async def author_list(page: int = 1) -> tuple[InputMediaPhoto, InlineKeyboardMarkup]:
    authors, total_pages = await get_authors(page)

    media = InputMediaPhoto(
        media=FSInputFile("assets/images/start-banner.png"),
        caption=(
            "👤 <b>Авторы цитат</b>\n\n"
            "🔍 Ниже перечислены авторы, цитаты которых вы можете получить."
        ),
        parse_mode="HTML"
    )
    return media, get_author_kb(
        authors=authors,
        total_pages=total_pages,
        level=1,
        page=page
    )
