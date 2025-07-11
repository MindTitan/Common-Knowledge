from pydantic import BaseModel, HttpUrl


class BaseObject(BaseModel):
    agency_name: str
    agency_id: str
    source_name: str
    source_id: str


class SpecifiedLinksScrapeTask(BaseObject):
    urls: list[HttpUrl]


class SitemapCollectScrapperTask(BaseObject):
    url: HttpUrl
