from starlette.requests import Request


def get_db(request: Request):
    return request.state.db


def get_async_db(request: Request):
    return request.state.async_db
