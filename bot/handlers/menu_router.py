from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from keyboards.inline import get_main_menu_kb, MenuCallback
from handlers.user_menu import user_menu
from utils.analytics import send_ga4_act


menu_router = Router()


@menu_router.message(Command("start"))
async def start_handler(message: types.Message):
    banner = FSInputFile("assets/images/start-banner.png")

    # отслеживание старта работы с ботом для сервиса аналитики
    send_ga4_act(
        client_id=str(message.from_user.id),
        act_name='start'
    )

    caption = (
        "📚 <b>Главное меню</b>\n\n"
        "✨ Вы можете получить <b>случайную цитату</b>, "
        "а также выбрать цитату по <i>жанру</i> или <i>автору</i>.\n\n"
        "👇 Используйте кнопки ниже, чтобы начать."
    )

    await message.answer_photo(
        photo=banner,
        caption=caption,
        reply_markup=get_main_menu_kb(),
        parse_mode="HTML"
    )


menu_router.callback_query.register(user_menu, MenuCallback.filter())
