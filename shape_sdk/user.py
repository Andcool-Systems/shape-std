import os
from . import api_manager
from .types.user_type import UserType

apiManager = api_manager.ApiManager()


async def getUser(user_id: int) -> UserType | None:
    body, status = await apiManager.send_request('/bot/users', user_id)
    if status != 200:
        return None
    
    return UserType(**body)


async def setEmail(user_id: int, email: str) -> bool:
    _, status = await apiManager.send_request(f'/bot/users/email/set?email={email}', user_id, method='PATCH')
    return status == 200


async def createUser(user_id: int, first_name: str, last_name: str) -> bool:
    body = {
        'first_name': first_name,
        'last_name': last_name
    }
    res, status = await apiManager.send_request('/bot/users/create', user_id, body=body, method='POST')
    print(res)
    return status
