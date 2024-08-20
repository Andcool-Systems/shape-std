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


def getPriceStr(products: List[ProductType], nominal_id: str):
    for product in products:
        if product.nominal_id == nominal_id:
            return f'{product.price}₽'
    return None


def buildProductsMain(products: List[ProductType]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=f"Премиум скин x64 — {getPriceStr(products, 'skin_premium') or 'Недоступно'}", callback_data='about_skin_premium' if getPriceStr(products, 'skin_premium') else 'pass'))
    builder.row(types.InlineKeyboardButton(text=f"Стандарт скин x64 — {getPriceStr(products, 'skin64') or 'Недоступно'}", callback_data='about_skin64' if getPriceStr(products, 'skin64') else 'pass'))
    builder.row(types.InlineKeyboardButton(text=f"Аватар — {getPriceStr(products, 'avatar') or 'Недоступно'}", callback_data='about_avatar' if getPriceStr(products, 'avatar') else 'pass'),
                types.InlineKeyboardButton(text=f"Тотем — {getPriceStr(products, 'totem') or 'Недоступно'}", callback_data='about_totem' if getPriceStr(products, 'totem') else 'pass'))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))

    return builder.as_markup()


def buildProductsSkinsMain(products: List[ProductType]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=f"Премиум скин x64 — {getPriceStr(products, 'skin_premium') or 'Недоступно'}", callback_data='about_skin_premium' if getPriceStr(products, 'skin_premium') else 'pass'))
    builder.row(types.InlineKeyboardButton(text=f"Стандарт скин x64 — {getPriceStr(products, 'skin64') or 'Недоступно'}", callback_data='about_skin64' if getPriceStr(products, 'skin64') else 'pass'))
    builder.row(types.InlineKeyboardButton(text="« Главное меню", callback_data='main_menu'))

    return builder.as_markup()


def buildProductKeyboard(product: ProductType) -> InlineKeyboardBuilder:
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


def buildInputsCorrectionKeyboard(order_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Продолжить", callback_data=f'correction_done_{order_id}'))
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
            builder.row(types.InlineKeyboardButton(text="✨ Посмотреть результат", callback_data=f'view_result_{order.id}'))
            builder.row(types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f'confirm_{order.id}'),
                        types.InlineKeyboardButton(text="🔄 Запросить правки", callback_data=f'corrections_add_{order.id}'))
        case 'done':
            builder.row(types.InlineKeyboardButton(text="✨ Посмотреть результат", callback_data=f'view_result_{order.id}'))
    builder.row(types.InlineKeyboardButton(text="⬆️ Свернуть", callback_data=f'order_expand_less_{order.id}'))
    return builder.as_markup()


def buildPaymentCheck(order_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💳 Проверить статус оплаты", callback_data=f'check_payment_{order_id}'))
    return builder.as_markup()

