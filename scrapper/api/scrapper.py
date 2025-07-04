import subprocess
import shlex

from api.models import SinglePageScrapperTask, SitemapCollectScrapperTask


def single_page_scrapper_task(task: SinglePageScrapperTask):
    dumped_version = task.model_dump_json()
    escaped_version = shlex.quote(dumped_version)

    p = subprocess.Popen(['python', 'run_single_page_scrapper.py', escaped_version])
    p.wait()
    # todo: catch logs here


def sitemap_collect_scrapper_task(task: SitemapCollectScrapperTask):
    dumped_version = task.model_dump_json()
    escaped_version = shlex.quote(dumped_version)

    p = subprocess.Popen(['python', 'run_sitemap_collect_scrapper.py', escaped_version])
    p.wait()
