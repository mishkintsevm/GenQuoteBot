import math
from aiogram.types import InlineKeyboardButton


class Paginator:
    def __init__(
        self,
        total_items: int,
        page: int,
        items_per_page: int = 10,
        level: int = 1,
        menu_name: str = "",
        extra_key: str = "",
        extra_value: str | None = None,
    ):
        self.total = total_items
        self.page = page
        self.per_page = items_per_page
        self.level = level
        self.menu_name = menu_name
        self.extra_key = extra_key
        self.extra_value = extra_value


    @property
    def total_pages(self) -> int:
        return math.ceil(self.total / self.per_page)


    def get_nav_buttons(self, packer) -> list[InlineKeyboardButton]:
        """Вернёт [prev?, next?] для InlineKeyboardMarkup."""
        buttons: list[InlineKeyboardButton] = []
        if self.page > 1:
            buttons.append(
                InlineKeyboardButton(
                    text="⏮ Назад",
                    callback_data=packer(
                        level=self.level,
                        menu_name=self.menu_name,
                        page=self.page - 1,
                        **({self.extra_key: self.extra_value} if self.extra_value else {})
                    )
                )
            )
        if self.page < self.total_pages:
            buttons.append(
                InlineKeyboardButton(
                    text="⏭ Далее",
                    callback_data=packer(
                        level=self.level,
                        menu_name=self.menu_name,
                        page=self.page + 1,
                        **({self.extra_key: self.extra_value} if self.extra_value else {})
                    )
                )
            )
        return buttons
