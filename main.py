import asyncio
import logging
from typing import List
from aiogram import Bot, Dispatcher, types, F
from aiogram.methods import DeleteWebhook
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import time
import modules.keyboards as keyboards
import modules.texts as texts
from dotenv import load_dotenv
import os
import shape_sdk
from aiogram.filters import Command
from modules.session import OrderSession
from email_validator import validate_email, EmailNotValidError

load_dotenv()
logging.basicConfig(level=logging.INFO)
TOKEN=os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()


class States(StatesGroup):
    """Стейты для aiogram"""
    email_wait = State()
    params_waiting = State()


async def clearTemp(state: FSMContext):
    messages: List[types.Message] = (await state.get_data()).get('temporary_messages', None)
    if not messages:
        return
    for message in messages:
        try:
            await message.delete()
        except Exception:
            ...
    await state.update_data(temporary_messages=None)


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()

    aiogram_user = message.from_user
    user = await shape_sdk.user.getUser(aiogram_user.id)
    if not user:
        await shape_sdk.user.createUser(aiogram_user.id, aiogram_user.first_name or 'first', aiogram_user.last_name or 'last')

    await message.answer_photo(
        photo=FSInputFile("static/hello.jpg"),
        caption=texts.buildStartText(message.from_user.full_name),
        parse_mode="Markdown",
        reply_markup=keyboards.buildStartKeyboard()
    )


# ------------------------------- Catalog -------------------------------------


@dp.callback_query(F.data == 'catalog')
async def catalog(callback: types.CallbackQuery):
    await callback.message.edit_caption(caption="Каталог 📚",
                                        parse_mode="Markdown",
                                        reply_markup=keyboards.buildProductsMain()
    )


@dp.callback_query(F.data == 'keyboard_skins')
async def keyboard_skins(callback: types.CallbackQuery):
    await callback.message.edit_caption(caption="Скины 📚",
                                        parse_mode="Markdown",
                                        reply_markup=keyboards.buildProductsSkinsMain()
    )


@dp.callback_query(F.data == 'main_menu')
async def main_menu(callback: types.CallbackQuery):
    await callback.message.edit_caption(
        caption=texts.buildStartText(callback.from_user.full_name),
        parse_mode="Markdown",
        reply_markup=keyboards.buildStartKeyboard()
    )


@dp.callback_query(F.data.startswith("about_"))
async def aboutProduct(callback: types.CallbackQuery):
    nominal_id = callback.data.replace("about_", "")
    product = await shape_sdk.products.getProduct(callback.from_user.id, nominal_id)
    await callback.message.edit_caption(
        caption=texts.buildProductText(product),
        reply_markup=keyboards.buildProductKeyboard(product, nominal_id)
    )

# ------------------------------- Orders -------------------------------------

@dp.callback_query(F.data == 'my_orders')
async def orders(callback: types.CallbackQuery, state: FSMContext):
    orders = await shape_sdk.orders.getOrders(callback.from_user.id)
    await clearTemp(state)
        
    if orders == None:
        await callback.answer(text='⚠️ Не удалось получить список заказов!')
        return
    
    if len(orders) == 0:
        await callback.answer(text='У вас еще нет заказов')
        return
    
    await callback.answer()
    temporary_messages = []
    for order in orders:
        temporary_messages.append(await callback.message.answer(
            text=texts.buildOrderText(order),
            reply_markup=keyboards.buildOrderKeyboard(order)
        ))
    await state.update_data(temporary_messages=temporary_messages)


@dp.callback_query(F.data.startswith("order_expand_"))
async def moreOrder(callback: types.CallbackQuery):
    state, order_id = callback.data.replace("order_expand_", "").split('_')
    order = await shape_sdk.orders.getOrder(callback.from_user.id, order_id)
    text = texts.buildOrderText(order) if state == 'less' else texts.buildOrderTextMore(order)
    keyboard = keyboards.buildOrderKeyboard(order) if state == 'less' else keyboards.buildOrderKeyboardMore(order)
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


@dp.callback_query(F.data.startswith("jump_payment_"))
async def jumpPayment(callback: types.CallbackQuery, state: FSMContext):
    order_id: int | None = (await state.get_data()).get('jump_payment_', None)
    await clearTemp(state)
    await createPayment(callback.from_user.id, callback.message, state, order_id)


# ----------------------------- Orders ------------------------------------

@dp.callback_query(F.data.startswith("orderProduct_"))
async def orderProduct(callback: types.CallbackQuery, state: FSMContext):
    nominal_id = callback.data.replace("orderProduct_", "")
    _session: OrderSession | None = (await state.get_data()).get('session', None)

    if _session:
        await callback.answer(text='У Вас есть незавершённый заказ. Завершите оформление всех заказов, прежде чем начать новый.')
        return

    product = await shape_sdk.products.getProduct(callback.from_user.id, nominal_id)
    if not product:
        await callback.answer('⚠️ Произошла ошибка при заказе товара! Перезагрузите бота или попробуйте позже')
        return
    await state.update_data(session=OrderSession(product.id, product.nominal_id))

    if nominal_id in ['skin64', 'skin_premium']:
        await selectHands(callback, state)
        return
    await inputParams(callback, state)


async def selectHands(callback: types.CallbackQuery, state: FSMContext):
    _session: OrderSession | None = (await state.get_data()).get('session', None)
    await callback.answer()
    if not _session:
        await callback.message.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    await callback.message.answer(
        text='💠 Выберите тип рук вашего скина',
        reply_markup=keyboards.buildHandsKeyboard()
    )


@dp.callback_query(F.data.startswith("hands_"))
async def inputParams(callback: types.CallbackQuery, state: FSMContext):
    _session: OrderSession | None = (await state.get_data()).get('session', None)
    await callback.answer()
    if not _session:
        await callback.message.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    if callback.data.startswith('hands_'):
        message = await callback.message.edit_text(
            text=texts.buildInputsKeyboard(),
            reply_markup=keyboards.buildInputsKeyboard(),
            parse_mode='Markdown'
        )
        hands_type = callback.data.replace("hands_", "")
        _session.parameters.append({
            'name': 'Тип рук',
            'value': 'Стандартные' if hands_type == 'default' else 'Тонкие'
        })
    else:
        message = await callback.message.answer(
            text=texts.buildInputsKeyboard(),
            reply_markup=keyboards.buildInputsKeyboard(),
            parse_mode='Markdown'
        )

    await state.set_state(States.params_waiting)
    await state.update_data(inputs_message=message)


@dp.message(States.params_waiting)
async def handleParams(message: types.Message, state: FSMContext):
    _session: OrderSession | None = (await state.get_data()).get('session', None)
    inputs_message: types.Message | None = (await state.get_data()).get('inputs_message', None)
    if not _session:
        await message.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    if message.photo:
        file = await bot.get_file(message.photo[-1].file_id)
        url = f'https://api.telegram.org/file/bot{TOKEN}/{file.file_path}'
        _session.attachments.append({
            'title': file.file_path.split('/')[-1],
            'extension': file.file_path.split('.')[-1],
            'url': url
        })
        message.caption and _session.descriptions.append(message.caption)

    elif message.document:
        file = await bot.get_file(message.document.file_id)
        url = f'https://api.telegram.org/file/bot{TOKEN}/{file.file_path}'
        _session.attachments.append({
            'title': message.document.file_name,
            'extension': file.file_path.split('.')[-1],
            'url': url
        })
        message.caption and _session.descriptions.append(message.caption)

    elif message.video:
        file = await bot.get_file(message.video.file_id)
        url = f'https://api.telegram.org/file/bot{TOKEN}/{file.file_path}'
        _session.attachments.append({
            'title': message.video.file_name,
            'extension': file.file_path.split('.')[-1],
            'url': url
        })
        message.caption and _session.descriptions.append(message.caption)

    else:
        if message.text:
           _session.descriptions.append(message.text)

    if inputs_message:
        try:
            await inputs_message.edit_text(
                text=texts.buildInputsKeyboard() + \
                    f'\n\nКоличество вложений: *{len(_session.attachments)}*',
                reply_markup=keyboards.buildInputsKeyboard(),
                parse_mode='Markdown'
            )
        except Exception:
            ...


@dp.callback_query(F.data == 'inputs_done')
async def inputsDone(callback: types.CallbackQuery, state: FSMContext):
    _session: OrderSession | None = (await state.get_data()).get('session', None)
    if not _session:
        await callback.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    descriptions = ' '.join(_session.descriptions)
    _session.parameters.append({
        'name': 'Техническое задание',
        'value': descriptions
    })
    if not descriptions:
        await callback.message.answer('Отправьте хотя бы одно сообщение с описанием заказа!')
        return
    
    await callback.message.delete()

    response = await shape_sdk.orders.createOrder(
        callback.from_user.id,
        _session.product_id,
        _session.parameters,
        _session.attachments                   
    )

    if response != 200:
        await callback.message.answer('⚠️ Не удалось создать заказ')
        return

    
    orders = await shape_sdk.orders.getOrders(callback.from_user.id)
    if not orders:
        await callback.message.answer('⚠️ Произошла ошибка при создании ссылки для оплаты!')
        return
    
    await state.update_data(order_id=orders[-1].id)
    await createPayment(callback.from_user.id, callback.message, state)


async def createPayment(user_id: int, message: types.Message, state: FSMContext, orderId: int = None):
    order_id: int | None = orderId or (await state.get_data()).get('order_id', None)
    user = await shape_sdk.user.getUser(user_id)
    if not user.email:
        await getEmail(message, state)
        return

    payment = await shape_sdk.orders.createPayment(user_id, order_id)
    await message.answer(text=texts.buildPaymentText(payment))


async def getEmail(message: types.Message, state: FSMContext):
    await message.answer('Пожалуйста, отправьте Ваш адрес электронной почты')
    await state.set_state(States.email_wait)


@dp.message(F.text, States.email_wait)
async def handleEmail(message: types.Message, state: FSMContext):
    try:
        email_info = validate_email(message.text)
        result = await shape_sdk.user.setEmail(message.from_user.id, email_info.normalized)
        if not result:
            await message.answer('⚠️ Не удалось установить адрес электронной почты')
            return
        await createPayment(message.from_user.id, message, state)
    except EmailNotValidError:
        await message.answer('Ваш адрес электронной почты имеет неправильный формат!')


async def start_bot():
    """Асинхронная функция для запуска диспатчера"""

    started = True
    while started:
        try:
            await bot(DeleteWebhook(drop_pending_updates=True))
            await dp.start_polling(bot)
            started = False
        except Exception:
            started = True
            print("An error has occurred, reboot in 10 seconds")
            time.sleep(10)
            print("rebooting...")


if __name__ == '__main__':
    asyncio.run(start_bot())