import shlex
import subprocess

from celery import Celery

from api.config import settings
from api.models import SpecifiedLinksScrapeTask, SitemapCollectScrapperTask, EntireSourceScrapperTask
from worker.utils import un_json

app = Celery('ckb', broker=settings.broker_url.unicode_string())

# app.conf.update(
#     task_serializer='pickle',
#     result_serializer='pickle',
#     accept_content=['pickle'],
# )


@app.task
@un_json(SpecifiedLinksScrapeTask)
def specified_links_scrapper_task(task: SpecifiedLinksScrapeTask):
    dumped_version = task.model_dump_json()
    escaped_version = shlex.quote(dumped_version)

    p = subprocess.Popen(['python', 'run_specified_links_scrapper.py', escaped_version])
    p.wait()
    # todo: catch logs here


@app.task
@un_json(SitemapCollectScrapperTask)
def sitemap_collect_scrapper_task(task: SitemapCollectScrapperTask):
    dumped_version = task.model_dump_json()
    escaped_version = shlex.quote(dumped_version)

    p = subprocess.Popen(['python', 'run_sitemap_collect_scrapper.py', escaped_version])
    p.wait()


@app.task
@un_json(EntireSourceScrapperTask)
def entire_source_scrapped_task(task: EntireSourceScrapperTask):
    dumped_version = task.model_dump_json()
    escaped_version = shlex.quote(dumped_version)

    p = subprocess.Popen(['python', 'run_entire_source_scrapper.py', escaped_version])
    p.wait()