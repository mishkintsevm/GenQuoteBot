from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.get_quotes_api import (
    get_random_quote,
    get_quotes_by_category,
    get_quotes_by_author,
)

from handlers.menu_processing import get_menu_content
from keyboards.inline import MenuCallback
from utils.analytics import send_ga4_act


async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallback):
    """
    Многоуровневое меню строится через редактирование(edit_media, edit_caption),
    чтобы вся работа с ботом проходила в одном сообщение и чат не "засорялся".

    Пункты меню(inline-кнопки):
      • random_quote(получение случайной цитаты)
      • topic_quotes(вывод жанров цитат)
      • author_quotes(вывод авторов цитат)
      • навигация меню (темы/авторы/страницы)
    """
    # Кнопка "Случайная цитата"
    if callback_data.menu_name == "random_quote":

        # получение случайной цитаты
        quote = await get_random_quote()

        # отправка данных в сервис аналитики
        send_ga4_act(
            client_id=str(callback.from_user.id),
            act_name="random_quote",
            params={"quote_id": quote["id"]}
        )

        # формирование сообщения с html-разметкой с текстом цитаты и именем автора
        caption = (
            "💭 <i>" + quote["quote"] + "</i>\n\n"
            "🖋️ <b>" + quote["author"] + "</b>"
        )

        # формирование клавиатуры: кнопки для получения новой цитаты и возвращения назад
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="🔄 Ещё цитата",
                callback_data=MenuCallback(
                    level=1, menu_name="random_quote"
                ).pack()
            ),
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=MenuCallback(
                    level=0, menu_name="main"
                ).pack()
            ),
        ).adjust(2)

        try:
            # редактирование(вывод) сообщения с использованием html разметки
            await callback.message.edit_caption(
                caption=caption,
                parse_mode="HTML",
                reply_markup=builder.as_markup()
            )
        except TelegramBadRequest as e:
            # обработка ошибки Telegram "message is not modified" на случай если цитат больше нет
            if "message is not modified" in str(e):
                # вывод сообщения пользователю и избежание зависания бота
                await callback.answer("Других цитат нет.", show_alert=False)
                return
            raise
        await callback.answer()
        return

    # Цитата по жанру
    if callback_data.menu_name == "topic_quotes" and callback_data.topic:

        # получение цитаты выбранного жанра(темы), исключая текущую
        data = await get_quotes_by_category(callback_data.topic, exclude_quote_id=callback_data.quote_id)

        if not data:
            await callback.answer("Для этой темы больше нет цитат.", show_alert=False)
            return

        # отправка данных в сервис аналитики
        send_ga4_act(
            client_id=str(callback.from_user.id),
            act_name="next_topic_quote" if callback_data.quote_id else "get_topic_quote",
            params={"topic": callback_data.topic, "quote_id": data["id"]}
        )

        # формирование сообщения с html разметкой с цитатой и автором
        caption = (
            "💭 <i>" + data["quote"] + "</i>\n\n"
            "🖋️ <b>" + data["author"] + "</b>"
        )

        # формирование клавиатуры для страницы цитаты с кнопками другой цитаты и возвращения назад
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="🔄 Ещё цитата",
                callback_data=MenuCallback(
                    level=1,
                    menu_name="topic_quotes",
                    topic=callback_data.topic,
                    quote_id=data["id"],
                ).pack()
            ),
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=MenuCallback(
                    level=1,
                    menu_name="topics",
                    page=callback_data.page or 1
                ).pack()
            ),
        ).adjust(2)

        try:
            # редактирование(вывод) сообщения с использованием html разметки
            await callback.message.edit_caption(
                caption=caption,
                parse_mode="HTML",
                reply_markup=builder.as_markup()
            )
        except TelegramBadRequest as e:
            # обработка ошибки Telegram "message is not modified" на случай если цитат больше нет
            if "message is not modified" in str(e):
                # вывод сообщения пользователю и избежание зависания бота
                await callback.answer("Для этой темы больше нет новых цитат.", show_alert=False)
                return
            raise
        await callback.answer()
        return

    # Цитата по автору
    if callback_data.menu_name == "author_quotes" and callback_data.author_name:

        # получение цитаты выбранного автора, исключая текущую
        data = await get_quotes_by_author(
            callback_data.author_name,
            exclude_quote_id=callback_data.quote_id,
        )

        if not data:
            await callback.answer("Для этого автора больше нет новых цитат.", show_alert=False)
            return

        # отправка данных в сервис аналитики
        send_ga4_act(
            client_id=str(callback.from_user.id),
            act_name="next_author_quote" if callback_data.quote_id else "get_author_quote",
            params={"author": callback_data.author_name, "quote_id": data["id"]}
        )

        # формирование сообщения с html разметкой с цитатой и автором
        caption = (
            "💭 <i>" + data["quote"] + "</i>\n\n"
            "🖋️ <b>" + data["author"] + "</b>"
        )

        # формирование клавиатуры для страницы цитаты с кнопками другой цитаты и возвращения назад
        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="🔄 Ещё цитата",
                callback_data=MenuCallback(
                    level=1,
                    menu_name="author_quotes",
                    author_name=callback_data.author_name,
                    quote_id=data["id"],
                ).pack()
            ),
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=MenuCallback(
                    level=1,
                    menu_name="authors",
                    page=callback_data.page or 1
                ).pack()
            ),
        ).adjust(2)

        try:
            # редактирование(вывод) сообщения с использованием html разметки
            await callback.message.edit_caption(
                caption=caption,
                parse_mode="HTML",
                reply_markup=builder.as_markup()
            )
        except TelegramBadRequest as e:
            # Если выдалась та же цитата, сообщение не изменится и Telegram вернёт ошибку "message is not modified"
            if "message is not modified" in str(e):
                await callback.answer("Для этого автора больше нет новых цитат.", show_alert=False)
                return
            raise
        await callback.answer()
        return

    # Навигация по меню (жанры / авторы / цитаты)
    media, reply_markup = await get_menu_content(
        level=callback_data.level, # уровень вложенности меню (жанры / авторы / цитаты)
        menu_name=callback_data.menu_name,
        page=callback_data.page,
        topic=callback_data.topic,
        author_name=callback_data.author_name,
    )
    try:
        # редактируем текущее сообщение новым контентом и клавиатурой
        await callback.message.edit_media(media=media, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        # Если выдалась та же цитата, сообщение не изменится и Telegram вернёт ошибку "message is not modified"
        if "message is not modified" in str(e):
            # подтверждаем нажатие кнопки, чтобы избежать зависания
            await callback.answer()
            return
        # если это другая ошибка — пробрасываем дальше, чтобы не сломать бота
        raise
    # подтверждаем обработку коллбэка, чтобы бот работал
    await callback.answer()
