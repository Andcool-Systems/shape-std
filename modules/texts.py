import time
from typing import List
from shape_sdk import ProductType, OrderType
from shape_sdk.types.order_type import OrderResultType
from shape_sdk.types.payments import PaymentHandler
from aiogram.utils.markdown import link
from datetime import datetime


def buildStartText(name: str) -> str:
    """Конструктор главного сообщения бота"""

    return f"Привет, {name}!\n\n" + \
            "Для оформления заказа используйте клавиатуру\n\n" + \
            "При возникновении проблем перезагрузите бота. Для перезагрузки отправьте команду /start"


def buildProductText(product: ProductType | None) -> str:
    """Конструктор описания продукта"""

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
    """Конструктор краткой информации о заказе"""

    return f'Заказ #{order.id} — {order.product.title}'


def buildOrderTextMore(order: OrderType) -> str:
    """Конструктор полного сообщения информации о заказе"""

    created_at = datetime.fromisoformat(order.created_at).timestamp() + 10_800
    return f'Заказ #{order.id} — {order.product.title}\n\n' + \
           f'Статус: *{state_str[order.status]}*\n' + \
           f'Товар: *{order.product.title}*\n' + \
           f'Создан: *{timeDelta(created_at)}*'


def buildInputsText() -> str:
    """Конструктор сообщения ожидания описания заказа"""

    return 'Опишите ваш заказ\n\n' + \
           'Можете прикреплять фотографии и файлы (развёртку скина нужно отправить в виде PNG документа).\n\n' + \
           'Как будете уверены, что всё отправлено полностью нажмите «Продолжить»'


def buildPaymentText(payment: PaymentHandler) -> str:
    """Конструктор сообщения об оплате"""

    return f'Ссылка для оплаты заказа на сумму {payment.amount}₽ создана.'


def buildNoAttachmentText() -> str:
    """Конструктор сообщения об отсутствии вложений"""

    return f'В вашем описании нет вложений, желаете продолжить?'


def buildPaymentErrorText() -> str:
    return 'Оплата не прошла\n\n' + \
           'Попробуйте оплатить снова или обратитесь в поддержку: @aktib4ik'
