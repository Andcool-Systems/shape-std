from shape_sdk import ProductType, OrderType


def buildStartText(name: str) -> str:
    return f"Привет, {name}!\n" + \
            "Для оформления заказа используйте клавиатуру\n" + \
            "При возникновении проблем перезагрузите бота. Для перезагрузки отправьте команду /start"


def buildProductText(product: ProductType) -> str:
    return f'{product.title} — {product.price}₽\n' + \
           f'🏷 Скидка: {product.discount}%\n\n' + \
           product.description


state_str = {
    'created': '✨ Создан',
    'on_correction': '🔄 На доработке',
    'awaiting_payment': '💳 Ожидание оплаты',
    'in_queue': '⏳ В очереди',
    'appointed_to_artist': '🎨 Взят художником',
    'in_progress': '⏳ В работе',
    'awaiting_confirmation': '⏺️ Ожидает подтверждения',
    'done': '✅ Выполнен'
}


def buildOrderText(order: OrderType) -> str:
    return f'Заказ №{order.id} — {order.product.title}\n' + \
           f'Статус: {state_str.get(order.status, state_str["created"])}'
