class PaymentHandler:
    def __init__(self, 
                 id: int, 
                 amount: int, 
                 url: str, 
                 ):
        self.id: int = id
        self.amount: int = amount
        self.url: str = url
