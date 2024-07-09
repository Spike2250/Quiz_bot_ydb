from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from quiz_bot.bucket import get_image
from quiz_bot.service import new_quiz, handle_answer
from quiz_bot.db_service import get_records_table


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!",
                         reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    img = types.BufferedInputFile(get_image('quiz_img.png'), filename='quiz_img.png')
    await message.answer_photo(img)
    await new_quiz(message)


@router.message(Command("records"))
async def cmd_quiz(message: types.Message):
    records = await get_records_table()
    await message.answer(f"`{records}`", parse_mode='MarkdownV2')


@router.callback_query(F.data.endswith("_right"))
async def right_answer(callback: types.CallbackQuery):
    await handle_answer(callback, right_answer=True)


@router.callback_query(F.data.endswith("_wrong"))
async def wrong_answer(callback: types.CallbackQuery):
    await handle_answer(callback, right_answer=False)
