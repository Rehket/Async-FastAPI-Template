# FastAPI Repo to identify an issue.(Now Fixed)

- This repo to demonstrate a bug I am experiencing with trying to run a fastapi application. 
- The fix is to convert response from a SQLAlchemy model instance to a dict, a pydantic model instance or by setting  ```orm_mode = True``` in the model config class. 

## Issue Details
### Environment
- Windows 10
- Postgres Database Running in Docker
- Python 3.7.2
- Package versions included in req.txt
- Docker 2.1.0.0

### Setup
- Create and activate a virtual environment
- Setup the env.ps1 script with desired variables. 
- In the virtual environment:
    - run the ```env.ps1``` script to set the environment variables. 
    - install the packages included in the ```req.txt```
    - run ```python ./bootstrap.py```
    - run ```alembic upgrade head```
    - run ```python ./initial_data.py```
    - run ```uvicorn app.main:app --reload``` to start the application 

## Behavior
- Once the application is running, by 
going to ```localhost:8000/docs``` or what you configured in the env.ps1, you will be able to login and tryout the endpoints. 

### Expected
- When retrieving the data from the User Endpoints, the user data present in the database should be returned as json. 

### Actual
-  A server error is raised indicating the response is not a dict.

``` python 
Traceback (most recent call last):
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 375, in run_asgi
    result = await app(self.scope, self.receive, self.send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\applications.py", line 133, in __call__
    await self.error_middleware(scope, receive, send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\middleware\errors.py", line 177, in __call__
    raise exc from None
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\middleware\errors.py", line 155, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\middleware\base.py", line 25, in __call__
    response = await self.dispatch_func(request, self.call_next)
  File "C:/Users/adama/Workspace/Python/TryFast/app/main.py", line 34, in db_session_middleware
    response = await call_next(request)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\middleware\base.py", line 45, in call_next
    task.result()
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\middleware\base.py", line 38, in coro
    await self.app(scope, receive, send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\middleware\cors.py", line 76, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\exceptions.py", line 73, in __call__
    raise exc from None
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\exceptions.py", line 62, in __call__
    await self.app(scope, receive, sender)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\routing.py", line 585, in __call__
    await route(scope, receive, send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\routing.py", line 207, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\starlette\routing.py", line 40, in app
    response = await func(request)
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\fastapi\routing.py", line 122, in app
    skip_defaults=response_model_skip_defaults,
  File "C:\Users\adama\.virtualenvs\TryFast\lib\site-packages\fastapi\routing.py", line 54, in serialize_response
    raise ValidationError(errors)
pydantic.error_wrappers.ValidationError: 1 validation error
response
  value is not a valid dict (type=type_error.dict)

```


