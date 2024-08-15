class OrderType:
    def __init__(self, 
                 id: int,
                 product_id: int,
                 executor_id: int | None,
                 status: str,
                 rate: int,
                 profit: str,
                 corrections_limit: str,
                 created_at: str,
                 start_time: str,
                 send_time: str,
                 confirm_time: str) -> None:
        self.id: int = id
        self.product_id: int = product_id
        self.executor_id: int | None = executor_id
        self.status: str = status
        self.rate: int = rate
        self.profit: str = profit
        self.corrections_limit: str = corrections_limit
        self.created_at: str = created_at
        self.start_time: str = start_time
        self.send_time: str = send_time
        self.confirm_time: str = confirm_time


class OrderResultType:
    def __init__(self, 
                id: str,
                s3url: str,
                title: str,
                extension: str,
                size: int) -> None:
        self.id: str = id
        self.s3url: str = s3url
        self.title: str = title
        self.extension: str = extension
        self.size: int = size