from typing import List


class OrderSession:
    def __init__(self, product_id: str):
        self.descriptions: str = ''
        self.attachments: List[str] = []
        self.product_id: str = product_id
