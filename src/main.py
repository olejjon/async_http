import aiohttp
import asyncio
import aiofiles
import json

MAX_CONCURRENT_REQUESTS = 5


async def fetch_url(session, url):
    try:
        async with session.get(
            url, timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            return url, response.status
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error fetching {url}: {e}")
        return url, 0


async def worker(session, queue, results):
    while True:
        url = await queue.get()
        if url is None:
            break
        result = await fetch_url(session, url)
        results.append(result)
        queue.task_done()


async def fetch_urls(urls: list[str], file_path: str):
    queue = asyncio.Queue()
    results = []

    async with aiohttp.ClientSession() as session:
        workers = [
            asyncio.create_task(worker(session, queue, results))
            for _ in range(MAX_CONCURRENT_REQUESTS)
        ]

        for url in urls:
            await queue.put(url)

        await queue.join()

        for _ in range(MAX_CONCURRENT_REQUESTS):
            await queue.put(None)
        await asyncio.gather(*workers)

    async with aiofiles.open(file_path, mode="w") as out_f:
        for url, status_code in results:
            result = {"url": url, "status_code": status_code}
            await out_f.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
        "https://keyauto.m4.systems/#/desktop",
    ]
    asyncio.run(fetch_urls(urls, "./results.jsonl"))
