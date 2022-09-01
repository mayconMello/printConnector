from typing import Callable, Dict


class BaseClass(object):
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        raise NotImplementedError


class HandlerFactoryEvents:
    events = {}

    @classmethod
    def register_handler(cls, event: str):
        def wrapper(handler_cls):
            cls.events[event] = handler_cls
            return handler_cls

        return wrapper

    @classmethod
    def get_handler(cls, event: str) -> Callable[[BaseClass], Dict]:
        return cls.events[event]
