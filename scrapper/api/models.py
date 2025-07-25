from pydantic import BaseModel, HttpUrl


class BaseObject(BaseModel):
    agency_name: str
    agency_id: str
    source_name: str
    source_id: str


class LinkToScrape(BaseModel):
    url: HttpUrl
    id: str
    hash: str


class SpecifiedLinksScrapeTask(BaseObject):
    urls: list[LinkToScrape]


class SitemapCollectScrapperTask(BaseObject):
    url: HttpUrl


class EntireSourceScrapperTask(BaseObject):
    pass
