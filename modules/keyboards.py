from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

from shape_sdk.types.order_type import OrderType
from shape_sdk.types.product_type import ProductType

def buildStartKeyboard(more: bool = False) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Заказать скин 🛒", callback_data='keyboard_skins')
                )
    builder.row(types.InlineKeyboardButton(text="Мои заказы 📦", callback_data='my_orders'),
                types.InlineKeyboardButton(text="Каталог 📚", callback_data='catalog')
                )
    
    if more:
        builder.row(types.InlineKeyboardButton(text="Связаться с нами", url='https://vk.com/shapestd'))
    return builder.as_markup()


def buildProductsMain() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Скины »", callback_data='keyboard_skins'))
    builder.row(types.InlineKeyboardButton(text="Тотем", callback_data='about_totem'))
    builder.row(types.InlineKeyboardButton(text="Аватар", callback_data='about_avatar'), )
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))

    return builder.as_markup()


def buildProductsSkinsMain() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Скин x64", callback_data='about_skin64'))
    builder.row(types.InlineKeyboardButton(text="Премиум скин", callback_data='about_skin_premium'))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data='catalog'),
                types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))

    return builder.as_markup()


def buildProductKeyboard(product: ProductType, nominal_id: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    bool(product) and builder.row(types.InlineKeyboardButton(text="📦 Заказать", callback_data=f'orderProduct_{product.nominal_id}'))
    back_callback = 'keyboard_skins' if nominal_id in ['skin64', 'skin_premium'] else 'catalog'
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data=back_callback),
                types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))
    return builder.as_markup()


def buildHandsKeyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Обычные", callback_data='hands_default'),
                types.InlineKeyboardButton(text="Тонкие", callback_data='hands_slim'))
    return builder.as_markup()


def buildInputsKeyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Продолжить", callback_data='inputs_done'))
    return builder.as_markup()


def buildOrderKeyboard(order: OrderType) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⬇️ Раскрыть", callback_data=f'order_expand_more_{order.id}'))
    return builder.as_markup()


def buildOrderKeyboardMore(order: OrderType) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    match order.status:
        case 'created':
            builder.row(types.InlineKeyboardButton(text="💳 Перейти к оплате", callback_data=f'jump_payment_{order.id}'))
        case 'awaiting_payment':
            builder.row(types.InlineKeyboardButton(text="💳 Проверить статус оплаты", callback_data=f'check_payment_{order.id}'))
        case 'awaiting_confirmation':
            builder.row(types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f'confirm_{order.id}'))
    builder.row(types.InlineKeyboardButton(text="⬆️ Свернуть", callback_data=f'order_expand_less_{order.id}'))
    return builder.as_markup()