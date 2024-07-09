from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from quiz_bot.bucket import get_image
from quiz_bot.db_service import (
    update_quiz_index,
    get_quiz_index,
    update_question_order,
    get_question_order,
    update_current_score,
    get_current_score,
    update_top_score,
    get_top_score,
    update_user_name,
    get_question_list,
    create_question_list_from_indexes,
)

async def new_quiz(message):
    user_id = message.from_user.id
    questions = await get_question_list(
        shuffle=True,  # перемешать вопросы
        number=10  # сколько вопросов взять на квиз
    )
    current_question_index = 0
    current_score = 0
    await update_quiz_index(user_id, current_question_index)
    await update_question_order(user_id, questions['index_list'])
    await update_current_score(user_id, current_score)
    await get_question(message, user_id)


async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    current_question_index_list = await get_question_order(user_id)
    current_question_list = await create_question_list_from_indexes(current_question_index_list)

    correct_index = current_question_list[current_question_index]['correct_option']
    opts = current_question_list[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{current_question_list[current_question_index]['question']}",
                         reply_markup=kb)


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for asw_index, option in enumerate(answer_options):
        callback = f'answer_{asw_index}{"_right" if option == right_answer else "_wrong"}'

        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=callback
            )
        )
    builder.adjust(1)
    return builder.as_markup()


async def handle_answer(callback: types.CallbackQuery,
                        right_answer: bool):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    current_question_index_list = await get_question_order(callback.from_user.id)
    current_question_list = await create_question_list_from_indexes(current_question_index_list)
    current_score = await get_current_score(callback.from_user.id)

    user_answer_index = int(callback.data.split('_')[1])
    user_answer = current_question_list[current_question_index]['options'][user_answer_index]

    if right_answer:
        # img = types.BufferedInputFile(get_image('correct.png'),
        #                               filename='correct.png')
        message = f"Ваш ответ: {user_answer}.\nВерно! Вы получаете +10 очков!"
        current_score += 10
        await update_current_score(callback.from_user.id, current_score)
    else:
        # img = types.BufferedInputFile(get_image('incorrect.png'),
        #                               filename='incorrect.png')
        correct_option = current_question_list[current_question_index]['correct_option']
        message = f'Ваш ответ: "{user_answer}". Неправильно :(\nПравильный ответ: ' \
                  f'"{current_question_list[current_question_index]["options"][correct_option]}"'
    # await callback.message.answer_photo(img)
    await callback.message.answer(message)

    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(current_question_list):
        await get_question(callback.message, callback.from_user.id)
    else:
        top_score = await get_top_score(callback.from_user.id)
        if current_score > top_score:
            await update_top_score(callback.from_user.id, current_score)
            await update_user_name(callback.from_user.id, callback.from_user.full_name)
            add_msg = f'Вы установили свой новый рекорд! Предыдущий рекорд был {top_score} очков.'
        elif current_score == top_score:
            add_msg = f'Вы повторили свой рекорд!'
        else:
            add_msg = f'Ваш рекорд, к сожалению, побить не удалось! Ваш рекорд {top_score} очков.'

        msg = f"Это был последний вопрос. Квиз завершен!\n"\
              f"Вы набрали {current_score} очков!\n{add_msg}"
        await callback.message.answer(msg)
