from enum import StrEnum


class Category(StrEnum):
    CREDIT_REPORTING = "Credit reporting"
    DEBT_COLLECTION = "Debt collection"
    MORTGAGE = "Mortgage"
    CREDIT_CARD = "Credit card"
    BANK_ACCOUNT = "Bank account or service"
    CONSUMER_LOAN = "Consumer loan"
    MONEY_TRANSFER = "Money transfer or service"


CATEGORY_VALUES = tuple(category.value for category in Category)

