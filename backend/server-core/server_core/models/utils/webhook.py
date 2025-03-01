import asyncio
import aiohttp
import json
from concurrent.futures import ThreadPoolExecutor

DEFAULT_MAX_WORKERS = 10
DEFAULT_TIMEOUT = 10

executor = ThreadPoolExecutor(max_workers=DEFAULT_MAX_WORKERS)


async def send_webhook_async(url, payload, callback=None):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, timeout=DEFAULT_TIMEOUT) as response:
                print(f"Webhook sent. Status: {response.status}")
                if callback:
                    callback(True, json.dumps(response.json(), default=str))
        except aiohttp.ClientError as e:
            print(f"Error sending webhook: {e}")
            if callback:
                callback(False, str(e))


def run_async_task(url, payload, callback=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_webhook_async(url, payload, callback))


def trigger_webhook(url, payload, callback=None):
    webhook_url = url 
    payload = payload or {"message": "Hello from Asset Manager!"}

    executor.submit(run_async_task, webhook_url, payload, callback)

