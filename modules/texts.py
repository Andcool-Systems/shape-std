from shape_sdk import ProductType


def buildStartText(name: str) -> str:
    return f"Привет, {name}!\n" + \
            "Для оформления заказа используйте клавиатуру\n" + \
            "При возникновении проблем перезагрузите бота. Для перезагрузки отправьте команду /start"


def buildProductText(product: ProductType) -> str:
    return f'{product.title} — {product.price}{product.nominal_id}\n' + \
           f'🏷 Скидка: {product.discount}%\n\n' + \
           product.description
