import asyncio
from scrapy import Request, Spider
from scrapy.http import Response
from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler


class DownloadHandler(ScrapyPlaywrightDownloadHandler):
    async def _download_request(self, request: Request, spider: Spider) -> Response:
        try:
            spider.logger.info(f'request started: {request.url}')
            async with asyncio.timeout(30):
                r = await super()._download_request(request, spider)
                spider.logger.info(f'request finished: {request.url}')
                return r
        except TimeoutError:
            spider.logger.warning(f'request timed out due to playwright: {request.url}. Try again')
            return await self._download_request(request, spider)
