class PaystackError(Exception):
    pass

class PaystackVerificationError(PaystackError):
    def __init__(self, message):
        self.message = message

class OrderNotFoundError(PaystackError):
    def __init__(self, reference):
        self.message = f"Order with reference '{reference}' not found."