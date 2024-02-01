# FastAPI-Proxy

A webproxy base on FastAPI.Can build to vercel and any support python serverless platform.

## Compatibility

Currently(2024/2/1), there are different versions of Python on different serverless platforms. The following is a list of the versions of Python supported by different serverless platforms:

- [Vercel](https://vercel.com/): 3.9
- [Render](https://render.com/) 3.11

So the project needs to be compatible with a minimum of Python 3.9. All kinds of high-level grammatical sugar in Python 3.11 are not supported.Example: `str | None` union type / `match` statement ...

related discussion: <https://github.com/orgs/vercel/discussions/639>

## Development

Use `black` for code formatting and `mypy` for static code analysis.

**Must use python virual envirement to develop.Use Python3.8 to develop**

In Windows.

```shell
# build python virtual envirement
python -m venv ./venv
# If your have multiple python version,use specific python version to build virtual envirement
py --list # list all python version
py -3.11 -m venv ./venv

# Set Powershell Limited
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate virtual envirement
.\venv\Scripts\Activate.ps1

# update pip version
python -m pip install --upgrade pip --index-url=https://pypi.org/simple

# install require model
pip install --upgrade -r requirements.txt --index-url=https://pypi.org/simple

# run fastapi by uvicorn
uvicorn app.main:app --port 8000 --reload
```

## API Interface

detail API Document please visit `http://IP/docs` or `http://IP/redoc`. This is FastAPI auto generate API document by Swagger and Redoc.

1. webproxy:
    - url: `/proxy/{url:path}` method: GET,POST desc: proxy website request
    - url: `/file/{url:path}` method: GET,POST desc: streaming download large file

2. access log:
    - url: `/log/` method: GET desc: get access log
    - url: `/log/rm?key={password}` method: GET desc: remove all access log

3. ip info: (use qqwry ip database)
    - url: `/ip/?ip=1.1.1.1` method: GET desc: get ip info if without ip param will get client ip info.

## Notice

source: https://github.com/vercel/vercel/issues/8477

Because FastAPI is ASGI framework,so it have some problem when deploy to vercel.

vercel ASGI runtime create an new event loop on each request.So when use some async module will create new event loop in sigle request like `aiohttp` and `httpx` will raise error.

```shell
2023-12-19 08:50:21.426 | ERROR    | app.helper.func:wrapper:43 - retry 1 times.reason: Task <Task pending name='starlette.middleware.base.BaseHTTPMiddleware.__call__.<locals>.call_next.<locals>.coro' coro=<BaseHTTPMiddleware.__call__.<locals>.call_next.<locals>.coro() running at /var/task/starlette/middleware/base.py:70> cb=[TaskGroup._spawn.<locals>.task_done() at /var/task/anyio/_backends/_asyncio.py:661]> got Future <Future pending> attached to a different loop
```

one solution way is add a retry decorator to any use async module function.
