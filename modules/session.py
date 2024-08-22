from typing import Dict, List


class OrderSession:
    """Объект, хранящий временные данные заказа пользователя"""

    def __init__(self, id: int, nominal_id: str):
        self.descriptions: List[str] = []
        self.parameters: List[Dict[str, str]] = []
        self.attachments: List[str] = []
        self.product_id: str = id
        self.nominal_id = nominal_id
