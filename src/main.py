import asyncio
import json

import aiohttp


async def fetch_url(url, session, semaphore):
    async with semaphore:
        try:
            async with session.get(url) as response:
                return {'url': url, 'status_code': response.status}
        except aiohttp.ClientError:
            return {"url": url, "status_code": 0}


async def fetch_urls(urls: list[str], file_path: str):
    semaphore = asyncio.Semaphore(5)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(url, session, semaphore) for url in urls]
        results = await asyncio.gather(*tasks)

    with open(file_path, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')

if __name__ == '__main__':
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
        "https://keyauto.m4.systems/#/desktop"
    ]
    asyncio.run(fetch_urls(urls, './results.jsonl'))
