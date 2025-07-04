from pydantic import BaseModel, HttpUrl


class SinglePageScrapperTask(BaseModel):
    url: HttpUrl


class SitemapCollectScrapperTask(BaseModel):
    url: HttpUrl
