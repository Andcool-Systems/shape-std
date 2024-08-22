from typing import List


class UserType:
    """User type"""

    def __init__(self, 
                 id: int, 
                 email: str, 
                 first_name: str, 
                 last_name: str, 
                 created_at: str, 
                 roles: List[str]):
        self.id: int = id
        self.email: str = email
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.created_at = created_at
        self.roles: List[str] = roles
