import asyncio
from aiogram.filters.command import Command
from aiogram import F, types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from bot import bot, dp
from database import *
from quizdata import quiz_data

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Результат"))
    builder.add(types.KeyboardButton(text="Топ-10"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(Command('stop'))
async def stop_bot(message: types.Message):
    await message.answer("Бот остановлен.")

@dp.message(Command("info"))
async def cmd_start(message: types.Message):
    await message.answer("Это квизбот.\nВ нем вы можете протестировать свое общее развитие и логику.\nНаписан бот студентом курса Founder с помощью гуглешки.")


@dp.message(F.text == "Начать игру")
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)

@dp.message(F.text == "Результат")
async def cmd_stats(message: types.Message):
    score = await get_quiz_score(message.from_user.id)
    await message.answer(f'Ваш последний результат: {score}/{len(quiz_data)}') if score != -1 else await message.answer("Вы еще не проходили квиз.")

@dp.message(F.text == "Топ-10")
async def cmd_stats(message: types.Message):
    results = await get_stats()
    str = '/n'.join([f'{id} - {score}/{len(quiz_data)}' for id, score in results])
    await message.answer(str)

@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id) + 1
    score = await get_quiz_score(callback.from_user.id) + 1
    await update_quiz_status(callback.from_user.id, current_question_index, score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {score}/{len(quiz_data)}")

@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    score = await get_quiz_score(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    current_question_index += 1
    await update_quiz_status(callback.from_user.id, current_question_index, score)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Ваш результат: {score}/{len(quiz_data)}")

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )
    builder.adjust(1)
    return builder.as_markup()

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    score = 0
    await update_quiz_status(user_id, current_question_index, score)
    await get_question(message, user_id)

async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())