import asyncio
import logging
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

load_dotenv()
logging.basicConfig(level=logging.INFO)
TOKEN=os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

class States(StatesGroup):
    """Стейты для aiogram"""
    active_order = State()
    params_waiting = State()


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


@dp.callback_query(F.data.startswith("more_"))
async def more(callback: types.CallbackQuery):
    more = callback.data.replace("more_", "") == 'more'
    await callback.message.edit_caption(caption=texts.buildStartText(callback.from_user.full_name),
                                        parse_mode="Markdown",
                                        reply_markup=keyboards.buildStartKeyboard(more)
    )


@dp.callback_query(F.data == 'catalog')
async def catalog(callback: types.CallbackQuery):
    products = await shape_sdk.products.getProducts(callback.from_user.id)
    await callback.answer()

    if not products:
        await callback.message.answer(text='⚠️ Не удалось получить каталог товаров!')
        return
    
    for product in products:
        await callback.message.answer(text=texts.buildProductText(product),
                                      reply_markup=keyboards.buildProductKeyboard(product.id))
        

@dp.callback_query(F.data == 'my_orders')
async def orders(callback: types.CallbackQuery):
    orders = await shape_sdk.orders.getOrders(callback.from_user.id)
    await callback.answer()
    
    if len(orders) == 0:
        await callback.message.answer(text='У вас еще нет заказов')
        return
        
    if not orders:
        await callback.message.answer(text='⚠️ Не удалось получить список заказов!')
        return
    
    for order in sorted(orders, key=lambda order: order.id):
        await callback.message.answer(text=texts.buildOrderText(order))


@dp.callback_query(F.data.startswith("orderProduct_"))
async def orderProduct(callback: types.CallbackQuery, state: FSMContext):
    product_id = callback.data.replace("orderProduct_", "")
    _session: OrderSession | None = (await state.get_data()).get('session', None)

    if _session:
        await callback.answer('У Вас есть незавершённый заказ. Завершите оформление всех заказов, прежде чем начать новый.')
        return
    
    await state.update_data(session=OrderSession(product_id))


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