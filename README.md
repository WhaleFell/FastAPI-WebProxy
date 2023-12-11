# FastAPI-Proxy

A webproxy base on FastAPI.Can build to vercel and any support python serverless platform.

## Development

**Must use python virual envirement to develop.Use Python3.8 to develop**

In Windows.

```shell

python -m venv ./venv

# Set Powershell Limited
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Activate
.\venv\Scripts\Activate.ps1

# update pip version
python -m pip install --upgrade pip

# install require model
pip install --upgrade -r requirements.txt --index-url=https://pypi.org/simple

uvicorn app.main:app --port 8000 --reload
```
