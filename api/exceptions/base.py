class APIError(Exception):
    def __ini__(self, message="An error occurred.", status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
