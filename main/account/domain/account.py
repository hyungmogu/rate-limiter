class Account:
    def __init__(self, hashed_iPv6: str):
        self._id = hashed_iPv6
    
    def get_id(self):
        return self._id
    
    def get_count(self):
        pass

    def set_count(self):
        pass