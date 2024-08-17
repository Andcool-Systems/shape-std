import os
import aiohttp
import orjson

class ApiManager:
    def __init__(self):
        self.headers = {
            'shape-bot-token': os.getenv('SHAPE_TOKEN'),
            'network-id': 'TG',
            'Content-Type': 'application/json'
        }

    async def send_request(self, url: str, user_id: int, body: any = None, method='GET'):
        headers = self.headers.copy()
        headers['user-id'] = str(user_id)
        try:
            async with aiohttp.ClientSession(os.getenv('API_URL')) as session:
                match method:
                    case 'GET':
                        async with session.get(url, headers=headers) as response:
                            response_data = await response.json()
                            return response_data, response.status
                    case 'POST':
                        async with session.post(url, headers=headers, data=orjson.dumps(body)) as response:
                            response_data = await response.json()
                            return response_data, response.status
                    case 'PATCH':
                        async with session.patch(url, headers=headers, data=orjson.dumps(body)) as response:
                            response_data = await response.json()
                            return response_data, response.status
        except Exception as e:
            print('API exception has ocurred:', e)
            return None, 502
