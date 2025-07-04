import mimetypes
import hashlib

from functools import cache
from urllib.parse import urljoin, urlparse

from scrapy import Spider, Request
from scrapy.http import Response

from scrapper.items import FileItem, ScrappedItem, Metadata


class SitemapCollectSpider(Spider):
    name = 'sitemap_collect_spider'
    # start_urls = ['https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf']
    # start_urls = ['https://calibre-ebook.com/downloads/demos/demo.docx']
    start_urls = [
        # "https://www.terviseamet.ee",
        # "https://www.tervisekassa.ee",
        # "https://www.ravimiamet.ee",
        # "https://www.sm.ee",
        # "https://www.sotsiaalkindlustusamet.ee",
        # "https://www.tootukassa.ee", #?????????????????
        # "https://www.transpordiamet.ee", # ??????????????  -- requires selenium
        # "https://elron.ee/",
        # "https://www.airport.ee",
        # "https://www.ts.ee",??????????????
       # "https://www.lkf.ee/et",
       #  "https://www.fi.ee",
       #  "https://www.eestipank.ee",
       #  "https://www.kredex.ee",
       #  "https://www.emta.ee",
       #  "https://www.fin.ee",
    #     "https://www.ti.ee",
    #     "https://www.eakl.ee",
    #     "https://www.tooelu.ee",
    #     "https://www.minukarjaar.ee",
    #     "https://www.just.ee",
    #     "https://www.notar.ee",
    #     "https://www.kohus.ee",
    #     "https://www.kpkoda.ee",
    #     "https://www.riigiteataja.ee",
    #     "https://www.korruptsioon.ee",
    #     "https://www.maaamet.ee",
    #     "https://www.tallinn.ee/et/ehitus",
    #     "https://www.hm.ee",
    #     "https://www.harno.ee",
    #     "https://www.politsei.ee",
    #     "https://www.valimised.ee",
    #     "https://integratsioon.ee/",
    #     "https://www.siseministeerium",
    #     "https://www.tja.ee",
    #     "https://www.kaitseministeerium.ee",
    #     "https://www.mil.ee",
    #     "https://www.kaitseliit.ee",
    #     "https://www.kriis.ee",
    #     "https://www.rescue.ee",
    #     "https://www.kapo.ee",
    #     "https://www.kul.ee",
    #     "https://www.kik.ee",
    #     "https://www.envir.ee",
    #     "https://www.keskkonnaagentuur.ee",
    #     "https://www.keskkonnaamet.ee",
    #     "https://www.pria.ee",
    #     "https://www.agri.ee",
    #     "https://www.peaasi.ee",
    #     "https://www.lasteabi.ee",
    #     "https://www.vaimnetervis.ee",
    #     "https://koolirahu.lastekaitseliit.ee/et/",
    #     "https://www.itvaatlik.ee",
    #     "https://www.riigikogu.ee",
    #     "https://www.muinsuskaitseamet.ee",
    #     "https://www.eesti.ee",
    #     "https://www.epa.ee",
    ]
    # custom_settings = {
    #     'ROBOTSTXT_OBEY': False
    # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.visited_urls = set()
        self.valid_urls = set()
        self.hashes = set()

    def get_pure_domain(self, url: str) -> str:
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        if netloc is None:
            return ''

        return '.'.join(netloc.split('.')[-2:])

    @property
    @cache
    def pure_allowed_domains(self):
        pure_domains = [self.get_pure_domain(url) for url in self.start_urls]
        return pure_domains

    def guess_file_extension(self, content_type: str) -> str:
        pure_content_type = content_type.split(';')[0]
        guessed_extension = mimetypes.guess_extension(pure_content_type)
        return guessed_extension

    def parse(self, response: Response, **kwargs):
        self.visited_urls.add(response.url)

        file_extension = self.guess_file_extension(
            response.headers.get(b'Content-Type', 'text/html').decode('utf-8')
        )
        if file_extension not in self.settings.get('ALLOWED_FILETYPES'):
            # TODO: place log here
            return
        self.valid_urls.add(response.url)
        hashed = hashlib.sha1(response.body).hexdigest()
        if hashed in self.hashes:
            return
        self.hashes.add(hashed)

        yield FileItem(body=response.body, source_url=response.url, extension=file_extension)

        yield ScrappedItem(file_type=file_extension, metadata=Metadata(), source_url=response.url)

        if file_extension != '.html':
            return

        for href in response.css("a::attr(href)").getall():
            next_url = urljoin(response.url, href)
            next_url = next_url.split('#')[0]

            # Only follow links within allowed_domains
            if self.get_pure_domain(next_url) not in self.pure_allowed_domains:
                continue

            if next_url not in self.visited_urls:
                yield Request(next_url, callback=self.parse)
