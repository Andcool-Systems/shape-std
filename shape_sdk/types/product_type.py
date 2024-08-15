class ProductType:
    """Product object"""
    
    def __init__(self, 
                 id: int, 
                 nominal_id: str, 
                 title: str, 
                 price: int, 
                 discount: int, 
                 description: str):
        self.id: int = id
        self.nominal_id: str = nominal_id
        self.title: str = title
        self.price: int = price
        self.discount: int = discount
        self.description: str = description
