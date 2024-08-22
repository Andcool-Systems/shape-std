"""
by AndcoolSystems, 2024
"""

from email_validator import validate_email, EmailNotValidError
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteWebhook
from modules.session import OrderSession
import modules.keyboards as keyboards
from aiogram.types import FSInputFile
from aiogram.filters import Command
from dotenv import load_dotenv
import modules.texts as texts
from typing import List
import shape_sdk
import asyncio
import logging
import time
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
TOKEN=os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()
api_manager = shape_sdk.api_manager.ApiManager()


class States(StatesGroup):
    """Стейты для aiogram"""

    email_wait = State()
    params_waiting = State()


async def clearTemp(state: FSMContext):
    """Очищает временные сообщения после главного сообщения"""

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
    """Хендлер команды /start"""
    await state.clear()

    aiogram_user = message.from_user
    user = await shape_sdk.user.getUser(aiogram_user.id)  # Получаем юзера из апи
    if not user:
        """Если юзера нет, отправляем запрос на его создание"""
        await shape_sdk.user.createUser(aiogram_user.id, aiogram_user.first_name or 'first', aiogram_user.last_name or 'last')

    await message.answer_photo(
        photo=FSInputFile("static/hello.jpg"),
        caption=texts.buildStartText(message.from_user.full_name),
        parse_mode="Markdown",
        reply_markup=keyboards.buildStartKeyboard()
    )


@dp.callback_query(F.data == 'pass')
async def handlePass(callback: types.CallbackQuery):
    await callback.answer()


# ------------------------------- Catalog -------------------------------------


@dp.callback_query(F.data == 'catalog')
async def catalog(callback: types.CallbackQuery):
    """Хендлер колбэка кнопки каталога"""

    products = await shape_sdk.products.getProducts(callback.from_user.id) or []
    await callback.message.edit_caption(caption="Каталог 📚",
                                        parse_mode="Markdown",
                                        reply_markup=keyboards.buildProductsMain(products)
    )


@dp.callback_query(F.data == 'keyboard_skins')
async def keyboard_skins(callback: types.CallbackQuery):
    """Хендлер колбека кнопки заказа скина"""

    products = await shape_sdk.products.getProducts(callback.from_user.id) or []
    await callback.message.edit_caption(caption="Скины 📚",
                                        parse_mode="Markdown",
                                        reply_markup=keyboards.buildProductsSkinsMain(products)
    )


@dp.callback_query(F.data == 'main_menu')
async def main_menu(callback: types.CallbackQuery):
    """Хендлер колбека кнопки Главного меню"""

    await callback.message.edit_caption(
        caption=texts.buildStartText(callback.from_user.full_name),
        parse_mode="Markdown",
        reply_markup=keyboards.buildStartKeyboard()
    )


@dp.callback_query(F.data.startswith("about_"))
async def aboutProduct(callback: types.CallbackQuery):
    """Хендлер колбека кнопки товара"""

    nominal_id = callback.data.replace("about_", "")
    product = await shape_sdk.products.getProduct(callback.from_user.id, nominal_id)
    await callback.message.edit_caption(
        caption=texts.buildProductText(product),
        reply_markup=keyboards.buildProductKeyboard(product)
    )

# ------------------------------- Orders -------------------------------------

@dp.callback_query(F.data == 'my_orders')
async def orders(callback: types.CallbackQuery, state: FSMContext):
    """Хендлер кнопки моих заказов"""

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
    await state.update_data(temporary_messages=temporary_messages)  # Записываем временные заказы в FSM


@dp.callback_query(F.data.startswith("order_expand_"))
async def moreOrder(callback: types.CallbackQuery):
    """Колбек кнопки свёртывания/развёртывания информации о заказе"""

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
    """Колбек для кнопки 'Оплатить заказ' в моих заказах"""

    order_id = callback.data.replace("jump_payment_", "")
    await clearTemp(state)
    await createPayment(callback.from_user.id, callback.message, state, order_id)


@dp.callback_query(F.data.startswith("check_payment_"))
async def checkPayment(callback: types.CallbackQuery, state: FSMContext):
    """Колбек для кнопки 'Проверить статус оплаты'"""

    order_id = callback.data.replace("check_payment_", "")
    order = await shape_sdk.orders.checkPayment(callback.from_user.id, order_id)

    if not order:
        await callback.answer('⚠️ Не удалось проверить статус оплаты')
        return
    
    if order.status == 'awaiting_payment':
        await callback.answer('Оплата не прошла. Попробуйте снова через несколько секунд')
        return
    
    await callback.message.edit_text(
        text=texts.buildOrderTextMore(order),
        reply_markup=keyboards.buildOrderKeyboardMore(order),
        parse_mode='Markdown'
    )

    await state.clear()  # По сути поток заказа завершён, чистим все временные данные 🧹


# ----------------------------- Orders ------------------------------------

@dp.callback_query(F.data.startswith("orderProduct_"))
async def orderProduct(callback: types.CallbackQuery, state: FSMContext):
    """
    Колбек для кнопки заказать в каталоге.  
    Начинает поток заказа
    """

    nominal_id = callback.data.replace("orderProduct_", "")
    _session: OrderSession | None = (await state.get_data()).get('session', None)  # Проверяем существование запущенного потока заказа
    await clearTemp(state)

    if _session:
        await callback.answer(text='У Вас есть незавершённый заказ. Завершите оформление всех заказов, прежде чем начать новый.')
        return

    product = await shape_sdk.products.getProduct(callback.from_user.id, nominal_id)
    if not product:
        await callback.answer('⚠️ Произошла ошибка при заказе товара! Перезагрузите бота или попробуйте позже')
        return

    await state.update_data(session=OrderSession(product.id, product.nominal_id))  # Создаем и записываем новый объект временных данных для пользователя

    if nominal_id in ['skin64', 'skin_premium']:
        """Если продуктом является скин — переходим к этапу выбора рук"""
        await selectHands(callback, state)
        return
    await inputParams(callback, state)


async def selectHands(callback: types.CallbackQuery, state: FSMContext):
    """Отправка сообщения с выбором рук (вызывается выше)"""

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
    """
    Колбек для кнопок выбора рук
    Так же переходим к этой функции без выбора рук, если заказ не является скином
    """

    _session: OrderSession | None = (await state.get_data()).get('session', None)
    await callback.answer()
    if not _session:
        await callback.message.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    if callback.data.startswith('hands_'):
        """
        Если функция была вызвана колбеком с кнопок выбора рук - записываем
        параметр рук в объект временных данных
        """
    
        message = await callback.message.edit_text(
            text=texts.buildInputsText(),
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
            text=texts.buildInputsText(),
            reply_markup=keyboards.buildInputsKeyboard(),
            parse_mode='Markdown'
        )

    await state.set_state(States.params_waiting)  # Устанавливаем FSM в состояние ожидания параметров
    await state.update_data(inputs_message=message)  # Запоминаем сообщение об отправке описания заказа на будущее


@dp.message(States.params_waiting)
async def handleParams(message: types.Message, state: FSMContext):
    """Принимает все сообщения в состоянии ожидания описания"""

    _session: OrderSession | None = (await state.get_data()).get('session', None)
    inputs_message: types.Message | None = (await state.get_data()).get('inputs_message', None)
    if not _session:
        await message.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    if message.photo:
        """Если сообщение - фото (далее по аналогии)"""

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
        """Если тип сообщения не подходит ко всем вышеперечисленным - пытаемся достать оттуда текст"""

        if message.text:
           _session.descriptions.append(message.text)

    if inputs_message:
        try:
            await inputs_message.edit_text(
                text=texts.buildInputsText() + \
                    f'\n\nКоличество вложений: *{len(_session.attachments)}*',
                reply_markup=inputs_message.reply_markup,
                parse_mode='Markdown'
            )
        except Exception:
            ...


@dp.callback_query(F.data == 'inputs_done')
async def inputsDone(callback: types.CallbackQuery, state: FSMContext):
    """Колбек кнопки подтверждения ввода параметров"""

    _session: OrderSession | None = (await state.get_data()).get('session', None)
    if not _session:
        await callback.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    """Собираем все данные для АПИ"""
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
    
    """
    ⚠️Важная пометка⚠️
    АПИ не возвращает id только что созданного заказа,
    поэтому приходится брать самый последний заказ из бд
    """
    await state.update_data(order_id=orders[-1].id)
    await createPayment(callback.from_user.id, callback.message, state)


async def createPayment(user_id: int, message: types.Message, state: FSMContext, orderId: int = None):
    """Функция для начала этапа оплаты"""

    # Прокинуть айдишник заказа через колбеки тут не выйдет, поэтому достаём его из FSM
    order_id: int | None = orderId or (await state.get_data()).get('order_id', None)
    user = await shape_sdk.user.getUser(user_id)
    if not user.email:
        """
        Если у текущего юзера не установлена почта,
        отправляем его на диалог добавления почты
        """
        await getEmail(message, state)
        return

    payment = await shape_sdk.orders.createPayment(user_id, order_id)
    await message.answer(
        text=texts.buildPaymentText(payment),
        reply_markup=keyboards.buildPaymentCheck(order_id),
        parse_mode='Markdown'
    )


async def getEmail(message: types.Message, state: FSMContext):
    """Функция для начала диалога добавления почты"""

    await message.answer('Пожалуйста, отправьте Ваш адрес электронной почты')
    await state.set_state(States.email_wait)  # Заставляем бота ждать почту


@dp.message(F.text, States.email_wait)
async def handleEmail(message: types.Message, state: FSMContext):
    """Хендлер сообщения с почтой"""

    try:
        email_info = validate_email(message.text)  # Валидируем почту
        result = await shape_sdk.user.setEmail(message.from_user.id, email_info.normalized)
        if not result:
            await message.answer('⚠️ Не удалось установить адрес электронной почты')
            return
        await createPayment(message.from_user.id, message, state)  # Возвращаемся к самому началу диалога оплаты
    except EmailNotValidError:
        """Если валидация не пошла"""
    
        await message.answer('Ваш адрес электронной почты имеет неправильный формат!')


@dp.callback_query(F.data.startswith("confirm_"))
async def confirmOrder(callback: types.CallbackQuery):
    """Колбек кнопки подтверждения заказа"""

    order_id = callback.data.replace("confirm_", "")
    status_code = await shape_sdk.orders.confirmOrder(callback.from_user.id, order_id)
    if status_code != 200:
        await callback.answer('⚠️ Не удалось подтвердить заказ')
        return
    
    order = await shape_sdk.orders.getOrder(callback.from_user.id, order_id)
    await callback.message.edit_text(
        text=texts.buildOrderTextMore(order),
        reply_markup=keyboards.buildOrderKeyboardMore(order),
        parse_mode='Markdown'
    )


@dp.callback_query(F.data.startswith("view_result_"))
async def viewResult(callback: types.CallbackQuery, state: FSMContext):
    """Колбек для кнопки просмотра результата"""

    order_id = callback.data.replace("view_result_", "")
    await clearTemp(state)

    order = await shape_sdk.orders.getOrder(callback.from_user.id, order_id)
    results = await shape_sdk.orders.getResult(callback.from_user.id, order_id)
    temporary_messages = [await callback.message.answer(
        text=texts.buildOrderTextMore(order),
        reply_markup=keyboards.buildOrderKeyboardMore(order, False),
        parse_mode='Markdown'
    )]
    await state.update_data(temporary_messages=temporary_messages)

    if not results:
        await callback.answer('⚠️ Не удалось получить результат')
        return
    
    for result in results:
        data = await api_manager.getResultPhoto(result.s3url)
        if not data:
            await callback.message.answer('⚠️ Не удалось получить результат!')
            return
        
        message_temp = await callback.message.answer_document(
            document=types.BufferedInputFile(file=data, filename="result.png"),
            parse_mode='Markdown'
        )
        temporary_messages.append(message_temp)

    await state.update_data(temporary_messages=temporary_messages)


@dp.callback_query(F.data.startswith("corrections_add_"))
async def addCorrections(callback: types.CallbackQuery, state: FSMContext):
    """Хендлер для кнопки внесения правок"""

    order_id = callback.data.replace("corrections_add_", "")
    await clearTemp(state)
    message = await callback.message.answer(
        text=texts.buildInputsText(),
        reply_markup=keyboards.buildInputsCorrectionKeyboard(order_id),
        parse_mode='Markdown'
    )
    """
    ⚠️Важная пометка⚠️
    Коррекции и заказ имеют один и тот же поток ввода описания,
    различия только в кнопках 'Подтвердить', которые относят к разным колбекам
    """
    await state.update_data(inputs_message=message, session=OrderSession(-1, -1))
    await state.set_state(States.params_waiting)  # Запускаем поток ввода описания


@dp.callback_query(F.data.startswith("correction_done_"))
async def correctionsFinish(callback: types.CallbackQuery, state: FSMContext):
    """Колбек с кнопки подтвердить ввод коррекции"""

    order_id = callback.data.replace("correction_done_", "")
    _session: OrderSession | None = (await state.get_data()).get('session', None)
    await callback.answer()
    if not _session:
        await callback.message.answer('Не удалось найти заказ! Отправьте /start что бы начать заново')
        return
    
    order = await shape_sdk.orders.getOrder(callback.from_user.id, order_id)
    if not order:
        await callback.answer('⚠️ Не удалось получить заказ для исправления')
        return
    
    descriptions = ' '.join(_session.descriptions)
    if not descriptions:
        await callback.message.answer('Отправьте хотя бы одно сообщение с описанием исправления!')
        return
    
    code = await shape_sdk.orders.createCorrection(
        callback.from_user.id,
        int(order_id),
        order.executor_id,  # Executor_id достаём из объекта заказа
        descriptions,
        _session.attachments
    )
    if code != 200:
        await callback.answer('⚠️ Не удалось создать исправление!')
        return
    
    await callback.message.answer('Запрос на исправление заказа успешно отправлен!')


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