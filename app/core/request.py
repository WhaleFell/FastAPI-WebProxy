#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# request.py
# rewapped httpx in order to support vercel serverless.
# because vercel serverless doesn't support asynchronous greatly.
# deploy in vercel. May cause attached to a different loop.

import httpx

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
}


# async def log_request(request):
#     print(f"Request event hook: {request.method} {request.url} - Waiting for response")


# async def log_response(response):
#     request = response.request
#     print(
#         f"Response event hook: {request.method} {request.url} - Status {response.status_code}"
#     )


GLOBAL_ASYNC_CLIENT = httpx.AsyncClient(
    headers=header,
    limits=httpx.Limits(max_keepalive_connections=1000),
    verify=False,
    timeout=8,
    # event_hooks={"request": [log_request], "response": [log_response]},
)

GLOBAL_CLIENT = httpx.Client(
    headers=header,
    limits=httpx.Limits(max_keepalive_connections=1000),
    verify=False,
    timeout=8,
)
