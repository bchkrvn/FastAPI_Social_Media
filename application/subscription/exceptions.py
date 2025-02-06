from application.base.exceptions import BaseAppException


class ReSubscriptionError(BaseAppException):
    def __init__(self, details: dict):
        self.msg = "Нельзя подписаться дважды на кого-либо"
        self.details = details


class SubscriptionForYourselfError(BaseAppException):
    def __init__(self, details: dict):
        self.msg = "Нельзя подписаться дважды на кого-либо"
        self.details = details
