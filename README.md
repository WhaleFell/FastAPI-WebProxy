# FastAPI-Proxy

A webproxy base on FastAPI.Can build to vercel and any support python serverless platform.

## Development

Use `black` for code formatting and `mypy` for static code analysis.

**Must use python virual envirement to develop.Use Python3.8 to develop**

In Windows.

```shell
# build python virtual envirement
python -m venv ./venv

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

1. webproxy:
    - url: `/proxy/{url:path}` method: GET,POST desc: proxy website request
    - url: `/file/{url:path}` method: GET,POST desc: streaming download large file

2. access log:
    - url: `/log/` method: GET desc: get access log
    - url: `/log/rm?key={password}` method: GET desc: remove all access log

3. ip info: (use qqwry ip database)
    - url: `/ip/?ip=1.1.1.1` method: GET desc: get ip info if without ip param will get client ip info.