from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallback(CallbackData, prefix="menu"):
  level: int
  menu_name: str
  page: int | None = None
  topic: str | None = None
  author_name: str | None = None
  quote_id: int | None = None


def get_main_menu_kb(*, level: int = 0) -> InlineKeyboardMarkup:
  builder = InlineKeyboardBuilder()

  # 1) Случайная цитата
  builder.add(
    InlineKeyboardButton(
      text="🎲 Случайная цитата",
      callback_data=MenuCallback(
        level=1,
        menu_name="random_quote"
      ).pack()
    )
  )

  # 2) По тематике / По авторам
  builder.add(
    InlineKeyboardButton(
      text="🗂️ По тематике",
      callback_data=MenuCallback(level=1, menu_name="topics", page=1).pack()
    ),
    InlineKeyboardButton(
      text="👤 По авторам",
      callback_data=MenuCallback(level=1, menu_name="authors", page=1).pack()
    )
  )

  return builder.adjust(1, 2).as_markup()


def get_topic_kb(
          topics: list[str],
          total_pages: int,
          *,
          level: int = 1,
          page: int = 1
  ) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # 1) Кнопки тем
    for topic in topics:
      builder.add(
        InlineKeyboardButton(
          text=f"📚 {topic}",
          callback_data=MenuCallback(
            level=level + 1,
            menu_name="topic_quotes",
            topic=topic
          ).pack()
        )
      )

    # 2) Навигация ⏮ / ⏭
    if page > 1:
      builder.add(
        InlineKeyboardButton(
          text="⏮ Назад",
          callback_data=MenuCallback(
            level=level,
            menu_name="topics",
            page=page - 1
          ).pack()
        )
      )
    if page < total_pages:
      builder.add(
        InlineKeyboardButton(
          text="⏭ Далее",
          callback_data=MenuCallback(
            level=level,
            menu_name="topics",
            page=page + 1
          ).pack()
        )
      )

    # 3) Применяем adjust(2) — всё, что было добавлено до этого,
    builder.adjust(2)

    # 4) Отдельным рядом добавляем одну кнопку возврата
    builder.row(
      InlineKeyboardButton(
        text="🔙 Вернуться в меню",
        callback_data=MenuCallback(
          level=0,
          menu_name="main"
        ).pack()
      )
    )

    return builder.as_markup()


def get_author_kb(
        authors: list[str],
        total_pages: int,
        *,
        level: int = 1,
        page: int = 1
) -> InlineKeyboardMarkup:
  builder = InlineKeyboardBuilder()

  # 1) Список авторов
  for name in authors:
    builder.add(
      InlineKeyboardButton(
        text=f"👤 {name}",
        callback_data=MenuCallback(
          level=level + 1,
          menu_name="author_quotes",
          author_name=name
        ).pack()
      )
    )

  # 2) Навигация «⏮ Назад» / «⏭ Далее»
  if page > 1:
    builder.add(
      InlineKeyboardButton(
        text="⏮ Назад",
        callback_data=MenuCallback(
          level=level,
          menu_name="authors",
          page=page - 1
        ).pack()
      )
    )
  if page < total_pages:
    builder.add(
      InlineKeyboardButton(
        text="⏭ Далее",
        callback_data=MenuCallback(
          level=level,
          menu_name="authors",
          page=page + 1
        ).pack()
      )
    )

  # 3) Сгруппировать всё добавленное по 2 кнопки на ряд
  builder.adjust(2)

  # 4) Отдельным последним рядом — единая кнопка «Вернуться в меню»
  builder.row(
    InlineKeyboardButton(
      text="🔙 Вернуться в меню",
      callback_data=MenuCallback(
        level=0,
        menu_name="main"
      ).pack()
    )
  )

  return builder.as_markup()
