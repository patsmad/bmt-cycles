from .util_io import readJSON
from flask import request
from functools import wraps
from typing import Optional, Callable

class Config:
    def __init__(self) -> None:
        config: dict = readJSON('config')
        self.api_key: str = config['api-key']
        self.headers: dict = config['headers']

    def api_key_match(self, api_key: str) -> bool:
        return api_key == self.api_key

    def api_check(self, fnc: Callable) -> Callable:
        @wraps(fnc)
        def inner_api_check(*args, **kwargs):
            maybe_api_key: Optional[str] = request.args.get('api_key')
            if maybe_api_key is None:
                raise APIMissingException
            elif not self.api_key_match(maybe_api_key):
                raise APIInvalidException
            else:
                return fnc(*args, **kwargs)
        return inner_api_check

class APIMissingException(Exception):

    def __init__(self) -> None:
        super().__init__("Must provide valid api_key as ?api_key=<key> on request")

class APIInvalidException(Exception):
    "Must provide valid api_key as ?api_key=<key> on request"

    def __init__(self) -> None:
        super().__init__("Invalid API Key")
