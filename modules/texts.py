import time
from typing import List
from shape_sdk import ProductType, OrderType
from shape_sdk.types.payments import PaymentHandler
from datetime import datetime


def buildStartText(name: str) -> str:
    return f"Привет, {name}!\n" + \
            "Для оформления заказа используйте клавиатуру\n" + \
            "При возникновении проблем перезагрузите бота. Для перезагрузки отправьте команду /start"


def buildProductText(product: ProductType | None) -> str:
    if not product:
        return '⚠️ Не удалось получить информацию о продукте!'

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


def numbersTxt(num: str, variations: List[str]):
    past = str(int(num))[-1:]
    first = str(int(num))[-2:-1]
    
    if past == "1" and int(num) != 11: text = variations[0]  # голос
    elif past in ["2", "3", "4"] and first != "1": text = variations[1]  # голоса
    else: text = variations[2]  # голосов

    return str(num) + " " + text


def timeDelta(timestamp: str):
    onlineTime = 300  # 5min
    delta = round(time.time() - timestamp)
    if delta < onlineTime: return "Только что"
    elif delta < 3600: return numbersTxt(delta // 60, ["минуту", "минуты", "минут"]) + " назад"
    elif delta // 3600 < 24: return numbersTxt(delta // 3600, ["час", "часа", "часов"]) + " назад"
    elif delta // 86_400 < 30: return numbersTxt(delta // 86_400, ["день", "дня", "дней"]) + " назад"
    elif delta // 2_592_000 < 12: return numbersTxt(delta // 2_592_000, ["месяц", "месяца", "месяцев"]) + " назад"
    else: return numbersTxt(delta // 31_104_000, ["год", "года", "лет"]) + " назад"


def buildOrderText(order: OrderType) -> str:
    return f'Заказ #{order.id} — {order.product.title}'


def buildOrderTextMore(order: OrderType) -> str:
    created_at = datetime.fromisoformat(order.created_at).timestamp() + 10_800
    return f'Заказ #{order.id} — {order.product.title}\n\n' + \
           f'Статус: *{state_str[order.status]}*\n' + \
           f'Товар: *{order.product.title}*\n' + \
           f'Создан: *{timeDelta(created_at)}*'


def buildInputsKeyboard() -> str:
    return 'Теперь опишите ваш заказ. Можете отправлять референсы *как файлы* или же просто опишите заказ текстом.\n\n' + \
           'Затем нажмите кнопку "Продолжить"'


def buildPaymentText(payment: PaymentHandler) -> str:
    return f'Ссылка для оплаты заказа на сумму {payment.amount}₽ создана.\n\n' + \
           str(payment.url)
