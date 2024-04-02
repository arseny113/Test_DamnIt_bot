import re
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, StateFilter
from aiogram import F
from aiogram.fsm import state
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
logging.basicConfig(level=logging.INFO)

TOKKEN = "7187931260:AAHZXNhRpq7ApIEFxlFy1y0RGyH1_SRh3fk"

CONSTANT_USER_ID = 365189030

bot = Bot(token=TOKKEN)

dp = Dispatcher()

class EnterData(StatesGroup):
    enter_user_name = State()
    enter_user_number = State()
    enner_user_comment = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(f"{message.from_user.id}, Добро пожаловать в компанию DamnIT")
    await message.answer(f"Напишете свое ФИО")
    await state.set_state(EnterData.enter_user_name)

@dp.message(EnterData.enter_user_name, F.text)
async   def get_user_name(message:types.Message, state: FSMContext):
    text = message.text
    if not any([i.isdigit() for i in text]):
        await state.update_data(user_name=text)
        await message.answer('Укажите Ваш номер телефона')
        await state.set_state(EnterData.enter_user_number)
    else:
        await message.answer("ФИО некорректно: цифр быть не должно")

@dp.message(EnterData.enter_user_number, F.text)
async   def get_user_number(message:types.Message, state: FSMContext):
    text = ''.join(message.text.split())
    pattern = '7\d{10}'
    if re.fullmatch(pattern, text):
        await state.update_data(user_number=message.text)
        await message.answer("Напишите любой комментарий")
        await state.set_state(EnterData.enner_user_comment)
    else:
        await message.answer("Неверный формат, попробуй еще раз")

@dp.message(EnterData.enner_user_comment, F.text)
async   def get_user_comment(message:types.Message, state: FSMContext):
    text = message.text
    await state.update_data(user_comment=text)
    await message.answer("Последний шаг! Ознакомься с вводными положениями")
    await message.answer_document(FSInputFile('C:\\Users\\arsen\\PycharmProjects\\Test_damnit\\test.pdf', 'основные положения'))
    inline_btn = InlineKeyboardButton(text='Да!', callback_data='button1')
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[[inline_btn]])
    await message.answer("Ознакомился?", reply_markup=inline_kb)

@dp.callback_query(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Спасибо за успешную регистрацию')
    await bot.send_photo(chat_id=callback_query.from_user.id, photo=FSInputFile("C:\\Users\\arsen\\PycharmProjects\\Test_damnit\\photo.jpg"))
    user_data = await state.get_data()
    await bot.send_message(chat_id=CONSTANT_USER_ID, text=f"Пришла новая заявка от {callback_query.from_user.id}"
                                                     f"\n ФИО: {user_data.get('user_name')}"
                                                     f"\n Телефон: {user_data.get('user_number')}"
                                                     f"\n Комментарий: {user_data.get('user_comment')}")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())