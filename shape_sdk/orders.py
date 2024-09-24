from shape_sdk.types.payments import PaymentHandler
from . import api_manager
from .types.corrections_type import CorrectionType
from .types.order_type import OrderType, OrderResultType, PromocodeType
from typing import List
from .products import getProducts


apiManager = api_manager.ApiManager()


async def createOrder(user_id: int, product_id: int, parameters: any, attachments: any) -> int:
    """Create order"""

    body = {
        'product_id': product_id,
        'parameters': parameters,
        'attachments': attachments
    }
    _, status = await apiManager.send_request('/bot/orders/create', user_id, body=body, method='POST')
    return status


async def confirmOrder(user_id: int, order_id: str) -> int:
    """Confirm order by id"""

    _, status = await apiManager.send_request(f'/bot/orders/{order_id}/confirm', user_id, method='POST')
    return status


async def getOrder(user_id: int, order_id: str) -> OrderType | None: 
    """Get order by id"""

    body, status = await apiManager.send_request(f'/bot/orders/{order_id}', user_id)
    products = await getProducts(user_id)
    if status != 200 or not products:
        return None
    
    return OrderType(products, **body)


async def getOrders(user_id: int) -> List[OrderType] | None:
    """Get user's orders"""

    body, status = await apiManager.send_request(f'/bot/users/orders', user_id)
    products = await getProducts(user_id)
    if status != 200 or not products:
        return None

    return sorted(list(map(lambda order: OrderType(products, **order), body)), key=lambda order: order.id)


async def getCorrections(user_id: int, order_id: int) -> List[CorrectionType] | None:
    """Get order corrections"""

    body, status = await apiManager.send_request(f'/bot/orders/{order_id}/corrections', user_id)

    if status != 200:
        return None
    
    return list(map(lambda order: CorrectionType(**order), body))


async def createCorrection(user_id: int, order_id: int, executor_id: int, task: str, attachments: any) -> int:
    """Create order correction"""

    requestBody = {
        'order_id': order_id,
        'executor_id': executor_id,
        'task': task,
        'attachments': attachments
    }
    _, status = await apiManager.send_request(f'/bot/corrections/create', user_id, body=requestBody, method='POST')

    return status


async def correctionHandler(user_id: int, correction_id: int) -> CorrectionType | None:
    """Get correction by id"""

    body, status = await apiManager.send_request(f'/bot/corrections/{correction_id}', user_id)
    if status != 200:
        return None
    
    return CorrectionType(**body)


async def getResult(user_id: int, order_id: int) -> List[OrderResultType] | None:
    """Get order result by id"""

    body, status = await apiManager.send_request(f'/bot/orders/{order_id}/result', user_id)
    if status != 200:
        return None
    
    return list(map(lambda order: OrderResultType(**order), body))


async def createPayment(user_id: int, order_id: int) -> PaymentHandler | None:
    """Create order payment"""

    body, status = await apiManager.send_request(f'/bot/orders/{order_id}/payment/create', user_id)
    if status != 200:
        return None
    
    return PaymentHandler(**body)


async def checkPayment(user_id: int, order_id: int) -> OrderType | None:
    """Check order payment status"""

    body, status = await apiManager.send_request(f'/bot/orders/{order_id}/payment/check', user_id)
    products = await getProducts(user_id)
    if status != 200:
        return None
    
    return OrderType(products, **body)


async def getPromocode(user_id: int, promocode_id: str) -> PromocodeType | None: 
    """Get promocode by id"""

    body, status = await apiManager.send_request(f'/bot/promocodes/{promocode_id}', user_id)
    if status != 200:
        return None
    
    return PromocodeType(**body)


async def usePromocode(user_id: int, order_id: str, promocode_id: str) -> bool: 
    """Use promocode in order"""

    _, status = await apiManager.send_request(f'/bot/orders/{order_id}/promocode?id={promocode_id}', user_id, method='POST')
    return status
