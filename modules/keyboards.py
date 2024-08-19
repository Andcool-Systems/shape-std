from typing import List
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


def getPrice(products: List[ProductType], nominal_id: str):
    for product in products:
        if product.nominal_id == nominal_id:
            return product.price
    return None


def buildProductsMain(products: List[ProductType]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=f"Премиум скин x64 — {getPrice(products, 'skin_premium') or 499}₽", callback_data='about_skin_premium'))
    builder.row(types.InlineKeyboardButton(text=f"Стандарт скин x64 — {getPrice(products, 'skin64') or 299}₽", callback_data='about_skin64'))
    builder.row(types.InlineKeyboardButton(text=f"Аватар — {getPrice(products, 'avatar') or 249}₽", callback_data='about_avatar'),
                types.InlineKeyboardButton(text=f"Тотем — {getPrice(products, 'totem') or 139}₽", callback_data='about_totem'))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))

    return builder.as_markup()


def buildProductsSkinsMain(products: List[ProductType]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=f"Премиум скин x64 — {getPrice(products, 'skin_premium') or 499}₽", callback_data='about_skin_premium'))
    builder.row(types.InlineKeyboardButton(text=f"Стандарт скин x64 — {getPrice(products, 'skin64') or 299}₽", callback_data='about_skin64'))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))

    return builder.as_markup()


def buildProductKeyboard(product: ProductType, nominal_id: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    product and builder.row(types.InlineKeyboardButton(text="📦 Заказать", callback_data=f'orderProduct_{product.nominal_id}'))
    builder.row(types.InlineKeyboardButton(text="« Назад", callback_data='catalog'),
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
