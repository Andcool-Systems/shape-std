from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def buildStartKeyboard(more: bool = False) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Заказать скин 🛒", callback_data='order_skin'),
                types.InlineKeyboardButton(text="Каталог 📚", callback_data='catalog'))
    builder.row(types.InlineKeyboardButton(text="Мои заказы 📦", callback_data='my_orders'),
                types.InlineKeyboardButton(text="Купоны 🎟", callback_data='my_coupons'),
                types.InlineKeyboardButton(text='Ещё ⚙' if not more else 'Скрыть ⚙', callback_data='more_more' if not more else 'more_less'))
    
    if more:
        builder.row(types.InlineKeyboardButton(text="Связаться с нами", url='https://vk.com/shapestd'))
    return builder.as_markup()


def buildProductKeyboard(product_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📦 Заказать", callback_data=f'orderProduct_{product_id}'))