class CorrectionType:
    def __init__(self,
                 id: int,
                 order_id: int,
                 executor_id: int,
                 complete: bool,
                 task: str,
                 created_at: str) -> None:
        self.id: int = id
        self.order_id: int = order_id
        self.executor_id: int = executor_id
        self.complete: bool = complete
        self.task: str = task
        self.created_at: str = created_at