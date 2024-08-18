from . import api_manager
from .types.corrections_type import CorrectionType
from .types.order_type import OrderType, OrderResultType
from typing import List
from .products import getProducts


apiManager = api_manager.ApiManager()


async def createOrder(user_id: int, product_id: int, parameters: any, attachments: any) -> int:
    body = {
        'product_id': product_id,
        'parameters': parameters,
        'attachments': attachments
    }
    _, status = await apiManager.send_request('/bot/orders/create', user_id, body=body, method='POST')
    return status


async def confirmOrder(user_id: int, order_id: str) -> int:
    _, status = await apiManager.send_request(f'/bot/orders/{order_id}/confirm', user_id, method='POST')
    return status


async def getOrder(user_id: int, order_id: str) -> OrderType | None: 
    body, status = await apiManager.send_request(f'/bot/orders/{order_id}', user_id)
    if status != 200:
        return None
    
    return OrderType(**body)


async def getOrders(user_id: int) -> List[OrderType] | None: 
    body, status = await apiManager.send_request(f'/bot/users/orders', user_id)
    products = await getProducts(user_id)
    if status != 200 or not products:
        return None

    return list(map(lambda order: OrderType(products, **order), body))


async def getCorrections(user_id: int, order_id: int) -> List[CorrectionType] | None:
    body, status = await apiManager.send_request(f'/bot/orders/{order_id}/corrections', user_id)

    if status != 200:
        return None
    
    return list(map(lambda order: CorrectionType(**order), body))


async def placeToQueue(user_id: int, order_id: int) -> bool:
    _, status = await apiManager.send_request(f'/bot/orders/{order_id}/queue', user_id)
    return status


async def createCorrection(user_id: int, order_id: int, executor_id: int, task: str, attachments: any) -> int:
    requestBody = {
        'order_id': order_id,
        'executor_id': executor_id,
        'task': task,
        'attachments': attachments
    }
    _, status = await apiManager.send_request(f'/bot/corrections/create', user_id, body=requestBody, method='POST')

    return status


async def correctionHandler(user_id: int, correction_id: int) -> CorrectionType | None:
    body, status = await apiManager.send_request(f'/bot/corrections/{correction_id}', user_id)
    if status != 200:
        return None
    
    return CorrectionType(**body)


async def getResult(user_id: int, order_id: int) -> OrderResultType | None:
    body, status = await apiManager.send_request(f'/bot/orders/{order_id}/result', user_id)
    if status != 200:
        return None
    
    return list(map(lambda order: OrderResultType(**order), body))
