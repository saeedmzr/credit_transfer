from enum import Enum

class TransactionStatuses(Enum):

    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    FAILED = "Failed"
    REJECTED = "Rejected"
    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]

class TransactionTypes(Enum):
    CHARGE = "Charge"
    TRANSFER_IN = "Transfer_in"
    TRANSFER_OUT = "Transfer_out"

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]