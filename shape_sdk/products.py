from . import api_manager
from .types.product_type import ProductType
from typing import List

apiManager = api_manager.ApiManager()


async def getProducts(user_id: int) -> List[ProductType] | None:
    """Get all products"""

    body, status = await apiManager.send_request('/bot/products', user_id)
    if status != 200:
        return None

    return list(map(lambda product: ProductType(**product), body))


async def getProduct(user_id: int, product_id: str) -> ProductType | None:
    """Get product by id"""

    body, status = await apiManager.send_request(f'/bot/products/{product_id}', user_id)
    if status != 200:
        return None

    return ProductType(**body)
